"""Note tag field."""

from data_types.field_base import Field


class Tag(Field):
    """Non-empty tag, normalized to lowercase."""

    def __init__(self, value: object) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Tag cannot be empty")
        super().__init__(value.strip().lower())
