"""Note identifier field."""

from typing import ClassVar

from data_types.field_base import Field


class NoteId(Field):
    """Non-negative integer note id."""

    PROMPT_HINT: ClassVar[str] = " [non-negative integer — try again or cancel]"

    def __init__(self, value: object) -> None:
        if isinstance(value, str):
            value = value.strip()
        try:
            n = int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError) as e:
            raise ValueError("Note id must be a non-negative integer") from e
        if n < 0:
            raise ValueError("Note id must be a non-negative integer")
        super().__init__(n)
