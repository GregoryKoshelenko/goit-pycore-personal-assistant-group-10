from collections.abc import Callable
from dataclasses import dataclass

from address_book import AddressBook
from db import DB
from notes import NotesBook

PromptFn = Callable[[str], str]


@dataclass(slots=True)
class CommandResult:
    """Result of a command execution for CLI rendering."""

    kind: str
    message: str
    should_exit: bool = False


def ask_required(prompt: PromptFn, message: str) -> str:
    """Prompt until a non-empty value is entered."""
    value = ""
    while not value:
        value = prompt(message).strip()
    return value


def phone_command(args: list[str], book: AddressBook, prompt: PromptFn) -> str:
    """Handle command that shows contact details by name."""
    name = " ".join(args).strip() if args else ""
    while not name:
        name = prompt("What is the contact name?: ")

    details = book.get_contact_details(name)
    if details is None:
        return f"Contact {name} not found."
    return details


def search_command(args: list[str], book: AddressBook, prompt: PromptFn) -> str:
    """Handle contact search by any contact field."""
    query = " ".join(args[1:]).strip() if len(args) > 1 else ""
    while not query:
        query = prompt("What is the contact search query?: ")

    results = book.search_details(query)
    if not results:
        return "No contacts found."
    return "\n\n".join(results)


def search_contact_field_command(field_name: str, args: list[str], book: AddressBook, prompt: PromptFn) -> str:
    """Handle contact search by one specific field."""
    query = " ".join(args[1:]).strip() if len(args) > 1 else ""
    while not query:
        query = prompt(f"What is the {field_name} search query?: ")

    results = book.search_field_details(field_name, query)
    if not results:
        return "No contacts found."
    return "\n\n".join(results)


def add_contact_command(args: list[str], book: AddressBook, db: DB, prompt: PromptFn) -> str:
    """Handle adding a contact with optional interactive prompts."""
    if not args or args[0].lower() != "contact":
        return "Usage: add contact <name> [address] [email] [birthday] [phone1 phone2 ...]"

    while True:
        positional = args[1:]
        name = positional[0].strip() if positional else ""
        if not name:
            name = ask_required(prompt, "What is the contact name?: ")

        address = positional[1].strip() or None if len(positional) > 1 else None
        if len(positional) <= 1:
            raw_address = prompt(f"What is the {name} address? (press Enter to skip): ").strip()
            address = raw_address or None

        email = positional[2].strip() or None if len(positional) > 2 else None
        if len(positional) <= 2:
            raw_email = prompt(f"What is the {name} email? (press Enter to skip): ").strip()
            email = raw_email or None

        birthday = positional[3].strip() or None if len(positional) > 3 else None
        if len(positional) <= 3:
            raw_birthday = prompt(f"What is the {name} birthday? (DD.MM.YYYY, press Enter to skip): ").strip()
            birthday = raw_birthday or None

        if len(positional) > 4:
            phones = [phone.strip() for phone in positional[4:] if phone.strip()]
        else:
            raw_phones = prompt(f"What are the {name} phone numbers? (comma separated, Enter to skip): ")
            phones = [phone.strip() for phone in raw_phones.split(",") if phone.strip()]

        contact_id = db.next_contact_id()
        try:
            book.add_contact(
                contact_id=contact_id,
                name=name,
                address=address,
                phones=phones,
                email=email,
                birthday=birthday,
            )
            break
        except ValueError as error:
            reply = prompt(f"Invalid contact input: {error}. Press Enter to retry, or type 'cancel' to abort: ").strip().lower()
            if reply == "cancel":
                return "Contact creation canceled."

            continue

    db.save_contacts(book.data)
    return f"Added contact #{contact_id}: {name}."


