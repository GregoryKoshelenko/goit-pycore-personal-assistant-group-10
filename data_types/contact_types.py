from typing import TypedDict


class Contact(TypedDict):
    email: str
    tel: str
    name: str
    birthday: str


Contacts = dict[str, Contact]
