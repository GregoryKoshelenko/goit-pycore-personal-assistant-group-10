"""Email field."""

import re

from data_types.field_base import Field

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class Email(Field):
    """Email address matching a simple local@domain pattern."""

    def __init__(self, value: object) -> None:
        if not isinstance(value, str):
            raise ValueError("Email must be a string")
        candidate = value.strip().lower()
        if not EMAIL_RE.fullmatch(candidate):
            raise ValueError("Email must look like local@example.com")
        super().__init__(candidate)
