from address_book import AddressBook
from db import DB, PickleDBProvider
from notes import NotesBook


def parse_input(user_input: str) -> tuple[str, list[str]]:
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


def seed_book() -> AddressBook:
    book = AddressBook()
    book.add_contact(contact_id=DB.next_id(book.data), name="Alice", phones=["0501234567"])
    book.add_contact(contact_id=DB.next_id(book.data), name="Bob", phones=["0670001122", "0998887766"])
    book.add_contact(contact_id=DB.next_id(book.data), name="Carol", phones=["+38 (050) 555-12-34"])
    return book


def save_address_book(book: AddressBook, db: DB) -> None:
    db.save_contacts(book.data)


def save_notes_book(notes: NotesBook, db: DB) -> None:
    db.save_notes(notes.all_notes())


def load_books(db: DB) -> tuple[AddressBook, NotesBook]:
    contacts_data = db.load_contacts()
    notes_data = db.get_notes()

    if contacts_data:
        book = AddressBook(contacts_data)
    else:
        book = seed_book()
        save_address_book(book, db)

    notes_book = NotesBook(notes_data)
    return book, notes_book


def phone_command(args: list[str], book: AddressBook) -> str:
    if not args:
        return "Please provide contact name."

    name = " ".join(args)
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    if not record.phones:
        return f"No phone numbers for {name}."
    return f"{record.name}: {', '.join(record.phones)}"


def search_command(args: list[str], book: AddressBook) -> str:
    if not args:
        return "Please provide search query."

    query = " ".join(args)
    results = book.search(query)
    if not results:
        return "No contacts found."

    lines: list[str] = []
    for record in results:
        phones = ", ".join(record.phones) if record.phones else "-"
        lines.append(f"{record.name}: {phones}")
    return "\n".join(lines)


def add_note_command(args: list[str], notes_book: NotesBook, db: DB) -> str:
    if not args:
        return "Please provide note text."
    text = " ".join(args).strip()
    if not text:
        return "Please provide note text."

    note_id = db.next_note_id()
    notes_book.add_note(note_id=note_id, text=text)
    save_notes_book(notes_book, db)
    return f"Added note #{note_id}."


def notes_command(notes_book: NotesBook) -> str:
    notes_by_id = notes_book.all_notes()
    if not notes_by_id:
        return "No notes found."
    return "\n".join(
        f"#{note_id}: {note.text}" + (f" [tags: {', '.join(note.tags)}]" if note.tags else "")
        for note_id, note in notes_by_id.items()
    )


def search_notes_command(args: list[str], notes_book: NotesBook) -> str:
    if not args:
        return "Please provide search query for notes."

    query = " ".join(args)
    results_by_id = notes_book.search_by_text(query)
    if not results_by_id:
        return "No notes found."
    return "\n".join(
        f"#{note_id}: {note.text}" + (f" [tags: {', '.join(note.tags)}]" if note.tags else "")
        for note_id, note in results_by_id.items()
    )


def delete_note_command(args: list[str], notes_book: NotesBook, db: DB) -> str:
    if not args:
        return "Please provide note id."
    try:
        note_id = int(args[0])
    except ValueError:
        return "Note id must be an integer."

    if not notes_book.remove_note(note_id):
        return f"Note #{note_id} not found."

    save_notes_book(notes_book, db)
    return f"Deleted note #{note_id}."


def main() -> None:
    provider = PickleDBProvider("storage/assistant.pkl")
    db = DB(provider)
    book, notes_book = load_books(db)
    print("Welcome to assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            print("Good bye!")
            break
        if command == "phone":
            print(phone_command(args, book))
        elif command == "search":
            print(search_command(args, book))
        else:
            print(
                "Invalid command. Try 'help'. Example patterns: add note <text>, "
                "add phone <name> <phone>, delete note <id>."
            )


if __name__ == "__main__":
    main()
