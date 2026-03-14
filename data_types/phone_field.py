"""Phone number field: 10 digits stored; flexible input (spaces, +, country code)."""

import re

from data_types.field_base import Field


class Phone(Field):
    """
    Stored value is exactly 10 digits (national mobile format).

    Input is normalized to digits only. If more than 10 digits (e.g. +38 050…),
    the last 10 are used so formats like +38(050)6758374 are accepted.
    """

    @staticmethod
    def normalize(value: object) -> str:
        """Digits only; use for search/matching. Does not require length 10."""
        if value is None:
            return ""
        return re.sub(r"\D", "", str(value))

    @staticmethod
    def _to_stored_digits(digits: str) -> str:
        """Strip non-digits already done; take last 10 if country code was included."""
        if len(digits) >= 10:
            return digits[-10:]
        return digits

    def __init__(self, value: object) -> None:
        if not isinstance(value, str):
            raise ValueError("Phone number must be a string")
        cleaned = Phone.normalize(value)
        stored = Phone._to_stored_digits(cleaned)
        if not re.fullmatch(r"\d{10}", stored):
            raise ValueError(
                "Phone must be 10 digits (e.g. 0506758374 or +38(050)6758374)"
            )
        super().__init__(stored)