def edit_contact_command(args: list[str], book: AddressBook, db: DB, prompt: PromptFn) -> str:
    """Handle contact editing for all fields."""
    if not args or args[0].lower() != "contact":
        return "Usage: edit contact <name>"

    current_name = " ".join(args[1:]).strip() if args[1:] else ""
    if not current_name:
        current_name = ask_required(prompt, "What is the contact name to edit?: ")

    record = book.find(current_name)
    if record is None:
        return f"Contact {current_name} not found."

    def prompt_update(label: str, current_value: str) -> str:
        return prompt(f"{label} [{current_value}] (Enter to keep): ").strip()

    name_input = prompt_update("Name", record.name)
    new_name = name_input or None

    address_input = prompt_update("Address", record.address or "-")
    new_address = address_input if address_input else None

    email_input = prompt_update("Email", record.email or "-")
    new_email = email_input if email_input else None

    birthday_input = prompt(
        f"Birthday [{record.birthday.strftime('%d.%m.%Y') if record.birthday else '-'}] (DD.MM.YYYY, Enter to keep): "
    ).strip()
    new_birthday = birthday_input if birthday_input else None

    phones_current = ", ".join(record.phones) if record.phones else "-"
    phones_input = prompt_update("Phones (comma separated)", phones_current)
    new_phones = [phone.strip() for phone in phones_input.split(",") if phone.strip()] if phones_input else None

    try:
        book.edit_contact(
            current_name,
            new_name=new_name,
            new_address=new_address,
            new_email=new_email,
            new_birthday=new_birthday,
            new_phones=new_phones,
        )
    except ValueError as error:
        if "birthday" in str(error).lower():
            return "Invalid contact input: birthday must be in DD.MM.YYYY format."
        return f"Invalid contact input: {error}"

    db.save_contacts(book.data)
    updated = book.find(new_name or current_name)
    if updated is None:
        return "Contact was not updated."
    return f"Updated contact: {updated.name}."


def edit_note_command(args: list[str], notes_book: NotesBook, db: DB, prompt: PromptFn) -> str:
    """Handle note editing with Enter-to-keep behavior."""
    raw_note_id = args[1].strip() if len(args) > 1 else ""
    while not raw_note_id:
        raw_note_id = prompt("What is the note id to edit?: ").strip()

    try:
        note_id = int(raw_note_id)
    except ValueError:
        return "Note id must be an integer."

    note = notes_book.get_note(note_id)
    if note is None:
        return f"Note #{note_id} not found."

    text_input = prompt(f"Text [{note.text}] (Enter to keep): ").strip()
    current_tags = ", ".join(note.tags) if note.tags else "-"
    tags_input = prompt(f"Tags [{current_tags}] (comma separated, Enter to keep): ").strip()

    new_text = text_input if text_input else None
    new_tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()] if tags_input else None

    try:
        notes_book.edit_note(note_id, text=new_text, tags=new_tags)
    except ValueError as error:
        return f"Invalid note input: {error}"
    except KeyError:
        return f"Note #{note_id} not found."

    db.save_notes(notes_book.all_notes())
    return f"Updated note #{note_id}."


def delete_contact_command(args: list[str], book: AddressBook, db: DB, prompt: PromptFn) -> str:
    """Handle contact deletion by name."""
    if not args or args[0].lower() != "contact":
        return "Usage: delete contact <name>"

    name = " ".join(args[1:]).strip()
    while not name:
        name = prompt("What is the contact name to delete?: ")

    if not book.delete_contact(name):
        return f"Contact {name} not found."

    db.save_contacts(book.data)
    return f"Deleted contact: {name}."


def add_note_command(args: list[str], notes_book: NotesBook, db: DB, prompt: PromptFn) -> str:
    """Handle note creation with interactive prompt for missing text."""
    text = " ".join(args).strip() if args else ""
    if not text:
        text = ask_required(prompt, "What is the note text?: ")

    note_id = db.next_note_id()
    try:
        notes_book.add_note(note_id=note_id, text=text)
    except ValueError as error:
        return f"Invalid note input: {error}"
    db.save_notes(notes_book.all_notes())
    return f"Added note #{note_id}."


def notes_command(notes_book: NotesBook) -> str:
    """Render all notes for display."""
    return notes_book.render_all_notes()


def contacts_command(book: AddressBook) -> str:
    """Render all contacts for display."""
    return book.render_all_contacts()


def search_notes_command(args: list[str], notes_book: NotesBook, prompt: PromptFn) -> str:
    """Search notes by text or tags with optional prompt."""
    query = " ".join(args[1:]).strip() if len(args) > 1 else ""
    while not query:
        query = prompt("What is the note search query?: ")
    return notes_book.render_search(query)


def search_note_field_command(field_name: str, args: list[str], notes_book: NotesBook, prompt: PromptFn) -> str:
    """Handle note search by one specific field."""
    query = " ".join(args[1:]).strip() if len(args) > 1 else ""
    while not query:
        query = prompt(f"What is the {field_name} search query?: ")
    return notes_book.render_search_by_field(field_name, query)


