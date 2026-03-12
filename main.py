from address_book import AddressBook, Record


def parse_input(user_input: str) -> tuple[str, list[str]]:
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


def seed_book() -> AddressBook:
    book = AddressBook()
    book.add_record(Record("Alice", ["(050)123-45-67"], "alice@example.com"))
    book.add_record(Record("Bob", ["(067)000-11-22", "(099)888-77-66"], "bob@example.com"))
    book.add_record(Record("Carol", ["(050)555-12-34"]))
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
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
