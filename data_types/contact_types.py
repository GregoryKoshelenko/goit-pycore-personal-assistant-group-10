from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, cast

from data_types.address_field import Address
from data_types.birthday_field import Birthday
from data_types.email_field import Email
from data_types.field_utils import normalize_optional, normalize_required
from data_types.name_field import Name
from data_types.phone_field import Phone


@dataclass(slots=True)
class Contact:
    name: str
    address: str | None = None
    phones: list[str] = field(default_factory=list)
    email: str | None = None
    birthday: datetime | None = None

    def __post_init__(self) -> None:
        """Normalize contact values through dedicated field types (Field.value)."""
        self.name = cast(str, normalize_required(self.name, Name))
        self.address = cast(str | None, normalize_optional(self.address, Address))
        self.phones = [cast(str, normalize_required(phone, Phone)) for phone in self.phones]
        self.email = cast(str | None, normalize_optional(self.email, Email))
        self.birthday = cast(datetime | None, normalize_optional(self.birthday, Birthday))


Contacts = Dict[str, Contact]
