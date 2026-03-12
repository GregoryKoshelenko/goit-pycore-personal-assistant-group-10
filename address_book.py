from collections import UserDict
import re


class Field:
    """Base class for contact fields."""

    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Contact name field."""

    def __init__(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name is required")
        super().__init__(value.strip())


class Phone(Field):
    """Phone field in format (XXX)XXX-XX-XX."""

    _PATTERN = re.compile(r"^\(\d{3}\)\d{3}-\d{2}-\d{2}$")

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Phone must be a string")
        candidate = value.strip()
        if self._PATTERN.fullmatch(candidate) is None:
            raise ValueError("Phone must match format (XXX)XXX-XX-XX")
        super().__init__(candidate)

    @staticmethod
    def normalize(value: str) -> str:
        return re.sub(r"\D", "", value or "")


class Email(Field):
    """Email field."""

    _PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Email must be a string")
        candidate = value.strip()
        if not candidate:
            raise ValueError("Email cannot be empty")
        if self._PATTERN.fullmatch(candidate) is None:
            raise ValueError("Invalid email format")
        super().__init__(candidate)


class Record:
    def __init__(
        self,
        name: str,
        phones: list[str] | None = None,
        email: str | None = None,
    ):
        self.name = Name(name)
        self.phones: list[Phone] = [Phone(phone) for phone in (phones or [])]
        self.email: Email | None = Email(email) if email is not None else None


class AddressBook(UserDict):
    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        target = name.strip().lower()
        for record in self.data.values():
            if record.name.value.lower() == target:
                return record
        return None

    def edit_contact(
        self,
        name: str,
        *,
        new_name: str | None = None,
        new_phones: list[str] | None = None,
        new_email: str | None = None,
    ) -> bool:
        record = self.find(name)
        if record is None:
            return False

        # Rename contact and keep dictionary key in sync.
        if new_name is not None:
            candidate_name = Name(new_name).value

            existing = self.find(candidate_name)
            if existing is not None and existing is not record:
                raise ValueError("Contact with this name already exists")

            old_key = record.name.value
            record.name = Name(candidate_name)
            if old_key in self.data:
                del self.data[old_key]
            self.data[record.name.value] = record

        # Replace all phones for contact (if provided).
        if new_phones is not None:
            record.phones = [Phone(phone) for phone in new_phones]
            self.data[record.name.value] = record

        # Update email for contact (if provided).
        if new_email is not None:
            record.email = Email(new_email)
            self.data[record.name.value] = record

        return True

    def delete_contact(self, name: str) -> bool:
        record = self.find(name)
        if record is None:
            return False
        if record.name.value in self.data:
            del self.data[record.name.value]
            return True
        return False

    def search(self, query: str) -> list[Record]:
        query_text = (query or "").strip().lower()
        if not query_text:
            return []

        query_digits = Phone.normalize(query_text)
        results: list[Record] = []
        for record in self.data.values():
            name_match = query_text in record.name.value.lower()
            phone_match = bool(query_digits) and any(
                query_digits in Phone.normalize(phone.value) for phone in record.phones
            )
            if name_match or phone_match:
                results.append(record)
        return results
