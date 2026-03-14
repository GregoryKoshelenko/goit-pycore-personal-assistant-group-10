"""Day count field (non-negative integer)."""

from typing import ClassVar

from data_types.field_base import Field


class Days(Field):
    """Non-negative integer (e.g. birthdays lookahead window)."""

    PROMPT_HINT: ClassVar[str] = " [non-negative integer — try again or cancel]"

    def __init__(self, value: object) -> None:
        if isinstance(value, str):
            value = value.strip()
        try:
            n = int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError) as e:
            raise ValueError("Days must be a non-negative integer") from e
        if n < 0:
            raise ValueError("Days must be a non-negative integer")
        super().__init__(n)
