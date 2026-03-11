"""
Module: edit_delete_records

Book-level editing/deletion helpers for AddressBook records.
"""

from pathlib import Path
import re
import sys
from typing import Any


# Allow importing validators from both old and new folder layouts.
REPO_ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_DIRS = [
    REPO_ROOT / "feature" / "Validate-Contact-Data",
    REPO_ROOT / "features" / "validators",
]
for validators_dir in CANDIDATE_DIRS:
    if validators_dir.exists() and str(validators_dir) not in sys.path:
        sys.path.append(str(validators_dir))

from validators import validate_email, validate_phone


class _EmailField:
    """Fallback field object for projects that expect .value on email."""

    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


def _value(field: Any) -> Any:
    return field.value if hasattr(field, "value") else field


def _normalize_phone(phone: str) -> str:
    return re.sub(r"\D", "", str(phone or ""))


def _find_record(book: Any, name: str) -> tuple[Any | None, Any | None]:
    target = (name or "").strip().lower()
    if not target:
        raise ValueError("Name cannot be empty")

    for key, record in getattr(book, "data", {}).items():
        key_name = str(key).strip().lower()
        record_name = str(_value(getattr(record, "name", ""))).strip().lower()
        if target == key_name or target == record_name:
            return key, record
    return None, None


def _build_email_field(book: Any, email_value: str) -> Any:
    # Reuse existing email field type from any record in the book when possible.
    for existing_record in getattr(book, "data", {}).values():
        candidate = getattr(existing_record, "email", None)
        if candidate is None or not hasattr(candidate, "value"):
            continue

        email_type = type(candidate)
        try:
            return email_type(email_value)
        except Exception:
            # If constructor signature is different, try direct assignment.
            try:
                instance = email_type.__new__(email_type)
                instance.value = email_value
                return instance
            except Exception:
                continue

    return _EmailField(email_value)


def edit_contact_name(book: Any, current_name: str, new_name: str) -> bool:
    if not new_name or not new_name.strip():
        raise ValueError("New name cannot be empty")

    old_key, record = _find_record(book, current_name)
    if record is None:
        return False

    target = new_name.strip()
    for key, existing_record in book.data.items():
        if key == old_key:
            continue
        existing_name = str(_value(getattr(existing_record, "name", ""))).strip().lower()
        if str(key).strip().lower() == target.lower() or existing_name == target.lower():
            raise ValueError("Contact with this name already exists")

    name_field = getattr(record, "name", None)
    if name_field is None:
        raise ValueError("Record does not have name field")
    if hasattr(name_field, "value"):
        name_field.value = target
    else:
        record.name = target

    if old_key is not None and old_key in book.data:
        del book.data[old_key]
    book.data[target] = record
    return True


def edit_contact_phone(book: Any, name: str, old_phone: str, new_phone: str) -> bool:
    if not validate_phone(new_phone):
        raise ValueError("Invalid phone number format")

    _, record = _find_record(book, name)
    if record is None:
        return False

    phones = getattr(record, "phones", None)
    if phones is None:
        raise ValueError("Record does not have phones field")

    old_norm = _normalize_phone(old_phone)
    for idx, phone in enumerate(phones):
        if _normalize_phone(_value(phone)) == old_norm:
            if hasattr(phone, "value"):
                phone.value = new_phone.strip()
            else:
                phones[idx] = new_phone.strip()
            return True
    return False


def delete_contact_phone(book: Any, name: str, phone_to_delete: str) -> bool:
    _, record = _find_record(book, name)
    if record is None:
        return False

    phones = getattr(record, "phones", None)
    if phones is None:
        raise ValueError("Record does not have phones field")

    target_norm = _normalize_phone(phone_to_delete)
    for idx, phone in enumerate(phones):
        if _normalize_phone(_value(phone)) == target_norm:
            del phones[idx]
            return True
    return False


def edit_contact_email(book: Any, name: str, new_email: str) -> bool:
    if not validate_email(new_email):
        raise ValueError("Invalid email format")

    _, record = _find_record(book, name)
    if record is None:
        return False

    email_value = new_email.strip()
    email_field = getattr(record, "email", None)
    if email_field is not None and hasattr(email_field, "value"):
        email_field.value = email_value
    else:
        record.email = _build_email_field(book, email_value)
    return True


def delete_contact(book: Any, name: str) -> bool:
    key, record = _find_record(book, name)
    if record is None or key is None:
        return False
    del book.data[key]
    return True
