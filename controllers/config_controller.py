"""
Configuration controller for managing application settings.
"""

import curses
import os
from typing import Dict, Any

from models.config import Config
from ui.utils import get_screen_size, draw_border, write_text
from ui.dialog import display_dialog
from config.constants import Colors, Symbols


class ConfigController:
    """Controller for configuration management."""

    def configure_osr_id(
        self, stdscr, config: Dict[str, Any], config_manager: Config
    ) -> None:
        """Configure the OSR ID for the application."""
        height, width = get_screen_size(stdscr)
        stdscr.clear()

        # Get current OSR ID from config or environment
        current_osrid = config.get("osr_id", os.environ.get("OSR_ID", ""))

        # Create dialog for OSR ID configuration
        dialog_width = min(width - 8, 70)
        dialog_height = 10
        dialog_x = (width - dialog_width) // 2
        dialog_y = (height - dialog_height) // 2

        # Draw dialog box with title
        draw_border(
            stdscr,
            dialog_y,
            dialog_x,
            dialog_height,
            dialog_width,
            f" {Symbols.SETTINGS} Configure OSR ID ",
            Colors.BORDER,
        )

        try:
            # Show current OSR ID
            current_label = f"{Symbols.INFO} Current OSR ID:"
            write_text(
                stdscr,
                dialog_y + 2,
                dialog_x + 2,
                current_label,
                curses.color_pair(Colors.HEADER) | curses.A_BOLD,
            )

            # Display current value
            if current_osrid:
                current_value = current_osrid
                value_color = Colors.SUCCESS
            else:
                env_osrid = os.environ.get("OSR_ID", "")
                if env_osrid:
                    current_value = f"(environment: {env_osrid})"
                    value_color = Colors.INFO
                else:
                    current_value = "(not configured)"
                    value_color = Colors.WARNING

            write_text(
                stdscr,
                dialog_y + 3,
                dialog_x + 4,
                current_value,
                curses.color_pair(value_color),
            )

            # Input prompt
            input_label = f"{Symbols.EDIT} Enter new OSR ID:"
            write_text(
                stdscr,
                dialog_y + 5,
                dialog_x + 2,
                input_label,
                curses.color_pair(Colors.TEXT),
            )

            # Instructions
            instructions = f"{Symbols.KEY} [ENTER] to save • [Ctrl+C] to cancel • Leave empty for environment"
            write_text(
                stdscr,
                dialog_y + 7,
                dialog_x + 2,
                instructions[: dialog_width - 4],  # Truncate if too long
                curses.color_pair(Colors.INFO) | curses.A_DIM,
            )

            # Input field background
            input_y = dialog_y + 6
            input_x = dialog_x + 4
            input_width = dialog_width - 8
            write_text(
                stdscr,
                input_y,
                input_x,
                " " * input_width,
                curses.color_pair(Colors.INPUT_BG),
            )

        except curses.error:
            pass

        stdscr.refresh()

        # Get user input with proper input handling
        curses.echo()
        curses.curs_set(1)

        try:
            # Position cursor and get input
            stdscr.move(input_y, input_x)
            new_osrid = (
                stdscr.getstr(input_y, input_x, input_width - 1).decode("utf-8").strip()
            )

            # Process the input
            if new_osrid:
                # Set new OSR ID in config
                config["osr_id"] = new_osrid
                success_msg = f"{Symbols.SUCCESS} OSR ID updated to: {new_osrid}"
                msg_type = "success"
            else:
                # Remove from config to use environment variable
                config.pop("osr_id", None)
                env_osrid = os.environ.get("OSR_ID", "")
                if env_osrid:
                    success_msg = f"{Symbols.SUCCESS} OSR ID cleared - now using environment: {env_osrid}"
                    msg_type = "success"
                else:
                    success_msg = f"{Symbols.WARNING} OSR ID cleared - environment variable OSR_ID not set!"
                    msg_type = "warning"

            config_manager.save(config)
            display_dialog(stdscr, success_msg, "Configuration", msg_type)

        except KeyboardInterrupt:
            # User cancelled with Ctrl+C
            pass
        finally:
            curses.noecho()
            curses.curs_set(0)
