"""History controller for viewing and managing order history."""

import time
from typing import Dict, Any

from models.config import Config
from models.history import History
from models.order_sender import OrderCanceller
from ui.menu import display_menu
from ui.dialog import display_dialog
from ui.utils import (
    get_screen_size,
    show_status,
)
from config.constants import ServerType, Symbols
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
            osr_orders = History.get_orders_for_osr(current_osrid)

            if not osr_orders:
                show_status(
                    stdscr,
                    f"No order history found for OSR {current_osrid}.",
                    "info",
                )
                stdscr.refresh()
                time.sleep(2)
                return

            # Prepare display options
            options = []
            for order in osr_orders:
                created = order.get("created", "Unknown")
                status = order.get("status", "unknown")
                order_id = order.get("order_id", "unknown")

                display_text = f"{order_id} - {status.upper()} - {created}"
                options.append(display_text)

            # Show the menu - let menu.py handle all key processing
            try:
                selected_idx = display_menu(
                    stdscr,
                    options=options,
                    title=f"Order History for OSR {current_osrid} ({len(osr_orders)} orders)",
                    instructions="[Enter] View Details • [B] Back to Main • [R] Refresh • [Q] Quit",
                )
            except KeyboardInterrupt:
                break

            # Only handle actual business logic based on menu return codes
            if selected_idx is None:
                break  # User quit with 'q'
            elif selected_idx == -2:  # Menu detected 'r' - refresh data
                continue  # Refresh by reloading the loop
            elif selected_idx == -3:  # Menu detected 'b' - go back
                break  # Go back to main menu
            elif selected_idx >= 0 and selected_idx < len(osr_orders):
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
            "sent": "SENT",
            "cancelled": "CANCELLED",
            "cancelled_dry_run": "CANCELLED (DRY RUN)",
            "completed": "COMPLETED",
            "failed": "FAILED",
            "processing": "PROCESSING",
            "pending": "PENDING",
        }.get(status, status.upper())

        # Prepare the order details display
        details_lines = [
            f"Order ID: {order_id}",
            f"Type: {order_type}",
            f"OSR ID: {osrid}",
            f"Status: {status_symbol}",
            "",
            f"Created: {created}",
        ]

        # Only show updated time if it exists and is different from created
        if updated and updated != created:
            details_lines.append(f"Updated: {updated}")

        # Add action options
        details_lines.extend(
            [
                "",
                "Available Actions:",
                "1. Resend Same Order",
                "2. Edit and Resend Order",
            ]
        )

        # Add sandbox commands for test servers
        server_type = config.get("server_type", ServerType.LIVE)
        if server_type == ServerType.TEST:
            details_lines.append("3. Generate Sandbox Commands")

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
                instructions="[0-9] Select Action • [Q] Back to History",
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
                show_status(stdscr, "No active orders found.", "info")
                stdscr.refresh()
                time.sleep(2)  # Show status for 2 seconds
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
                title="Cancel Orders - Select orders to cancel",
                instructions="[Space] Select Multiple • [Enter] Cancel Selected • [Q] Back",
                allow_multiple=True,
            )

            if selected_indices is None or not selected_indices:
                break  # User cancelled or no selection

            # Confirm and cancel orders
            self._confirm_and_cancel_orders(stdscr, orders, selected_indices)
            break

    def _confirm_and_cancel_orders(self, stdscr, orders, selected_indices) -> None:
        """Confirm and cancel selected orders."""
        from ui.dialog import display_dialog

        selected_orders = [orders[i] for i in selected_indices]

        # Get confirmation using consistent dialog
        confirm_msg = (
            f"Cancel {len(selected_orders)} orders?\n\nThis action cannot be undone!"
        )

        # Use the consistent yes/no dialog
        confirmed = display_dialog(
            stdscr,
            confirm_msg,
            "Confirm Order Cancellation",
            "question",
            show_yes_no=True,
        )

        if not confirmed:
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
            show_status(
                stdscr,
                f"Successfully cancelled {success_count} orders!",
                "success",
            )
            stdscr.refresh()
            time.sleep(2)  # Show status for 2 seconds
        elif success_count > 0:
            msg = f"Cancelled {success_count} orders. Failed:\n" + "\n".join(
                failed_orders
            )
            display_dialog(stdscr, msg, "Partial Success", "warning")
        else:
            msg = f"Failed to cancel any orders!\n" + "\n".join(failed_orders)
            display_dialog(stdscr, msg, "Error", "error")
