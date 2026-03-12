from address_book import AddressBook, Record
from datetime import date, timedelta


def parse_input(user_input: str) -> tuple[str, list[str]]:
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


def seed_book() -> AddressBook:
    book = AddressBook()
    today = date.today()
    soon_birthday = (today + timedelta(days=2)).replace(year=1992).strftime("%d.%m.%Y")
    later_birthday = (today + timedelta(days=20)).replace(year=1990).strftime("%d.%m.%Y")

    book.add_record(Record("Alice", ["0501234567"], soon_birthday))
    book.add_record(Record("Bob", ["0670001122", "0998887766"], later_birthday))
    book.add_record(Record("Carol", ["+38 (050) 555-12-34"]))
    return book


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


def birthdays_command(args: list[str], book: AddressBook) -> str:
    if len(args) != 1:
        return "Please provide number of days. Example: birthdays 7"

    try:
        days = int(args[0])
        if days < 0:
            return "Days must be a non-negative integer."
    except ValueError:
        return "Days must be a non-negative integer."

    upcoming = book.get_upcoming_birthdays(days)
    if not upcoming:
        return f"No birthdays in the next {days} day(s)."

    lines = [f"Birthdays in the next {days} day(s):"]
    for item in upcoming:
        lines.append(f"{item['name']}: {item['birthday']} (in {item['days_left']} day(s))")
    return "\n".join(lines)


def main() -> None:
    book = seed_book()
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
        elif command == "birthdays":
            print(birthdays_command(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
