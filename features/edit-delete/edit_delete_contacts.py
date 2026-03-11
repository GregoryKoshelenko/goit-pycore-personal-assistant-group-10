"""
Module: edit_delete_contacts

Provides functions to edit and delete contacts
from the AddressBook.
"""

from pathlib import Path
import sys

# Allow importing validators from both old and new folder layouts.
REPO_ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_DIRS = [
    REPO_ROOT / "feature" / "Validate-Contact-Data",
    REPO_ROOT / "features" / "validators",
]
for validators_dir in CANDIDATE_DIRS:
    if validators_dir.exists() and str(validators_dir) not in sys.path:
        sys.path.append(str(validators_dir))

from validators import validate_phone, validate_email


def edit_contact_name(record, new_name):
    """
    Change the name of a contact.

    Args:
        record: Record object
        new_name (str): new contact name
    """

    if not new_name.strip():
        raise ValueError("Name cannot be empty")

    record.name.value = new_name.strip()


def edit_contact_phone(record, old_phone, new_phone):
    """
    Replace an existing phone number with a new one.

    Args:
        record: Record object
        old_phone (str): phone number to replace
        new_phone (str): new phone number

    Returns:
        bool: True if phone was updated
    """

    if not validate_phone(new_phone):
        raise ValueError("Invalid phone number format")

    for phone in record.phones:
        if phone.value == old_phone:
            phone.value = new_phone
            return True

    return False


def delete_contact_phone(record, phone_to_delete):
    """
    Delete a phone number from a contact.

    Args:
        record: Record object
        phone_to_delete (str): phone number to remove

    Returns:
        bool: True if phone was deleted
    """

    for phone in record.phones:
        if phone.value == phone_to_delete:
            record.phones.remove(phone)
            return True

    return False


def edit_contact_email(record, new_email):
    """
    Add or update email address for a contact.

    Args:
        record: Record object
        new_email (str): email address
    """

    if not validate_email(new_email):
        raise ValueError("Invalid email format")

    record.email.value = new_email


def delete_contact(book, name):
    """
    Remove a contact from AddressBook by name.

    Args:
        book: AddressBook instance
        name (str): contact name

    Returns:
        bool: True if contact was removed
    """

    key = name.strip()

    if key in book.data:
        del book.data[key]
        return True

    return False
