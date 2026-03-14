import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from address_book import AddressBook
from ai_assistant import is_chat_available
from data_types.address_field import Address
from data_types.birthday_field import Birthday
from data_types.days_field import Days
from data_types.email_field import Email
from data_types.field_utils import normalize_optional
from data_types.name_field import Name
from data_types.note_id_field import NoteId
from data_types.note_text_field import NoteText
from data_types.phone_field import Phone
from data_types.tag_field import Tag
from db import DB
from notes import NotesBook

PromptFn = Callable[[str], str]
CANCELED = "Canceled."
R = TypeVar("R")


class PromptCancelled(Exception):
    """Raised when the user types cancel."""


def validate_line(
    prompt: PromptFn,
    message: str,
    parse: Callable[[str], R],
    *,
    field_optional: bool | None = None,
    suffix_before_colon: str = "",
    on_invalid: str | Callable[[ValueError, str], str] = "Invalid: {error}",
    on_empty: Callable[[], R] | None = None,
    empty_retry_message: str | None = None,
) -> R:
    """If field_optional is set, message gets [Enter to skip, cancel to abort] (or cancel only)."""
    if field_optional is not None:
        parts = ["cancel to abort"]
        if field_optional:
            parts.insert(0, "Enter to skip")
        hint = f" [{', '.join(parts)}]"
        full_message = f"{message}{hint}{suffix_before_colon}: "
    else:
        hint = ""
        full_message = f"{message}{suffix_before_colon}"

    while True:
        raw = prompt(full_message).strip()
        if raw.lower() == "cancel":
            raise PromptCancelled
        if raw == "" and on_empty is not None:
            return on_empty()
        if raw == "" and empty_retry_message:
            # Print only — do not use prompt()/input() or the next line would be consumed as "reply".
            print(empty_retry_message)
            continue
        try:
            return parse(raw)
        except ValueError as e:
            if callable(on_invalid):
                msg = on_invalid(e, hint)
            else:
                msg = on_invalid.format(error=e)
            # Print only — prompt() would eat the user's retry input on the error line.
            print(msg.rstrip())


@dataclass(slots=True)
class CommandResult:
    kind: str
    message: str
    should_exit: bool = False


def _guard(run: Callable[[], str]) -> str:
    try:
        return run()
    except PromptCancelled:
        return CANCELED


def _parse_add_contact_cli(pos: list[str]) -> tuple[str, str | None, str | None, str | None, list[str]]:
    """
    name, address, email, birthday, phones.

    Two bare tokens with no @ / date / phone tail → one full name (e.g. Ivan Ivanenko);
    address is left unset so the UI still asks for it.
    """
    if not pos:
        return "", None, None, None, []

    rest = list(pos)
    phones: list[str] = []
    while rest and len(Phone.normalize(rest[-1])) >= 10:
        phones.insert(0, rest.pop())
    birthday_s: str | None = None
    if rest and re.fullmatch(r"\d{1,2}\.\d{1,2}\.\d{4}", rest[-1]):
        birthday_s = rest.pop()
    email_s: str | None = None
    if rest and "@" in rest[-1]:
        email_s = rest.pop()

    structured = bool(phones or birthday_s or email_s)
    if not structured and len(rest) == 2:
        return f"{rest[0]} {rest[1]}".strip(), None, None, None, []
    if not structured and len(rest) == 1:
        return rest[0], None, None, None, []
    if not structured and len(rest) >= 3:
        return rest[0], " ".join(rest[1:]).strip() or None, None, None, []
    if not rest:
        return "", None, email_s, birthday_s, phones

    name = rest[0]
    address_s = rest[1] if len(rest) > 1 else None
    if len(rest) > 2 and email_s is None:
        email_s = rest[2]
    if len(rest) > 3 and birthday_s is None:
        birthday_s = rest[3]
    if len(rest) > 4 and not phones:
        phones = rest[4:]
    return name, address_s, email_s, birthday_s, phones


def phone_command(args: list[str], book: AddressBook, prompt: PromptFn) -> str:
    name = " ".join(args).strip() or str(
        validate_line(
            prompt,
            "Contact name",
            lambda r: Name(r).value,
            field_optional=False,
            on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
            empty_retry_message="Required. Enter a value or cancel.",
        )
    )
    d = book.get_contact_details(name)
    return d if d else f"Contact {name} not found."


