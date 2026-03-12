import re
from datetime import datetime


EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class Field:
    """Base field wrapper for validated record values."""

    def __init__(self, value: object) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Store and validate a required contact name."""

    def __init__(self, value: object) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name is required")
        super().__init__(value.strip())


class Address(Field):
    """Store and validate a contact address."""

    def __init__(self, value: object) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Address cannot be empty")
        super().__init__(value.strip())


class Email(Field):
    """Store and validate an email address."""

    def __init__(self, value: object) -> None:
        if not isinstance(value, str):
            raise ValueError("Email must be a string")
        candidate = value.strip()
        if not EMAIL_RE.fullmatch(candidate):
            raise ValueError("Email must look like local@example.com")
        super().__init__(candidate)


class Phone(Field):
    """Store and validate a phone number with normalized digits."""

    def __init__(self, value: object) -> None:
        if not isinstance(value, str):
            raise ValueError("Phone number must be a string")
        cleaned = re.sub(r"\D", "", value)
        if re.fullmatch(r"\d{10,15}", cleaned) is None:
            raise ValueError("Phone number must contain 10 to 15 digits")
        super().__init__(cleaned)


class Birthday(Field):
    """Store and validate a birthday as datetime using DD.MM.YYYY format."""

    def __init__(self, value: object) -> None:
        if isinstance(value, datetime):
            super().__init__(value)
            return
        if not isinstance(value, str):
            raise ValueError("Birthday must be a string in DD.MM.YYYY format")
        try:
            parsed = datetime.strptime(value.strip(), "%d.%m.%Y")
        except ValueError as error:
            raise ValueError(f"Invalid date format. Use DD.MM.YYYY. Error: {error}") from error
        super().__init__(parsed)

    def __str__(self) -> str:
        return self.value.strftime("%d.%m.%Y")


class NoteText(Field):
    """Store and validate note text."""

    def __init__(self, value: object) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Note text cannot be empty")
        super().__init__(value.strip())


class Tag(Field):
    """Store and validate a normalized note tag."""

    def __init__(self, value: object) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Tag cannot be empty")
        super().__init__(value.strip().lower())