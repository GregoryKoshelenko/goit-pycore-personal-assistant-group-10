from collections import UserDict
import re

from data_types.contact_types import Contact, Contacts


def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", value or "")


class AddressBook(UserDict):
    def __init__(self, contacts: Contacts | None = None) -> None:
        super().__init__()
        if contacts:
            self.data.update(contacts)

    def add_contact(
        self,
        *,
        name: str,
        phones: list[str] | None = None,
        email: str | None = None,
        birthday: str | None = None,
        contact_id: int,
    ) -> int:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Name is required")
        normalized_phones = [normalize_phone(phone) for phone in (phones or []) if normalize_phone(phone)]

        contact: Contact = {
            "name": normalized_name,
            "phones": normalized_phones,
        }
        if email and email.strip():
            contact["email"] = email.strip()
        if birthday and birthday.strip():
            contact["birthday"] = birthday.strip()

        effective_id = contact_id
        if effective_id in self.data:
            raise ValueError(f"Contact id={effective_id} already exists")

        self.data[effective_id] = contact
        return effective_id

    def find(self, name: str) -> Contact | None:
        target = name.strip().lower()
        for contact in self.data.values():
            if contact["name"].lower() == target:
                return contact
        return None

    def edit_contact(
        self,
        name: str,
        *,
        new_name: str | None = None,
        new_phones: list[str] | None = None,
    ) -> bool:
        contact = self.find(name)
        if contact is None:
            return False

        # Rename contact.
        if new_name is not None:
            candidate_name = new_name.strip()
            if not candidate_name:
                raise ValueError("New name is required")

            existing = self.find(candidate_name)
            if existing is not None and existing is not contact:
                raise ValueError("Contact with this name already exists")

            contact["name"] = candidate_name

        # Replace all phones for contact (if provided).
        if new_phones is not None:
            normalized = [normalize_phone(phone) for phone in new_phones if normalize_phone(phone)]
            contact["phones"] = normalized

        return True

    def delete_contact(self, name: str) -> bool:
        target = name.strip().lower()
        for contact_id, contact in list(self.data.items()):
            if contact["name"].lower() == target:
                del self.data[contact_id]
                return True

        return False

    def search(self, query: str) -> list[Contact]:
        query_text = (query or "").strip().lower()
        if not query_text:
            return []

        query_digits = normalize_phone(query_text)
        results: list[Contact] = []
        for contact in self.data.values():
            name_match = query_text in contact["name"].lower()
            phone_match = bool(query_digits) and any(query_digits in phone for phone in contact["phones"])
            if name_match or phone_match:
                results.append(contact)
        return results
