from typing import Any, Self

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    @classmethod
    def _data_columns(cls) -> list[str]:
        return [column.name for column in cls.__table__.columns if column.name != "id"]

    def to_dict(self) -> dict[str, Any]:
        return {field_name: getattr(self, field_name) for field_name in self._data_columns()}

    @classmethod
    def from_dict(cls, item_id: int, data: dict[str, Any]) -> Self:
        model_data: dict[str, Any] = {"id": item_id}
        for field_name in cls._data_columns():
            model_data[field_name] = data.get(field_name, None)

        return cls(**model_data)


class ContactModel(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    phones: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    name: Mapped[str] = mapped_column(String, nullable=False)
    birthday: Mapped[str | None] = mapped_column(String, nullable=True)


class NoteModel(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
