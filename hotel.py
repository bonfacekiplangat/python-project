"""
Hotel Management System
=======================
A terminal-based CLI app for managing hotel room bookings, check-ins, and check-outs.
Data is persisted to a local SQLite database (hotel.db).
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import Optional

DB_FILE = "hotel.db"

# ─────────────────────────────────────────────
# ANSI Color Helpers
# ─────────────────────────────────────────────
R  = "\033[0m"       # Reset
B  = "\033[1m"       # Bold
CY = "\033[96m"      # Cyan
GR = "\033[92m"      # Green
YL = "\033[93m"      # Yellow
RD = "\033[91m"      # Red
BL = "\033[94m"      # Blue
MG = "\033[95m"      # Magenta

def color(text, c): return f"{c}{text}{R}"
def bold(text):     return f"{B}{text}{R}"
def hr(char="─", width=58): print(color(char * width, CY))
def header(title):
    hr()
    print(color(f"  🏨  {title}", CY + B))
    hr()

# ─────────────────────────────────────────────
# Database Setup
# ─────────────────────────────────────────────
def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_number  TEXT PRIMARY KEY,
                room_type    TEXT NOT NULL,
                capacity     INTEGER NOT NULL,
                price_per_night REAL NOT NULL,
                status       TEXT NOT NULL DEFAULT 'available'
            );

            CREATE TABLE IF NOT EXISTS guests (
                guest_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name   TEXT NOT NULL,
                id_number   TEXT NOT NULL,
                phone       TEXT,
                email       TEXT
            );

            CREATE TABLE IF NOT EXISTS bookings (
                booking_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number     TEXT NOT NULL,
                guest_id        INTEGER NOT NULL,
                check_in_date   TEXT NOT NULL,
                check_out_date  TEXT NOT NULL,
                status          TEXT NOT NULL DEFAULT 'booked',
                total_amount    REAL,
                created_at      TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (room_number) REFERENCES rooms(room_number),
                FOREIGN KEY (guest_id)    REFERENCES guests(guest_id)
            );
        """)
        # Seed rooms if table is empty
        existing = c.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
        if existing == 0:
            seed_rooms(c)
        conn.commit()

def seed_rooms(cursor):
    rooms = [
        ("101", "Single",  1, 3500),
        ("102", "Single",  1, 3500),
        ("103", "Single",  1, 3500),
        ("201", "Double",  2, 5500),
        ("202", "Double",  2, 5500),
        ("203", "Double",  2, 5500),
        ("301", "Suite",   4, 12000),
        ("302", "Suite",   4, 12000),
        ("401", "Penthouse", 6, 25000),
    ]
    cursor.executemany(
        "INSERT INTO rooms (room_number, room_type, capacity, price_per_night) VALUES (?,?,?,?)",
        rooms
    )

# ─────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────
def prompt(label, required=True):
    while True:
        val = input(f"  {color('›', YL)} {label}: ").strip()
        if val or not required:
            return val
        print(color("  ✗ This field is required.", RD))

def confirm(message):
    ans = input(f"  {color('?', YL)} {message} (y/n): ").strip().lower()
    return ans == "y"

def parse_date(s):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None

def nights_between(ci, co):
    return (co - ci).days

def format_ksh(amount):
    return f"KSh {amount:,.2f}"

def status_badge(status):
    badges = {
        "available":   color("● available",   GR),
        "occupied":    color("● occupied",    RD),
        "booked":      color("● booked",      BL),
        "checked_in":  color("● checked-in",  YL),
        "checked_out": color("● checked-out", MG),
        "cancelled":   color("● cancelled",   RD),
    }
    return badges.get(status, status)

def press_enter():
    input(f"\n  {color('↵  Press Enter to continue...', CY)}")

# ─────────────────────────────────────────────
# Room Operations
# ─────────────────────────────────────────────
def list_rooms(filter_status=None):
    header("Room Directory")
    with get_connection() as conn:
        c = conn.cursor()
        if filter_status:
            rows = c.execute(
                "SELECT room_number, room_type, capacity, price_per_night, status "
                "FROM rooms WHERE status=? ORDER BY room_number", (filter_status,)
            ).fetchall()
        else:
            rows = c.execute(
                "SELECT room_number, room_type, capacity, price_per_night, status "
                "FROM rooms ORDER BY room_number"
            ).fetchall()

    if not rows:
        print(color("  No rooms found.", YL))
    else:
        print(f"  {'Room':>6}  {'Type':<12} {'Capacity':>8}  {'Rate/Night':>14}  Status")
        hr("─")
        for room_number, rtype, cap, price, status in rows:
            print(f"  {bold(room_number):>6}  {rtype:<12} {cap:>8}  {format_ksh(price):>14}  {status_badge(status)}")
    press_enter()