def delete_note_command(args: list[str], notes_book: NotesBook, db: DB, prompt: PromptFn) -> str:
    """Delete one note by identifier."""
    raw = args[0].strip() if args else ""
    while not raw:
        raw = prompt("What is the note id?: ")
    try:
        note_id = int(raw)
    except ValueError:
        return "Note id must be an integer."

    if not notes_book.remove_note(note_id):
        return f"Note #{note_id} not found."

    db.save_notes(notes_book.all_notes())
    return f"Deleted note #{note_id}."


def help_command() -> str:
    """Return help message with supported commands."""
    return "\n".join(
        [
            "Available commands:",
            "- help: show this help message",
            "- add contact <name> [address] [email] [birthday] [phone1 phone2 ...]: add a new contact",
            "- edit contact <name>: edit contact fields",
            "- edit note <id>: edit note text and tags",
            "- delete contact <name>: delete a contact",
            "- add note <text>: add a new note",
            "- show contacts: show all contacts",
            "- show notes: show all notes",
            "- notes: show all notes",
            "- search contact <query>: search contacts by name, address, phone, email, or birthday",
            "- search note <query>: search notes by text or tags",
            "- search address <query>: search contacts by address field",
            "- search phone <query>: search contacts by phone field",
            "- search email <query>: search contacts by email field",
            "- search birthday <query>: search contacts by birthday field",
            "- search tag <query>: search notes by tag field",
            "- delete note <id>: delete a note",
            "- phone <name>: show full contact details",
            "- close | exit: quit the assistant",
        ]
    )


def execute_command(
    command: str,
    args: list[str],
    *,
    book: AddressBook,
    notes_book: NotesBook,
    db: DB,
    prompt: PromptFn,
) -> CommandResult:
    """Dispatch a parsed command and return render-ready result."""
    if command in ("close", "exit"):
        return CommandResult(kind="command", message="Good bye!", should_exit=True)

    if command == "help":
        return CommandResult(kind="command", message=help_command())

    if command == "add":
        if args and args[0].lower() == "note":
            return CommandResult(kind="note", message=add_note_command(args[1:], notes_book, db, prompt))
        return CommandResult(kind="contact", message=add_contact_command(args, book, db, prompt))

    if command == "edit":
        if args and args[0].lower() == "note":
            return CommandResult(kind="note", message=edit_note_command(args, notes_book, db, prompt))
        return CommandResult(kind="contact", message=edit_contact_command(args, book, db, prompt))

    if command == "delete":
        if args and args[0].lower() == "note":
            return CommandResult(kind="note", message=delete_note_command(args[1:], notes_book, db, prompt))
        return CommandResult(kind="contact", message=delete_contact_command(args, book, db, prompt))

    if command == "phone":
        return CommandResult(kind="contact", message=phone_command(args, book, prompt))

    if command == "search":
        if args and args[0].lower() == "address":
            return CommandResult(kind="contact", message=search_contact_field_command("address", args, book, prompt))
        if args and args[0].lower() == "phone":
            return CommandResult(kind="contact", message=search_contact_field_command("phone", args, book, prompt))
        if args and args[0].lower() == "email":
            return CommandResult(kind="contact", message=search_contact_field_command("email", args, book, prompt))
        if args and args[0].lower() == "birthday":
            return CommandResult(kind="contact", message=search_contact_field_command("birthday", args, book, prompt))
        if args and args[0].lower() == "tag":
            return CommandResult(kind="note", message=search_note_field_command("tag", args, notes_book, prompt))
        if args and args[0].lower() == "note":
            return CommandResult(kind="note", message=search_notes_command(args, notes_book, prompt))
        if args and args[0].lower() == "contact":
            return CommandResult(kind="contact", message=search_command(args, book, prompt))
        return CommandResult(
            kind="command",
            message=(
                "Usage: search contact <query> | search note <query> | search address <query> | "
                "search phone <query> | search email <query> | search birthday <query> | search tag <query>"
            ),
        )

    if command == "notes":
        return CommandResult(kind="note", message=notes_command(notes_book))

    if command == "show":
        if args and args[0].lower() in ("contact", "contacts"):
            return CommandResult(kind="contact", message=contacts_command(book))
        if args and args[0].lower() in ("note", "notes"):
            return CommandResult(kind="note", message=notes_command(notes_book))
        return CommandResult(kind="command", message="Usage: show contacts | show notes")

    return CommandResult(
        kind="command",
        message=(
            "Invalid command. Try 'help'. Example patterns: add note <text>, "
            "add contact <name> <phone>, search contact <query>, search address <query>, search tag <query>."
        ),
    )
