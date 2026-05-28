import random
import string
import argparse


def generate_password(
    length: int = 12,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> str:
    """
    Generate a random password with the given options.

    Args:
        length:            Number of characters in the password.
        use_uppercase:     Include uppercase letters (A-Z).
        use_lowercase:     Include lowercase letters (a-z).
        use_digits:        Include digits (0-9).
        use_symbols:       Include special characters (!@#$ …).
        exclude_ambiguous: Exclude characters that look alike (0, O, l, 1, I).

    Returns:
        A randomly generated password string.

    Raises:
        ValueError: If no character sets are selected or length < 4.
    """
    if length < 4:
        raise ValueError("Password length must be at least 4.")

    AMBIGUOUS = set("0Ol1I")

    pool = ""
    required_chars = []

    if use_uppercase:
        chars = string.ascii_uppercase
        if exclude_ambiguous:
            chars = "".join(c for c in chars if c not in AMBIGUOUS)
        pool += chars
        required_chars.append(random.choice(chars))

    if use_lowercase:
        chars = string.ascii_lowercase
        if exclude_ambiguous:
            chars = "".join(c for c in chars if c not in AMBIGUOUS)
        pool += chars
        required_chars.append(random.choice(chars))

    if use_digits:
        chars = string.digits
        if exclude_ambiguous:
            chars = "".join(c for c in chars if c not in AMBIGUOUS)
        pool += chars
        required_chars.append(random.choice(chars))

    if use_symbols:
        chars = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        pool += chars
        required_chars.append(random.choice(chars))

    if not pool:
        raise ValueError("At least one character set must be selected.")

    # Fill remaining slots from the full pool
    remaining = [random.choice(pool) for _ in range(length - len(required_chars))]

    # Combine required + remaining, then shuffle
    password_list = required_chars + remaining
    random.shuffle(password_list)

    return "".join(password_list)


def generate_multiple(count: int, **kwargs) -> list[str]:
    """Generate multiple passwords with the same settings."""
    return [generate_password(**kwargs) for _ in range(count)]


def password_strength(password: str) -> str:
    """Return a simple strength rating: Weak / Fair / Strong / Very Strong."""
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password):
        score += 1

    if score <= 2:
        return "Weak"
    elif score <= 3:
        return "Fair"
    elif score <= 4:
        return "Strong"
    else:
        return "Very Strong"


def main():
    parser = argparse.ArgumentParser(description="Secure Password Generator")
    parser.add_argument("-l", "--length",     type=int,  default=12,    help="Password length (default: 12)")
    parser.add_argument("-n", "--count",      type=int,  default=1,     help="Number of passwords to generate (default: 1)")
    parser.add_argument("--no-uppercase",     action="store_true",      help="Exclude uppercase letters")
    parser.add_argument("--no-lowercase",     action="store_true",      help="Exclude lowercase letters")
    parser.add_argument("--no-digits",        action="store_true",      help="Exclude digits")
    parser.add_argument("--no-symbols",       action="store_true",      help="Exclude symbols")
    parser.add_argument("--no-ambiguous",     action="store_true",      help="Exclude ambiguous characters (0, O, l, 1, I)")
    args = parser.parse_args()

    options = dict(
        length=args.length,
        use_uppercase=not args.no_uppercase,
        use_lowercase=not args.no_lowercase,
        use_digits=not args.no_digits,
        use_symbols=not args.no_symbols,
        exclude_ambiguous=args.no_ambiguous,
    )

    passwords = generate_multiple(args.count, **options)

    print(f"\n{'─' * 40}")
    print(f"  Generated {args.count} password(s)  |  length: {args.length}")
    print(f"{'─' * 40}")
    for i, pw in enumerate(passwords, 1):
        strength = password_strength(pw)
        print(f"  {i:>2}. {pw}   [{strength}]")
    print(f"{'─' * 40}\n")


if __name__ == "__main__":
    main()