# ─────────────────────────────────────────────
# Guest Operations
# ─────────────────────────────────────────────
def add_guest(conn, name, id_number, phone="", email=""):
    c = conn.cursor()
    c.execute(
        "INSERT INTO guests (full_name, id_number, phone, email) VALUES (?,?,?,?)",
        (name, id_number, phone, email)
    )
    return c.lastrowid

def find_or_create_guest(conn):
    """Search for existing guest or create a new one."""
    print(f"\n  {bold('Guest Information')}")
    id_number = prompt("Guest ID / Passport number")
    c = conn.cursor()
    row = c.execute("SELECT guest_id, full_name FROM guests WHERE id_number=?", (id_number,)).fetchone()
    if row:
        print(color(f"  ✓ Returning guest found: {row[1]}", GR))
        return row[0]
    print(color("  ℹ New guest — please enter details.", BL))
    name  = prompt("Full name")
    phone = prompt("Phone number", required=False)
    email = prompt("Email address", required=False)
    gid   = add_guest(conn, name, id_number, phone, email)
    print(color(f"  ✓ Guest registered with ID #{gid}.", GR))
    return gid

# ─────────────────────────────────────────────
# Booking
# ─────────────────────────────────────────────
def make_booking():
    header("New Booking")
    with get_connection() as conn:
        c = conn.cursor()

        # Show available rooms
        avail = c.execute(
            "SELECT room_number, room_type, capacity, price_per_night "
            "FROM rooms WHERE status='available' ORDER BY room_number"
        ).fetchall()
        if not avail:
            print(color("  ✗ No rooms are currently available.", RD))
            press_enter()
            return

        print(f"  {'Room':>6}  {'Type':<12} {'Cap':>4}  {'Rate/Night':>14}")
        hr("─")
        for rno, rtype, cap, price in avail:
            print(f"  {bold(rno):>6}  {rtype:<12} {cap:>4}  {format_ksh(price):>14}")

        # Choose room
        print()
        room_no = prompt("Enter room number").upper()
        room = c.execute(
            "SELECT room_type, price_per_night, status FROM rooms WHERE room_number=?", (room_no,)
        ).fetchone()
        if not room:
            print(color("  ✗ Room not found.", RD)); press_enter(); return
        if room[2] != "available":
            print(color(f"  ✗ Room {room_no} is not available ({room[2]}).", RD)); press_enter(); return

        rtype, price, _ = room

        # Dates
        print()
        while True:
            ci_str = prompt("Check-in date  (YYYY-MM-DD)")
            ci = parse_date(ci_str)
            if ci: break
            print(color("  ✗ Invalid date format.", RD))

        while True:
            co_str = prompt("Check-out date (YYYY-MM-DD)")
            co = parse_date(co_str)
            if co and co > ci: break
            print(color("  ✗ Check-out must be after check-in.", RD))

        nights = nights_between(ci, co)
        total  = nights * price

        # Summary
        print()
        hr("─")
        print(f"  Room    : {bold(room_no)} ({rtype})")
        print(f"  Dates   : {ci} → {co}  ({nights} night{'s' if nights > 1 else ''})")
        print(f"  Total   : {color(format_ksh(total), GR)}")
        hr("─")

        if not confirm("Confirm this booking?"): 
            print(color("  Booking cancelled.", YL)); press_enter(); return

        guest_id = find_or_create_guest(conn)

        c.execute(
            "INSERT INTO bookings (room_number, guest_id, check_in_date, check_out_date, status, total_amount) "
            "VALUES (?,?,?,?,?,?)",
            (room_no, guest_id, str(ci), str(co), "booked", total)
        )
        booking_id = c.lastrowid
        c.execute("UPDATE rooms SET status='booked' WHERE room_number=?", (room_no,))
        conn.commit()

        print(color(f"\n  ✓ Booking #{booking_id} confirmed!", GR))
        press_enter()

# ─────────────────────────────────────────────
# Check-In
# ─────────────────────────────────────────────
def check_in():
    header("Guest Check-In")
    room_no = prompt("Room number").upper()
    with get_connection() as conn:
        c = conn.cursor()
        booking = c.execute(
            """SELECT b.booking_id, g.full_name, b.check_in_date, b.check_out_date, b.total_amount, b.status
               FROM bookings b JOIN guests g ON b.guest_id = g.guest_id
               WHERE b.room_number=? AND b.status='booked'
               ORDER BY b.check_in_date LIMIT 1""", (room_no,)
        ).fetchone()

        if not booking:
            print(color(f"  ✗ No confirmed booking found for room {room_no}.", RD))
            press_enter(); return

        bid, gname, ci, co, total, _ = booking
        print(f"\n  Booking #{bid}")
        print(f"  Guest   : {bold(gname)}")
        print(f"  Dates   : {ci} → {co}")
        print(f"  Total   : {color(format_ksh(total), GR)}")

        if not confirm("Proceed with check-in?"):
            press_enter(); return

        c.execute("UPDATE bookings SET status='checked_in' WHERE booking_id=?", (bid,))
        c.execute("UPDATE rooms SET status='occupied' WHERE room_number=?", (room_no,))
        conn.commit()
        print(color(f"\n  ✓ {gname} has been checked in to room {room_no}.", GR))
    press_enter()

