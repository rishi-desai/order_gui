"""
Menu component for navigation and selection.
"""

import curses
from typing import List, Optional, Union

from .utils import (
    get_screen_size,
    center_string,
    truncate_text,
    draw_border,
    show_status,
)
from config.constants import Colors, Symbols


def display_menu(
    stdscr,
    options: List[str],
    title: str = "Menu",
    instructions: str = "Use UP/DOWN to navigate, ENTER to select, 'q' to quit",
    allow_multiple: bool = False,
) -> Optional[Union[int, List[int]]]:
    """Enhanced menu rendering with better visual design."""
    curses.curs_set(0)
    current_row = 0
    selected = set() if allow_multiple else None
    height, width = get_screen_size(stdscr)

    while True:
        stdscr.clear()

        # Calculate box dimensions
        extra_width = 6 if allow_multiple else 0
        box_width = min(
            width - 4,
            max(60, max(len(option) for option in options) + 10 + extra_width),
        )
        box_height = min(height - 4, len(options) + 8)
        box_x = (width - box_width) // 2
        box_y = (height - box_height) // 2

        # Draw main box
        draw_border(stdscr, box_y, box_x, box_height, box_width, title, Colors.BORDER)

        # Draw menu options
        option_start_y = box_y + 3
        for idx, option in enumerate(options):
            y_pos = option_start_y + idx
            if y_pos >= box_y + box_height - 3:
                break

            # Prepare option text
            if allow_multiple:
                checkbox = Symbols.BOX_CHECKED if idx in selected else Symbols.BOX_EMPTY
                option_text = f"{checkbox} {option}"
            else:
                option_text = f"{option}"

            # Truncate if too long
            max_option_width = box_width - 8
            option_text = truncate_text(option_text, max_option_width)

            # Draw option
            if idx == current_row:
                arrow = f"{Symbols.ARROW_RIGHT} "
                full_text = arrow + option_text
                try:
                    stdscr.addstr(
                        y_pos,
                        box_x + 2,
                        full_text,
                        curses.color_pair(Colors.SELECTED) | curses.A_BOLD,
                    )
                except curses.error:
                    pass
            else:
                try:
                    stdscr.addstr(
                        y_pos, box_x + 4, option_text, curses.color_pair(Colors.TEXT)
                    )
                except curses.error:
                    pass

        # Draw instructions
        instructions_y = box_y + box_height - 2
        if allow_multiple:
            instructions_text = center_string(
                f"{Symbols.KEY} Space to toggle • Enter to finish • Q to quit",
                box_width - 4,
            )
        else:
            instructions_text = center_string(instructions, box_width - 4)
        try:
            stdscr.addstr(
                instructions_y,
                box_x + 2,
                instructions_text,
                curses.color_pair(Colors.INFO),
            )
        except curses.error:
            pass

        # Status bar
        if allow_multiple:
            show_status(
                stdscr, f"Selected: {len(selected)} items • Use Space to toggle", "info"
            )
        else:
            show_status(stdscr, "Navigate with arrow keys, Enter to select", "info")

        stdscr.refresh()

        key = stdscr.getch()

        # Handle navigation
        if key in (curses.KEY_UP, ord("k")) and current_row > 0:
            current_row -= 1
        elif key in (curses.KEY_DOWN, ord("j")) and current_row < len(options) - 1:
            current_row += 1
        elif key == 32:  # Space for toggling in multi-select
            if allow_multiple:
                if current_row in selected:
                    selected.remove(current_row)
                else:
                    selected.add(current_row)
        elif key in (curses.KEY_ENTER, 10, 13, ord("l")):  # Enter
            if allow_multiple:
                return list(selected)
            else:
                return current_row
        elif key >= ord("1") and key <= ord("9"):  # Number keys
            num = key - ord("1")
            if num < len(options):
                if allow_multiple:
                    if num in selected:
                        selected.remove(num)
                    else:
                        selected.add(num)
                else:
                    return num
        elif key == ord("r") or key == ord("R"):  # Refresh
            return -2
        elif key == ord("b") or key == ord("B"):  # Back
            return -3
        elif key == ord("q") or key == ord("Q"):
            return list(selected) if allow_multiple else None
