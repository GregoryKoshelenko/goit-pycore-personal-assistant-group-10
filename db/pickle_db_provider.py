import pickle
from pathlib import Path
from typing import cast
from uuid import uuid4

from data_types.contact_types import Contact, Contacts

from db.db_provider import DBProvider


class PickleDBProvider(DBProvider):
    def __init__(self, file_path: str = "contacts.pkl") -> None:
        self.file_path: Path = Path(file_path)
        self._ensure_storage_exists()

    def get_contacts(self) -> Contacts:
        if not self.file_path.exists():
            return {}

        try:
            with self.file_path.open("rb") as file:
                data: object = pickle.load(file)
        except (pickle.UnpicklingError, EOFError):
            # Return an empty contacts mapping if the pickle file is corrupted or empty.
            return {}

        if not isinstance(data, dict):
            # Unexpected data type; treat as no contacts rather than failing at runtime.
            return {}
        return cast(Contacts, data)

    def save_contacts(self, contacts: Contacts) -> None:
        with self.file_path.open("wb") as file:
            pickle.dump(contacts, file)

    def get_contact_by_email(self, email: str) -> Contact | None:
        contacts: Contacts = self.get_contacts()
        for contact in contacts.values():
            if contact["email"] == email:
                return contact
        return None

    def save_contact(self, contact: Contact, contact_id: str | None = None) -> None:
        effective_contact_id: str = contact_id or str(uuid4())
        contacts: Contacts = self.get_contacts()
        contacts[effective_contact_id] = contact
        self.save_contacts(contacts)

    def _ensure_storage_exists(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            with self.file_path.open("wb") as file:
                pickle.dump({}, file)
