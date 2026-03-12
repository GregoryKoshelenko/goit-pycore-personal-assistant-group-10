from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict

from data_types.fields import Address, Birthday, Email, Name, Phone


@dataclass(slots=True)
class Contact:
    name: str
    address: str | None = None
    phones: list[str] = field(default_factory=list)
    email: str | None = None
    birthday: datetime | None = None

    def __post_init__(self) -> None:
        """Normalize contact values through dedicated field types."""
        self.name = str(self.name) if isinstance(self.name, Name) else str(Name(self.name))
        self.address = None if self.address is None else (str(self.address) if isinstance(self.address, Address) else str(Address(self.address)))
        self.phones = [str(phone) if isinstance(phone, Phone) else str(Phone(phone)) for phone in self.phones]
        self.email = None if self.email is None else (str(self.email) if isinstance(self.email, Email) else str(Email(self.email)))
        self.birthday = None if self.birthday is None else (self.birthday.value if isinstance(self.birthday, Birthday) else Birthday(self.birthday).value)


Contacts = Dict[int, Contact]
