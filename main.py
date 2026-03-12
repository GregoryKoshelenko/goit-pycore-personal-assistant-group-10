import os

from address_book import AddressBook
from colorama import Fore, Style, init
from commands import execute_command
from db import DB, PickleDBProvider, SQLiteDBProvider
from notes import NotesBook
from welcome_message import print_welcome_message


init(autoreset=True)


def as_note(text: str) -> str:
    """Colorize notes output in yellow."""
    return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"


def as_command(text: str) -> str:
    """Colorize command-related output in blue."""
    return f"{Fore.BLUE}{text}{Style.RESET_ALL}"


def as_contact(text: str) -> str:
    """Colorize contacts output in purple."""
    return f"{Fore.MAGENTA}{text}{Style.RESET_ALL}"


def parse_input(user_input: str) -> tuple[str, list[str]]:
    """Parse raw user input into command and argument tokens."""
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


def clear_screen() -> None:
    """Clear terminal screen before rendering the welcome banner."""
    os.system("cls" if os.name == "nt" else "clear")


def seed_book() -> AddressBook:
    """Create an address book with initial sample contacts."""
    book = AddressBook()
    book.add_contact(contact_id=DB.next_id(book.data), name="Alice", phones=["0501234567"])
    book.add_contact(contact_id=DB.next_id(book.data), name="Bob", phones=["0670001122", "0998887766"])
    book.add_contact(contact_id=DB.next_id(book.data), name="Carol", phones=["+38 (050) 555-12-34"])
    return book


def save_address_book(book: AddressBook, db: DB) -> None:
    """Persist the current address book state to storage."""
    db.save_contacts(book.data)


def save_notes_book(notes: NotesBook, db: DB) -> None:
    """Persist the current notes collection to storage."""
    db.save_notes(notes.all_notes())


def load_books(db: DB) -> tuple[AddressBook, NotesBook]:
    """Load contacts and notes from storage, seeding contacts if empty."""
    contacts_data = db.load_contacts()
    notes_data = db.get_notes()

    if contacts_data:
        book = AddressBook(contacts_data)
    else:
        book = seed_book()
        save_address_book(book, db)

    notes_book = NotesBook(notes_data)
    return book, notes_book


def prompt_user(prompt_text: str) -> str:
    """Prompt the user with command color and return stripped text."""
    return input(as_command(prompt_text)).strip()


def main() -> None:
    """Run the interactive assistant command loop."""
    provider = SQLiteDBProvider("storage/assistant.db")
    # Alternative:
    # provider = PickleDBProvider("storage/assistant.pkl")
    db = DB(provider)
    book, notes_book = load_books(db)
    clear_screen()
    print_welcome_message()

    while True:
        user_input = prompt_user("Enter a command(try 'help'): ")
        command, args = parse_input(user_input)

        result = execute_command(
            command,
            args,
            book=book,
            notes_book=notes_book,
            db=db,
            prompt=prompt_user,
        )

        if result.kind == "note":
            print(as_note(result.message))
        elif result.kind == "contact":
            print(as_contact(result.message))
        else:
            print(as_command(result.message))

        if result.should_exit:
            break


if __name__ == "__main__":
    main()
