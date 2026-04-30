#!/usr/bin/env python3
"""
Simple Command-Line Calculator
Supports basic arithmetic and advanced operations.
"""

import math


def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Error: Division by zero is not allowed.")
    return a / b

def power(a, b):
    return a ** b

def square_root(a):
    if a < 0:
        raise ValueError("Error: Cannot take square root of a negative number.")
    return math.sqrt(a)

def modulo(a, b):
    if b == 0:
        raise ValueError("Error: Modulo by zero is not allowed.")
    return a % b


def get_number(prompt):
    """Prompt the user for a number, with error handling."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  Invalid input. Please enter a numeric value.")


def display_menu():
    print("\n" + "=" * 40)
    print("         PYTHON CALCULATOR")
    print("=" * 40)
    print("  1. Add              (+)")
    print("  2. Subtract         (-)")
    print("  3. Multiply         (*)")
    print("  4. Divide           (/)")
    print("  5. Power            (^)")
    print("  6. Square Root      (√)")
    print("  7. Modulo           (%)")
    print("  0. Exit")
    print("=" * 40)


def format_result(value):
    """Display as integer if result is a whole number."""
    return int(value) if value == int(value) else value


def main():
    print("\nWelcome to the Python Calculator!")

    while True:
        display_menu()
        choice = input("  Select an option: ").strip()

        if choice == "0":
            print("\nGoodbye! 👋\n")
            break

        elif choice in ("1", "2", "3", "4", "5", "7"):
            a = get_number("  Enter first number:  ")
            b = get_number("  Enter second number: ")

            try:
                ops = {
                    "1": (add,      "+"),
                    "2": (subtract, "-"),
                    "3": (multiply, "×"),
                    "4": (divide,   "÷"),
                    "5": (power,    "^"),
                    "7": (modulo,   "%"),
                }
                func, symbol = ops[choice]
                result = func(a, b)
                print(f"\n  ✔  {format_result(a)} {symbol} {format_result(b)} = {format_result(result)}")
            except ValueError as e:
                print(f"\n  ✘  {e}")

        elif choice == "6":
            a = get_number("  Enter number: ")
            try:
                result = square_root(a)
                print(f"\n  ✔  √{format_result(a)} = {format_result(result)}")
            except ValueError as e:
                print(f"\n  ✘  {e}")

        else:
            print("\n  ✘  Invalid option. Please choose from the menu.")


if __name__ == "__main__":
    main()