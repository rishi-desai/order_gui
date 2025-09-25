"""
Menu component for navigation and selection.
"""

import curses
from typing import List, Optional, Union, Dict

from .utils import (
    get_screen_size,
    center_string,
    truncate_text,
    draw_border,
    show_status,
)
from config.constants import Colors, Symbols


def display_sectioned_menu(
    stdscr,
    sections: Dict[str, List[str]],
    title: str = "Menu",
    status_info: str = "",
    instructions: str = None,
) -> Optional[int]:
    """
    Display a menu with sections for better organization.

    Args:
        stdscr: curses screen object
        sections: Dict with section names as keys and option lists as values
        title: Menu title
        status_info: Additional status information to display
        instructions: Custom instructions text

    Returns:
        Index of selected option (global index across all sections) or None
    """
    curses.curs_set(0)
    current_row = 0

    # Flatten options and create section mapping
    all_options = []
    section_starts = {}
    current_index = 0

    for section_name, options in sections.items():
        section_starts[section_name] = current_index
        all_options.extend(options)
        current_index += len(options)

    total_options = len(all_options)
    height, width = get_screen_size(stdscr)

    while True:
        stdscr.clear()

        # Enhanced layout calculation
        max_option_len = max(len(opt) for opt in all_options) if all_options else 30
        max_section_len = (
            max(len(section) for section in sections.keys()) if sections else 20
        )

        box_width = min(width - 6, max(80, max_option_len + 20, max_section_len + 15))
        sections_height = sum(
            len(opts) + 2 for opts in sections.values()
        )  # +2 for header and spacing
        box_height = min(height - 4, sections_height + 8)
        box_x = (width - box_width) // 2
        box_y = (height - box_height) // 2

        # Draw main container with enhanced styling
        draw_border(stdscr, box_y, box_x, box_height, box_width, title, Colors.HEADER)

        # Display status info in header area
        if status_info:
            status_y = box_y + 1
            status_text = center_string(status_info, box_width - 4)
            try:
                stdscr.addstr(
                    status_y,
                    box_x + 2,
                    status_text,
                    curses.color_pair(Colors.INFO) | curses.A_BOLD,
                )
            except curses.error:
                pass

        # Draw sections with enhanced styling
        current_y = box_y + 3 + (1 if status_info else 0)
        option_index = 0

        for section_name, options in sections.items():
            # Section header with your requested format
            if current_y >= box_y + box_height - 3:
                break

            # Create the header in format: ╭─ Section Name -------------------------╮
            header_text = f" {section_name} "
            # Account for the border symbols and spacing: TOP_LEFT + " " + TOP_RIGHT + padding
            available_width = (
                box_width - 4 - len(header_text) - 2
            )  # -2 for the TOP_LEFT and TOP_RIGHT symbols
            padding_dashes = max(0, available_width)
            section_header = f"{Symbols.TOP_LEFT}{Symbols.HORIZONTAL_LINE} {section_name} {Symbols.HORIZONTAL_LINE * padding_dashes}{Symbols.TOP_RIGHT}"

            try:
                stdscr.addstr(
                    current_y,
                    box_x + 2,
                    section_header,
                    curses.color_pair(Colors.SECTION_HEADER) | curses.A_BOLD,
                )
            except curses.error:
                pass
            current_y += 1

            # Section options with enhanced visual design
            for i, option in enumerate(options):
                if current_y >= box_y + box_height - 3:
                    break

                # Prepare option text with numbering (0-9)
                option_num = option_index % 10
                if option_index == current_row:
                    # Enhanced selection display
                    display_text = f"  {Symbols.ARROW_RIGHT} [{option_num}] {option}"
                    try:
                        stdscr.addstr(
                            current_y,
                            box_x + 2,
                            display_text,
                            curses.color_pair(Colors.SELECTED) | curses.A_BOLD,
                        )
                    except curses.error:
                        pass
                else:
                    display_text = f"     [{option_num}] {option}"
                    try:
                        # Show number in different color for better visibility
                        stdscr.addstr(
                            current_y,
                            box_x + 2,
                            f"     [{option_num}]",
                            curses.color_pair(Colors.SUCCESS),
                        )
                        stdscr.addstr(
                            current_y,
                            box_x + 2 + len(f"     [{option_num}]"),
                            f" {option}",
                            curses.color_pair(Colors.TEXT),
                        )
                    except curses.error:
                        pass

                current_y += 1
                option_index += 1

            # Add spacing after section
            current_y += 1

        # Enhanced instructions with custom support
        instructions_y = box_y + box_height - 2
        if instructions:
            instructions_text = center_string(instructions, box_width - 4)
        else:
            instructions_text = center_string(
                f"{Symbols.ARROW_UP}/{Symbols.ARROW_DOWN} Navigate • [0-9] Quick Select • [Enter] Choose • [Q] Quit",
                box_width - 4,
            )
        try:
            stdscr.addstr(
                instructions_y,
                box_x + 2,
                instructions_text,
                curses.color_pair(Colors.TEXT) | curses.A_BOLD,
            )
        except curses.error:
            pass

        stdscr.refresh()
        key = stdscr.getch()

        # Navigation
        if key in (curses.KEY_UP, ord("k")) and current_row > 0:
            current_row -= 1
        elif key in (curses.KEY_DOWN, ord("j")) and current_row < total_options - 1:
            current_row += 1
        elif key in (curses.KEY_ENTER, 10, 13):
            return current_row
        elif key >= ord("0") and key <= ord("9"):
            num = key - ord("0")
            if num < total_options:
                return num
        elif key in (ord("q"), ord("Q")):
            return None

    return None


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

        # Calculate enhanced box dimensions
        extra_width = 6 if allow_multiple else 0
        max_option_len = max(len(option) for option in options) if options else 20
        box_width = min(
            width - 6,
            max(70, max_option_len + 15 + extra_width),
        )
        box_height = min(height - 4, len(options) + 8)
        box_x = (width - box_width) // 2
        box_y = (height - box_height) // 2

        # Draw main box with enhanced styling
        draw_border(stdscr, box_y, box_x, box_height, box_width, title, Colors.HEADER)

        # Draw menu options with enhanced design
        option_start_y = box_y + 3
        for idx, option in enumerate(options):
            y_pos = option_start_y + idx
            if y_pos >= box_y + box_height - 3:
                break

            # Prepare option text with enhanced styling
            option_num = idx % 10  # Support 0-9 numbering
            if allow_multiple:
                checkbox = Symbols.BOX_CHECKED if idx in selected else Symbols.BOX_EMPTY
                option_text = f"{checkbox} {option}"
            else:
                option_text = f"{option}"

            # Truncate if too long
            max_option_width = box_width - 12
            option_text = truncate_text(option_text, max_option_width)

            # Draw option with better visual hierarchy
            if idx == current_row:
                # Enhanced selection display
                if allow_multiple:
                    display_text = (
                        f"  {Symbols.ARROW_RIGHT} [{option_num}] {option_text}"
                    )
                else:
                    display_text = (
                        f"  {Symbols.ARROW_RIGHT} [{option_num}] {option_text}"
                    )
                try:
                    stdscr.addstr(
                        y_pos,
                        box_x + 2,
                        display_text,
                        curses.color_pair(Colors.SELECTED) | curses.A_BOLD,
                    )
                except curses.error:
                    pass
            else:
                # Non-selected option with number highlighting
                try:
                    if allow_multiple:
                        display_text = f"     [{option_num}] {option_text}"
                    else:
                        display_text = f"     [{option_num}] {option_text}"
                    # Show number in different color
                    stdscr.addstr(
                        y_pos,
                        box_x + 2,
                        f"     [{option_num}]",
                        curses.color_pair(Colors.SUCCESS),
                    )
                    stdscr.addstr(
                        y_pos,
                        box_x + 2 + len(f"     [{option_num}]"),
                        f" {option_text}",
                        curses.color_pair(Colors.TEXT),
                    )
                except curses.error:
                    pass

        # Draw enhanced instructions
        instructions_y = box_y + box_height - 2
        if allow_multiple:
            instructions_text = center_string(
                f"[Space] Toggle • [0-9] Quick Select • [Enter] Finish • [Q] Quit",
                box_width - 4,
            )
        else:
            instructions_text = center_string(
                f"{Symbols.ARROW_UP}/{Symbols.ARROW_DOWN} Navigate • [0-9] Quick Select • [Enter] Choose • [Q] Quit",
                box_width - 4,
            )
        try:
            stdscr.addstr(
                instructions_y,
                box_x + 2,
                instructions_text,
                curses.color_pair(Colors.TEXT) | curses.A_BOLD,
            )
        except curses.error:
            pass

        # Enhanced status bar
        if allow_multiple:
            show_status(
                stdscr,
                f"Selected: {len(selected)} items • Use Space to toggle selection",
                "info",
            )
        else:
            show_status(
                stdscr,
                "Navigate with arrow keys or number keys, Enter to select",
                "info",
            )

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
        elif key >= ord("0") and key <= ord("9"):  # Number keys 0-9
            num = key - ord("0")
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
