"""
Central terminal colors and CLI stylers (Colorama + RGB ANSI).
Use with colorama.init(autoreset=True) once at app startup (see main.py).
"""

from __future__ import annotations

from collections.abc import Callable

from colorama import Back, Fore, Style

BACK_RESET = Back.RESET

# --- RGB (truecolor) ----------------------------------------------------------
NEON_BLUE = "\033[38;2;0;230;255m"  # prompts, command / chat UI

# --- Semantic Foreground (CLI + search highlight base) -----------------------
NOTE_FORE = Fore.YELLOW
CONTACT_FORE = Fore.MAGENTA

# --- Welcome banner gradient steps (truecolor) --------------------------------
UNICORN_SHADES: tuple[str, ...] = (
    "\033[38;2;120;70;168m",
    "\033[38;2;140;85;185m",
    "\033[38;2;165;100;200m",
    "\033[38;2;185;115;210m",
    "\033[38;2;200;130;220m",
    "\033[38;2;215;140;215m",
    "\033[38;2;228;155;225m",
    "\033[38;2;238;175;235m",
    "\033[38;2;245;195;240m",
    "\033[38;2;248;215;250m",
)

CYAN_SHADES: tuple[str, ...] = (
    "\033[38;2;55;95;140m",
    "\033[38;2;50;115;155m",
    "\033[38;2;45;135;170m",
    "\033[38;2;40;155;185m",
    "\033[38;2;35;175;200m",
    "\033[38;2;55;200;220m",
    "\033[38;2;100;215;235m",
    "\033[38;2;150;228;248m",
    "\033[38;2;185;240;255m",
    "\033[38;2;210;248;255m",
)

FRAME_SHADES: tuple[str, ...] = (
    "\033[38;2;60;100;145m",
    "\033[38;2;50;120;165m",
    "\033[38;2;45;145;185m",
    "\033[38;2;55;170;200m",
    "\033[38;2;70;195;220m",
    "\033[38;2;110;215;235m",
    "\033[38;2;150;230;250m",
    "\033[38;2;190;245;255m",
)

# --- Search highlight fragments (text_utils) ----------------------------------
HIGHLIGHT_BLOCK_BG = Back.YELLOW
HIGHLIGHT_BLOCK_FG = Fore.BLACK
HIGHLIGHT_INLINE_MATCH = Fore.YELLOW  # bright match for contacts


def _reset() -> str:
    return Style.RESET_ALL


def style_note(text: str) -> str:
    return f"{NOTE_FORE}{text}{_reset()}"


def style_contact(text: str) -> str:
    return f"{CONTACT_FORE}{text}{_reset()}"


def style_command(text: str) -> str:
    return f"{NEON_BLUE}{text}{_reset()}"


# CommandResult.kind -> styler (default: command)
CLI_STYLERS: dict[str, Callable[[str], str]] = {
    "note": style_note,
    "contact": style_contact,
    "command": style_command,
}

__all__ = [
    "NEON_BLUE",
    "NOTE_FORE",
    "CONTACT_FORE",
    "UNICORN_SHADES",
    "CYAN_SHADES",
    "FRAME_SHADES",
    "HIGHLIGHT_BLOCK_BG",
    "HIGHLIGHT_BLOCK_FG",
    "HIGHLIGHT_INLINE_MATCH",
    "BACK_RESET",
    "style_note",
    "style_contact",
    "style_command",
    "CLI_STYLERS",
]
