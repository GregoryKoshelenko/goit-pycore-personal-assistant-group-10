from address_book import AddressBook 

def parse_input(user_input: str):
    """Parses user input into command and arguments."""
    if not user_input.strip():
        return "", []
    parts = user_input.split()
    cmd = parts[0].strip().lower()
    args = parts[1:]
    return cmd, args

def add_contact_handler(args: list, book: AddressBook) -> str:
    """
    Handles the 'add' command. 
    Checks for duplicates and asks for confirmation if found.
    """
    if len(args) < 2:
        return "Error: Name and phone are required."
    
    name, phone = args[0], args[1]
    
    # Check for existing contact
    result = book.add_contact(name, phone)
    
    if result == "DUPLICATE_EXISTS":
        # Prompt that accepts both 'y' and 'yes'
        choice = input(f"Warning: Contact '{name}' with phone '{phone}' already exists. Add anyway? (y/n): ").strip().lower()
        
        if choice in ['y', 'yes']:
            # Force add if user confirmed
            return book.add_contact(name, phone, force=True)
        else:
            return "Addition cancelled by user."
            
    return result

def main():
    """Main application cycle."""
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