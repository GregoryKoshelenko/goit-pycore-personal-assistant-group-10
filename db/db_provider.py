from abc import ABC, abstractmethod


class DBProvider(ABC):
    @abstractmethod
    def load_table(self, table_name: str) -> dict[int, object]:
        """Return full table data as id->item mapping."""

    @abstractmethod
    def save_table(self, table_name: str, table: dict[int, object]) -> None:
        """Persist full table data."""

    @abstractmethod
    def load_item(self, table_name: str, item_id: int) -> object | None:
        """Return single item by id from selected table."""

    @abstractmethod
    def save_item(self, table_name: str, item_id: int, item: object) -> None:
        """Persist one item by id into selected table."""
