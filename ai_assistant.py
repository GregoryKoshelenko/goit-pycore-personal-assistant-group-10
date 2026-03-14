"""
Gemini function-calling helper for conversational command execution.

Uses the Generative Language API (same as curl). Docs:
https://ai.google.dev/gemini-api/docs/function-calling
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
GENERATE_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)


def gemini_api_key() -> str | None:
    """API key from env (stripped); None if unset or empty."""
    k = os.getenv(GEMINI_API_KEY_ENV, "").strip()
    return k or None


def is_chat_available() -> bool:
    return gemini_api_key() is not None


def _function_declarations() -> list[dict[str, Any]]:
    """OpenAPI-style declarations for every CLI action we expose to the model."""
    return [
        {
            "name": "help",
            "description": "Show all available CLI commands and usage.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "exit_app",
            "description": "Quit the personal assistant application.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "add_contact",
            "description": "Add a new contact. Name required; others optional.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Contact full name"},
                    "address": {"type": "string", "description": "Postal address"},
                    "email": {"type": "string"},
                    "birthday": {"type": "string", "description": "DD.MM.YYYY"},
                    "phones": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Phone numbers as strings",
                    },
                },
                "required": ["name"],
            },
        },
        {
            "name": "edit_contact",
            "description": "Edit an existing contact by current name; user will be prompted for fields.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Current contact name to edit"},
                },
                "required": ["name"],
            },
        },
        {
            "name": "delete_contact",
            "description": "Delete a contact by name.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
        {
            "name": "add_note",
            "description": "Add a new note with text.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Note body"}},
                "required": ["text"],
            },
        },
        {
            "name": "edit_note",
            "description": "Edit note by id (user prompted for text/tags).",
            "parameters": {
                "type": "object",
                "properties": {"note_id": {"type": "integer"}},
                "required": ["note_id"],
            },
        },
        {
            "name": "delete_note",
            "description": "Delete a note by numeric id.",
            "parameters": {
                "type": "object",
                "properties": {"note_id": {"type": "integer"}},
                "required": ["note_id"],
            },
        },
        {
            "name": "phone",
            "description": "Show full contact details for a person by name.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
        {
            "name": "show_contacts",
            "description": "List all contacts.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "show_notes",
            "description": "List all notes.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "birthdays",
            "description": "Show upcoming birthdays in the next N days.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days ahead"},
                },
                "required": ["days"],
            },
        },
        {
            "name": "search_contact",
            "description": "Search contacts by any field (name, phone, email, address, birthday).",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        {
            "name": "search_note",
            "description": "Search notes by text or tags.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        {
            "name": "search_address",
            "description": "Search contacts by address field only.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        {
            "name": "search_phone",
            "description": "Search contacts by phone field.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        {
            "name": "search_email",
            "description": "Search contacts by email field.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        {
            "name": "search_birthday",
            "description": "Search contacts by birthday field.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
        {
            "name": "search_tag",
            "description": "Search notes by tag.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    ]


SYSTEM_INSTRUCTION = """You are a helpful Personal Assistant copilot with two roles:

1) **Local app actions** — add/edit/delete contacts and notes, list, search the user's address book and notes (the only tools you have).
2) **General assistant** — answer from general knowledge when no tool is needed.

