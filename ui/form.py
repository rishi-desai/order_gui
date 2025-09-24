"""
Form component for field editing.
"""

import curses
import time
from typing import List, Dict, Any, Optional

from .utils import (
    get_screen_size,
    center_string,
    truncate_text,
    draw_border,
    show_status,
)
from config.constants import Colors, Symbols


def edit_form(
    stdscr, fields: List[str], values: Dict[str, Any], title: str = "Edit Fields"
) -> Optional[Dict[str, Any]]:
    """Enhanced field editing with better visual design."""
    current_row = 0
    height, width = get_screen_size(stdscr)

    while True:
        stdscr.clear()

        # Calculate box dimensions
        max_field_len = max(len(field) for field in fields) if fields else 20
        max_value_len = (
            max(len(str(values.get(field, ""))) for field in fields) if fields else 20
        )
        box_width = min(width - 4, max(60, max_field_len + max_value_len + 15))
        box_height = min(height - 4, len(fields) + 10)
        box_x = (width - box_width) // 2
        box_y = (height - box_height) // 2

        # Draw main box
        draw_border(stdscr, box_y, box_x, box_height, box_width, title, Colors.BORDER)

        # Draw fields
        field_start_y = box_y + 2
        for idx, field in enumerate(fields):
            y_pos = field_start_y + idx + 1
            if y_pos >= box_y + box_height - 4:
                break

            value = str(values.get(field, ""))
            field_display = f"{idx + 1:2d}. {field}:"
            max_field_display_width = box_width // 2
            field_display = truncate_text(field_display, max_field_display_width)

            max_value_width = box_width - len(field_display) - 6
            value_display = truncate_text(value, max_value_width) if value else "─"

            if idx == current_row:
                # Highlighted field
                arrow = f"{Symbols.ARROW_RIGHT} "
                try:
                    stdscr.addstr(
                        y_pos,
                        box_x + 2,
                        arrow,
                        curses.color_pair(Colors.SELECTED) | curses.A_BOLD,
                    )
                    stdscr.addstr(
                        y_pos,
                        box_x + 4,
                        field_display,
                        curses.color_pair(Colors.SELECTED) | curses.A_BOLD,
                    )
                    stdscr.addstr(
                        y_pos,
                        box_x + 4 + len(field_display) + 1,
                        value_display,
                        curses.color_pair(Colors.SELECTED) | curses.A_BOLD,
                    )
                except curses.error:
                    pass
            else:
                # Normal field
                try:
                    stdscr.addstr(
                        y_pos, box_x + 4, field_display, curses.color_pair(Colors.TEXT)
                    )
                    stdscr.addstr(
                        y_pos,
                        box_x + 4 + len(field_display) + 1,
                        value_display,
                        curses.color_pair(Colors.INFO),
                    )
                except curses.error:
                    pass

        # Draw action buttons
        action_y = box_y + box_height - 3
        actions = f"[S]ave/Send  •  [B]ack  •  [Enter] Edit Field"
        actions_centered = center_string(actions, box_width - 4)
        try:
            stdscr.addstr(
                action_y,
                box_x + 2,
                actions_centered,
                curses.color_pair(Colors.WARNING) | curses.A_BOLD,
            )
        except curses.error:
            pass

        # Status bar
        show_status(stdscr, f"Editing field: {fields[current_row]}", "info")
        stdscr.refresh()

        key = stdscr.getch()

        if key in (curses.KEY_UP, ord("k")) and current_row > 0:
            current_row -= 1
        elif key in (curses.KEY_DOWN, ord("j")) and current_row < len(fields) - 1:
            current_row += 1
        elif key == ord("s") or key == ord("S"):
            show_status(stdscr, "Saving configuration...", "success")
            stdscr.refresh()
            time.sleep(0.5)
            return values
        elif key in (ord("b"), ord("B"), ord("h")):
            return None
        elif key in (curses.KEY_ENTER, 10, 13, ord("l")):  # Enter
            field_name = fields[current_row]
            current_value = str(values.get(field_name, ""))

            # Show input prompt
            show_status(stdscr, f"Editing {field_name} - Enter new value:", "info")
            stdscr.refresh()

            # Enable input
            curses.curs_set(1)
            curses.echo()

            try:
                prompt_y = box_y + box_height - 2
                prompt_x = box_x + 2

                # Clear input area
                stdscr.addstr(
                    prompt_y,
                    prompt_x,
                    " " * (box_width - 4),
                    curses.color_pair(Colors.TEXT),
                )
                stdscr.addstr(
                    prompt_y,
                    prompt_x,
                    f"{field_name}: ",
                    curses.color_pair(Colors.TEXT),
                )
                stdscr.addstr(
                    prompt_y,
                    prompt_x + len(field_name) + 2,
                    current_value,
                    curses.A_REVERSE,
                )
                stdscr.move(
                    prompt_y, prompt_x + len(field_name) + 2 + len(current_value)
                )
                stdscr.refresh()

                # Get user input
                new_value = (
                    stdscr.getstr(prompt_y, prompt_x + len(field_name) + 2, 40)
                    .decode("utf-8")
                    .strip()
                )

                if new_value or new_value == "":  # Allow empty values
                    values[field_name] = new_value
                    show_status(stdscr, f"Updated {field_name}", "success")
                    stdscr.refresh()
                    time.sleep(0.3)

            except KeyboardInterrupt:
                show_status(stdscr, "Edit cancelled", "warning")
                stdscr.refresh()
                time.sleep(0.3)
            finally:
                curses.noecho()
                curses.curs_set(0)
