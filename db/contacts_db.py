from data_types.contact_types import Contact, Contacts

from db.db_provider import DBProvider


class ContactsDB:
    def __init__(self, provider: DBProvider) -> None:
        self.provider = provider

    def get_contacts(self) -> Contacts:
        return self.provider.get_contacts()

    def save_contacts(self, contacts: Contacts) -> None:
        self.provider.save_contacts(contacts)

    def get_contact_by_email(self, email: str) -> Contact | None:
        return self.provider.get_contact_by_email(email)

    def save_contact(self, contact: Contact, contact_id: str | None = None) -> None:
        self.provider.save_contact(contact, contact_id)

    def load_contacts(self) -> Contacts:
        return self.get_contacts()
