from typing import Dict, NotRequired, TypedDict


class Contact(TypedDict):
    name: str
    phones: list[str]
    email: NotRequired[str]
    birthday: NotRequired[str]


Contacts = Dict[int, Contact]
