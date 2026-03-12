from colorama import Style

# ANSI 24-bit foreground color shades from deep to light purple.
PURPLE_SHADES: tuple[str, ...] = (
    "\033[38;2;88;28;135m",
    "\033[38;2;103;39;152m",
    "\033[38;2;119;53;168m",
    "\033[38;2;136;67;185m",
    "\033[38;2;154;83;201m",
    "\033[38;2;171;100;216m",
    "\033[38;2;190;121;230m",
)

BLUE_SHADES: tuple[str, ...] = (
    "\033[38;2;61;90;254m",
    "\033[38;2;79;114;255m",
    "\033[38;2;97;136;255m",
    "\033[38;2;117;157;255m",
    "\033[38;2;136;177;255m",
    "\033[38;2;158;197;255m",
)

FRAME_BLUE = "\033[38;2;97;136;255m"

TITLE_ART: tuple[str, ...] = (
    " █████╗ ██████╗ ██████╗ ██████╗ ███████╗███████╗███████╗    ██████╗  ██████╗  ██████╗ ██╗  ██╗",
    "██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝    ██╔══██╗██╔═══██╗██╔═══██╗██║ ██╔╝",
    "███████║██║  ██║██║  ██║██████╔╝█████╗  ███████╗███████╗    ██████╔╝██║   ██║██║   ██║█████╔╝ ",
    "██╔══██║██║  ██║██║  ██║██╔══██╗██╔══╝  ╚════██║╚════██║    ██╔══██╗██║   ██║██║   ██║██╔═██╗ ",
    "██║  ██║██████╔╝██████╔╝██║  ██║███████╗███████║███████║    ██████╔╝╚██████╔╝╚██████╔╝██║  ██╗",
    "╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝    ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝",
    "========================Personal Assistant by Purple Unicorns v0.1============================",
)

UNICORN_ART: tuple[str, ...] = (
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⡀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡴⠊⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⣠⣴⣿⠟⠀⠀⠀⠀",
    "⠀⠀⠀⠀    ⢀⣀⣀⣠⣤⣤⣤⣄⡀⠀⣴⣿⣿⠁⠀⣠⣶⣿⣿⠟⠁⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀    ⢈⡉⠛⠛⠿⠿⠋⣁⣴⣾⣿⣿⣿⣀⠘⢿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀",
    "    ⠀⠐⠚⠛⠛⠻⠿⠗⣠⣴⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "    ⠀⠿⠿⢿⡿⢀⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "    ⠀⣶⠖⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣴⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀    ⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⠉⢿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀",
    "⠀    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀",
    "⠀    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠈⠻⠿⠿⠿⢿⣿⣿⣿⣷⡄⠀⠀⠀⠀",
    "⠀    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠿⣿⡿⠟⠁⠀⠀⠀⠀",
    "⠀    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
)

BOOK_ART: tuple[str, ...] = (
    "        _________   _________",
    "   ____/IMPORTANT\\/ NOTES  \\____",
    " /| ------------- |  ------------ |\\",
    "||| ------------- | ------------- |||",
    "||| ------------- | ------------- |||",
    "||| ------- ----- | ------------- |||",
    "||| ------------- | ------------- |||",
    "||| ------------- | ------------- |||",
    "||| ------------- | ------ -----  |||",
    "||| ------------  | ------------- |||",
    "|||_____________  |  _____________|||",
    "L/___/----------\\\\_//----------\\____\\",
)


def render_welcome_message() -> str:
    """Return title, unicorn, and book rendered with themed color palettes."""
    unicorn_width = max(len(line) for line in UNICORN_ART)
    gap = " " * 6
    top_padding = max((len(UNICORN_ART) - len(BOOK_ART)) // 2, 0)
    aligned_book = ("",) * top_padding + BOOK_ART
    if len(aligned_book) < len(UNICORN_ART):
        aligned_book = aligned_book + ("",) * (len(UNICORN_ART) - len(aligned_book))

    title_raw_lines: list[str] = []
    title_lines: list[str] = []
    for index, line in enumerate(TITLE_ART):
        shade = BLUE_SHADES[index % len(BLUE_SHADES)]
        title_raw_lines.append(line)
        title_lines.append(f"{shade}{line}{Style.RESET_ALL}")

    art_raw_lines: list[str] = []
    colored_lines: list[str] = []
    for index, unicorn_line in enumerate(UNICORN_ART):
        book_line = aligned_book[index]
        unicorn_shade = PURPLE_SHADES[index % len(PURPLE_SHADES)]
        unicorn_block = unicorn_line.ljust(unicorn_width)
        unicorn_part = f"{unicorn_shade}{unicorn_block}{Style.RESET_ALL}"
        if book_line:
            book_shade = BLUE_SHADES[index % len(BLUE_SHADES)]
            book_part = f"{book_shade}{book_line}{Style.RESET_ALL}"
            art_raw_lines.append(f"{unicorn_block}{gap}{book_line}")
            colored_lines.append(f"{unicorn_part}{gap}{book_part}")
        else:
            art_raw_lines.append(unicorn_block)
            colored_lines.append(unicorn_part)

    raw_lines = title_raw_lines + [""] + art_raw_lines
    display_lines = title_lines + [""] + colored_lines
    inner_width = max(len(line) for line in raw_lines)

    top_border = f"{FRAME_BLUE}+{'=' * (inner_width + 2)}+{Style.RESET_ALL}"
    bottom_border = top_border
    framed_lines: list[str] = [top_border]

    for raw_line, display_line in zip(raw_lines, display_lines):
        padding = " " * (inner_width - len(raw_line))
        framed_lines.append(f"{FRAME_BLUE}|| {Style.RESET_ALL}{display_line}{padding}{FRAME_BLUE} ||{Style.RESET_ALL}")

    framed_lines.append(bottom_border)
    return "\n".join(framed_lines)


def print_welcome_message() -> None:
    """Print the colored unicorn welcome banner."""
    print(render_welcome_message())
