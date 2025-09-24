"""
Basic UI utilities and helpers for curses interface.
"""

import curses
from typing import Tuple

from config.constants import Colors, Symbols


def setup_colors() -> None:
    """Initialize curses color pairs."""
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(Colors.HEADER, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(Colors.TEXT, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(Colors.SELECTED, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(Colors.SUCCESS, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(Colors.ERROR, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(Colors.WARNING, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(Colors.INFO, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(Colors.BORDER, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(Colors.INPUT_BG, curses.COLOR_BLACK, curses.COLOR_WHITE)


def write_text(stdscr, y: int, x: int, text: str, attr: int = 0) -> None:
    """Safely add string to screen with encoding fallbacks."""
    try:
        stdscr.addstr(y, x, text, attr)
    except (UnicodeEncodeError, curses.error):
        try:
            stdscr.addstr(y, x, text.encode("latin1", "replace").decode("latin1"), attr)
        except (UnicodeEncodeError, curses.error):
            try:
                safe_text = text.encode("ascii", "replace").decode("ascii")
                stdscr.addstr(y, x, safe_text, attr)
            except curses.error:
                pass  # Skip if all else fails


def get_screen_size(stdscr) -> Tuple[int, int]:
    """Get terminal dimensions with safe fallbacks."""
    try:
        height, width = stdscr.getmaxyx()
        return max(height, 10), max(width, 40)
    except:
        return 24, 80


def center_string(text: str, width: int) -> str:
    """Center text within a given width."""
    if len(text) >= width:
        return text[:width]
    padding = (width - len(text)) // 2
    return " " * padding + text + " " * (width - len(text) - padding)


def truncate_text(text: str, max_width: int, suffix: str = "...") -> str:
    """Truncate text to fit within max_width."""
    if len(text) <= max_width:
        return text
    return text[: max_width - len(suffix)] + suffix


def draw_border(
    stdscr,
    y: int,
    x: int,
    height: int,
    width: int,
    title: str = "",
    color_pair: int = 0,
) -> None:
    """Draw a box with optional title using ASCII characters."""
    # Draw borders
    stdscr.addstr(y, x, Symbols.TOP_LEFT, curses.color_pair(color_pair))
    stdscr.addstr(
        y, x + 1, Symbols.HORIZONTAL_LINE * (width - 2), curses.color_pair(color_pair)
    )
    stdscr.addstr(y, x + width - 1, Symbols.TOP_RIGHT, curses.color_pair(color_pair))

    for i in range(1, height - 1):
        stdscr.addstr(y + i, x, Symbols.VERTICAL_LINE, curses.color_pair(color_pair))
        stdscr.addstr(
            y + i, x + width - 1, Symbols.VERTICAL_LINE, curses.color_pair(color_pair)
        )

    stdscr.addstr(y + height - 1, x, Symbols.BOTTOM_LEFT, curses.color_pair(color_pair))
    stdscr.addstr(
        y + height - 1,
        x + 1,
        Symbols.HORIZONTAL_LINE * (width - 2),
        curses.color_pair(color_pair),
    )
    stdscr.addstr(
        y + height - 1,
        x + width - 1,
        Symbols.BOTTOM_RIGHT,
        curses.color_pair(color_pair),
    )

    # Add title if provided
    if title:
        title_text = f" {title} "
        if len(title_text) < width - 2:
            title_x = x + (width - len(title_text)) // 2
            stdscr.addstr(
                y, title_x, title_text, curses.color_pair(Colors.HEADER) | curses.A_BOLD
            )


def show_status(stdscr, message: str, status_type: str = "info") -> None:
    """Create status bar at bottom of screen."""
    height, width = get_screen_size(stdscr)
    stdscr.move(height - 1, 0)
    stdscr.clrtoeol()

    color_map = {
        "info": Colors.INFO,
        "success": Colors.SUCCESS,
        "error": Colors.ERROR,
        "warning": Colors.WARNING,
    }
    color = color_map.get(status_type, Colors.INFO)

    icon_map = {
        "info": Symbols.BULLET,
        "success": Symbols.CHECK,
        "error": Symbols.CROSS,
        "warning": Symbols.WARNING,
    }
    icon = icon_map.get(status_type, Symbols.BULLET)

    status_text = f" {icon} {message}"
    if len(status_text) > width:
        status_text = truncate_text(status_text, width)

    try:
        stdscr.addstr(
            height - 1, 0, status_text, curses.color_pair(color) | curses.A_BOLD
        )
    except curses.error:
        pass
