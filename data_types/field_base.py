"""Base field type for record values."""


class Field:
    """Base class for validated record fields."""

    def __init__(self, value: object) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)
