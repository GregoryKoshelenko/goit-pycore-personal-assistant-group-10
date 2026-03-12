from typing import Mapping, cast

from data_types.contact_types import Contact, Contacts
from data_types.note_types import Note, Notes

from db.db_provider import DBProvider


class DB:
    def __init__(self, provider: DBProvider) -> None:
        self.provider = provider

    def load_table(self, table_name: str) -> dict[int, object]:
        return self.provider.load_table(table_name)

    def save_table(self, table_name: str, table: dict[int, object]) -> None:
        self.provider.save_table(table_name, table)

    def load_item(self, table_name: str, item_id: int) -> object | None:
        return self.provider.load_item(table_name, item_id)

    def save_item(self, table_name: str, item_id: int, item: object) -> None:
        self.provider.save_item(table_name, item_id, item)

    def get_contacts(self) -> Contacts:
        return cast(Contacts, self.load_table("contacts"))

    def save_contacts(self, contacts: Contacts) -> None:
        self.save_table("contacts", cast(dict[int, object], contacts))

    def get_contact(self, contact_id: int) -> Contact | None:
        return cast(Contact | None, self.load_item("contacts", contact_id))

    def save_contact(self, contact: Contact, contact_id: int | None = None) -> int:
        effective_contact_id = contact_id or self.next_contact_id()
        self.save_item("contacts", effective_contact_id, contact)
        return effective_contact_id

    def get_contact_by_email(self, email: str) -> Contact | None:
        target = email.strip().lower()
        for contact in self.get_contacts().values():
            if contact.get("email", "").strip().lower() == target:
                return contact
        return None

    def load_contacts(self) -> Contacts:
        return self.get_contacts()

    def get_notes(self) -> Notes:
        return cast(Notes, self.load_table("notes"))

    def save_notes(self, notes: Notes) -> None:
        self.save_table("notes", cast(dict[int, object], notes))

    def get_note(self, note_id: int) -> Note | None:
        return cast(Note | None, self.load_item("notes", note_id))

    def save_note(self, note: Note, note_id: int | None = None) -> int:
        effective_note_id = note_id or self.next_note_id()
        self.save_item("notes", effective_note_id, note)
        return effective_note_id

    @staticmethod
    def next_id(items: Mapping[int, object]) -> int:
        return max(items.keys(), default=0) + 1

    def next_contact_id(self) -> int:
        return self.next_id(self.get_contacts())

    def next_note_id(self) -> int:
        return self.next_id(self.get_notes())
