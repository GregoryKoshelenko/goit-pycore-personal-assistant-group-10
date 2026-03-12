from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Note:
    """Represents a single note in the system."""
    id: int
    text: str
    tags: List[str] = field(default_factory=list)


class NotesBook:
    """A collection of notes with support for searching, tagging, and sorting.

    Notes are stored in memory and assigned incremental integer
    identifiers. Text searches are case-insensitive and tags
    are normalized to lowercase to ease matching.
    """

    def __init__(self) -> None:
        self._notes: Dict[int, Note] = {}
        self._next_id: int = 1

    def add_note(self, text: str, tags: Optional[List[str]] = None) -> Note:
        """Create and add a new note to the collection."""
        note = Note(
            id=self._next_id,
            text=text,
            tags=[t.strip().lower() for t in (tags or []) if t.strip()],
        )
        self._notes[note.id] = note
        self._next_id += 1
        return note

    def get_note(self, note_id: int) -> Optional[Note]:
        """Retrieve a note by its identifier."""
        return self._notes.get(note_id)

    def edit_note(
        self,
        note_id: int,
        *,
        text: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Note:
        """Safely update a note by its identifier.

        - text: new note body; stripped and validated as non-empty.
        - tags: list of tag strings to replace the current set.
        """
        note = self.get_note(note_id)
        if note is None:
            raise KeyError(f"Note with id={note_id} not found.")

        if text is not None:
            text = text.strip()
            if not text:
                raise ValueError("Note text cannot be empty.")
            note.text = text

        if tags is not None:
            note.tags = [t.strip().lower() for t in tags if t.strip()]

        return note

    def remove_note(self, note_id: int) -> bool:
        """Remove a note from the collection by its ID."""
        return self._notes.pop(note_id, None) is not None

    def all_notes(self) -> List[Note]:
        """Return a list of all existing notes."""
        return list(self._notes.values())

    def search_by_text(self, query: str) -> List[Note]:
        """Search for notes containing the query string (case-insensitive)."""
        query_lower = query.lower()
        return [n for n in self._notes.values() if query_lower in n.text.lower()]

    def search_by_tags(self, tags: List[str]) -> List[Note]:
        """Search notes by tags, sorting them by relevance (number of matching tags)."""
        tags_lower = {t.strip().lower() for t in tags if t.strip()}

        def match_score(note: Note) -> int:
            return len(tags_lower.intersection({t.lower() for t in note.tags}))

        notes_with_score = [(note, match_score(note)) for note in self._notes.values()]
        # Filter only notes that have at least one match
        filtered_with_score = [(n, score) for n, score in notes_with_score if score > 0]
        # Sort by relevance score descending
        filtered_with_score.sort(key=lambda item: item[1], reverse=True)
        return [n for n, _ in filtered_with_score]

    def get_all_unique_tags(self) -> List[str]:
        """Return a sorted list of all unique tags present in the notebook."""
        unique_tags = set()
        for note in self._notes.values():
            unique_tags.update(note.tags)
        return sorted(list(unique_tags))