import pickle
from pathlib import Path
from typing import TypedDict

from db.db_provider import DBProvider


class PickleStorage(TypedDict):
    contacts: dict[int, object]
    notes: dict[int, object]


class PickleDBProvider(DBProvider):
    def __init__(self, file_path: str = "contacts.pkl") -> None:
        self.file_path: Path = Path(file_path)
        self._ensure_storage_exists()

    def load_table(self, table_name: str) -> dict[int, object]:
        storage = self._load_storage()
        return storage[table_name]

    def save_table(self, table_name: str, table: dict[int, object]) -> None:
        storage = self._load_storage()
        storage[table_name] = table
        self._save_storage(storage)

    def load_item(self, table_name: str, item_id: int) -> object | None:
        table = self.load_table(table_name)
        return table.get(item_id)

    def save_item(self, table_name: str, item_id: int, item: object) -> None:
        table = self.load_table(table_name)
        table[item_id] = item
        self.save_table(table_name, table)

    def _ensure_storage_exists(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._save_storage(self._empty_storage())

    def _empty_storage(self) -> PickleStorage:
        return {"contacts": {}, "notes": {}}

    def _load_storage(self) -> PickleStorage:
        if not self.file_path.exists():
            return self._empty_storage()

        try:
            with self.file_path.open("rb") as file:
                data: object = pickle.load(file)
        except (pickle.UnpicklingError, EOFError):
            return self._empty_storage()

        if not isinstance(data, dict):
            return self._empty_storage()

        contacts_raw = data.get("contacts", {})
        notes_raw = data.get("notes", {})
        if not isinstance(contacts_raw, dict):
            contacts_raw = {}
        if not isinstance(notes_raw, dict):
            notes_raw = {}
        return {"contacts": contacts_raw, "notes": notes_raw}

    def _save_storage(self, storage: PickleStorage) -> None:
        with self.file_path.open("wb") as file:
            pickle.dump(storage, file)
