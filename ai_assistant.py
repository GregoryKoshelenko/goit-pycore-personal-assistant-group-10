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


SYSTEM_INSTRUCTION = """You are the Personal Assistant CLI copilot. You map user requests to exactly one function when possible.

Rules:
- If the user wants to run an action (add contact, search, list, etc.), call the matching function with the arguments you can infer.
- If required information is missing (e.g. which contact, which note id), do NOT guess: reply in plain text with ONE short clarifying question.
- If the user is vague (e.g. "delete something"), ask what exactly: contact vs note, and which name or id.
- For add_contact, always include name; use phones array for phone numbers.
- Never invent contact names or note ids; ask the user.
- Small talk or meta questions: answer briefly in text without calling a function unless they ask to run a command.
- After contact/note tools (search, phone, lists): the app already printed results in color—one short follow-up line only; do not repeat full listings.
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


def run_chat_turn(
    api_key: str,
    contents: list[dict[str, Any]],
    *,
    execute_fn: Callable[[str, list[str]], tuple[str, str, bool]],
) -> tuple[list[dict[str, Any]], ChatTurnResult]:
    """
    One user message may trigger multiple model rounds (function call -> result -> final text).
    execute_fn(command, args) -> (message, kind, should_exit)
    Returns updated contents and final turn result.
    """
    tools = [{"functionDeclarations": _function_declarations()}]
    body: dict[str, Any] = {
        "contents": contents,
        "tools": tools,
        "toolConfig": {"functionCallingConfig": {"mode": "AUTO"}},
        "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
    }
    max_rounds = 8
    for _ in range(max_rounds):
        raw = _api_request(api_key, body)
        candidates = raw.get("candidates") or []
        if not candidates:
            msg = raw.get("error", {}).get("message") or json.dumps(raw)[:500]
            return contents, ChatTurnResult(assistant_text=f"API error: {msg}", should_exit=False)
        cand = candidates[0]
        parts = _parts_from_candidate(cand)
        model_content = cand.get("content") or {"role": "model", "parts": parts}
        calls = _function_calls_from_parts(parts)

        if not calls:
            text = _text_from_parts(parts)
            contents.append(model_content)
            return contents, ChatTurnResult(assistant_text=text or None, should_exit=False)

        contents.append(model_content)
        response_parts: list[dict[str, Any]] = []
        should_exit = False
        for fc in calls:
            fname = fc.get("name") or ""
            fargs = dict(fc.get("args") or {})
            try:
                cmd, cmd_args = function_call_to_command(fname, fargs)
            except Exception as e:
                response_parts.append(
                    {
                        "functionResponse": {
                            "name": fname,
                            "response": {"error": str(e), "ok": False},
                        }
                    }
                )
                continue
            msg, _kind, exit_flag = execute_fn(cmd, cmd_args)
            should_exit = should_exit or exit_flag
            response_parts.append(
                {"functionResponse": {"name": fname, "response": {"result": msg, "ok": True}}}
            )
        contents.append({"role": "user", "parts": response_parts})
        if should_exit:
            return contents, ChatTurnResult(assistant_text=None, should_exit=True)
        body["contents"] = contents

    return contents, ChatTurnResult(
        assistant_text="Too many tool rounds; try a simpler request.", should_exit=False
    )


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
    print_fn("Chat mode — natural language maps to commands. Type 'exit' or 'quit' to leave chat.")
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
