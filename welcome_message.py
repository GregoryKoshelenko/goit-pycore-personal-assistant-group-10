from colorama import Style

# Unicorn: lighter purple base → orchid → pink (no near-black)
UNICORN_SHADES: tuple[str, ...] = (
    "\033[38;2;120;70;168m",  # soft violet
    "\033[38;2;140;85;185m",
    "\033[38;2;165;100;200m",
    "\033[38;2;185;115;210m",
    "\033[38;2;200;130;220m",  # orchid
    "\033[38;2;215;140;215m",  # magenta-pink
    "\033[38;2;228;155;225m",
    "\033[38;2;238;175;235m",
    "\033[38;2;245;195;240m",
    "\033[38;2;248;215;250m",  # lilac-pink
)

# Title + book: steel-cyan → teal → bright cyan → ice (lighter than navy)
CYAN_SHADES: tuple[str, ...] = (
    "\033[38;2;55;95;140m",  # steel blue
    "\033[38;2;50;115;155m",
    "\033[38;2;45;135;170m",
    "\033[38;2;40;155;185m",
    "\033[38;2;35;175;200m",
    "\033[38;2;55;200;220m",  # cyan
    "\033[38;2;100;215;235m",
    "\033[38;2;150;228;248m",
    "\033[38;2;185;240;255m",
    "\033[38;2;210;248;255m",  # pale sky
)

# Frame: lighter teal/cyan sweep (readable on dark terminals)
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
        shade = CYAN_SHADES[index % len(CYAN_SHADES)]
        title_raw_lines.append(line)
        title_lines.append(f"{shade}{line}{Style.RESET_ALL}")

    art_raw_lines: list[str] = []
    colored_lines: list[str] = []
    for index, unicorn_line in enumerate(UNICORN_ART):
        book_line = aligned_book[index]
        unicorn_shade = UNICORN_SHADES[index % len(UNICORN_SHADES)]
        unicorn_block = unicorn_line.ljust(unicorn_width)
        unicorn_part = f"{unicorn_shade}{unicorn_block}{Style.RESET_ALL}"
        if book_line:
            book_shade = CYAN_SHADES[(index + 3) % len(CYAN_SHADES)]  # offset = slight gradient shift
            book_part = f"{book_shade}{book_line}{Style.RESET_ALL}"
            art_raw_lines.append(f"{unicorn_block}{gap}{book_line}")
            colored_lines.append(f"{unicorn_part}{gap}{book_part}")
        else:
            art_raw_lines.append(unicorn_block)
            colored_lines.append(unicorn_part)

    raw_lines = title_raw_lines + [""] + art_raw_lines
    display_lines = title_lines + [""] + colored_lines
    inner_width = max(len(line) for line in raw_lines)
    n_frame = len(FRAME_SHADES)

    def frame_bar(line_index: int) -> str:
        """Top/bottom border with per-char gradient (navy → cyan → ice)."""
        c = FRAME_SHADES[line_index % n_frame]
        return f"{c}+{'=' * (inner_width + 2)}+{Style.RESET_ALL}"

    framed_lines: list[str] = [frame_bar(0)]

    for row_i, (raw_line, display_line) in enumerate(zip(raw_lines, display_lines)):
        padding = " " * (inner_width - len(raw_line))
        side = FRAME_SHADES[(row_i + 1) % n_frame]
        framed_lines.append(
            f"{side}|| {Style.RESET_ALL}{display_line}{padding}{side} ||{Style.RESET_ALL}"
        )

    framed_lines.append(frame_bar(len(raw_lines) + 1))
    return "\n".join(framed_lines)


def print_welcome_message() -> None:
    """Print the colored unicorn welcome banner."""
    print(render_welcome_message())
