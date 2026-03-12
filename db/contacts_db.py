from collections.abc import Mapping
from typing import Any, cast

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
        raw_contacts = self.load_table("contacts")
        contacts: Contacts = {}
        for contact_id, item in raw_contacts.items():
            if isinstance(item, Contact):
                contacts[contact_id] = item
            elif isinstance(item, Mapping):
                contacts[contact_id] = Contact.from_dict(cast(Mapping[str, Any], item))
        return contacts

    def save_contacts(self, contacts: Contacts) -> None:
        serialized = {contact_id: contact.to_dict() for contact_id, contact in contacts.items()}
        self.save_table("contacts", cast(dict[int, object], serialized))

    def get_contact(self, contact_id: int) -> Contact | None:
        raw_item = self.load_item("contacts", contact_id)
        if isinstance(raw_item, Contact):
            return raw_item
        if isinstance(raw_item, Mapping):
            return Contact.from_dict(cast(Mapping[str, Any], raw_item))
        return None

    def save_contact(self, contact: Contact, contact_id: int | None = None) -> int:
        effective_contact_id = contact_id or self.next_contact_id()
        self.save_item("contacts", effective_contact_id, contact.to_dict())
        return effective_contact_id

    def get_contact_by_email(self, email: str) -> Contact | None:
        target = email.strip().lower()
        for contact in self.get_contacts().values():
            if (contact.email or "").strip().lower() == target:
                return contact
        return None

    def load_contacts(self) -> Contacts:
        return self.get_contacts()

    def get_notes(self) -> Notes:
        raw_notes = self.load_table("notes")
        notes: Notes = {}
        for note_id, item in raw_notes.items():
            if isinstance(item, Note):
                notes[note_id] = item
            elif isinstance(item, Mapping):
                notes[note_id] = Note.from_dict(cast(Mapping[str, Any], item))
        return notes

    def save_notes(self, notes: Notes) -> None:
        serialized = {note_id: note.to_dict() for note_id, note in notes.items()}
        self.save_table("notes", cast(dict[int, object], serialized))

    def get_note(self, note_id: int) -> Note | None:
        raw_item = self.load_item("notes", note_id)
        if isinstance(raw_item, Note):
            return raw_item
        if isinstance(raw_item, Mapping):
            return Note.from_dict(cast(Mapping[str, Any], raw_item))
        return None

    def save_note(self, note: Note, note_id: int | None = None) -> int:
        effective_note_id = note_id or self.next_note_id()
        self.save_item("notes", effective_note_id, note.to_dict())
        return effective_note_id

    @staticmethod
    def next_id(items: Mapping[int, object]) -> int:
        return max(items.keys(), default=0) + 1

    def next_contact_id(self) -> int:
        return self.next_id(self.get_contacts())

    def next_note_id(self) -> int:
        return self.next_id(self.get_notes())
