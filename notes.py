import re
from typing import List, Optional

from colorama import Back, Fore, Style
from data_types.note_types import Note, Notes


def highlight_matches(value: str, query: str, *, base_color: str = Fore.YELLOW) -> str:
    """Highlight matched query fragments inside note text."""
    if not value or not query:
        return value
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(
        lambda match: f"{Back.YELLOW}{Fore.BLACK}{Style.BRIGHT}{match.group(0)}{Style.NORMAL}{Back.RESET}{base_color}",
        value,
    )


class NotesBook:
    """A collection of notes with support for searching, tagging, and sorting.

    Notes are stored in memory and assigned incremental integer
    identifiers. Text searches are case-insensitive and tags
    are normalized to lowercase to ease matching.
    """

    def __init__(self, notes_data: Notes | None = None) -> None:
        """Initialize notes storage with optional preloaded data."""
        self._notes: Notes = notes_data.copy() if notes_data else {}

    def add_note(self, note_id: int, text: str, tags: Optional[List[str]] = None) -> int:
        """Create and add a new note to the collection."""
        if note_id in self._notes:
            raise ValueError(f"Note id={note_id} already exists.")

        self._notes[note_id] = Note(text=text, tags=tags or [])
        return note_id

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

        updated = Note(
            text=note.text if text is None else text,
            tags=note.tags if tags is None else tags,
        )
        note.text = updated.text
        note.tags = updated.tags

        return note

    def remove_note(self, note_id: int) -> bool:
        """Remove a note from the collection by its ID."""
        return self._notes.pop(note_id, None) is not None

    def all_notes(self) -> Notes:
        """Return all existing notes keyed by ID."""
        return self._notes

    @staticmethod
    def format_note(note_id: int, note: Note) -> str:
        """Render one note as a single printable line."""
        return f"#{note_id}: {note.text}" + (f" [tags: {', '.join(note.tags)}]" if note.tags else "")

    @staticmethod
    def format_note_search_result(note_id: int, note: Note, query: str) -> str:
        """Render one note with highlighted query matches."""
        tags = ", ".join(highlight_matches(tag, query) for tag in note.tags)
        return f"#{note_id}: {highlight_matches(note.text, query)}" + (f" [tags: {tags}]" if tags else "")

    def render_all_notes(self) -> str:
        """Render all notes as a multi-line string."""
        if not self._notes:
            return "No notes found."
        return "\n".join(self.format_note(note_id, note) for note_id, note in self._notes.items())

    def render_search(self, query: str) -> str:
        """Render notes that match a text query or tags."""
        results_by_id = self.search(query)
        if not results_by_id:
            return "No notes found."
        return "\n".join(self.format_note_search_result(note_id, note, query) for note_id, note in results_by_id.items())

    def render_search_by_field(self, field_name: str, query: str) -> str:
        """Render notes that match a query in one specific field."""
        results_by_id = self.search_by_field(field_name, query)
        if not results_by_id:
            return "No notes found."
        return "\n".join(self.format_note_search_result(note_id, note, query) for note_id, note in results_by_id.items())

    def search_by_text(self, query: str) -> Notes:
        """Search for notes containing the query string in text."""
        query_lower = query.lower()
        return {note_id: note for note_id, note in self._notes.items() if query_lower in note.text.lower()}

    def search(self, query: str) -> Notes:
        """Search for notes containing the query in text or tags."""
        query_lower = query.lower()
        return {
            note_id: note
            for note_id, note in self._notes.items()
            if query_lower in note.text.lower() or any(query_lower in tag.lower() for tag in note.tags)
        }

    def search_by_field(self, field_name: str, query: str) -> Notes:
        """Search for notes containing the query in a specific field."""
        query_lower = query.lower()
        normalized_field = field_name.strip().lower()
        return {
            note_id: note
            for note_id, note in self._notes.items()
            if (
                normalized_field == "note" and (query_lower in note.text.lower() or any(query_lower in tag.lower() for tag in note.tags))
            )
            or (normalized_field == "text" and query_lower in note.text.lower())
            or (normalized_field == "tag" and any(query_lower in tag.lower() for tag in note.tags))
        }

    def search_by_tags(self, tags: List[str]) -> Notes:
        """Search notes by tags, sorting them by relevance (number of matching tags)."""
        tags_lower = {t.strip().lower() for t in tags if t.strip()}

        def match_score(note: Note) -> int:
            return len(tags_lower.intersection({t.lower() for t in note.tags}))

        notes_with_score = [(note_id, note, match_score(note)) for note_id, note in self._notes.items()]
        # Filter only notes that have at least one match
        filtered_with_score = [(note_id, note, score) for note_id, note, score in notes_with_score if score > 0]
        # Sort by relevance score descending
        filtered_with_score.sort(key=lambda item: item[2], reverse=True)
        return {note_id: note for note_id, note, _ in filtered_with_score}

    def get_all_unique_tags(self) -> List[str]:
        """Return a sorted list of all unique tags present in the notebook."""
        unique_tags = set()
        for note in self._notes.values():
            unique_tags.update(note.tags)
        return sorted(list(unique_tags))

