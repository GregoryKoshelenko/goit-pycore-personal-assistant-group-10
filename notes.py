from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Note:
    id: int
    text: str
    tags: List[str] = field(default_factory=list)


class NotesBook:
    """
    Колекція нотаток із підтримкою пошуку та роботи з тегами.
    """

    def __init__(self) -> None:
        self._notes: Dict[int, Note] = {}
        self._next_id: int = 1

    def add_note(self, text: str, tags: Optional[List[str]] = None) -> Note:
        note = Note(
            id=self._next_id,
            text=text,
            tags=[t.strip().lower() for t in (tags or []) if t.strip()],
        )
        self._notes[note.id] = note
        self._next_id += 1
        return note

    def get_note(self, note_id: int) -> Optional[Note]:
        return self._notes.get(note_id)

    def edit_note(
        self,
        note_id: int,
        *,
        text: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Note:
        """
        Безпечне редагування нотатки за id.

        - Якщо `text` is None — текст не змінюється
        - Якщо `tags` is None — теги не змінюються
        """
        note = self.get_note(note_id)
        if note is None:
            raise KeyError(f"Нотатку з id={note_id} не знайдено.")

        if text is not None:
            text = text.strip()
            if not text:
                raise ValueError("Текст нотатки не може бути порожнім.")
            note.text = text

        if tags is not None:
            note.tags = [t.strip().lower() for t in tags if t.strip()]

        return note

    def remove_note(self, note_id: int) -> bool:
        return self._notes.pop(note_id, None) is not None

    def all_notes(self) -> List[Note]:
        return list(self._notes.values())

    def search_by_text(self, query: str) -> List[Note]:
        query_lower = query.lower()
        return [n for n in self._notes.values() if query_lower in n.text.lower()]

    def search_by_tags(self, tags: List[str]) -> List[Note]:
        tags_lower = {t.lower() for t in tags}

        def match(note: Note) -> int:
            return len(tags_lower.intersection({t.lower() for t in note.tags}))

        notes_with_score = [(note, match(note)) for note in self._notes.values()]
        filtered = [n for n, score in notes_with_score if score > 0]
        filtered.sort(key=lambda n: match(n), reverse=True)
        return filtered