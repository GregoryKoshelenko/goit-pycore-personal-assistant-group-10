from collections import UserDict
import re


class Field:
    """Base class for record fields."""

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
    """Phone field (exactly 10 digits after normalization)."""

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Phone number must be a string")
        normalized = re.sub(r"\D", "", value)
        if re.fullmatch(r"\d{10}", normalized) is None:
            raise ValueError("Phone number must contain exactly 10 digits")
        super().__init__(normalized)


class Record:
    """Contact record with name and one or more phone numbers."""

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: list[Phone] = []

    def add_phone(self, phone: str) -> None:
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        phone_obj = self.find_phone(phone)
        if phone_obj is None:
            raise ValueError("Phone not found")
        self.phones.remove(phone_obj)

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        phone_obj = self.find_phone(old_phone)
        if phone_obj is None:
            raise ValueError("Phone not found")
        phone_obj.value = Phone(new_phone).value

    def find_phone(self, phone: str) -> "Phone | None":
        normalized = re.sub(r"\D", "", phone)
        for phone_obj in self.phones:
            if phone_obj.value == normalized:
                return phone_obj
        return None

    def __str__(self) -> str:
        phones_str = "; ".join(phone.value for phone in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}"


class AddressBook(UserDict):
    """Address book container for contact records."""

    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> "Record | None":
        return self.data.get(name)

    def delete(self, name: str) -> None:
        if name in self.data:
            del self.data[name]