Rules:
- **Beyond local tools** (live news, LinkedIn, current prices, "find this person online", anything needing the open web): you cannot browse or search from this app. Tell the user clearly, then **ask them to search in a browser** (Google, LinkedIn, etc.) and give a **concrete search query** they can paste. If they have a saved contact, suggest using **search_contact** / **phone** first so they can copy email/name into their own search.
- **App actions**: call the matching function for address book / notes only.
- Generic math, coding, advice: plain text; no tool.
- If required info is missing for an app action, ask ONE short clarifying question.
- For add_contact, always include name; use phones array for phone numbers.
- After contact/note tools: the app already printed results—one short follow-up only; do not repeat full listings.
"""


def _api_request(api_key: str, body: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{GENERATE_URL}?key={api_key}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="replace")
        raise RuntimeError(f"Gemini API HTTP {e.code}: {err_body}") from e


def _parts_from_candidate(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    content = candidate.get("content") or {}
    return list(content.get("parts") or [])


def _text_from_parts(parts: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for p in parts:
        if "text" in p:
            chunks.append(p["text"])
    return "".join(chunks).strip()


def _function_calls_from_parts(parts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in parts:
        fc = p.get("functionCall")
        if fc:
            out.append(fc)
    return out


def function_call_to_command(name: str, args: dict[str, Any]) -> tuple[str, list[str]]:
    """Map Gemini function name + args to execute_command(command, args)."""
    a = args or {}
    if name == "help":
        return "help", []
    if name == "exit_app":
        return "exit", []
    if name == "add_contact":
        name_ = str(a.get("name", "")).strip()
        bits = ["contact", name_]
        if a.get("address"):
            bits.append(str(a["address"]))
        if a.get("email"):
            bits.append(str(a["email"]))
        if a.get("birthday"):
            bits.append(str(a["birthday"]))
        for p in a.get("phones") or []:
            bits.append(str(p))
        return "add", bits
    if name == "edit_contact":
        return "edit", ["contact", str(a.get("name", "")).strip()]
    if name == "delete_contact":
        return "delete", ["contact", str(a.get("name", "")).strip()]
    if name == "add_note":
        return "add", ["note", str(a.get("text", "")).strip()]
    if name == "edit_note":
        return "edit", ["note", str(int(a["note_id"]))]
    if name == "delete_note":
        return "delete", ["note", str(int(a["note_id"]))]
    if name == "phone":
        return "phone", [str(a.get("name", "")).strip()]
    if name == "show_contacts":
        return "show", ["contacts"]
    if name == "show_notes":
        return "show", ["notes"]
    if name == "birthdays":
        return "birthdays", [str(int(a["days"]))]
    if name == "search_contact":
        return "search", ["contact", str(a.get("query", "")).strip()]
    if name == "search_note":
        return "search", ["note", str(a.get("query", "")).strip()]
    if name == "search_address":
        return "search", ["address", str(a.get("query", "")).strip()]
    if name == "search_phone":
        return "search", ["phone", str(a.get("query", "")).strip()]
    if name == "search_email":
        return "search", ["email", str(a.get("query", "")).strip()]
    if name == "search_birthday":
        return "search", ["birthday", str(a.get("query", "")).strip()]
    if name == "search_tag":
        return "search", ["tag", str(a.get("query", "")).strip()]
    raise ValueError(f"Unknown function: {name}")


@dataclass
class ChatTurnResult:
    assistant_text: str | None
    should_exit: bool


def _fn_response(tool_name: str, *, ok: bool, result: str | None = None, error: str | None = None) -> dict[str, Any]:
    """Single Gemini functionResponse part."""
    payload: dict[str, Any] = {"ok": ok}
    if result is not None:
        payload["result"] = result
    if error is not None:
        payload["error"] = error
    return {"functionResponse": {"name": tool_name, "response": payload}}


def run_chat_turn(
    api_key: str,
    contents: list[dict[str, Any]],
    *,
    execute_fn: Callable[[str, list[str]], tuple[str, str, bool]],
    max_rounds: int = 8,
) -> tuple[list[dict[str, Any]], ChatTurnResult]:
    """
    Model round-trip: optional function calls via execute_fn, then optional final text.
    execute_fn(cmd, args) -> (message, kind, should_exit)
    """
    body: dict[str, Any] = {
        "contents": contents,
        "tools": [{"functionDeclarations": _function_declarations()}],
        "toolConfig": {"functionCallingConfig": {"mode": "AUTO"}},
        "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
    }

    for _ in range(max_rounds):
        raw = _api_request(api_key, body)
        cands = raw.get("candidates") or []
        if not cands:
            err = raw.get("error", {}).get("message") or json.dumps(raw)[:500]
            return contents, ChatTurnResult(f"API error: {err}", False)

        parts = _parts_from_candidate(cands[0])
        model_msg = cands[0].get("content") or {"role": "model", "parts": parts}
        contents.append(model_msg)

        calls = _function_calls_from_parts(parts)
        if not calls:
            return contents, ChatTurnResult(_text_from_parts(parts) or None, False)

        responses: list[dict[str, Any]] = []
        exit_app = False
        for fc in calls:
            name = (fc.get("name") or "").strip() or "unknown"
            try:
                cmd, args = function_call_to_command(name, dict(fc.get("args") or {}))
            except Exception as e:
                responses.append(_fn_response(name, ok=False, error=str(e)))
                continue
            msg, _, should_exit = execute_fn(cmd, args)
            exit_app |= should_exit
            responses.append(_fn_response(name, ok=True, result=msg))

        contents.append({"role": "user", "parts": responses})
        if exit_app:
            return contents, ChatTurnResult(None, True)
        body["contents"] = contents

    return contents, ChatTurnResult("Too many tool rounds; try a simpler request.", False)


def run_chat_session(
    *,
    prompt_fn: Callable[[str], str],
    print_fn: Callable[[str], None],
    execute_fn: Callable[[str, list[str]], tuple[str, str, bool]],
) -> None:
    """REPL: read user lines until exit or empty."""
    key = gemini_api_key()
    if not key:
        print_fn("GEMINI_API_KEY is not set; chat is unavailable.")
        return
    print_fn(
        "Chat mode — app commands and general Q&A. For live web info, the assistant will suggest browser searches. "
        "Type 'exit' or 'quit' to leave."
    )
    contents: list[dict[str, Any]] = []
    while True:
        line = prompt_fn("chat> ").strip()
        if not line:
            continue
        if line.lower() in ("exit", "quit", "close"):
            print_fn("Left chat.")
            break
        contents.append({"role": "user", "parts": [{"text": line}]})
        try:
            contents, turn = run_chat_turn(key, contents, execute_fn=execute_fn)
        except Exception as e:
            print_fn(f"Error: {e}")
            contents.pop()
            continue
        if turn.should_exit:
            print_fn("Good bye!")
            break
        if turn.assistant_text:
            print_fn(turn.assistant_text)