def search_command(args: list[str], book: AddressBook, prompt: PromptFn) -> str:
    q = " ".join(args[1:]).strip() if len(args) > 1 else ""
    q = q or validate_line(
        prompt,
        "Contact search query: ",
        lambda r: r,
        empty_retry_message="Please enter a value or cancel.",
    )
    r = book.search_details(q)
    return "\n\n".join(r) if r else "No contacts found."


def search_contact_field_command(
    field_name: str, args: list[str], book: AddressBook, prompt: PromptFn
) -> str:
    q = " ".join(args[1:]).strip() if len(args) > 1 else ""
    q = q or validate_line(
        prompt,
        f"{field_name} search query: ",
        lambda r: r,
        empty_retry_message="Please enter a value or cancel.",
    )
    r = book.search_field_details(field_name, q)
    return "\n\n".join(r) if r else "No contacts found."


def add_contact_command(args: list[str], book: AddressBook, db: DB, prompt: PromptFn) -> str:
    if not args or args[0].lower() != "contact":
        return (
            "Usage: add contact <name> [address] [email] [birthday] [phone1 …]\n"
            "Two words alone (e.g. Ivan Ivanenko) = full name; address is asked next."
        )

    while True:
        pos = args[1:]
        if not pos:
            name = str(
                validate_line(
                    prompt,
                    "Contact name",
                    lambda r: Name(r).value,
                    field_optional=False,
                    on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
                    empty_retry_message="Required. Enter a value or cancel.",
                )
            )
            address = validate_line(
                prompt,
                f"Address for {name}",
                lambda r: Address(r).value,
                field_optional=True,
                on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
                on_empty=lambda: None,
            )
            address = str(address) if address else None
            ev = validate_line(
                prompt,
                f"Email for {name}",
                lambda r: Email(r).value,
                field_optional=True,
                on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
                on_empty=lambda: None,
            )
            email = str(ev) if ev else None
            birthday = validate_line(
                prompt,
                "Birthday (DD.MM.YYYY)",
                lambda r: Birthday(r).value,
                field_optional=True,
                on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
                on_empty=lambda: None,
            )
            phones = validate_line(
                prompt,
                f"Phones for {name}",
                lambda raw: (
                    [Phone(p).value for p in parts]
                    if (parts := [p.strip() for p in raw.split(",") if p.strip()])
                    else []
                ),
                field_optional=True,
                suffix_before_colon=" (comma-separated)",
                on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}\n",
                on_empty=lambda: [],
            )
        else:
            name_s, address_s, email_s, birthday_s, phone_tokens = _parse_add_contact_cli(pos)
            try:
                name = Name(name_s.strip()).value
            except ValueError:
                prompt(f"Invalid name ({name_s.strip()!r}).\n")
                name = str(
                    validate_line(
                        prompt,
                        "Contact name",
                        lambda r: Name(r).value,
                        field_optional=False,
                        on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
                        empty_retry_message="Required. Enter a value or cancel.",
                    )
                )
            address = normalize_optional(address_s, Address) if address_s else None
            email = normalize_optional(email_s, Email) if email_s else None
            birthday = normalize_optional(birthday_s, Birthday) if birthday_s else None
            phones: list[str] = []
            if phone_tokens:
                try:
                    phones = [Phone(p).value for p in phone_tokens if str(p).strip()]
                except ValueError:
                    phones = []
            if address is None:
                a = validate_line(
                    prompt,
                    f"Address for {name}",
                    lambda r: Address(r).value,
                    field_optional=True,
                    on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
                    on_empty=lambda: None,
                )
                address = str(a) if a else None
            if email is None:
                ev = validate_line(
                    prompt,
                    f"Email for {name}",
                    lambda r: Email(r).value,
                    field_optional=True,
                    on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
                    on_empty=lambda: None,
                )
                email = str(ev) if ev else None
            if birthday is None:
                birthday = validate_line(
                    prompt,
                    "Birthday (DD.MM.YYYY)",
                    lambda r: Birthday(r).value,
                    field_optional=True,
                    on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
                    on_empty=lambda: None,
                )
            if not phones:
                phones = validate_line(
                    prompt,
                    f"Phones for {name}",
                    lambda raw: (
                        [Phone(p).value for p in parts]
                        if (parts := [p.strip() for p in raw.split(",") if p.strip()])
                        else []
                    ),
                    field_optional=True,
                    suffix_before_colon=" (comma-separated)",
                    on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}\n",
                    on_empty=lambda: [],
                )

        cid = db.next_contact_id()
        try:
            book.add_contact(
                contact_id=cid,
                name=name,
                address=address,
                phones=phones,
                email=email,
                birthday=birthday.strftime("%d.%m.%Y") if birthday else None,
            )
        except ValueError as e:
            if prompt(f"Could not save: {e}\nEnter — retry  cancel — stop: ").strip().lower() == "cancel":
                return "Contact creation canceled."
            args = ["contact"]
            continue
        if err := db.save_contacts(book.data):
            return err
        return f"Added contact #{cid}: {name}."


