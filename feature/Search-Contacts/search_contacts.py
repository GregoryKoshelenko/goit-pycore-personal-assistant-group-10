"""
Module: search_contacts

Provides functionality to search contacts in the AddressBook
by different criteria such as name, phone number, or email.
"""


def search_contacts(book, query):
    """
    Search contacts by name, phone or email.

    Args:
        book: AddressBook instance containing contacts in book.data
        query (str): text to search

    Returns:
        list: list of matching Record objects
    """

    results = []

    # Normalize search query
    query = query.lower().strip()

    if not query:
        return results

    for record in book.data.values():

        # --- Search by name ---
        name = record.name.value.lower()
        if query in name:
            results.append(record)
            continue

        # --- Search by phone ---
        for phone in record.phones:
            if query in phone.value.lower():
                results.append(record)
                break

        # --- Search by email ---
        if hasattr(record, "email") and record.email:
            if query in record.email.value.lower():
                results.append(record)

    return results


def print_search_results(results):
    """
    Utility function to print search results.

    Args:
        results (list): list of Record objects
    """

    if not results:
        print("No contacts found.")
        return

    for record in results:
        print(record)