"""
Basic Web Scraper using requests + BeautifulSoup
Install dependencies:
    pip install requests beautifulsoup4
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time


# ── helpers ──────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def get_soup(url: str, delay: float = 1.0) -> BeautifulSoup | None:
    """Fetch a URL and return a BeautifulSoup object, or None on failure."""
    try:
        time.sleep(delay)                          # be polite — don't hammer servers
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()                # raise on 4xx / 5xx
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"[ERROR] Could not fetch {url}: {e}")
        return None


# ── example 1: scrape page title & all headings ───────────────────────────────

def scrape_headings(url: str) -> dict:
    """
    Extract the page title and every h1–h3 heading from a URL.

    Example:
        data = scrape_headings("https://example.com")
    """
    soup = get_soup(url)
    if not soup:
        return {}

    title = soup.title.string.strip() if soup.title else "No title"

    headings = []
    for tag in ["h1", "h2", "h3"]:
        for el in soup.find_all(tag):
            text = el.get_text(strip=True)
            if text:
                headings.append({"level": tag, "text": text})

    return {"url": url, "title": title, "headings": headings}


# ── example 2: scrape all links from a page ───────────────────────────────────

def scrape_links(url: str) -> list[dict]:
    """
    Extract all <a> tags — returns href + anchor text.

    Example:
        links = scrape_links("https://example.com")
    """
    soup = get_soup(url)
    if not soup:
        return []

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(strip=True) or "(no text)"
        if href and not href.startswith("#"):       # skip in-page anchors
            links.append({"text": text, "href": href})

    print(f"Found {len(links)} links on {url}")
    return links


# ── example 3: scrape a table from a page ─────────────────────────────────────

def scrape_table(url: str, table_index: int = 0) -> list[dict]:
    """
    Parse an HTML <table> into a list of dicts (first row = header).

    Example:
        rows = scrape_table("https://en.wikipedia.org/wiki/Python_(programming_language)", 0)
    """
    soup = get_soup(url)
    if not soup:
        return []

    tables = soup.find_all("table")
    if not tables:
        print("[INFO] No tables found on this page.")
        return []

    if table_index >= len(tables):
        print(f"[INFO] Only {len(tables)} table(s) found; using index 0.")
        table_index = 0

    table = tables[table_index]
    rows = table.find_all("tr")

    # first row → headers
    headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
    if not headers:
        return []

    data = []
    for row in rows[1:]:
        cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
        if cells:
            # zip with headers; pad if row is shorter
            record = dict(zip(headers, cells + [""] * (len(headers) - len(cells))))
            data.append(record)

    print(f"Scraped {len(data)} row(s) from table #{table_index}")
    return data


# ── example 4: scrape quotes from quotes.toscrape.com ────────────────────────

def scrape_quotes(pages: int = 1) -> list[dict]:
    """
    Scrape quotes from https://quotes.toscrape.com (a practice scraping site).
    Set pages > 1 to paginate.

    Example:
        quotes = scrape_quotes(pages=2)
    """
    base_url = "https://quotes.toscrape.com/page/{}/"
    all_quotes = []

    for page in range(1, pages + 1):
        url = base_url.format(page)
        soup = get_soup(url)
        if not soup:
            break

        quote_divs = soup.find_all("div", class_="quote")
        if not quote_divs:
            print(f"[INFO] No quotes found on page {page}; stopping.")
            break

        for div in quote_divs:
            text   = div.find("span", class_="text").get_text(strip=True)
            author = div.find("small", class_="author").get_text(strip=True)
            tags   = [t.get_text(strip=True) for t in div.find_all("a", class_="tag")]
            all_quotes.append({"quote": text, "author": author, "tags": tags})

        print(f"Page {page}: scraped {len(quote_divs)} quotes")

    return all_quotes


# ── export helpers ─────────────────────────────────────────────────────────────

def save_csv(data: list[dict], filename: str) -> None:
    """Save a list of dicts to a CSV file."""
    if not data:
        print("[WARN] No data to save.")
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved {len(data)} rows → {filename}")


def save_json(data, filename: str) -> None:
    """Save any JSON-serialisable object to a file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved → {filename}")


# ── main demo ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # --- 1. headings from example.com ---
    print("\n=== Example 1: Page headings ===")
    data = scrape_headings("https://example.com")
    print(f"Title : {data.get('title')}")
    for h in data.get("headings", []):
        print(f"  [{h['level']}] {h['text']}")

    # --- 2. links from example.com ---
    print("\n=== Example 2: Links ===")
    links = scrape_links("https://example.com")
    for link in links[:5]:                         # show first 5
        print(f"  {link['text']:30s}  {link['href']}")

    # --- 3. quotes (paginated) ---
    print("\n=== Example 3: Quotes (2 pages) ===")
    quotes = scrape_quotes(pages=2)
    for q in quotes[:3]:                           # show first 3
        print(f"  {q['author']:20s} — {q['quote'][:60]}…")

    # --- save to files ---
    save_csv(quotes, "quotes.csv")
    save_json(quotes, "quotes.json")
    save_json(links,  "links.json")

    print("\nDone.")