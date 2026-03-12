from pathlib import Path

from db.db_provider import DBProvider
from db.session import with_session
from orm.models import Base, ContactModel, NoteModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class SQLiteDBProvider(DBProvider):
    TABLE_MODELS = {
        ContactModel.__tablename__: ContactModel,
        NoteModel.__tablename__: NoteModel,
    }

    def __init__(self, db_path: str = "contacts.db") -> None:
        self.db_path: Path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.db_path.resolve()}")
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self._init_db()

    @with_session
    def load_table(self, table_name: str, *, session: Session) -> dict[int, object]:
        model = self._get_model(table_name)
        rows = session.query(model).all()
        return {row.id: row.to_dict() for row in rows}

    @with_session
    def save_table(self, table_name: str, table: dict[int, object], *, session: Session) -> None:
        model = self._get_model(table_name)
        session.query(model).delete()
        session.add_all(
            [
                model.from_dict(item_id, item)
                for item_id, item in table.items()
                if isinstance(item, dict)
            ]
        )
        session.commit()

    @with_session
    def load_item(self, table_name: str, item_id: int, *, session: Session) -> object | None:
        model = self._get_model(table_name)
        row = session.get(model, item_id)
        return row.to_dict() if row else None

    @with_session
    def save_item(self, table_name: str, item_id: int, item: object, *, session: Session) -> None:
        model = self._get_model(table_name)
        if not isinstance(item, dict):
            raise ValueError("Item must be a dictionary")

        existing = session.get(model, item_id)
        if existing:
            for field_name in model._data_columns():
                setattr(existing, field_name, item.get(field_name, None))
        else:
            session.add(model.from_dict(item_id, item))
        session.commit()

    def _init_db(self) -> None:
        Base.metadata.create_all(self.engine)

    def _get_model(self, table_name: str):
        model = self.TABLE_MODELS.get(table_name)
        if model is None:
            raise ValueError(f"Unsupported table name: {table_name}")
        return model

    def _validate_table_name(self, table_name: str) -> None:
        self._get_model(table_name)
