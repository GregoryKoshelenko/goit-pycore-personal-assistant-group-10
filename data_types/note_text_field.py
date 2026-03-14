"""Note body field."""

from data_types.field_base import Field


class NoteText(Field):
    """Non-empty note text."""

    def __init__(self, value: object) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Note text cannot be empty")
        super().__init__(value.strip())
