"""
Input validation helpers.

Provides reusable validation functions for emails, phone numbers,
ISBNs, and generic required‑field checks used across services and views.
"""

import re


def validate_email(email: str) -> bool:
    """
    Return ``True`` if *email* matches a basic email pattern.

    Args:
        email: The email address string to validate.
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Return ``True`` if *phone* contains 7–15 digits (optional leading ``+``).

    Args:
        phone: The phone number string to validate.
    """
    pattern = r"^\+?\d{7,15}$"
    return bool(re.match(pattern, phone.replace(" ", "").replace("-", "")))


def validate_isbn(isbn: str) -> bool:
    """
    Return ``True`` if *isbn* is a valid ISBN‑10 or ISBN‑13.

    Args:
        isbn: The ISBN string (hyphens are stripped internally).
    """
    cleaned = isbn.replace("-", "").replace(" ", "")
    if len(cleaned) == 10:
        return cleaned[:9].isdigit() and (cleaned[9].isdigit() or cleaned[9] == "X")
    if len(cleaned) == 13:
        return cleaned.isdigit()
    return False


def validate_required_fields(fields: dict[str, str]) -> list[str]:
    """
    Check that every value in *fields* is non‑empty after stripping.

    Args:
        fields: Mapping of ``{field_name: value}``.

    Returns:
        List of field names whose values are empty.  An empty list means
        all fields are valid.
    """
    return [name for name, value in fields.items() if not str(value).strip()]