# ─────────────────────────────────────────────
# Check-Out
# ─────────────────────────────────────────────
def check_out():
    header("Guest Check-Out")
    room_no = prompt("Room number").upper()
    with get_connection() as conn:
        c = conn.cursor()
        booking = c.execute(
            """SELECT b.booking_id, g.full_name, b.check_in_date, b.check_out_date, b.total_amount
               FROM bookings b JOIN guests g ON b.guest_id = g.guest_id
               WHERE b.room_number=? AND b.status='checked_in'""", (room_no,)
        ).fetchone()

        if not booking:
            print(color(f"  ✗ No active check-in found for room {room_no}.", RD))
            press_enter(); return

        bid, gname, ci, co, total = booking
        today = date.today()
        planned_co = parse_date(co)
        nights_actual = nights_between(parse_date(ci), today)

        room_info = c.execute("SELECT price_per_night FROM rooms WHERE room_number=?", (room_no,)).fetchone()
        price = room_info[0]
        amount_due = nights_actual * price

        late = today > planned_co
        extra_nights = (today - planned_co).days if late else 0

        print(f"\n  Booking #{bid}")
        print(f"  Guest        : {bold(gname)}")
        print(f"  Checked in   : {ci}")
        print(f"  Planned out  : {co}")
        print(f"  Today        : {today}")
        print(f"  Nights stayed: {nights_actual}")
        if late:
            print(color(f"  ⚠  Late check-out: {extra_nights} extra night(s)", YL))
        hr("─")
        print(f"  Amount Due   : {color(format_ksh(amount_due), GR)}")
        hr("─")

        if not confirm("Confirm check-out and generate invoice?"):
            press_enter(); return

        c.execute(
            "UPDATE bookings SET status='checked_out', total_amount=?, check_out_date=? WHERE booking_id=?",
            (amount_due, str(today), bid)
        )
        c.execute("UPDATE rooms SET status='available' WHERE room_number=?", (room_no,))
        conn.commit()

        print_invoice(gname, room_no, ci, str(today), nights_actual, price, amount_due, bid)
    press_enter()

def print_invoice(gname, room_no, ci, co, nights, rate, total, booking_id):
    hr("═")
    print(color(f"  {'HOTEL INVOICE':^54}", CY + B))
    hr("═")
    print(f"  Invoice #  : INV-{booking_id:04d}")
    print(f"  Date       : {date.today()}")
    hr("─")
    print(f"  Guest      : {bold(gname)}")
    print(f"  Room       : {room_no}")
    print(f"  Check-in   : {ci}")
    print(f"  Check-out  : {co}")
    print(f"  Nights     : {nights}")
    hr("─")
    print(f"  Rate/night : {format_ksh(rate)}")
    print(f"  {nights} × {format_ksh(rate):<20}")
    hr("─")
    print(f"  {bold('TOTAL DUE'):<20}: {color(format_ksh(total), GR + B)}")
    hr("═")
    print(color("  Thank you for staying with us!", MG))
    hr("═")

# ─────────────────────────────────────────────
# View Bookings
# ─────────────────────────────────────────────
def view_bookings():
    header("All Bookings")
    with get_connection() as conn:
        c = conn.cursor()
        rows = c.execute(
            """SELECT b.booking_id, b.room_number, g.full_name, b.check_in_date,
                      b.check_out_date, b.status, b.total_amount
               FROM bookings b JOIN guests g ON b.guest_id = g.guest_id
               ORDER BY b.created_at DESC"""
        ).fetchall()

    if not rows:
        print(color("  No bookings found.", YL))
    else:
        print(f"  {'ID':>4}  {'Room':>6}  {'Guest':<20} {'Check-in':<12} {'Check-out':<12} {'Amount':>14}  Status")
        hr("─")
        for bid, rno, gname, ci, co, status, amt in rows:
            amt_str = format_ksh(amt) if amt else "—"
            print(f"  {bid:>4}  {rno:>6}  {gname:<20} {ci:<12} {co:<12} {amt_str:>14}  {status_badge(status)}")
    press_enter()

