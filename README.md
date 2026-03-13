# Personal Assistant CLI by Purple Unicorns 🦄🦄🦄🦄

The app allows users to store contact information, manage notes, and quickly search for important data.
## Demo 
[![asciicast](https://asciinema.org/a/832566.svg)](https://asciinema.org/a/832566)

## Features

- Add and manage contacts
- Store phone numbers, emails,addresses, and birthdays
- Edit existing contacts
- Search contacts by name, phone, address, email, or birthday
- Create and manage notes
- Search notes by text or tags
- Persistent storage between sessions

## Commands Description

```
help | Show available commands
add contact | Add a new contact
edit contact | Edit contact fields
delete contact | Remove a contact
show contacts | Display all contacts
phone | Show phone numbers for a contact
search contact | Search contacts by name
search address | Search contacts by address
search phone | Search contacts by phone
search email | Search contacts by email
search birthday | Search contacts by birthday
add note | Create a note
edit note | Edit a note
delete note | Delete a note
search note | Search notes by text
search tag | Search notes by tag
show notes | Display all notes
exit / close | Exit the application
```

## Project Structure

```
goit-pycore-personal-assistant-group-10/

├── main.py # Application entry point
├── commands.py # CLI command handling
├── address_book.py # Contact management logic
├── notes.py # Notes management
├── welcome_message.py # CLI welcome screen
│
├── data_types/ # Custom field types and validations
├── db/ # Database configuration and storage
├── orm/ # ORM models and database interaction
│
├── requirements.txt # Project dependencies
├── pyproject.toml # Project configuration
├── .gitignore
└── README.md
```

## Tech Stack

- Python
- SQLAlchemy
- CLI interface
- SQLite / Pickle storage


## Installation (pip)

1. Create and activate a virtual environment (recommended):
Install python if you dont have it already isntalled: https://www.python.org/downloads/

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
python -m pip install -e .
```

## Run

```bash
python main.py
```
or just

```bash
book
```

On first run, the app creates storage at `storage/assistant.pkl` or `storage/assistant.db` depending on DB provider.


## Notes

- Contact names are currently parsed as a single word in `add contact`.
- Phone numbers are normalized to digits.
- Data is automatically saved after changes

