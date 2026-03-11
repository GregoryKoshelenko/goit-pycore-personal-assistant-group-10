from address_book import AddressBook, Record


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Not enough arguments provided."
        except KeyError:
            return "Contact not found."
        except Exception as e:
            return f"An error occurred: {str(e)}"

    return inner


def parse_input(user_input: str) -> tuple[str, list[str]]:
    parts = user_input.split()
    command = parts[0].strip().lower() if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    return command, args


@input_error
def add_contact(args: list[str], book: AddressBook) -> str:
    if len(args) < 2:
        return "Please provide name and phone number."

    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_phone(phone)
    return message


@input_error
def change_contact(args: list[str], book: AddressBook) -> str:
    if len(args) < 3:
        return "Please provide name, old phone and new phone."

    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."

    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args: list[str], book: AddressBook) -> str:
    if len(args) < 1:
        return "Please provide contact name."

    name = args[0]
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."

    if not record.phones:
        return f"No phone numbers for {name}."

    phones = ", ".join(p.value for p in record.phones)
    return f"{name}: {phones}"


@input_error
def show_all(_: list[str], book: AddressBook) -> str:
    if not book.data:
        return "No contacts in address book."

    result = []
    for record in book.data.values():
        result.append(str(record))
    return "\n".join(result)


def get_help() -> str:
    commands = [
        ("hello", "Show greeting."),
        ("add <name> <phone>", "Add contact or add phone to existing contact."),
        ("add-contact <name> <phone>", "Alias for add command."),
        ("change <name> <old_phone> <new_phone>", "Change existing phone."),
        ("phone <name>", "Show contact phone numbers."),
        ("all", "Show all contacts."),
        ("help", "Show command list."),
        ("close / exit", "Exit application."),
    ]
    width = max(len(cmd) for cmd, _ in commands) + 2
    lines = ["Available commands:", ""]
    for cmd, desc in commands:
        lines.append(f"  {cmd:<{width}} {desc}")
    return "\n".join(lines)


def main() -> None:
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            print("Please enter a command.")
            continue

        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        if command == "hello":
            print("How can I help you?")
        elif command == "help":
            print(get_help())
        elif command in ["add", "add-contact"]:
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
