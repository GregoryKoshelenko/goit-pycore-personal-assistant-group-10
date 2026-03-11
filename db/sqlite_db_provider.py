from pathlib import Path
from uuid import uuid4

from data_types.contact_types import Contact, Contacts

from db.db_provider import DBProvider
from orm.models import Base, ContactModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class SQLiteDBProvider(DBProvider):
    def __init__(self, db_path: str = "contacts.db") -> None:
        self.db_path: Path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.db_path.resolve()}")
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self._init_db()

    def get_contacts(self) -> Contacts:
        with self.session_factory() as session:
            rows: list[ContactModel] = session.query(ContactModel).all()

        return {
            row.id: {
                "email": row.email,
                "tel": row.tel,
                "name": row.name,
                "birthday": row.birthday,
            }
            for row in rows
        }

    def save_contacts(self, contacts: Contacts) -> None:
        with self.session_factory() as session:
            session.query(ContactModel).delete()
            session.add_all(
                [
                    ContactModel(
                        id=contact_id,
                        email=contact["email"],
                        tel=contact["tel"],
                        name=contact["name"],
                        birthday=contact["birthday"],
                    )
                    for contact_id, contact in contacts.items()
                ]
            )
            session.commit()

    def get_contact_by_email(self, email: str) -> Contact | None:
        with self.session_factory() as session:
            row: ContactModel | None = (
                session.query(ContactModel)
                .filter(ContactModel.email == email)
                .first()
            )

        if not row:
            return None

        return {
            "email": row.email,
            "tel": row.tel,
            "name": row.name,
            "birthday": row.birthday,
        }

    def save_contact(self, contact: Contact, contact_id: str | None = None) -> None:
        effective_contact_id: str = contact_id or str(uuid4())

        with self.session_factory() as session:
            existing: ContactModel | None = session.get(ContactModel, effective_contact_id)
            if existing:
                existing.email = contact["email"]
                existing.tel = contact["tel"]
                existing.name = contact["name"]
                existing.birthday = contact["birthday"]
            else:
                session.add(
                    ContactModel(
                        id=effective_contact_id,
                        email=contact["email"],
                        tel=contact["tel"],
                        name=contact["name"],
                        birthday=contact["birthday"],
                    )
                )
            session.commit()

    def _init_db(self) -> None:
        Base.metadata.create_all(self.engine)