def edit_contact_command(args: list[str], book: AddressBook, db: DB, prompt: PromptFn) -> str:
    if not args or args[0].lower() != "contact":
        return "Usage: edit contact <name>"

    current = " ".join(args[1:]).strip() or str(
        validate_line(
            prompt,
            "Contact to edit",
            lambda r: Name(r).value,
            field_optional=False,
            on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
            empty_retry_message="Required. Enter a value or cancel.",
        )
    )
    rec = book.find(current)
    if not rec:
        return f"Contact {current} not found."

    while True:
        nn = validate_line(
            prompt,
            f"Name [{rec.name}] (Enter keep)",
            lambda r: Name(r).value,
            field_optional=True,
            on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
            on_empty=lambda: None,
        )
        new_name = str(nn) if nn else None
        na = validate_line(
            prompt,
            f"Address [{rec.address or '-'}] (Enter keep)",
            lambda r: Address(r).value,
            field_optional=True,
            on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
            on_empty=lambda: None,
        )
        new_address = None if na is None else str(na)
        ne = validate_line(
            prompt,
            f"Email [{rec.email or '-'}] (Enter keep)",
            lambda r: Email(r).value,
            field_optional=True,
            on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
            on_empty=lambda: None,
        )
        new_email = None if ne is None else str(ne)
        nb = validate_line(
            prompt,
            f"Birthday [{rec.birthday.strftime('%d.%m.%Y') if rec.birthday else '-'}] (Enter keep)",
            lambda r: Birthday(r).value,
            field_optional=True,
            on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
            on_empty=lambda: None,
        )
        new_bday = None if nb is None else nb.strftime("%d.%m.%Y")
        line = prompt(f"Phones [{', '.join(rec.phones) if rec.phones else '-'}] (comma, Enter keep): ").strip()
        if line.lower() == "cancel":
            raise PromptCancelled
        new_phones = None
        if line:
            try:
                parts = [x.strip() for x in line.split(",") if x.strip()]
                new_phones = [Phone(p).value for p in parts]
            except ValueError:
                prompt("Invalid phone(s). Need 10 digits each. Try again on next round.\n")
                continue

        try:
            book.edit_contact(
                rec.name,
                new_name=new_name,
                new_address=new_address,
                new_email=new_email,
                new_birthday=new_bday,
                new_phones=new_phones,
            )
        except ValueError as e:
            if prompt(f"Invalid: {e}\nEnter — again  cancel — stop: ").strip().lower() == "cancel":
                return "Canceled (not saved)."
            rec = book.find(new_name or current) or rec
            continue
        break

    if err := db.save_contacts(book.data):
        return f"{err} Changes were not saved (reloaded from storage)."
    u = book.find(new_name or current)
    return f"Updated contact: {u.name}." if u else "Not updated."


def edit_note_command(args: list[str], notes_book: NotesBook, db: DB, prompt: PromptFn) -> str:
    arg = args[1].strip() if len(args) > 1 else None
    if arg:
        try:
            note_id = NoteId(arg).value
        except ValueError as e:
            prompt(f"{e} ({arg!r}).\n")
            note_id = validate_line(
                prompt,
                f"Note id to edit{NoteId.PROMPT_HINT}: ",
                lambda r: NoteId(r).value,
                on_invalid=lambda e, _h: f"{e}. Try again or cancel.\n",
            )
    else:
        note_id = validate_line(
            prompt,
            f"Note id to edit{NoteId.PROMPT_HINT}: ",
            lambda r: NoteId(r).value,
            on_invalid=lambda e, _h: f"{e}. Try again or cancel.\n",
        )
    note = notes_book.get_note(note_id)
    if not note:
        return f"No note #{note_id}."

    new_text = validate_line(
        prompt,
        f"Text [{note.text}] (Enter keep)",
        lambda r: NoteText(r).value,
        field_optional=True,
        on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
        on_empty=lambda: None,
    )
    new_text = str(new_text) if new_text else None
    new_tags = validate_line(
        prompt,
        f"Tags [{', '.join(note.tags) if note.tags else '-'}]",
        lambda raw: [
            Tag(t).value for t in (x.strip() for x in raw.split(",") if x.strip())
        ],
        field_optional=True,
        on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
        on_empty=lambda: None,
    )
    try:
        notes_book.edit_note(note_id, text=new_text, tags=new_tags)
    except (ValueError, KeyError) as e:
        return f"Could not update: {e}"
    if err := db.save_notes(notes_book.all_notes()):
        return f"{err} Note was not saved."
    return f"Updated note #{note_id}."


