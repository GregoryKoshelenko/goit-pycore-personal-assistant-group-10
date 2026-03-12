# Personal Assistant CLI

Simple personal assistant CLI app for storing contacts and notes

## What it does
- Adds and saves contacts
- Stores phone numbers and emails
- Supports birthday field and simple search

---
## Installation (pip)

1. Create and activate a virtual environment (recommended):
Install python if you dont have it already isntalled: https://www.python.org/downloads/

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

On first run, the app creates storage at `storage/assistant.pkl`.

## Available Commands

1. `add contact <name> <phone1> [phone2 ...]`
- Adds a contact and saves it.
- Example: `add contact Alice 0501234567`

2. `add note <text>`
- Adds a note and saves it.
- Example: `add note buy milk after work`

3. `phone <name>`
- Shows phone numbers for a contact by exact name.
- Example: `phone Alice`

4. `search <query>`
- Searches contacts by name or phone fragment.
- Example: `search 050`

5. `exit` or `close`
- Exits the application.

## Notes

- Contact names are currently parsed as a single word in `add contact`.
- Phone numbers are normalized to digits.

