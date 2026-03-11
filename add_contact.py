from typing import Dict, Optional

class AddressBook:
    """Клас для зберігання та управління контактами."""

    def __init__(self) -> None:
        # Дані зберігаються в словнику (global dict у межах екземпляра класу)
        self.data: Dict[str, Dict[str, Optional[str]]] = {}

    def add_contact(
        self, 
        name: str, 
        tel: str, 
        address: Optional[str] = None,
        email: Optional[str] = None, 
        birthday: Optional[str] = None
    ) -> str:
        """Додає новий контакт до книги."""
        self.data[name] = {
            "tel": tel,
            "address": address,
            "email": email,
            "birthday": birthday
        }
        return f"Contact {name} added successfully."