def delete_contact_command(args: list[str], book: AddressBook, db: DB, prompt: PromptFn) -> str:
    if not args or args[0].lower() != "contact":
        return "Usage: delete contact <name>"
    name = " ".join(args[1:]).strip() or str(
        validate_line(
            prompt,
            "Contact to delete",
            lambda r: Name(r).value,
            field_optional=False,
            on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
            empty_retry_message="Required. Enter a value or cancel.",
        )
    )
    if not book.delete_contact(name):
        return f"Contact {name} not found."
    if err := db.save_contacts(book.data):
        return f"{err} Delete was not saved (reloaded from storage)."
    return f"Deleted contact: {name}."


def add_note_command(args: list[str], notes_book: NotesBook, db: DB, prompt: PromptFn) -> str:
    raw = " ".join(args).strip()
    try:
        text: str | None = NoteText(raw).value if raw else None
    except ValueError:
        text = None
    if text is None:
        text = str(
            validate_line(
                prompt,
                "Note text",
                lambda r: NoteText(r).value,
                field_optional=False,
                on_invalid=lambda e, h: f"Invalid: {e}. Try again{h}.\n",
                empty_retry_message="Required. Enter a value or cancel.",
            )
        )
    nid = db.next_note_id()
    notes_book.add_note(note_id=nid, text=text)
    if err := db.save_notes(notes_book.all_notes()):
        notes_book.remove_note(nid)
        return f"{err} Note was not added."
    return f"Added note #{nid}."


def notes_command(notes_book: NotesBook) -> str:
    return notes_book.render_all_notes()


def contacts_command(book: AddressBook) -> str:
    return book.render_all_contacts()


def birthdays_command(args: list[str], book: AddressBook, prompt: PromptFn) -> str:
    raw = args[0].strip() if args else None
    if raw:
        try:
            days = Days(raw).value
        except ValueError as e:
            prompt(f"{e} ({raw!r}).\n")
            days = validate_line(
                prompt,
                f"Days ahead{Days.PROMPT_HINT}: ",
                lambda r: Days(r).value,
                on_invalid=lambda e, _h: f"{e}. Try again or cancel.\n",
            )
    else:
        days = validate_line(
            prompt,
            f"Days ahead{Days.PROMPT_HINT}: ",
            lambda r: Days(r).value,
            on_invalid=lambda e, _h: f"{e}. Try again or cancel.\n",
        )
    up = book.get_upcoming_birthdays(days)
    if not up:
        return f"No birthdays in the next {days} day(s)."
    lines = [f"Birthdays in the next {days} day(s):"]
    for x in up:
        lines.append(f"{x['name']}: {x['birthday']} (in {x['days_left']} day(s))")
    return "\n".join(lines)


def search_notes_command(args: list[str], notes_book: NotesBook, prompt: PromptFn) -> str:
    q = " ".join(args[1:]).strip() if len(args) > 1 else ""
    q = q or validate_line(
        prompt,
        "Note search query: ",
        lambda r: r,
        empty_retry_message="Please enter a value or cancel.",
    )
    return notes_book.render_search(q)


def search_note_field_command(
    field_name: str, args: list[str], notes_book: NotesBook, prompt: PromptFn
) -> str:
    q = " ".join(args[1:]).strip() if len(args) > 1 else ""
    q = q or validate_line(
        prompt,
        f"{field_name} search query: ",
        lambda r: r,
        empty_retry_message="Please enter a value or cancel.",
    )
    return notes_book.render_search_by_field(field_name, q)


