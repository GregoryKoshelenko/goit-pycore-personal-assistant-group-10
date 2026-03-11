"""
Module: validators

Contains validation functions for phone numbers
and email addresses used in contact records.
"""

import re


PHONE_PATTERN = r"^\+?\d{10,15}$"
EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"


def validate_phone(phone):
    """
    Validate phone number format.

    Allowed examples:
    0501234567
    +380501234567

    Args:
        phone (str): phone number

    Returns:
        bool: True if phone format is valid
    """

    if not isinstance(phone, str):
        return False

    phone = phone.strip()
    return bool(re.fullmatch(PHONE_PATTERN, phone))


def validate_email(email):
    """
    Validate email format.

    Example:
    user@example.com

    Args:
        email (str): email address

    Returns:
        bool: True if email format is valid
    """

    if not isinstance(email, str):
        return False

    email = email.strip()
    return bool(re.fullmatch(EMAIL_PATTERN, email))