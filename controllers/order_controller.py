"""
Order-specific controller for handling order creation and editing.
"""

import curses
import time
from typing import List, Dict, Optional

from config.constants import Colors, Symbols
from config.defaults import DEFAULT_ORDER_VALUES, FIELD_ORDER
from ui.utils import (
    get_screen_size,
    draw_border,
    show_status,
    truncate_text,
    center_string,
)
from ui.form import edit_form


class OrderController:
    """Controller for order creation and editing operations."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def edit_pick_lines(
        self, stdscr, mode: str, lines: List[Dict], values: List[Dict]
    ) -> bool:
        """Edit the picking lines for an order with enhanced UI."""
        idx = 0
        height, width = get_screen_size(stdscr)

        while True:
            stdscr.clear()

            # Calculate box dimensions
            max_line_len = (
                max(
                    len(
                        f"{line.get('Product Name', '')} ({line.get('Product Code', '')}), Qty: {line.get('Quantity', '')}"
                    )
                    for line in lines
                )
                if lines
                else 40
            )
            box_width = min(width - 4, max(70, max_line_len + 10))
            box_height = min(height - 4, len(lines) + 10)
            box_x = (width - box_width) // 2
            box_y = (height - box_height) // 2

            # Draw main box
            title = f" {Symbols.EDIT} Editing {mode} Lines "
            draw_border(
                stdscr, box_y, box_x, box_height, box_width, title, Colors.BORDER
            )

            try:
                # Instructions header
                instructions = f"{Symbols.ARROW_UP}/{Symbols.ARROW_DOWN} Navigate • [A]dd • [D]elete • [Enter] Edit • [S]ave • [B]ack"
                instructions_truncated = truncate_text(instructions, box_width - 4)
                instructions_centered = center_string(
                    instructions_truncated, box_width - 4
                )
                stdscr.addstr(
                    box_y + 2,
                    box_x + 2,
                    instructions_centered,
                    curses.color_pair(Colors.INFO) | curses.A_DIM,
                )

                # Separator line
                separator_y = box_y + 3
                stdscr.addstr(
                    separator_y,
                    box_x + 1,
                    Symbols.HORIZONTAL_LINE * (box_width - 2),
                    curses.color_pair(Colors.BORDER),
                )

                # Display lines
                lines_start_y = box_y + 5
                for i, line in enumerate(lines):
                    if lines_start_y + i >= box_y + box_height - 3:
                        break  # Don't overflow

                    line_str = "{} ({}), Qty: {}".format(
                        line.get("Product Name", "N/A"),
                        line.get("Product Code", "N/A"),
                        line.get("Quantity", "N/A"),
                    )
                    line_str = truncate_text(line_str, box_width - 8)

                    if i == idx:
                        # Highlighted line
                        arrow_text = f"{Symbols.ARROW_RIGHT} {line_str}"
                        stdscr.addstr(
                            lines_start_y + i,
                            box_x + 2,
                            arrow_text,
                            curses.color_pair(Colors.SELECTED) | curses.A_BOLD,
                        )
                    else:
                        # Normal line
                        stdscr.addstr(
                            lines_start_y + i,
                            box_x + 4,
                            line_str,
                            curses.color_pair(Colors.TEXT),
                        )

                # Status info
                status_y = box_y + box_height - 2
                status_text = (
                    f"Line {idx + 1} of {len(lines)} • {len(lines)} total lines"
                )
                status_centered = center_string(status_text, box_width - 4)
                stdscr.addstr(
                    status_y, box_x + 2, status_centered, curses.color_pair(Colors.INFO)
                )

            except curses.error:
                pass

            # Create status bar
            show_status(stdscr, f"Editing {mode} • Use arrow keys to navigate", "info")

            stdscr.refresh()

            key = stdscr.getch()
            if key in (curses.KEY_UP, ord("k")) and idx > 0:
                idx -= 1
            elif key in (curses.KEY_DOWN, ord("j")) and idx < len(lines) - 1:
                idx += 1
            elif key == ord("a") or key == ord("A"):
                # Add new line (copy last or default)
                new_line = (
                    lines[-1].copy() if lines else DEFAULT_ORDER_VALUES[mode][0].copy()
                )
                lines.append(new_line)
                idx = len(lines) - 1
                show_status(stdscr, "New line added", "success")
                stdscr.refresh()
                time.sleep(0.3)
            elif key == ord("d") or key == ord("D"):
                if len(lines) > 1:
                    del lines[idx]
                    idx = max(0, idx - 1)
                    show_status(stdscr, "Line deleted", "warning")
                    stdscr.refresh()
                    time.sleep(0.3)
                else:
                    show_status(stdscr, "Cannot delete the last line", "error")
                    stdscr.refresh()
                    time.sleep(0.5)
            elif key in (curses.KEY_ENTER, 10, 13, ord("l")):  # Enter
                result = self._edit_single_line(stdscr, lines[idx], mode)
                if result is True:
                    return True
            elif key == ord("s") or key == ord("S"):
                return True  # Save/send
            elif key in (ord("h"), ord("b"), ord("B")):
                return False  # Back

    def _edit_single_line(
        self, stdscr, line: Dict, mode: Optional[str] = None
    ) -> Optional[bool]:
        """Edit a single line in the picking order."""
        fields = [f for f in FIELD_ORDER.get(mode, []) if f in line]
        fields += [f for f in line if f not in fields]  # fallback for any extra fields

        # Use the generalized field navigation and editing function
        updated_values = edit_form(stdscr, fields, line, title=f"Edit {mode} Line")
        if updated_values is not None:
            line.update(updated_values)  # Update only the changed fields
            return None  # Continue editing
        return None
