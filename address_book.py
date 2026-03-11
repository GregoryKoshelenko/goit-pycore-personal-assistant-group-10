import uuid
from typing import Dict, Optional

class AddressBook:
    """
    Class for managing contact records.
    Uses unique IDs (UUID) as primary keys for each contact record.
    """
    
    def __init__(self) -> None:
        # Data storage where KEY is a unique UID
        self.data: Dict[str, Dict[str, Optional[str]]] = {}

    def add_contact(
        self, 
        name: str, 
        tel: str, 
        force: bool = False, 
        **kwargs
    ) -> str:
        """
        Logic for adding a contact. 
        Returns 'DUPLICATE_EXISTS' if name and phone match, 
        unless 'force' is True.
        """
        # Duplicate check logic
        if not force:
            for details in self.data.values():
                if details['name'] == name and details['tel'] == tel:
                    return "DUPLICATE_EXISTS"

        # Unique identifier generation
        uid = str(uuid.uuid4())[:8]
        
        self.data[uid] = {
            "name": name,
            "tel": tel,
            "address": kwargs.get('address'),
            "email": kwargs.get('email'),
            "birthday": kwargs.get('birthday')
        }
        return f"Contact '{name}' added successfully with ID: {uid}"