def delete_note_command(args: list[str], notes_book: NotesBook, db: DB, prompt: PromptFn) -> str:
    arg = args[0].strip() if args else None
    if arg:
        try:
            note_id = NoteId(arg).value
        except ValueError as e:
            prompt(f"{e} ({arg!r}).\n")
            note_id = validate_line(
                prompt,
                f"Note id to delete{NoteId.PROMPT_HINT}: ",
                lambda r: NoteId(r).value,
                on_invalid=lambda e, _h: f"{e}. Try again or cancel.\n",
            )
    else:
        note_id = validate_line(
            prompt,
            f"Note id to delete{NoteId.PROMPT_HINT}: ",
            lambda r: NoteId(r).value,
            on_invalid=lambda e, _h: f"{e}. Try again or cancel.\n",
        )
    if not notes_book.remove_note(note_id):
        return f"Note #{note_id} not found."
    if err := db.save_notes(notes_book.all_notes()):
        return f"{err} Delete was not saved (reloaded notes from storage)."
    return f"Deleted note #{note_id}."


def help_command() -> str:
    lines = [
        "Available commands:",
        "- help",
        "- add contact <name> [address] [email] [birthday] [phones…] (two tokens w/o @/date/phone = full name)",
        "- edit contact <name>",
        "- edit note <id>",
        "- delete contact <name>",
        "- add note <text>",
        "- birthdays <days>: upcoming birthdays in the next N days (also: show birthdays <days>)",
        "- show contacts | show notes",
        "- search contact|note|address|phone|email|birthday|tag <query>",
        "- delete note <id>",
        "- phone <name>",
    ]
    if is_chat_available():
        lines.append("- chat")
    lines.append("- close | exit")
    return "\n".join(lines)


def execute_command(
    command: str,
    args: list[str],
    *,
    book: AddressBook,
    notes_book: NotesBook,
    db: DB,
    prompt: PromptFn,
) -> CommandResult:
    command = command.lower()
    if command in ("close", "exit"):
        return CommandResult("command", "Good bye!", True)
    if command == "help":
        return CommandResult("command", help_command())

    if command == "add":
        if args and args[0].lower() == "note":
            return CommandResult(
                "note", _guard(lambda: add_note_command(args[1:], notes_book, db, prompt))
            )
        return CommandResult(
            "contact", _guard(lambda: add_contact_command(args, book, db, prompt))
        )
    if command == "edit":
        if args and args[0].lower() == "note":
            return CommandResult(
                "note", _guard(lambda: edit_note_command(args, notes_book, db, prompt))
            )
        return CommandResult(
            "contact", _guard(lambda: edit_contact_command(args, book, db, prompt))
        )
    if command == "delete":
        if args and args[0].lower() == "note":
            return CommandResult(
                "note", _guard(lambda: delete_note_command(args[1:], notes_book, db, prompt))
            )
        return CommandResult(
            "contact", _guard(lambda: delete_contact_command(args, book, db, prompt))
        )
    if command == "phone":
        return CommandResult("contact", _guard(lambda: phone_command(args, book, prompt)))
    if command == "birthdays":
        return CommandResult(
            "contact", _guard(lambda: birthdays_command(args, book, prompt))
        )
    if command == "search":
        if args and args[0].lower() == "address":
            return CommandResult(
                "contact",
                search_contact_field_command("address", args, book, prompt),
            )
        if args and args[0].lower() == "phone":
            return CommandResult(
                "contact",
                search_contact_field_command("phone", args, book, prompt),
            )
        if args and args[0].lower() == "email":
            return CommandResult(
                "contact",
                search_contact_field_command("email", args, book, prompt),
            )
        if args and args[0].lower() == "birthday":
            return CommandResult(
                "contact",
                search_contact_field_command("birthday", args, book, prompt),
            )
        if args and args[0].lower() == "tag":
            return CommandResult(
                "note",
                search_note_field_command("tag", args, notes_book, prompt),
            )
        if args and args[0].lower() == "note":
            return CommandResult(
                "note", search_notes_command(args, notes_book, prompt)
            )
        if args and args[0].lower() == "contact":
            return CommandResult("contact", search_command(args, book, prompt))
        return CommandResult(
            "command",
            "Usage: search contact|note|address|phone|email|birthday|tag <query>",
        )
    if command == "notes":
        return CommandResult("note", notes_command(notes_book))
    if command == "show":
        if args and args[0].lower() in ("contact", "contacts"):
            return CommandResult("contact", contacts_command(book))
        if args and args[0].lower() in ("note", "notes"):
            return CommandResult("note", notes_command(notes_book))
        if args and args[0].lower() == "birthdays":
            return CommandResult(
                "contact",
                _guard(lambda: birthdays_command(args[1:], book, prompt)),
            )
        return CommandResult(
            "command",
            "Usage: show contacts | show notes | show birthdays <days>",
        )
    return CommandResult("command", "Invalid command. Try help.")
