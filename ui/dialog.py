"""Dialog components for user interaction."""

import curses
from typing import Optional, Any

from .utils import (
    get_screen_size,
    center_string,
    truncate_text,
    draw_border,
    show_status,
)
from config.constants import Colors, Symbols


def display_dialog(
    stdscr,
    message: str,
    title: str = "Message",
    message_type: str = "info",
    show_yes_no: bool = False,
) -> Optional[bool]:
    """Display enhanced message dialog and wait for acknowledgment."""
    height, width = get_screen_size(stdscr)
    stdscr.clear()

    lines = message.split("\n")
    max_line_length = max(len(line) for line in lines) if lines else 0
    message_width = min(width - 10, max(max_line_length + 10, 50))
    message_height = len(lines) + 8

    y_start = (height - message_height) // 2
    x_start = (width - message_width) // 2

    type_config = {
        "error": (Colors.ERROR, "X", "Error"),
        "success": (Colors.SUCCESS, "✓", "Success"),
        "warning": (Colors.WARNING, "!", "Warning"),
        "info": (Colors.INFO, "i", "Information"),
        "question": (Colors.INFO, "?", "Question"),
    }
    color_pair, symbol, type_label = type_config.get(
        message_type, (Colors.INFO, "i", "Information")
    )

    # Draw enhanced message box
    display_title = f" {symbol} {title} "
    draw_border(
        stdscr,
        y_start,
        x_start,
        message_height,
        message_width,
        display_title,
        Colors.HEADER,
    )

    try:
        # Type indicator
        type_indicator = center_string(f"--- {type_label} ---", message_width - 4)
        stdscr.addstr(
            y_start + 2,
            x_start + 2,
            type_indicator,
            curses.color_pair(color_pair) | curses.A_BOLD,
        )

        # Separator line
        separator_y = y_start + 3
        stdscr.addstr(
            separator_y,
            x_start + 1,
            Symbols.HORIZONTAL_LINE * (message_width - 2),
            curses.color_pair(Colors.BORDER),
        )

        # Add message lines with better spacing
        for i, line in enumerate(lines):
            line_text = center_string(line, message_width - 4)
            stdscr.addstr(
                y_start + 5 + i,
                x_start + 2,
                line_text,
                curses.color_pair(Colors.TEXT) | curses.A_NORMAL,
            )

        # Enhanced instruction with visual prominence
        if show_yes_no:
            instruction = "[Y]es / [N]o"
        else:
            instruction = "Press any key to continue..."
        instruction_centered = center_string(instruction, message_width - 4)
        stdscr.addstr(
            y_start + message_height - 2,
            x_start + 2,
            instruction_centered,
            curses.color_pair(Colors.TEXT) | curses.A_BOLD,
        )
    except curses.error:
        pass

    stdscr.refresh()

    # Handle user input
    if show_yes_no:
        # Handle yes/no question
        while True:
            key = stdscr.getch()
            if key in (ord("y"), ord("Y")):
                return True
            elif key in (ord("n"), ord("N"), 27):  # N or Escape
                return False
    else:
        # Regular dialog - just wait for any key
        stdscr.getch()
        return None


