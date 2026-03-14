"""Contact address field (non-empty when provided)."""

from data_types.field_base import Field


class Address(Field):
    """Non-empty address string."""

    def __init__(self, value: object) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Address cannot be empty")
        super().__init__(value.strip())
