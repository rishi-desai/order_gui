"""Configuration controller for managing application settings."""

import curses
import os
import time
from typing import Dict, Any

from models.config import Config
from ui.utils import get_screen_size, draw_border, write_text, show_status
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

        current_osrid = config.get("osr_id", os.environ.get("OSR_ID", ""))

        dialog_width = min(width - 8, 80)
        dialog_height = 12
        dialog_x = (width - dialog_width) // 2
        dialog_y = (height - dialog_height) // 2

        draw_border(
            stdscr,
            dialog_y,
            dialog_x,
            dialog_height,
            dialog_width,
            " Configure OSR ID ",
            Colors.BORDER,
        )

        try:
            info_text = "Current OSR ID: {}".format(current_osrid or "Not Set")
            write_text(
                stdscr,
                dialog_y + 2,
                dialog_x + 2,
                info_text,
                curses.color_pair(Colors.HEADER) | curses.A_BOLD,
            )

            # Separator line for visual separation
            separator_y = dialog_y + 3
            stdscr.addstr(
                separator_y,
                dialog_x + 1,
                Symbols.HORIZONTAL_LINE * (dialog_width - 2),
                curses.color_pair(Colors.BORDER),
            )

            # Input prompt
            input_label = "✎ Enter new OSR ID:"
            write_text(
                stdscr,
                dialog_y + 5,
                dialog_x + 2,
                input_label,
                curses.color_pair(Colors.TEXT),
            )

            # Separator line for visual separation
            separator_y = dialog_y + 8
            stdscr.addstr(
                separator_y,
                dialog_x + 1,
                Symbols.HORIZONTAL_LINE * (dialog_width - 2),
                curses.color_pair(Colors.BORDER),
            )

            instructions = "[ENTER] Save • [Ctrl+C] Cancel • Leave empty to use environment variable"

            write_text(
                stdscr,
                dialog_y + 9,
                dialog_x + 2,
                instructions,
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
                success_msg = "✓ OSR ID updated to: {}".format(new_osrid)
                msg_type = "success"
            else:
                # Remove from config to use environment variable
                config.pop("osr_id", None)
                env_osrid = os.environ.get("OSR_ID", "")
                if env_osrid:
                    success_msg = "✓ OSR ID cleared - now using environment: {}".format(
                        env_osrid
                    )
                    msg_type = "success"
                else:
                    success_msg = (
                        "⚠ OSR ID cleared - environment variable OSR_ID not set!"
                    )
                    msg_type = "warning"

            config_manager.save(config)

            status_type = "success" if msg_type == "success" else "warning"
            show_status(stdscr, success_msg, status_type)
            stdscr.refresh()
            time.sleep(2)  # Show status for 2 seconds

        except KeyboardInterrupt:
            # User cancelled with Ctrl+C
            pass
        finally:
            curses.noecho()
            curses.curs_set(0)