def prompt_input(
    stdscr, prompt: str, allow_empty: bool = False, input_type=str
) -> Optional[Any]:
    """Enhanced user input dialog with better visual design."""
    height, width = get_screen_size(stdscr)
    stdscr.clear()

    dialog_width = min(width - 10, max(70, len(prompt) + 15))
    dialog_height = 10
    dialog_x = (width - dialog_width) // 2
    dialog_y = (height - dialog_height) // 2

    title = " Input Required "
    draw_border(
        stdscr, dialog_y, dialog_x, dialog_height, dialog_width, title, Colors.HEADER
    )

    try:
        # Enhanced prompt display
        prompt_text = truncate_text(prompt, dialog_width - 4)
        prompt_centered = center_string(prompt_text, dialog_width - 4)
        stdscr.addstr(
            dialog_y + 2,
            dialog_x + 2,
            prompt_centered,
            curses.color_pair(Colors.INFO) | curses.A_BOLD,
        )

        # Separator line
        separator_y = dialog_y + 3
        stdscr.addstr(
            separator_y,
            dialog_x + 1,
            Symbols.HORIZONTAL_LINE * (dialog_width - 2),
            curses.color_pair(Colors.BORDER),
        )

        # Enhanced input field with type indication
        input_y = dialog_y + 5
        input_x = dialog_x + 2
        input_label = f"Value ({input_type.__name__}): "
        stdscr.addstr(
            input_y,
            input_x,
            input_label,
            curses.color_pair(Colors.TEXT) | curses.A_BOLD,
        )

        # Enhanced instructions
        instructions = "[Enter] Confirm • [Ctrl+C] Cancel"
        if allow_empty:
            instructions += " • [Empty] Use Default"
        instructions_centered = center_string(instructions, dialog_width - 4)
        stdscr.addstr(
            dialog_y + 7,
            dialog_x + 2,
            instructions_centered,
            curses.color_pair(Colors.TEXT) | curses.A_BOLD,
        )
    except curses.error:
        pass

    stdscr.refresh()

    # Get input with better UX
    curses.echo()
    curses.curs_set(1)
    try:
        user_input = (
            stdscr.getstr(input_y, input_x + len(input_label), 40)
            .decode("utf-8")
            .strip()
        )
    except KeyboardInterrupt:
        return None
    finally:
        curses.noecho()
        curses.curs_set(0)

    if not allow_empty and not user_input:
        return None

    # Handle type conversion with better error handling
    if user_input and input_type != str:
        try:
            return input_type(user_input)
        except (ValueError, TypeError):
            # Show error message
            display_dialog(
                stdscr,
                f"Invalid {input_type.__name__} value: '{user_input}'\nPlease enter a valid {input_type.__name__}.",
                "Input Error",
                "error",
            )
            return prompt_input(stdscr, prompt, allow_empty, input_type)

    return user_input if user_input or allow_empty else None


def process_keys(
    stdscr, prompt: str, input_type=str, allow_empty: bool = False
) -> Optional[Any]:
    """Enhanced input handler with type validation."""
    height, width = get_screen_size(stdscr)

    while True:
        stdscr.clear()

        dialog_width = min(width - 10, max(60, len(prompt) + 10))
        dialog_height = 8
        dialog_x = (width - dialog_width) // 2
        dialog_y = (height - dialog_height) // 2

        title = " Input Required "
        draw_border(
            stdscr,
            dialog_y,
            dialog_x,
            dialog_height,
            dialog_width,
            title,
            Colors.BORDER,
        )

        try:
            # Add prompt
            prompt_text = truncate_text(prompt, dialog_width - 4)
            prompt_centered = center_string(prompt_text, dialog_width - 4)
            stdscr.addstr(
                dialog_y + 2,
                dialog_x + 2,
                prompt_centered,
                curses.color_pair(Colors.HEADER) | curses.A_BOLD,
            )

            # Input field
            input_y = dialog_y + 4
            input_x = dialog_x + 2
            input_label = f"Value ({input_type.__name__}): "
            stdscr.addstr(input_y, input_x, input_label, curses.color_pair(Colors.TEXT))

            # Instructions
            instructions = "Enter to confirm • Ctrl+C to cancel"
            if allow_empty:
                instructions += " • Leave empty for default"
            instructions_centered = center_string(instructions, dialog_width - 4)
            stdscr.addstr(
                dialog_y + 6,
                dialog_x + 2,
                instructions_centered,
                curses.color_pair(Colors.INFO) | curses.A_DIM,
            )
        except curses.error:
            pass

        stdscr.refresh()

        # Get input
        curses.echo()
        curses.curs_set(1)
        try:
            user_input = (
                stdscr.getstr(input_y, input_x + len(input_label), 20)
                .decode("utf-8")
                .strip()
            )
        except KeyboardInterrupt:
            return None
        finally:
            curses.noecho()
            curses.curs_set(0)

        if not allow_empty and not user_input:
            show_status(stdscr, "Input cannot be empty!", "error")
            stdscr.refresh()
            stdscr.getch()
            continue

        if allow_empty and not user_input:
            return input_type()

        try:
            return input_type(user_input)
        except ValueError:
            show_status(
                stdscr,
                f"Invalid {input_type.__name__} value! Please try again.",
                "error",
            )
            stdscr.refresh()
            stdscr.getch()
