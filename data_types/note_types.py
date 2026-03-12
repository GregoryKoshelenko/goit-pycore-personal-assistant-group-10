from dataclasses import dataclass, field
from typing import Dict


@dataclass(slots=True)
class Note:
    text: str
    tags: list[str] = field(default_factory=list)


Notes = Dict[int, Note]
