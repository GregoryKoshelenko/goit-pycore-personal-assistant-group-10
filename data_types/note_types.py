from dataclasses import dataclass, field
from typing import Dict

from data_types.fields import NoteText, Tag


@dataclass(slots=True)
class Note:
    text: str
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Normalize note values through dedicated field types."""
        self.text = str(self.text) if isinstance(self.text, NoteText) else str(NoteText(self.text))
        self.tags = [str(tag) if isinstance(tag, Tag) else str(Tag(tag)) for tag in self.tags]


Notes = Dict[int, Note]
