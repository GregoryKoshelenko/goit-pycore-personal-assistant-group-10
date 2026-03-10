from abc import ABC, abstractmethod

from data_types.contact_types import Contact, Contacts


class DBProvider(ABC):
    @abstractmethod
    def get_contacts(self) -> Contacts:
        """Return all contacts as a dictionary."""

    @abstractmethod
    def save_contacts(self, contacts: Contacts) -> None:
        """Persist the full contacts dictionary."""

    @abstractmethod
    def get_contact_by_email(self, email: str) -> Contact | None:
        """Return one contact by email or None when not found."""

    @abstractmethod
    def save_contact(self, contact: Contact, contact_id: str | None = None) -> None:
        """Persist one contact under its id."""
