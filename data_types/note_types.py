from typing import Dict, TypedDict


class Note(TypedDict):
    text: str
    tags: list[str]


Notes = Dict[int, Note]
