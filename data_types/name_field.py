"""Contact name field."""

from data_types.field_base import Field


class Name(Field):
    """Required non-empty contact name."""

    def __init__(self, value: object) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name is required")
        super().__init__(value.strip())
