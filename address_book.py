from collections import UserDict
from dataclasses import dataclass, field
import re


def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", value or "")


@dataclass
class Record:
    name: str
    phones: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Name is required")
        self.phones = [normalize_phone(phone) for phone in self.phones if normalize_phone(phone)]


class AddressBook(UserDict):
    def add_record(self, record: Record) -> None:
        self.data[record.name] = record

    def find(self, name: str) -> Record | None:
        target = name.strip().lower()
        for record in self.data.values():
            if record.name.lower() == target:
                return record
        return None

    def edit_contact(
        self,
        name: str,
        *,
        new_name: str | None = None,
        new_phones: list[str] | None = None,
    ) -> bool:
        record = self.find(name)
        if record is None:
            return False

        # Rename contact and keep dictionary key in sync.
        if new_name is not None:
            candidate_name = new_name.strip()
            if not candidate_name:
                raise ValueError("New name is required")

            existing = self.find(candidate_name)
            if existing is not None and existing is not record:
                raise ValueError("Contact with this name already exists")

            old_key = record.name
            record.name = candidate_name
            if old_key in self.data:
                del self.data[old_key]
            self.data[record.name] = record

        # Replace all phones for contact (if provided).
        if new_phones is not None:
            normalized = [normalize_phone(phone) for phone in new_phones if normalize_phone(phone)]
            record.phones = normalized
            self.data[record.name] = record

        return True

    def delete_contact(self, name: str) -> bool:
        record = self.find(name)
        if record is None:
            return False
        if record.name in self.data:
            del self.data[record.name]
            return True
        return False

    def search(self, query: str) -> list[Record]:
        query_text = (query or "").strip().lower()
        if not query_text:
            return []

        query_digits = normalize_phone(query_text)
        results: list[Record] = []
        for record in self.data.values():
            name_match = query_text in record.name.lower()
            phone_match = bool(query_digits) and any(query_digits in phone for phone in record.phones)
            if name_match or phone_match:
                results.append(record)
        return results
