import argparse
import os
import sys
from address_book import AddressBook
from ai_assistant import is_chat_available
from colorama import init
from commands import CommandResult, execute_command
from styles import CLI_STYLERS
from db import DB, SQLiteDBProvider
from notes import NotesBook
from welcome_message import print_welcome_message


init(autoreset=True)


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
    book.add_contact(contact_id=DB.next_id(book.data), name="Carol", phones=["0505551234"])
    return book


def load_books(db: DB) -> tuple[AddressBook, NotesBook]:
    """Load contacts and notes from storage, seeding contacts if empty."""
    contacts_data = db.load_contacts()
    notes_data = db.get_notes()

    # Seed sample contacts when storage is empty
    if contacts_data:
        book = AddressBook(contacts_data)
    else:
        book = seed_book()
        if db.save_contacts(book.data):
            raise RuntimeError("Could not seed initial contacts to storage.")

    return book, NotesBook(notes_data)


def prompt_user(prompt_text: str) -> str:
    """Prompt the user with command color and return stripped text."""
    return input(CLI_STYLERS["command"](prompt_text)).strip()


def print_result(result: CommandResult) -> None:
    """Print command output with kind-appropriate color."""
    styler = CLI_STYLERS.get(result.kind, CLI_STYLERS["command"])
    print(styler(result.message))


def run_app(*, chat_first: bool) -> None:
    """Run the interactive assistant; optional Gemini chat on startup."""
    provider = SQLiteDBProvider("storage/assistant.db")
    # Alternative: PickleDBProvider("storage/assistant.pkl")
    db = DB(provider)
    book, notes_book = load_books(db)
    clear_screen()
    print_welcome_message()

    # Shared executor for normal CLI and Gemini tool calls
    def run_cmd(cmd: str, args: list[str]) -> CommandResult:
        return execute_command(
            cmd, args, book=book, notes_book=notes_book, db=db, prompt=prompt_user
        )

    def execute_for_ai(cmd: str, args: list[str]) -> tuple[str, str, bool]:
        r = run_cmd(cmd, args)
        # Same highlight as normal CLI for contact/note tool results (search, phone, lists, …)
        if r.kind in ("contact", "note"):
            print_result(r)
        return r.message, r.kind, r.should_exit

    # Lazy import: only load ai_assistant when entering chat
    def enter_chat(banner: str | None = None) -> None:
        from ai_assistant import run_chat_session

        if banner:
            print(CLI_STYLERS["command"](banner))
        run_chat_session(
            prompt_fn=prompt_user,
            print_fn=lambda s: print(CLI_STYLERS["command"](s)),
            execute_fn=execute_for_ai,
        )

    # AI assistant is ON only with --chat and GEMINI_API_KEY
    gemini_on = chat_first and is_chat_available()
    if chat_first and not gemini_on:
        print(
            CLI_STYLERS["command"](
                "Flag --chat was set but GEMINI_API_KEY is missing. "
                "Running normal command mode. Set the key and use --chat or type 'chat'."
            )
        )
    if gemini_on:
        enter_chat("Gemini chat is ON (--chat + GEMINI_API_KEY). Type exit to leave chat.")

    while True:
        user_input = prompt_user("Enter a command(try 'help'): ")
        command, args = parse_input(user_input)

        # Conversational mode: needs key (same entry as --chat)
        if command == "chat":
            if not is_chat_available():
                print(
                    CLI_STYLERS["command"](
                        "GEMINI_API_KEY is not set. Export it and restart, or use --chat with the key set."
                    )
                )
                continue
            enter_chat()
            continue

        result = run_cmd(command, args)
        print_result(result)
        if result.should_exit:
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="Personal assistant CLI")
    parser.add_argument(
        "--chat",
        action="store_true",
        help="If GEMINI_API_KEY is set, start in (or enable) Gemini chat mode on launch.",
    )
    args = parser.parse_args()
    try:
        run_app(chat_first=args.chat)
    except KeyboardInterrupt:
        print(CLI_STYLERS["command"]("\nGood bye!"))
        sys.exit(0)


if __name__ == "__main__":
    main()
