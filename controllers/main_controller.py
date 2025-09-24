"""
Main application controller that orchestrates the GUI workflow.
"""

import curses
from typing import Dict, Any, List

from models.config import Config
from models.xml_generator import OrderXML
from models.order_sender import (
    OrderSender,
    extract_order_id_from_xml,
    get_order_type_from_xml,
)
from models.history import History
from config.constants import ORDER_TYPES, OrderMode, SERVER_TYPES, ServerType
from config.defaults import FIELD_ORDER
from ui.utils import (
    setup_colors,
    get_screen_size,
    write_text,
    center_string,
    draw_border,
)
from ui.menu import display_menu
from ui.dialog import display_dialog, prompt_input
from ui.form import edit_form
from controllers.order_controller import OrderController
from .history_controller import HistoryController
from .config_controller import ConfigController
from .sandbox_controller import SandboxController


class MainController:
    """Main application controller."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.config_manager = Config()
        self.order_controller = OrderController(dry_run)
        self.history_controller = HistoryController()
        self.config_controller = ConfigController()
        self.sandbox_controller = SandboxController(self.config_manager)

    def run(self, stdscr) -> None:
        """Main application entry point."""
        # Initialize curses settings
        curses.curs_set(0)  # Hide cursor
        setup_colors()

        # Load configuration
        config = self.config_manager.load()

        # Show intro on first run
        if config.get("first_run", True):
            self._intro_menu(stdscr, config)
            config["first_run"] = False
            self.config_manager.save(config)

        # Start main menu
        self._display_main_menu(stdscr, config)

    def _intro_menu(self, stdscr, config: Dict[str, Any]) -> None:
        """Display the introductory setup menu."""
        # Get user name
        name = prompt_input(
            stdscr, "Enter your name for order identification:", allow_empty=True
        )
        config["name"] = name if name else "src"

        # Server type selection
        server_type_idx = display_menu(
            stdscr,
            SERVER_TYPES,
            title="Select server type:",
            instructions="Choose whether this is a Live or Test server • This affects sandbox command generation",
        )

        if server_type_idx is not None:
            config["server_type"] = SERVER_TYPES[server_type_idx]
        else:
            config["server_type"] = ServerType.LIVE  # Default to live

        # Initialize capacity_specs
        capacity_specs = {}

        # Capacity specs input (optional)
        options = ["full", "half", "quarter", "eighth", "custom"]
        selected_idx = display_menu(
            stdscr,
            options,
            title="Select capacity specs (optional - skip to exclude from XML):",
            instructions="Select compartment types to include in orders • Press 'q' to skip",
            allow_multiple=True,
        )

        if selected_idx:
            for idx in selected_idx:
                option = options[idx]
                if option == "custom":
                    custom_names = prompt_input(
                        stdscr,
                        "Enter custom spec names (space or comma separated): ",
                        allow_empty=False,
                    )
                    if custom_names:
                        for custom_spec in custom_names.replace(",", " ").split():
                            max_qty = prompt_input(
                                stdscr,
                                f"Enter max quantity for {custom_spec}:",
                                input_type=int,
                            )
                            if max_qty is not None:
                                capacity_specs[custom_spec] = max_qty
                else:
                    max_qty = prompt_input(
                        stdscr, f"Enter max quantity for {option}:", input_type=int
                    )
                    if max_qty is not None:
                        capacity_specs[option] = max_qty

        config["capacity_specs"] = capacity_specs

    def _display_main_menu(self, stdscr, config: Dict[str, Any]) -> None:
        """Display the main menu for mode selection."""
        modes = ORDER_TYPES + [
            "View Order History",
            "Cancel Orders",
            "Configure OSR ID",
            "Configure Server Type",
        ]

        while True:
            # Get current OSR ID and server type for display
            current_osrid = self.config_manager.resolve_osr(config)
            osrid_display = (
                f"OSR: {current_osrid}" if current_osrid else "OSR: Not configured"
            )

            server_type = config.get("server_type", ServerType.LIVE)
            server_display = f"Server: {server_type}"

            selected_idx = display_menu(
                stdscr,
                options=modes,
                title=f"Select a processing mode ({osrid_display} | {server_display})",
            )

            if selected_idx is None:
                break  # Exit the menu

            selected_mode = modes[selected_idx]

            if selected_mode == "View Order History":
                self.history_controller.view_order_history_menu(stdscr, config)
                continue
            elif selected_mode == "Cancel Orders":
                self.history_controller.cancel_orders_menu(stdscr, config)
                continue
            elif selected_mode == "Configure OSR ID":
                self.config_controller.configure_osr_id(
                    stdscr, config, self.config_manager
                )
                continue
            elif selected_mode == "Configure Server Type":
                self._configure_server_type(stdscr, config)
                continue

            # Handle order creation
            self._handle_order_creation(stdscr, config, selected_mode)

    def _configure_server_type(self, stdscr, config: Dict[str, Any]) -> None:
        """Configure server type setting."""
        current_type = config.get("server_type", ServerType.LIVE)

        selected_idx = display_menu(
            stdscr,
            SERVER_TYPES,
            title=f"Configure Server Type (Current: {current_type})",
            instructions="Select the type of server this application is running on",
        )

        if selected_idx is not None:
            config["server_type"] = SERVER_TYPES[selected_idx]
            self.config_manager.save(config)

            message = f"Server type updated to: {SERVER_TYPES[selected_idx]}"
            if SERVER_TYPES[selected_idx] == ServerType.TEST:
                message += "\n\nTest server mode enables sandbox command generation"

            display_dialog(stdscr, message, "Configuration Updated", "success")

    def _handle_order_creation(
        self, stdscr, config: Dict[str, Any], selected_mode: str
    ) -> None:
        """Handle the creation and sending of orders."""
        values = config[selected_mode]

        # Set user name in values
        if isinstance(values, list):
            for v in values:
                v["name"] = config.get("name", "SRC")
        else:
            values["name"] = config.get("name", "SRC")

        # Handle different order types
        if selected_mode in (OrderMode.PICK_STANDARD, OrderMode.PICK_MANUAL):
            lines = [dict(v) for v in values]  # deep copy
            send_now = self.order_controller.edit_pick_lines(
                stdscr, selected_mode, lines, values
            )
            if send_now:
                config[selected_mode] = lines
                self.config_manager.save(config)
                order_data = {"mode": selected_mode, "values": values, "lines": lines}
                xml = OrderXML.generate(order_data, config)
                self._confirm_and_send_order(stdscr, xml, config)
        else:
            # Handle single order types
            send_now = self._edit_order(stdscr, selected_mode, values)
            if send_now:
                config[selected_mode] = values
                self.config_manager.save(config)
                order_data = {"mode": selected_mode, "values": values, "lines": None}
                xml = OrderXML.generate(order_data, config)
                self._confirm_and_send_order(stdscr, xml, config)

    def _edit_order(self, stdscr, mode: str, values: Dict) -> bool:
        """Edit the order fields for a given mode."""
        fields = FIELD_ORDER.get(mode, list(values.keys()))
        result = edit_form(stdscr, fields, values, title=f"Edit {mode} Order")
        return result is not None

    def _confirm_and_send_order(self, stdscr, xml_content: str, config: Dict) -> None:
        """Confirm and send order with proper XML formatting."""
        from config.constants import Colors, Symbols

        # Validate XML
        if xml_content is None:
            display_dialog(stdscr, "Error: Generated XML is None!", "Error", "error")
            return
        elif not xml_content.strip():
            display_dialog(stdscr, "Error: Generated XML is empty!", "Error", "error")
            return

        # Format XML for display
        formatted_xml = self._format_xml_for_display(xml_content)

        # Show confirmation dialog
        if self._show_xml_confirmation_dialog(stdscr, formatted_xml):
            self._send_order(stdscr, xml_content, config)

    def _format_xml_for_display(self, xml_content: str) -> List[str]:
        """Format XML content for better display."""
        try:
            import xml.dom.minidom

            dom = xml.dom.minidom.parseString(xml_content)
            formatted_xml = dom.toprettyxml(indent="    ", encoding=None)

            xml_lines = []
            for line in formatted_xml.split("\n"):
                if line.strip() and not line.strip().startswith("<?xml"):
                    xml_lines.append(line.rstrip())
            return xml_lines
        except Exception:
            # Fallback to basic formatting
            return self._basic_xml_formatting(xml_content)

    def _basic_xml_formatting(self, xml_content: str) -> List[str]:
        """Basic XML formatting fallback."""
        xml_lines = []
        indent_level = 0
        for line in xml_content.split("\n"):
            line = line.strip()
            if not line:
                continue

            if line.startswith("</"):
                indent_level = max(0, indent_level - 1)

            indented_line = "    " * indent_level + line
            xml_lines.append(indented_line)

            if (
                line.startswith("<")
                and not line.startswith("</")
                and not line.endswith("/>")
            ):
                indent_level += 1

        return xml_lines

    def _show_xml_confirmation_dialog(self, stdscr, xml_lines: List[str]) -> bool:
        """Show XML confirmation dialog and get user confirmation."""
        from config.constants import Colors, Symbols

        height, width = get_screen_size(stdscr)
        stdscr.clear()

        dialog_width = min(width - 6, 100)
        dialog_height = min(height - 3, 30)
        dialog_x = (width - dialog_width) // 2
        dialog_y = (height - dialog_height) // 2

        draw_border(
            stdscr,
            dialog_y,
            dialog_x,
            dialog_height,
            dialog_width,
            f" {Symbols.CONFIRM} Send Order Confirmation ",
            Colors.BORDER,
        )

        try:
            # XML preview header
            preview_text = f"{Symbols.EDIT} XML Preview:"
            write_text(
                stdscr,
                dialog_y + 2,
                dialog_x + 2,
                preview_text,
                curses.color_pair(Colors.HEADER) | curses.A_BOLD,
            )

            # Display XML content (simplified)
            max_preview_lines = dialog_height - 11
            display_lines = xml_lines[:max_preview_lines]

            for i, line in enumerate(display_lines):
                if dialog_y + 3 + i < dialog_y + dialog_height - 7:
                    write_text(
                        stdscr,
                        dialog_y + 3 + i,
                        dialog_x + 3,
                        line[: dialog_width - 6],  # Truncate long lines
                        curses.color_pair(Colors.TEXT),
                    )

            # Warning message
            warning = f"{Symbols.WARNING} This will send the order to the OSR system!"
            warning_centered = center_string(warning, dialog_width - 4)
            write_text(
                stdscr,
                dialog_y + dialog_height - 6,
                dialog_x + 2,
                warning_centered,
                curses.color_pair(Colors.WARNING) | curses.A_BOLD,
            )

            # Instructions
            instructions = (
                f"{Symbols.KEY} [Y]es to send  {Symbols.BULLET}  [N]o to cancel"
            )
            instructions_centered = center_string(instructions, dialog_width - 4)
            write_text(
                stdscr,
                dialog_y + dialog_height - 4,
                dialog_x + 2,
                instructions_centered,
                curses.color_pair(Colors.INFO),
            )

        except curses.error:
            pass

        stdscr.refresh()

        # Get user confirmation
        while True:
            key = stdscr.getch()
            if key in (ord("y"), ord("Y")):
                return True
            elif key in (ord("n"), ord("N"), 27):  # N or Escape
                return False

    def _send_order(self, stdscr, xml_content: str, config: Dict) -> None:
        """Send the order and handle sandbox commands for test servers."""
        osrid = self.config_manager.resolve_osr(config)
        if not osrid:
            error_msg = (
                "OSR_ID is not configured!\n\n"
                "Please either:\n"
                "• Set OSR_ID environment variable, or\n"
                "• Use 'Configure OSR ID' from main menu"
            )
            display_dialog(stdscr, error_msg, "Configuration Error", "error")
            return

        try:
            # Send the order first
            sender = OrderSender(osrid, self.dry_run)
            sender.send(xml_content)

            # Extract order information for tracking
            order_id = extract_order_id_from_xml(xml_content)
            order_type = get_order_type_from_xml(xml_content)

            if self.dry_run:
                History.add_order(order_id, order_type, osrid, "dry_run")
                success_msg = f"DRY RUN: Order would be sent successfully!"
            else:
                History.add_order(order_id, order_type, osrid, "sent")
                success_msg = f"Order sent successfully!"

            display_dialog(stdscr, success_msg, "Success", "success")

            # Handle sandbox commands for test servers
            server_type = config.get("server_type", ServerType.LIVE)
            if server_type == ServerType.TEST:
                self.sandbox_controller.handle_post_order(
                    stdscr, xml_content, osrid, config
                )

        except Exception as e:
            error_msg = f"Error sending order: {e}"
            display_dialog(stdscr, error_msg, "Error", "error")
