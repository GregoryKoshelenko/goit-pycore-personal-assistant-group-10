from dataclasses import dataclass, field
from typing import Dict


@dataclass(slots=True)
class Contact:
    name: str
    phones: list[str] = field(default_factory=list)
    email: str | None = None
    birthday: str | None = None


Contacts = Dict[int, Contact]