# ─────────────────────────────────────────────
# Cancel Booking
# ─────────────────────────────────────────────
def cancel_booking():
    header("Cancel Booking")
    try:
        bid = int(prompt("Booking ID to cancel"))
    except ValueError:
        print(color("  ✗ Invalid booking ID.", RD)); press_enter(); return

    with get_connection() as conn:
        c = conn.cursor()
        booking = c.execute(
            """SELECT b.room_number, g.full_name, b.status
               FROM bookings b JOIN guests g ON b.guest_id=g.guest_id
               WHERE b.booking_id=?""", (bid,)
        ).fetchone()

        if not booking:
            print(color("  ✗ Booking not found.", RD)); press_enter(); return

        room_no, gname, status = booking
        if status not in ("booked",):
            print(color(f"  ✗ Cannot cancel a booking with status '{status}'.", RD))
            press_enter(); return

        print(f"\n  Booking #{bid} — {gname} — Room {room_no}")
        if not confirm("Cancel this booking?"):
            press_enter(); return

        c.execute("UPDATE bookings SET status='cancelled' WHERE booking_id=?", (bid,))
        c.execute("UPDATE rooms SET status='available' WHERE room_number=?", (room_no,))
        conn.commit()
        print(color(f"\n  ✓ Booking #{bid} cancelled. Room {room_no} is now available.", GR))
    press_enter()

# ─────────────────────────────────────────────
# Dashboard Summary
# ─────────────────────────────────────────────
def dashboard():
    header("Dashboard Summary")
    with get_connection() as conn:
        c = conn.cursor()
        total_rooms    = c.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
        available      = c.execute("SELECT COUNT(*) FROM rooms WHERE status='available'").fetchone()[0]
        occupied       = c.execute("SELECT COUNT(*) FROM rooms WHERE status='occupied'").fetchone()[0]
        booked         = c.execute("SELECT COUNT(*) FROM rooms WHERE status='booked'").fetchone()[0]
        total_bookings = c.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        active         = c.execute("SELECT COUNT(*) FROM bookings WHERE status IN ('booked','checked_in')").fetchone()[0]
        revenue        = c.execute("SELECT SUM(total_amount) FROM bookings WHERE status='checked_out'").fetchone()[0] or 0

    occ_rate = ((occupied + booked) / total_rooms * 100) if total_rooms else 0
    bar_len  = int(occ_rate / 5)
    occ_bar  = color("█" * bar_len, GR) + color("░" * (20 - bar_len), RD)

    print(f"  {'Total Rooms':<24}: {bold(str(total_rooms))}")
    print(f"  {'Available':<24}: {color(str(available), GR)}")
    print(f"  {'Occupied':<24}: {color(str(occupied),  RD)}")
    print(f"  {'Booked (upcoming)':<24}: {color(str(booked),   BL)}")
    hr("─")
    print(f"  {'Occupancy Rate':<24}: {occ_bar}  {occ_rate:.1f}%")
    hr("─")
    print(f"  {'Total Bookings':<24}: {total_bookings}")
    print(f"  {'Active Bookings':<24}: {active}")
    print(f"  {'Revenue (check-outs)':<24}: {color(format_ksh(revenue), GR)}")
    hr()
    press_enter()

# ─────────────────────────────────────────────
# Main Menu
# ─────────────────────────────────────────────
MENU = [
    ("1", "📋  View All Rooms",        list_rooms),
    ("2", "🔍  Available Rooms Only",  lambda: list_rooms("available")),
    ("3", "📅  Make a Booking",        make_booking),
    ("4", "✅  Check In Guest",        check_in),
    ("5", "🚪  Check Out Guest",       check_out),
    ("6", "📜  View All Bookings",     view_bookings),
    ("7", "❌  Cancel Booking",        cancel_booking),
    ("8", "📊  Dashboard Summary",     dashboard),
    ("0", "🚪  Exit",                  None),
]

def main_menu():
    os.system("clear" if os.name == "posix" else "cls")
    header("GRAND HORIZON HOTEL — Management System")
    for key, label, _ in MENU:
        bullet = color(f"  [{key}]", YL)
        print(f"{bullet}  {label}")
    hr()
    return input(f"  {color('Choose an option:', CY)} ").strip()

def main():
    init_db()
    while True:
        choice = main_menu()
        action = {k: fn for k, _, fn in MENU}.get(choice)
        if choice == "0":
            print(color("\n  Goodbye! Have a great day. 👋\n", GR))
            break
        elif action:
            os.system("clear" if os.name == "posix" else "cls")
            action()
        else:
            print(color("  ✗ Invalid option. Try again.", RD))
            import time; time.sleep(1)

if __name__ == "__main__":
    main()