import sys
import time

from colorama import Style

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

TITLE_ART: tuple[str, ...] = (
    " █████╗ ██████╗ ██████╗ ██████╗ ███████╗███████╗███████╗    ██████╗  ██████╗  ██████╗ ██╗  ██╗",
    "██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝    ██╔══██╗██╔═══██╗██╔═══██╗██║ ██╔╝",
    "███████║██║  ██║██║  ██║██████╔╝█████╗  ███████╗███████╗    ██████╔╝██║   ██║██║   ██║█████╔╝ ",
    "██╔══██║██║  ██║██║  ██║██╔══██╗██╔══╝  ╚════██║╚════██║    ██╔══██╗██║   ██║██║   ██║██╔═██╗ ",
    "██║  ██║██████╔╝██████╔╝██║  ██║███████╗███████║███████║    ██████╔╝╚██████╔╝╚██████╔╝██║  ██╗",
    "╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝    ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝",
)

# Subtitle width matches row 0 so the frame is one tight band (no wide === rail)
_TITLE_W = len(TITLE_ART[0])
_SUB = " Personal Assistant · Purple Unicorns v0.1 "
_SUB_PAD = max(0, (_TITLE_W - len(_SUB)) // 2)
TITLE_ART = TITLE_ART + (
    "─" * _SUB_PAD + _SUB + "─" * (_TITLE_W - _SUB_PAD - len(_SUB)),
)

# Unicorn: trimmed dead columns; book sits 2 spaces away (was 6)
UNICORN_ART_RAW: tuple[str, ...] = (
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⡀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⣀⡴⠊⠀⠀",
    "⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⣠⣴⣿⠟⠀⠀⠀⠀",
    "⠀⠀⠀⠀    ⢀⣀⣀⣠⣤⣤⣤⣄⡀⠀⣴⣿⣿⠁⠀⣠⣶⣿⣿⠟⠁⠀⠀⠀⠀⠀",
    "⠀⠀⠀⠀    ⢈⡉⠛⠛⠿⠿⠋⣁⣴⣾⣿⣿⣿⣀⠘⢿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀",
    "    ⠀⠐⠚⠛⠛⠻⠿⠗⣠⣴⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "    ⠀⠿⠿⢿⡿⢀⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "    ⠀⣶⠖⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣴⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀    ⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⢿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀",
    "⠀    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀",
    "⠀    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠈⠻⠿⠿⠿⢿⣿⣿⣿⣷⡄⠀⠀⠀⠀",
    "⠀    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠈⠿⣿⡿⠟⠁⠀⠀⠀⠀",
    "⠀    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "⠀    ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
)

BOOK_ART: tuple[str, ...] = (
    "                                    ",
    "   ______________   _______________",
    " /|              \\ /              ||\\",
    "||| -- ---------- | ------- ----- |||",
    "||| ------------- | ------------- |||",
    "||| ------- ----- | -- ---------- |||",
    "||| ------------- | ------------- |||",
    "||| --- --------- | ------------- |||",
    "||| ------------- | ------ -----  |||",
    "||| ------- ----  |  --------- -- |||",
    "|||_____________  |  _____________|||",
    "L/////----------\\\\_//----------\\\\\\\\\\|",
)

def _trim_blank_columns(lines: tuple[str, ...]) -> tuple[str, ...]:
    """Drop leading/trailing columns that are only ⠀ or space on every row."""
    if not lines:
        return lines
    w = max(len(s) for s in lines)
    left = 0
    for c in range(w):
        if not all(len(s) <= c or s[c] in ("⠀", " ") for s in lines):
            break
        left += 1
    right = 0
    for c in range(w - 1, -1, -1):
        if not all(len(s) <= c or s[c] in ("⠀", " ") for s in lines):
            break
        right += 1
    end = w - right
    return tuple(s[left:end] for s in lines)


# Fills space right of book — block-art tree (one row per unicorn row)
_SIDEBAR_RAW: tuple[str, ...] = _trim_blank_columns(
    (
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣄⡀⠀⠀⠀⠀",
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣆⠀⠀⢻⡍⢳⡄⠀⠀⠀",
        "⠀⠀⠀⠀⠀⠀  ⠀⢀⠀⢀⣀⠀⢸⢁⣿⡄⠀⠈⢷⣈⣿⠀⠀⠀",
        "⠀⠀⠀⠀⠀⠀⠘⢿⡻⣿⠳⣾⡍⠻⣿⣾⢿⡛⠶⣦⡄⠈⣿⣏",
        "⠀⠀⠀⠀⠀⠀⢀⣈⣛⣿⠀⢹⡿⠶⣼⣿⠀⠙⠶⢬⣷⣿⢸⡏",
        "⠀⠀⠀⢼⡿⣦⠸⣯⡉⠛⠷⣾⡃⠀⠀⢸⣇⠀⠀⠀⠈⣽⡇⢿",
        "⠀⠀⢰⣾⣧⢻⡆⠈⠉⠉⠙⠙⠻⣦⣀⠀⢿⣄⠀⠀⠀⣿⡇⠈",
        "⠀⠀⠘⣧⠈⢿⡃⠀⣀⣤⣤⣀⠀⠀⠙⠳⢶⣿⣦⡀⠀⣿⡇⠀⠀",
        "⠀⢸⡿⢿⡷⠴⢷⡾⠥⠴⠞⠁⠀⠀⠀⠀⠀⠀⠉⠻⣦⣹⣇⠀⠀",
        "⠀⠈⢷⡈⣷⡀⠈⠻⣆⠀⠀⢀⣠⡤⢤⣤⠀⠀⠀⠀⠘⢿⣿⡄⠀",
        "⠀⠀⠀⠙⢿⣀⠀⠀⠙⠿⣦⡛⠛⠛⠛⠁⠀⠀⠀⠀⠀⠈⢿⣧⣴",
        "⠀⠀⠀⠀⠀⠉⠙⠛⠲⠶⠿⠿⣦⣄⣀⣀⣀⣀⣀⠀⠀⠀⢸⣿⠏",
        "            ⠀⠀⠀⠉⠛⠛⠻⠿⠿⠿⣷⣦⣼⣿⡄",
        "                        ⠈⠛⣿⣿⠇",
        "⠀⠀                        ⣼⣿⣠",
    )
)


UNICORN_ART: tuple[str, ...] = _trim_blank_columns(UNICORN_ART_RAW)

UNICORN_BOOK_GAP = 2


def _render_unicorn_3d(line: str, row_i: int, width: int) -> str:
    """Static 3D: darker left → lighter right."""
    text = line.ljust(width)
    n = len(UNICORN_SHADES)
    ink_end = 1
    for c, ch in enumerate(line):
        if ch not in ("⠀", " "):
            ink_end = max(ink_end, c + 1)
    parts: list[str] = []
    for col, ch in enumerate(text):
        if ch in (" ", "\n"):
            parts.append(ch)
            continue
        if ch == "⠀":
            parts.append(ch)
            continue
        t = col / max(ink_end - 1, 1)
        idx = int(t * (n - 1))
        idx = (idx + min(row_i, 4) // 2 - row_i // 4) % n
        idx = max(0, min(n - 1, idx))
        parts.append(f"{UNICORN_SHADES[idx]}{ch}")
    parts.append(Style.RESET_ALL)
    return "".join(parts)


def _gradient_line(
    text: str,
    palette: tuple[str, ...],
    phase: int,
    col_offset: int = 0,
) -> str:
    n = len(palette)
    parts: list[str] = []
    col = col_offset
    for ch in text:
        if ch.isspace() and ch != "\n":
            parts.append(ch)
            col += 1
            continue
        parts.append(f"{palette[(col + phase) % n]}{ch}")
        col += 1
    parts.append(Style.RESET_ALL)
    return "".join(parts)


def render_welcome_message(phase: int = 0) -> str:
    """Tight frame: title + unicorn ‖ book with minimal gap; no dead title rail."""
    unicorn_width = max(len(line) for line in UNICORN_ART)
    gap = " " * UNICORN_BOOK_GAP
    nu, nb = len(UNICORN_ART), len(BOOK_ART)
    top_pad = max((nu - nb) // 2, 0)
    bot_pad = max(nu - nb - top_pad, 0)
    aligned_book = ("",) * top_pad + BOOK_ART + ("",) * bot_pad

    inner_phase = 0
    n_cyan = len(CYAN_SHADES)
    title_raw_lines: list[str] = []
    title_lines: list[str] = []
    for index, line in enumerate(TITLE_ART):
        title_raw_lines.append(line)
        shade = CYAN_SHADES[(index + phase) % n_cyan]
        title_lines.append(f"{shade}{line}{Style.RESET_ALL}")

    art_raw_lines: list[str] = []
    colored_lines: list[str] = []
    for index, unicorn_line in enumerate(UNICORN_ART):
        book_line = aligned_book[index]
        unicorn_block = unicorn_line.ljust(unicorn_width)
        unicorn_part = _render_unicorn_3d(unicorn_line, index, unicorn_width)
        if book_line:
            after = len(unicorn_block) + len(gap)
            book_part = _gradient_line(book_line, CYAN_SHADES, inner_phase, col_offset=after)
            art_raw_lines.append(f"{unicorn_block}{gap}{book_line}")
            colored_lines.append(f"{unicorn_part}{gap}{book_part}")
        else:
            art_raw_lines.append(unicorn_block)
            colored_lines.append(unicorn_part)

    title_w = max(len(line) for line in title_raw_lines)
    art_w = max(len(line) for line in art_raw_lines)
    # Room for sidebar: at least title width, widen if art+sidebar needs it
    sidebar_w = max(len(s) for s in _SIDEBAR_RAW) + 1
    inner_width = max(title_w, art_w + 1 + sidebar_w)

    # Append sidebar to each art row (raw + magenta-tinted display)
    n_mag = len(UNICORN_SHADES)
    for i in range(len(art_raw_lines)):
        base = art_raw_lines[i]
        side = _SIDEBAR_RAW[i % len(_SIDEBAR_RAW)]
        pad = inner_width - len(base) - 1 - len(side)
        if pad < 0:
            side = side[: max(0, inner_width - len(base) - 1)]
            pad = inner_width - len(base) - 1 - len(side)
        filler = " " * max(0, pad)
        art_raw_lines[i] = f"{base}{filler} {side}"
        unicorn_line = UNICORN_ART[i]
        unicorn_block = unicorn_line.ljust(unicorn_width)
        book_line = aligned_book[i]
        if book_line:
            after = len(unicorn_block) + len(gap)
            mid = f"{_render_unicorn_3d(unicorn_line, i, unicorn_width)}{gap}{_gradient_line(book_line, CYAN_SHADES, inner_phase, col_offset=after)}"
        else:
            mid = _render_unicorn_3d(unicorn_line, i, unicorn_width)
        side_colored = "".join(
            f"{UNICORN_SHADES[(j + i) % n_mag]}{c}" if c not in (" ",) else c
            for j, c in enumerate(side)
        )
        colored_lines[i] = f"{mid}{filler} {side_colored}{Style.RESET_ALL}"

    raw_lines = title_raw_lines + art_raw_lines
    display_lines = title_lines + colored_lines
    inner_width = max(len(line) for line in raw_lines)
    n_frame = len(FRAME_SHADES)

    def frame_bar(phase_off: int) -> str:
        segs = [f"{FRAME_SHADES[phase_off % n_frame]}+"]
        for j in range(inner_width + 2):
            segs.append(f"{FRAME_SHADES[(j + phase_off) % n_frame]}=")
        segs.append(f"{FRAME_SHADES[(inner_width + 2 + phase_off) % n_frame]}+{Style.RESET_ALL}")
        return "".join(segs)

    framed_lines: list[str] = [frame_bar(phase)]
    for row_i, (raw_line, display_line) in enumerate(zip(raw_lines, display_lines)):
        padding = " " * (inner_width - len(raw_line))
        left = FRAME_SHADES[(row_i + phase) % n_frame]
        right = FRAME_SHADES[(row_i + 1 + phase) % n_frame]
        framed_lines.append(
            f"{left}||{Style.RESET_ALL}{display_line}{padding}{right}||{Style.RESET_ALL}"
        )
    framed_lines.append(frame_bar(len(raw_lines) + 1 + phase))
    return "\n".join(framed_lines)


def print_welcome_message(
    *,
    animate: bool | None = None,
    duration_sec: float = 3.5,
    fps: float = 2.5,
) -> None:
    tty = sys.stdout.isatty()
    use_anim = animate if animate is not None else tty

    def _finish_banner() -> None:
        sys.stdout.write("\n\n")
        sys.stdout.flush()

    if not use_anim:
        print(render_welcome_message(0))
        print()
        return

    sys.stdout.write("\033[?25l\033[H")
    t0 = time.perf_counter()
    frame = 0
    while True:
        sys.stdout.write("\033[H")
        sys.stdout.write(render_welcome_message(frame))
        sys.stdout.flush()
        if time.perf_counter() - t0 >= duration_sec:
            break
        time.sleep(0.2 / fps)
        frame += 1

    sys.stdout.write("\033[?25h")
    _finish_banner()
