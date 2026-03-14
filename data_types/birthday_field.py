"""Birthday field in DD.MM.YYYY format."""

from datetime import datetime

from data_types.field_base import Field


class Birthday(Field):
    """Birthday as datetime, parsed from DD.MM.YYYY string."""

    def __init__(self, value: object) -> None:
        if isinstance(value, datetime):
            super().__init__(value)
            return
        if not isinstance(value, str):
            raise ValueError("Birthday must be a string in DD.MM.YYYY format")
        try:
            parsed = datetime.strptime(value.strip(), "%d.%m.%Y")
        except ValueError as e:
            raise ValueError(f"Invalid date format. Use DD.MM.YYYY. Error: {e}") from e
        super().__init__(parsed)

    def __str__(self) -> str:
        if isinstance(self.value, datetime):
            return self.value.strftime("%d.%m.%Y")
        return str(self.value)
