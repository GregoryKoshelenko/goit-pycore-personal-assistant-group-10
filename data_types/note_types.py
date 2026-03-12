from dataclasses import dataclass, field
from typing import Any, Dict, Mapping


@dataclass(slots=True)
class Note:
    text: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Note":
        return cls(
            text=str(data.get("text", "")).strip(),
            tags=[str(tag).strip().lower() for tag in data.get("tags", []) if str(tag).strip()],
        )


Notes = Dict[int, Note]
