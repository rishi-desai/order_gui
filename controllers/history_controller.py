"""
History controller for viewing and managing order history.
"""

from typing import Dict, Any

from models.config import Config
from models.history import History
from models.order_sender import OrderCanceller
from ui.menu import display_menu
from ui.dialog import display_dialog
from ui.utils import (
    get_screen_size,
)
from config.constants import Symbols, ServerType
from .sandbox_controller import SandboxController


class HistoryController:
    """Controller for order history operations."""

    def __init__(self):
        self.config_manager = Config()
        self.sandbox_controller = SandboxController(self.config_manager)

    def view_order_history_menu(self, stdscr, config: Dict[str, Any]) -> None:
        """Display the order history menu."""
        current_osrid = self.config_manager.resolve_osr(config)

        if not current_osrid:
            display_dialog(
                stdscr, "Please configure OSR ID first.", "Warning", "warning"
            )
            return

        while True:
            # Load orders for current OSR
            osr_orders = History.get_orders_for_osr(current_osrid)

            if not osr_orders:
                display_dialog(
                    stdscr,
                    f"No order history found for OSR {current_osrid}.",
                    "Information",
                    "info",
                )
                return

            # Prepare display options
            options = []
            for order in osr_orders:
                created = order.get("created", "Unknown")
                status = order.get("status", "unknown")
                order_id = order.get("order_id", "unknown")

                display_text = f"{order_id} - {status.upper()} - {created}"
                options.append(display_text)

            # Add navigation options
            options.extend(
                [
                    "",
                    f"{Symbols.BACK} Back to Main Menu",
                    f"{Symbols.REFRESH} Refresh History",
                ]
            )

            # Show the menu
            try:
                selected_idx = display_menu(
                    stdscr,
                    options=options,
                    title=f"Order History for OSR {current_osrid} ({len(osr_orders)} orders)",
                    instructions="Press Enter to select, 'r' to refresh, 'b' to go back, Esc to exit",
                )
            except KeyboardInterrupt:
                break

            if selected_idx == -1:  # Escape pressed
                break
            elif selected_idx == -2:  # Special code for 'r' key (refresh)
                continue  # Refresh by reloading the loop
            elif selected_idx == -3:  # Special code for 'b' key (back)
                break  # Go back to main menu

            # Handle selection
            if selected_idx >= len(osr_orders):
                # Navigation options
                nav_option = selected_idx - len(osr_orders)
                if nav_option == 1:  # Back to Main Menu
                    break
                elif nav_option == 2:  # Refresh History
                    continue
            else:
                # Show detailed order information
                order = osr_orders[selected_idx]
                self._show_order_details(stdscr, order, config)

    def _show_order_details(self, stdscr, order: Dict, config: Dict[str, Any]) -> None:
        """Show detailed information about a specific order."""
        order_id = order.get("order_id", "Unknown")
        order_type = order.get("type", "unknown")
        status = order.get("status", "unknown")
        osrid = order.get("osrid", "Unknown")
        created = order.get("created", "Unknown")
        updated = order.get("updated", "")

        status_symbol = {
            "sent": f"{Symbols.CLOCK} SENT",
            "cancelled": f"{Symbols.ERROR} CANCELLED",
            "cancelled_dry_run": f"{Symbols.WARNING} CANCELLED (DRY RUN)",
            "completed": f"{Symbols.SUCCESS} COMPLETED",
            "failed": f"{Symbols.ERROR} FAILED",
            "processing": f"{Symbols.CLOCK} PROCESSING",
            "pending": f"{Symbols.CLOCK} PENDING",
        }.get(status, f"{Symbols.QUESTION} {status.upper()}")

        # Prepare the order details display
        details_lines = [
            f"{Symbols.ID} Order ID: {order_id}",
            f"{Symbols.TYPE} Type: {order_type}",
            f"{Symbols.OSR} OSR ID: {osrid}",
            f"{Symbols.STATUS} Status: {status_symbol}",
            "",
            f"{Symbols.TIME} Created: {created}",
        ]

        # Only show updated time if it exists and is different from created
        if updated and updated != created:
            details_lines.append(f"{Symbols.TIME} Updated: {updated}")

        # Add action options
        details_lines.extend(
            [
                "",
                "Available Actions:",
                f"1. {Symbols.ARROW_RIGHT} Resend Same Order",
                f"2. {Symbols.EDIT} Edit and Resend Order",
            ]
        )

        # Add sandbox commands for test servers
        server_type = config.get("server_type", ServerType.LIVE)
        if server_type == ServerType.TEST:
            details_lines.extend(
                [
                    f"3. {Symbols.SETTINGS} Generate Sandbox Commands",
                    f"4. {Symbols.BACK} Back to History",
                ]
            )
        else:
            details_lines.append(f"3. {Symbols.BACK} Back to History")

        # Show interactive menu
        action_options = []
        if server_type == ServerType.TEST:
            action_options = [
                "Resend Same Order",
                "Edit and Resend Order",
                "Generate Sandbox Commands",
                "Back to History",
            ]
        else:
            action_options = [
                "Resend Same Order",
                "Edit and Resend Order",
                "Back to History",
            ]

        try:
            selected_idx = display_menu(
                stdscr,
                options=action_options,
                title=f"Order Details: {order_id}",
                instructions="Select an action • Information shown above",
                allow_empty_selection=False,
            )
        except KeyboardInterrupt:
            return

        if selected_idx is None:  # No selection or escape
            return

        # Handle action selection
        if selected_idx == 0:  # Resend Same Order
            # TODO: Implement resend functionality
            display_dialog(
                stdscr,
                "Resend functionality not yet implemented.",
                "Information",
                "info",
            )
        elif selected_idx == 1:  # Edit and Resend Order
            # TODO: Implement edit and resend functionality
            display_dialog(
                stdscr,
                "Edit and resend functionality not yet implemented.",
                "Information",
                "info",
            )
        elif (
            server_type == ServerType.TEST and selected_idx == 2
        ):  # Generate Sandbox Commands
            self.sandbox_controller.handle_order_history(stdscr, order)
        # Back to History - just return (handled by returning from function)

    def cancel_orders_menu(self, stdscr, config: Dict[str, Any]) -> None:
        """Display the cancel orders menu and handle order cancellation."""
        current_osrid = self.config_manager.resolve_osr(config)
        if not current_osrid:
            error_msg = (
                "OSR_ID is not configured!\n\n"
                "Please configure OSR ID first from the main menu."
            )
            display_dialog(stdscr, error_msg, "Configuration Error", "error")
            return

        while True:
            # Get active orders
            try:
                orders = History.get_active_orders(current_osrid)
            except Exception as e:
                display_dialog(
                    stdscr, f"Error retrieving orders: {e}", "Error", "error"
                )
                return

            if not orders:
                display_dialog(stdscr, "No active orders found.", "Information", "info")
                return

            # Prepare menu options
            order_options = []
            for order in orders:
                display_text = (
                    f"{order['order_id']} ({order['type']}) - {order['status']}"
                )
                order_options.append(display_text)

            # Show cancel menu
            selected_indices = display_menu(
                stdscr,
                options=order_options,
                title=f"{Symbols.WARNING} Cancel Orders - Select orders to cancel",
                instructions=f"{Symbols.KEY} Use SPACE to select multiple • ENTER to cancel selected • 'q' to return",
                allow_multiple=True,
            )

            if selected_indices is None or not selected_indices:
                break  # User cancelled or no selection

            # Confirm and cancel orders
            self._confirm_and_cancel_orders(stdscr, orders, selected_indices)
            break

    def _confirm_and_cancel_orders(self, stdscr, orders, selected_indices) -> None:
        """Confirm and cancel selected orders."""
        selected_orders = [orders[i] for i in selected_indices]

        # Get confirmation (simplified)
        confirm_msg = f"Cancel {len(selected_orders)} orders? This cannot be undone!"

        # Simple confirmation dialog
        height, width = get_screen_size(stdscr)
        stdscr.clear()

        y = height // 2
        x = (width - len(confirm_msg)) // 2
        stdscr.addstr(y, x, confirm_msg)
        stdscr.addstr(y + 2, x, "Press Y to confirm, N to cancel")
        stdscr.refresh()

        key = stdscr.getch()
        if key not in (ord("y"), ord("Y")):
            return

        # Cancel the orders
        canceller = OrderCanceller(dry_run="--dry-run" in __import__("sys").argv)
        success_count = 0
        failed_orders = []

        for order in selected_orders:
            success, error_msg = canceller.cancel_order(
                order["type"], order["order_id"]
            )
            if success:
                success_count += 1
                History.update_status(order["order_id"], "cancelled")
            else:
                failed_orders.append(f"{order['order_id']}: {error_msg}")

        # Show results
        if success_count == len(selected_orders):
            display_dialog(
                stdscr,
                f"Successfully cancelled {success_count} orders!",
                "Success",
                "success",
            )
        elif success_count > 0:
            msg = f"Cancelled {success_count} orders. Failed:\n" + "\n".join(
                failed_orders
            )
            display_dialog(stdscr, msg, "Partial Success", "warning")
        else:
            msg = f"Failed to cancel any orders!\n" + "\n".join(failed_orders)
            display_dialog(stdscr, msg, "Error", "error")
