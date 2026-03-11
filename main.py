from address_book import AddressBook

def parse_input(user_input: str):
    if not user_input.strip():
        return "", []
    parts = user_input.split()
    cmd = parts[0].strip().lower()
    args = parts[1:]
    return cmd, args

def add_contact_handler(args: list, book: AddressBook) -> str:
    if len(args) < 2:
        return "Error: Name and phone are required."
    name, phone = args[0], args[1]
    return book.add_contact(name, phone)

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ").strip()
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact_handler(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()