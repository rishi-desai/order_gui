"""
Sandbox controller for test server operations.
"""

from typing import Dict, Any

from models.sandbox_commands import SandboxCommandGenerator, copy_to_clipboard
from ui.menu import display_menu
from ui.dialog import display_dialog, prompt_input
from config.constants import ServerType


class SandboxController:
    """Handles sandbox command generation and user interactions."""

    def __init__(self, config_manager=None):
        self.config_manager = config_manager

    def handle_post_order(
        self, stdscr, xml_content: str, osrid: str, config: Dict
    ) -> None:
        """Handle sandbox operations after order is sent."""
        options = [
            "Show insertion command",
            "Show all commands",
            "Skip sandbox operations",
        ]

        selected_idx = display_menu(
            stdscr,
            options,
            title="Test Server - Sandbox Operations",
            instructions="Choose how to handle carrier insertion",
        )

        if selected_idx is None or selected_idx == 2:
            return

        # Get element from user input (always require manual entry)
        element = self._get_custom_element(stdscr, config)
        if not element:
            return

        sandbox_gen = SandboxCommandGenerator(osrid)
        commands = sandbox_gen.generate_insertion_commands_for_order(
            xml_content, element
        )

        if selected_idx == 0:
            self._show_and_copy_command(stdscr, commands.get("insert_now", ""))
        elif selected_idx == 1:
            self._show_all_commands(stdscr, commands)

    def handle_order_history(self, stdscr, order: Dict) -> None:
        """Handle sandbox commands for order from history."""
        order_id = order.get("order_id", "Unknown")
        osrid = order.get("osrid", "")

        if not osrid:
            display_dialog(stdscr, "No OSR ID found for this order.", "Error", "error")
            return

        options = [
            "Show insertion command",
            "Show all commands",
            "Back",
        ]

        selected_idx = display_menu(
            stdscr,
            options,
            title=f"Sandbox Commands for Order {order_id}",
            instructions="Select action",
        )

        if selected_idx is None or selected_idx == 2:
            return

        # Always get element from user input
        element = self._get_custom_element(stdscr, {})
        if not element:
            return

        # Generate commands using container/tray ID from the order
        sandbox_gen = SandboxCommandGenerator(osrid)

        # Extract carrier from order data (container/tray ID)
        xml_content = order.get("xml_content", "")
        carrier = sandbox_gen.extract_carrier_from_xml(xml_content)
        if not carrier:
            carrier = f"carrier_{order_id}"  # fallback

        commands = {
            "insert_now": sandbox_gen.generate_insert_command(element, carrier),
            "remove_later": sandbox_gen.generate_remove_command(element, carrier),
        }

        if selected_idx == 0:
            self._show_and_copy_command(stdscr, commands["insert_now"])
        elif selected_idx == 1:
            self._show_all_commands(stdscr, commands)

    def _show_and_copy_command(self, stdscr, command: str) -> None:
        """Show single command and auto-copy it to clipboard."""
        if not command:
            return

        copied = copy_to_clipboard(command)
        if copied:
            msg = f"Command copied to clipboard:\n\n{command}\n\nPaste and run in sandbox shell."
            display_dialog(stdscr, msg, "Command Ready", "info")
        else:
            msg = f"Clipboard copy failed. Command:\n\n{command}\n\nCopy manually."
            display_dialog(stdscr, msg, "Manual Copy Required", "warning")

    def _show_all_commands(self, stdscr, commands: Dict) -> None:
        """Show all commands with usage instructions (no auto-copy)."""
        lines = [
            "=== INSERTION COMMANDS ===",
            f"Insert: {commands.get('insert_now', 'N/A')}",
            f"Remove: {commands.get('remove_later', 'N/A')}",
            "",
            "=== USAGE ===",
            "1. Run insertion command",
            "2. Use remove for cleanup",
            "",
            "Manually copy the command you want to use.",
        ]

        text = "\n".join(lines)
        display_dialog(stdscr, text, "All Sandbox Commands", "info")

    def _get_custom_element(self, stdscr, config: Dict) -> str:
        """Get workflow element from user input (manual entry only)."""
        default_element = "workflow.input.station.01"

        element = prompt_input(
            stdscr,
            f"Enter workflow element (default: {default_element}):",
            allow_empty=True,
        )

        if not element or element.strip() == "":
            return default_element

        return element.strip()
