from collections import UserDict
from dataclasses import dataclass, field
from datetime import date, datetime
import re


def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def parse_birthday(value: str | date | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError("Birthday must be a string in format DD.MM.YYYY")

    candidate = value.strip()
    if not candidate:
        raise ValueError("Birthday cannot be empty")

    try:
        return datetime.strptime(candidate, "%d.%m.%Y").date()
    except ValueError as error:
        raise ValueError("Birthday must match format DD.MM.YYYY") from error


@dataclass
class Record:
    name: str
    phones: list[str] = field(default_factory=list)
    birthday: str | date | None = None

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Name is required")
        self.phones = [normalize_phone(phone) for phone in self.phones if normalize_phone(phone)]
        self.birthday = parse_birthday(self.birthday)


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
        new_birthday: str | date | None = None,
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

        # Update birthday for contact (if provided).
        if new_birthday is not None:
            record.birthday = parse_birthday(new_birthday)
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

    def get_upcoming_birthdays(self, days: int) -> list[dict[str, str | int]]:
        if not isinstance(days, int) or days < 0:
            raise ValueError("Days must be a non-negative integer")

        today = date.today()
        upcoming: list[dict[str, str | int]] = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = record.birthday
            try:
                next_birthday = birthday.replace(year=today.year)
            except ValueError:
                # Handles 29 February in non-leap year.
                next_birthday = date(today.year, 2, 28)

            if next_birthday < today:
                try:
                    next_birthday = birthday.replace(year=today.year + 1)
                except ValueError:
                    next_birthday = date(today.year + 1, 2, 28)

            days_left = (next_birthday - today).days
            if 0 <= days_left <= days:
                upcoming.append(
                    {
                        "name": record.name,
                        "birthday": next_birthday.strftime("%d.%m.%Y"),
                        "days_left": days_left,
                    }
                )

        upcoming.sort(key=lambda item: int(item["days_left"]))
        return upcoming
