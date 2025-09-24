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
            "Insert carrier now (copy to clipboard)",
            "Show insertion command",
            "Show all commands",
            "Custom element insertion",
            "Skip sandbox operations",
        ]

        selected_idx = display_menu(
            stdscr,
            options,
            title="Test Server - Sandbox Operations",
            instructions="Choose how to handle carrier insertion",
        )

        if selected_idx is None or selected_idx == 4:
            return

        # Get element and generate commands
        if selected_idx == 3:  # Custom element
            element = self._get_custom_element(stdscr, config)
            if not element:
                return
        else:
            element = config.get("sandbox_default_element", "workflow.input.station.01")

        sandbox_gen = SandboxCommandGenerator(osrid)
        commands = sandbox_gen.generate_insertion_commands_for_order(
            xml_content, element
        )

        if selected_idx == 0:
            self._copy_command(stdscr, commands.get("insert_now", ""))
        elif selected_idx == 1:
            self._show_command(stdscr, commands.get("insert_now", ""))
        elif selected_idx == 2:
            self._show_all_commands(stdscr, commands)
        elif selected_idx == 3:
            self._handle_custom_element_commands(stdscr, commands)

    def handle_order_history(self, stdscr, order: Dict) -> None:
        """Handle sandbox commands for order from history."""
        order_id = order.get("order_id", "Unknown")
        osrid = order.get("osrid", "")

        if not osrid:
            display_dialog(stdscr, "No OSR ID found for this order.", "Error", "error")
            return

        options = [
            "Copy insertion command",
            "Show all commands",
            "Copy all commands",
            "Custom element commands",
            "Back",
        ]

        selected_idx = display_menu(
            stdscr,
            options,
            title=f"Sandbox Commands for Order {order_id}",
            instructions="Select action",
        )

        if selected_idx is None or selected_idx == 4:
            return

        # Get element for commands
        if selected_idx == 3:  # Custom element
            element = self._get_custom_element(stdscr, {})
            if not element:
                return
        else:
            element = "workflow.input.station.01"

        # Generate commands
        sandbox_gen = SandboxCommandGenerator(osrid)
        carrier = f"carrier_{order_id}"
        commands = {
            "insert_now": sandbox_gen.generate_insert_command(element, carrier),
            "remove_later": sandbox_gen.generate_remove_command(element, carrier),
        }

        if selected_idx == 0:
            self._copy_command(stdscr, commands["insert_now"])
        elif selected_idx == 1:
            self._show_history_commands(stdscr, order_id, osrid, commands)
        elif selected_idx == 2:
            self._copy_history_commands(stdscr, order_id, osrid, commands)
        elif selected_idx == 3:
            self._handle_custom_element_commands(stdscr, commands)

    def _copy_command(self, stdscr, command: str) -> None:
        """Copy single command to clipboard."""
        if not command:
            return

        copied = copy_to_clipboard(command)
        if copied:
            msg = f"Command copied to clipboard:\n\n{command}\n\nPaste and run in sandbox shell."
            display_dialog(stdscr, msg, "Command Ready", "info")
        else:
            msg = f"Clipboard copy failed. Command:\n\n{command}\n\nCopy manually."
            display_dialog(stdscr, msg, "Manual Copy Required", "warning")

    def _show_command(self, stdscr, command: str) -> None:
        """Show single command."""
        if command:
            msg = f"Insertion command:\n\n{command}\n\nCopy and run in sandbox shell."
            display_dialog(stdscr, msg, "Insertion Command", "info")

    def _show_all_commands(self, stdscr, commands: Dict) -> None:
        """Show all commands with usage instructions."""
        lines = [
            "=== INSERTION COMMANDS ===",
            f"Insert: {commands.get('insert_now', 'N/A')}",
            f"Remove: {commands.get('remove_later', 'N/A')}",
            "",
            "=== USAGE ===",
            "1. Run insertion command",
            "2. Use remove for cleanup",
        ]

        text = "\n".join(lines)
        copied = copy_to_clipboard(text)
        if copied:
            text += "\n\n(Commands copied to clipboard)"

        display_dialog(stdscr, text, "All Sandbox Commands", "info")

    def _show_history_commands(
        self, stdscr, order_id: str, osrid: str, commands: Dict
    ) -> None:
        """Show commands for historical order."""
        lines = [
            f"Order ID: {order_id}",
            f"OSR: {osrid}",
            "",
            "=== SANDBOX COMMANDS ===",
            f"Insert: {commands['insert_now']}",
            f"Remove: {commands['remove_later']}",
            "",
            "Note: Commands generated using order ID as carrier.",
            "Adjust element and carrier as needed.",
        ]

        text = "\n".join(lines)
        display_dialog(stdscr, text, "All Sandbox Commands", "info")

    def _copy_history_commands(
        self, stdscr, order_id: str, osrid: str, commands: Dict
    ) -> None:
        """Copy all commands for historical order."""
        lines = [
            f"# Sandbox commands for Order {order_id} (OSR: {osrid})",
            f"# Insert carrier",
            commands["insert_now"],
            f"# Remove carrier (cleanup)",
            commands["remove_later"],
        ]

        text = "\n".join(lines)
        copied = copy_to_clipboard(text)
        if copied:
            msg = f"All commands copied to clipboard!\n\n{text}"
            display_dialog(stdscr, msg, "Commands Copied", "success")
        else:
            msg = f"Clipboard copy failed. Commands:\n\n{text}"
            display_dialog(stdscr, msg, "Manual Copy Required", "warning")

    def _get_custom_element(self, stdscr, config: Dict) -> str:
        """Get custom workflow element from user input."""
        # Common workflow elements
        common_elements = [
            "workflow.input.station.01",
            "workflow.input.station.02",
            "workflow.output.station.01",
            "workflow.output.station.02",
            "workflow.shuttle.aisle.01",
            "workflow.shuttle.aisle.02",
            "workflow.lift.01",
            "workflow.lift.02",
        ]

        # Add saved custom elements
        custom_elements = config.get("sandbox_custom_elements", [])
        all_elements = common_elements + custom_elements + ["Enter new custom element"]

        selected_idx = display_menu(
            stdscr,
            all_elements,
            title="Select Workflow Element",
            instructions="Choose element or enter new custom one",
        )

        if selected_idx is None:
            return config.get("sandbox_default_element", "workflow.input.station.01")

        if selected_idx == len(all_elements) - 1:  # Enter new custom
            return self._get_and_save_custom_element(stdscr, config)
        else:
            return all_elements[selected_idx]

    def _get_and_save_custom_element(self, stdscr, config: Dict) -> str:
        """Get new custom element and optionally save it."""
        default_element = config.get(
            "sandbox_default_element", "workflow.input.station.01"
        )
        element = prompt_input(
            stdscr,
            f"Enter custom workflow element (default: {default_element}):",
            allow_empty=True,
        )

        if not element:
            return default_element

        # Ask if user wants to save this element for future use
        save_options = ["Yes, save for future use", "No, use once only"]
        save_idx = display_menu(
            stdscr,
            save_options,
            title=f"Save element '{element}'?",
            instructions="Choose whether to remember this element",
        )

        if save_idx == 0:  # Save it
            custom_elements = config.get("sandbox_custom_elements", [])
            if element not in custom_elements:
                custom_elements.append(element)
                config["sandbox_custom_elements"] = custom_elements
                if self.config_manager:
                    self.config_manager.save(config)
                display_dialog(
                    stdscr, f"Element '{element}' saved!", "Saved", "success"
                )

        return element

    def _handle_custom_element_commands(self, stdscr, commands: Dict) -> None:
        """Handle custom element command display options."""
        options = [
            "Copy insertion command",
            "Show insertion command",
            "Show all commands",
            "Copy all commands",
        ]

        selected_idx = display_menu(
            stdscr,
            options,
            title="Custom Element Commands",
            instructions="Select action for custom element commands",
        )

        if selected_idx is None:
            return

        if selected_idx == 0:
            self._copy_command(stdscr, commands.get("insert_now", ""))
        elif selected_idx == 1:
            self._show_command(stdscr, commands.get("insert_now", ""))
        elif selected_idx == 2:
            self._show_all_commands(stdscr, commands)
        elif selected_idx == 3:
            lines = [
                "# Custom element sandbox commands",
                f"# Insert carrier",
                commands.get("insert_now", ""),
                f"# Remove carrier (cleanup)",
                commands.get("remove_later", ""),
            ]
            text = "\n".join(lines)
            copied = copy_to_clipboard(text)
            if copied:
                msg = f"Commands copied to clipboard!\n\n{text}"
                display_dialog(stdscr, msg, "Commands Copied", "success")
            else:
                msg = f"Clipboard copy failed. Commands:\n\n{text}"
                display_dialog(stdscr, msg, "Manual Copy Required", "warning")
