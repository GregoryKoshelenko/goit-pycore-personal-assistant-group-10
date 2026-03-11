from typing import Dict, Optional

class AddressBook:
    """Class for storing and managing contact records."""
    
    def __init__(self) -> None:
        # Data is stored as an instance attribute
        self.data: Dict[str, Dict[str, Optional[str]]] = {}

    def add_contact(
        self, 
        name: str, 
        tel: str, 
        address: Optional[str] = None, 
        email: Optional[str] = None, 
        birthday: Optional[str] = None
    ) -> str:
        """
        Adds a new contact. If the contact already exists, it updates the information.
        """
        # We can either check if name exists or just update (overwrite)
        # To satisfy Copilot's 'overwrite' concern, we'll return a specific message
        message = "Contact updated." if name in self.data else "Contact added."
        
        self.data[name] = {
            "tel": tel,
            "address": address,
            "email": email,
            "birthday": birthday
        }
        return f"{message} {name} is now in the address book."