from dataclasses import dataclass, field
from typing import Any, Dict, Mapping


@dataclass(slots=True)
class Contact:
    name: str
    phones: list[str] = field(default_factory=list)
    email: str | None = None
    birthday: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "phones": list(self.phones),
            "email": self.email,
            "birthday": self.birthday,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Contact":
        return cls(
            name=str(data.get("name", "")).strip(),
            phones=[str(phone) for phone in data.get("phones", []) if str(phone).strip()],
            email=(str(data.get("email")).strip() if data.get("email") else None),
            birthday=(str(data.get("birthday")).strip() if data.get("birthday") else None),
        )


Contacts = Dict[int, Contact]
