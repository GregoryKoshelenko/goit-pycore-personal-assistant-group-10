from collections.abc import Mapping
from dataclasses import asdict
import logging

from data_types.contact_types import Contact, Contacts
from data_types.note_types import Note, Notes

from db.db_provider import DBProvider


logger = logging.getLogger(__name__)


class DB:
    def __init__(self, provider: DBProvider) -> None:
        """Initialize database facade with a concrete storage provider."""
        self.provider = provider

    def load_table(self, table_name: str) -> dict[int, object]:
        """Load a full table as an id-to-item mapping."""
        return self.provider.load_table(table_name)

    def save_table(self, table_name: str, table: dict[int, object]) -> None:
        """Save a full table mapping to storage."""
        self.provider.save_table(table_name, table)

    def load_item(self, table_name: str, item_id: int) -> object | None:
        """Load a single item from a table by identifier."""
        return self.provider.load_item(table_name, item_id)

    def save_item(self, table_name: str, item_id: int, item: object) -> None:
        """Save one item to a table under a given identifier."""
        self.provider.save_item(table_name, item_id, item)

    def get_contacts(self) -> Contacts:
        """Return contacts converted to Contact domain objects."""
        raw_contacts = self.load_table("contacts")
        contacts: Contacts = {}
        for contact_id, item in raw_contacts.items():
            if isinstance(item, Contact):
                contacts[contact_id] = item
            elif isinstance(item, Mapping):
                try:
                    contacts[contact_id] = Contact(**dict(item))
                except (TypeError, ValueError):
                    logger.debug("Skipping broken contact data for id=%s: %r", contact_id, item)
                    continue
        return contacts

    def save_contacts(self, contacts: Contacts) -> None:
        """Serialize and persist all contacts."""
        serialized: dict[int, object] = {
            contact_id: asdict(contact) for contact_id, contact in contacts.items()
        }
        self.save_table("contacts", serialized)

    def get_contact(self, contact_id: int) -> Contact | None:
        """Return one contact by id as a domain object if present."""
        raw_item = self.load_item("contacts", contact_id)
        if isinstance(raw_item, Contact):
            return raw_item
        if isinstance(raw_item, Mapping):
            try:
                return Contact(**dict(raw_item))
            except (TypeError, ValueError):
                logger.debug("Skipping broken contact data for id=%s: %r", contact_id, raw_item)
                return None
        return None

    def save_contact(self, contact: Contact, contact_id: int | None = None) -> int:
        """Persist a contact and return its effective identifier."""
        effective_contact_id = contact_id or self.next_contact_id()
        self.save_item("contacts", effective_contact_id, asdict(contact))
        return effective_contact_id

    def get_contact_by_email(self, email: str) -> Contact | None:
        """Find a contact by email, case-insensitively."""
        target = email.strip().lower()
        for contact in self.get_contacts().values():
            if (contact.email or "").strip().lower() == target:
                return contact
        return None

    def load_contacts(self) -> Contacts:
        """Alias for retrieving all contacts."""
        return self.get_contacts()

    def get_notes(self) -> Notes:
        """Return notes converted to Note domain objects."""
        raw_notes = self.load_table("notes")
        notes: Notes = {}
        for note_id, item in raw_notes.items():
            if isinstance(item, Note):
                notes[note_id] = item
            elif isinstance(item, Mapping):
                notes[note_id] = Note(**dict(item))
        return notes

    def save_notes(self, notes: Notes) -> None:
        """Serialize and persist all notes."""
        serialized: dict[int, object] = {
            note_id: asdict(note) for note_id, note in notes.items()
        }
        self.save_table("notes", serialized)

    def get_note(self, note_id: int) -> Note | None:
        """Return one note by id as a domain object if present."""
        raw_item = self.load_item("notes", note_id)
        if isinstance(raw_item, Note):
            return raw_item
        if isinstance(raw_item, Mapping):
            return Note(**dict(raw_item))
        return None

    def save_note(self, note: Note, note_id: int | None = None) -> int:
        """Persist a note and return its effective identifier."""
        effective_note_id = note_id or self.next_note_id()
        self.save_item("notes", effective_note_id, asdict(note))
        return effective_note_id

    @staticmethod
    def next_id(items: Mapping[int, object]) -> int:
        """Generate the next integer id for a mapping."""
        return max(items.keys(), default=0) + 1

    def next_contact_id(self) -> int:
        """Return the next available contact identifier."""
        return self.next_id(self.get_contacts())

    def next_note_id(self) -> int:
        """Return the next available note identifier."""
        return self.next_id(self.get_notes())
