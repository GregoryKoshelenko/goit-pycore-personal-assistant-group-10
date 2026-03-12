from collections import UserDict
from datetime import datetime
import re

from colorama import Fore, Style
from data_types.contact_types import Contact, Contacts


def normalize_phone(value: str) -> str:
    """Normalize a phone value by removing non-digit characters."""
    return re.sub(r"\D", "", value or "")


def highlight_matches(value: str, query: str, *, base_color: str = Fore.MAGENTA) -> str:
    """Highlight matched query fragments inside a field value."""
    if not value or not query:
        return value
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda match: f"{Fore.YELLOW}{Style.BRIGHT}{match.group(0)}{Style.NORMAL}{base_color}", value)


class AddressBook(UserDict):
    def __init__(self, contacts: Contacts | None = None) -> None:
        """Initialize address book with optional preloaded contacts."""
        super().__init__()
        if contacts:
            self.data.update(contacts)

    def add_contact(
        self,
        *,
        name: str,
        address: str | None = None,
        phones: list[str] | None = None,
        email: str | None = None,
        birthday: str | None = None,
        contact_id: int,
    ) -> int:
        """Add a new contact and return its assigned identifier."""
        contact = Contact(
            name=name,
            address=(address.strip() if address and address.strip() else None),
            phones=phones or [],
            email=(email.strip() if email and email.strip() else None),
            birthday=(birthday.strip() if birthday and birthday.strip() else None),
        )

        effective_id = contact_id
        if effective_id in self.data:
            raise ValueError(f"Contact id={effective_id} already exists")

        self.data[effective_id] = contact
        return effective_id

    def find(self, name: str) -> Contact | None:
        """Find a contact by exact name, case-insensitively."""
        target = name.strip().lower()
        for contact in self.data.values():
            if contact.name.lower() == target:
                return contact
        return None

    @staticmethod
    def format_contact_details(contact: Contact) -> str:
        """Render all contact fields into a human-readable block."""
        address = contact.address or "-"
        phones = ", ".join(contact.phones) if contact.phones else "-"
        email = contact.email or "-"
        birthday = contact.birthday.strftime("%d.%m.%Y") if isinstance(contact.birthday, datetime) else "-"
        return "\n".join(
            [
                f"Name: {contact.name}",
                f"Address: {address}",
                f"Phones: {phones}",
                f"Email: {email}",
                f"Birthday: {birthday}",
            ]
        )

    @staticmethod
    def format_contact_search_details(contact: Contact, query: str) -> str:
        """Render contact fields with highlighted query matches."""
        birthday = contact.birthday.strftime("%d.%m.%Y") if isinstance(contact.birthday, datetime) else "-"
        phones = contact.phones if contact.phones else ["-"]
        phone_query = normalize_phone(query) or query
        highlighted_phones = ", ".join(highlight_matches(phone, phone_query) for phone in phones)
        return "\n".join(
            [
                f"Name: {highlight_matches(contact.name, query)}",
                f"Address: {highlight_matches(contact.address or '-', query)}",
                f"Phones: {highlighted_phones}",
                f"Email: {highlight_matches(contact.email or '-', query)}",
                f"Birthday: {highlight_matches(birthday, query)}",
            ]
        )

    def get_contact_details(self, name: str) -> str | None:
        """Return formatted contact details by name or None if missing."""
        contact = self.find(name)
        if contact is None:
            return None
        return self.format_contact_details(contact)

    def render_all_contacts(self) -> str:
        """Render all contacts as a multi-contact block."""
        if not self.data:
            return "No contacts found."
        return "\n\n".join(self.format_contact_details(contact) for contact in self.data.values())

    def search_details(self, query: str) -> list[str]:
        """Search contacts and return formatted details for each match."""
        return [self.format_contact_search_details(contact, query) for contact in self.search(query)]

    def search_field_details(self, field_name: str, query: str) -> list[str]:
        """Search contacts by one field and return formatted details for each match."""
        return [self.format_contact_search_details(contact, query) for contact in self.search_by_field(field_name, query)]

    def edit_contact(
        self,
        name: str,
        *,
        new_name: str | None = None,
        new_address: str | None = None,
        new_email: str | None = None,
        new_birthday: str | None = None,
        new_phones: list[str] | None = None,
    ) -> bool:
        """Update contact fields by current name."""
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

            contact.name = candidate_name

        candidate_phones = contact.phones if new_phones is None else new_phones
        candidate_address = contact.address if new_address is None else (new_address.strip() or None)
        candidate_email = contact.email if new_email is None else (new_email.strip() or None)
        candidate_birthday = contact.birthday if new_birthday is None else (new_birthday.strip() or None)

        updated = Contact(
            name=contact.name,
            address=candidate_address,
            phones=candidate_phones,
            email=candidate_email,
            birthday=candidate_birthday,
        )

        contact.name = updated.name
        contact.address = updated.address
        contact.phones = updated.phones
        contact.email = updated.email
        contact.birthday = updated.birthday

        return True

    def delete_contact(self, name: str) -> bool:
        """Delete a contact by name and report whether it was removed."""
        target = name.strip().lower()
        for contact_id, contact in list(self.data.items()):
            if contact.name.lower() == target:
                del self.data[contact_id]
                return True

        return False

    def search(self, query: str) -> list[Contact]:
        """Search contacts by partial match in any contact field."""
        query_text = (query or "").strip().lower()
        if not query_text:
            return []

        query_digits = normalize_phone(query_text)
        results: list[Contact] = []
        for contact in self.data.values():
            birthday = contact.birthday.strftime("%d.%m.%Y") if isinstance(contact.birthday, datetime) else ""
            searchable_fields = [
                contact.name,
                contact.address or "",
                contact.email or "",
                birthday,
            ]
            text_match = any(query_text in field.lower() for field in searchable_fields)
            phone_match = bool(query_digits) and any(query_digits in normalize_phone(phone) for phone in contact.phones)
            if text_match or phone_match:
                results.append(contact)
        return results

    def search_by_field(self, field_name: str, query: str) -> list[Contact]:
        """Search contacts by a specific field."""
        query_text = (query or "").strip().lower()
        if not query_text:
            return []

        normalized_field = field_name.strip().lower()
        query_digits = normalize_phone(query_text)
        results: list[Contact] = []
        for contact in self.data.values():
            birthday = contact.birthday.strftime("%d.%m.%Y") if isinstance(contact.birthday, datetime) else ""
            field_value = {
                "contact": " ".join(filter(None, [contact.name, contact.address, contact.email, birthday, " ".join(contact.phones)])),
                "name": contact.name,
                "address": contact.address or "",
                "email": contact.email or "",
                "birthday": birthday,
                "phone": " ".join(contact.phones),
            }.get(normalized_field, "")

            if normalized_field == "phone":
                matched = bool(query_digits) and any(query_digits in normalize_phone(phone) for phone in contact.phones)
            else:
                matched = query_text in field_value.lower()

            if matched:
                results.append(contact)
        return results
