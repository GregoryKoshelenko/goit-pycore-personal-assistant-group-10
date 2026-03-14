"""Shared terminal text helpers: search highlights."""

import re

from colorama import Style

from styles import (
    BACK_RESET,
    HIGHLIGHT_BLOCK_BG,
    HIGHLIGHT_BLOCK_FG,
    HIGHLIGHT_INLINE_MATCH,
)

__all__ = ["highlight_matches"]


def highlight_matches(
    value: str,
    query: str,
    *,
    base_color: str,
    block: bool = False,
) -> str:
    """
    Wrap case-insensitive query matches in ANSI so they stand out in the terminal.

    - ``block=True`` (notes): yellow block + black bold text, then ``base_color``.
    - ``block=False`` (contacts): bright yellow match, then ``base_color``.
    """
    if not value or not query:
        return value
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    if block:

        def repl(m: re.Match[str]) -> str:
            return (
                f"{HIGHLIGHT_BLOCK_BG}{HIGHLIGHT_BLOCK_FG}{Style.BRIGHT}{m.group(0)}"
                f"{Style.NORMAL}{BACK_RESET}{base_color}"
            )

    else:

        def repl(m: re.Match[str]) -> str:
            return f"{HIGHLIGHT_INLINE_MATCH}{Style.BRIGHT}{m.group(0)}{Style.NORMAL}{base_color}"

    return pattern.sub(repl, value)
