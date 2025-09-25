"""Order-specific controller for handling order creation and editing."""

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

            instructions = f"{Symbols.ARROW_UP}/{Symbols.ARROW_DOWN} Navigate • [A]dd • [D]elete • [Enter] Edit • [S]end • [B]ack"
            min_width = max(len(instructions) + 8, max_line_len + 20, 80)

            box_width = min(width - 6, max(min_width, 100))  # Ensure adequate width
            box_height = min(
                height - 4, len(lines) + 12
            )  # More space for better layout
            box_x = (width - box_width) // 2
            box_y = (height - box_height) // 2

            # Enhanced main box with better styling
            # Enhanced title for order editor
            title = f" {mode} Order Editor "
            draw_border(
                stdscr, box_y, box_x, box_height, box_width, title, Colors.HEADER
            )

            try:
                # Enhanced instructions with guaranteed visibility
                instructions_y = box_y + 2
                instructions_truncated = truncate_text(instructions, box_width - 4)
                instructions_centered = center_string(
                    instructions_truncated, box_width - 4
                )
                stdscr.addstr(
                    instructions_y,
                    box_x + 2,
                    instructions_centered,
                    curses.color_pair(Colors.SUCCESS) | curses.A_BOLD,
                )

                # Visual separator for better organization
                separator_y = box_y + 3
                stdscr.addstr(
                    separator_y,
                    box_x + 1,
                    Symbols.HORIZONTAL_LINE * (box_width - 2),
                    curses.color_pair(Colors.BORDER),
                )

                # Order summary with key metrics
                summary_y = box_y + 4
                # Get order number from the first values entry if available
                order_number = values[0].get("Order Number", "N/A") if values else "N/A"
                order_info = (
                    f"Order: {order_number} • Lines: {len(lines)} • Type: {mode}"
                )
                order_info_truncated = truncate_text(order_info, box_width - 4)
                order_info_centered = center_string(order_info_truncated, box_width - 4)
                stdscr.addstr(
                    summary_y,
                    box_x + 2,
                    order_info_centered,
                    curses.color_pair(Colors.INFO) | curses.A_BOLD,
                )

                # Display lines
                lines_start_y = box_y + 6  # More space after summary
                for i, line in enumerate(lines):
                    if (
                        lines_start_y + i >= box_y + box_height - 4
                    ):  # Leave more space for footer
                        break

                    # Enhanced line display with better information hierarchy
                    line_num = f"{i + 1:2d}"
                    product_name = line.get("Product Name", "N/A")
                    product_code = line.get("Product Code", "N/A")
                    quantity = line.get("Quantity", "N/A")
                    destination = line.get("Destination", "")

                    # More informative line display
                    if destination:
                        line_str = f"{product_name} ({product_code}) → {destination}, Qty: {quantity}"
                    else:
                        line_str = f"{product_name} ({product_code}), Qty: {quantity}"

                    line_str = truncate_text(line_str, box_width - 12)

                    if i == idx:
                        # Enhanced highlighting for selected line
                        try:
                            stdscr.addstr(
                                lines_start_y + i,
                                box_x + 2,
                                f"{Symbols.ARROW_RIGHT}",
                                curses.color_pair(Colors.SELECTED) | curses.A_BOLD,
                            )
                            stdscr.addstr(
                                lines_start_y + i,
                                box_x + 4,
                                line_num,
                                curses.color_pair(Colors.SELECTED) | curses.A_BOLD,
                            )
                            stdscr.addstr(
                                lines_start_y + i,
                                box_x + 7,
                                f". {line_str}",
                                curses.color_pair(Colors.WARNING) | curses.A_BOLD,
                            )
                        except curses.error:
                            pass
                    else:
                        # Normal line with subtle hierarchy
                        try:
                            stdscr.addstr(
                                lines_start_y + i,
                                box_x + 4,
                                line_num,
                                curses.color_pair(Colors.INFO),
                            )
                            stdscr.addstr(
                                lines_start_y + i,
                                box_x + 7,
                                f". {line_str}",
                                curses.color_pair(Colors.TEXT),
                            )
                        except curses.error:
                            pass

                # Enhanced status footer with more useful information
                footer_y = box_y + box_height - 3
                # Separator line
                stdscr.addstr(
                    footer_y - 1,
                    box_x + 1,
                    Symbols.HORIZONTAL_LINE * (box_width - 2),
                    curses.color_pair(Colors.BORDER),
                )

                status_text = f"Line {idx + 1} of {len(lines)} selected • Total Lines: {len(lines)}"
                status_centered = center_string(status_text, box_width - 4)
                stdscr.addstr(
                    footer_y,
                    box_x + 2,
                    status_centered,
                    curses.color_pair(Colors.SUCCESS) | curses.A_BOLD,
                )

            except curses.error:
                pass

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
        updated_values = edit_form(
            stdscr, fields, line, title=f"Edit {mode} Line", enable_db_lookup=True
        )
        if updated_values is not None:
            line.update(updated_values)  # Update only the changed fields
            return None  # Continue editing
        return None

    def edit_transport_lines(
        self, stdscr, mode: str, lines: List[Dict], values: List[Dict]
    ) -> bool:
        """Edit the transport order lines with multi-slot capability."""
        from config.constants import OrderMode

        idx = 0
        height, width = get_screen_size(stdscr)

        while True:
            stdscr.clear()

            # Enhanced dynamic box sizing for transport orders
            max_line_len = (
                max(
                    len(
                        f"Slot {line.get('Slot Number', '')}: {line.get('Product Name', '')} ({line.get('Product Code', '')}), Qty: {line.get('Quantity', '')}"
                    )
                    for line in lines
                )
                if lines
                else 60
            )

            # Calculate minimum width for transport instructions
            instructions = f"{Symbols.ARROW_UP}/{Symbols.ARROW_DOWN} Navigate • [A]dd Slot • [D]elete • [Enter] Edit • [S]end • [B]ack"
            min_width = max(len(instructions) + 8, max_line_len + 20, 90)

            box_width = min(
                width - 6, max(min_width, 110)
            )  # Wider for transport complexity
            box_height = min(height - 4, len(lines) + 12)
            box_x = (width - box_width) // 2
            box_y = (height - box_height) // 2

            # Enhanced transport box with better title
            container_num = lines[0].get("Container Number", "N/A") if lines else "N/A"
            title = f" Transport Order Editor - Container {container_num} "
            draw_border(
                stdscr, box_y, box_x, box_height, box_width, title, Colors.HEADER
            )

            try:
                # Enhanced instructions with guaranteed visibility
                instructions_y = box_y + 2
                instructions_truncated = truncate_text(instructions, box_width - 4)
                instructions_centered = center_string(
                    instructions_truncated, box_width - 4
                )
                stdscr.addstr(
                    instructions_y,
                    box_x + 2,
                    instructions_centered,
                    curses.color_pair(Colors.SUCCESS) | curses.A_BOLD,
                )

                # Visual separator
                separator_y = box_y + 3
                stdscr.addstr(
                    separator_y,
                    box_x + 1,
                    Symbols.HORIZONTAL_LINE * (box_width - 2),
                    curses.color_pair(Colors.BORDER),
                )

                # Transport summary with key information
                summary_y = box_y + 4
                processing_mode = (
                    lines[0].get("Processing Mode", "standard") if lines else "standard"
                )
                if lines:
                    summary_info = f"Container: {container_num} • Slots: {len(lines)} • Mode: {processing_mode}"
                else:
                    summary_info = (
                        f"Transport Order • Mode: {processing_mode} • No slots defined"
                    )

                summary_centered = center_string(summary_info, box_width - 4)
                stdscr.addstr(
                    summary_y,
                    box_x + 2,
                    summary_centered,
                    curses.color_pair(Colors.INFO) | curses.A_BOLD,
                )

                # Display slot lines with enhanced formatting
                slots_start_y = box_y + 6
                lines_start_y = box_y + 6
                for i, line in enumerate(lines):
                    if lines_start_y + i >= box_y + box_height - 3:
                        break  # Don't overflow

                    slot_str = "Slot {}: {} ({}), Qty: {}".format(
                        line.get("Slot Number", "N/A"),
                        line.get("Product Name", "N/A"),
                        line.get("Product Code", "N/A"),
                        line.get("Quantity", "N/A"),
                    )
                    slot_str = truncate_text(slot_str, box_width - 8)

                    if i == idx:
                        # Highlighted slot
                        arrow_text = f"{Symbols.ARROW_RIGHT} {slot_str}"
                        stdscr.addstr(
                            lines_start_y + i,
                            box_x + 2,
                            arrow_text,
                            curses.color_pair(Colors.SELECTED) | curses.A_BOLD,
                        )
                    else:
                        # Normal slot
                        stdscr.addstr(
                            lines_start_y + i,
                            box_x + 4,
                            slot_str,
                            curses.color_pair(Colors.TEXT),
                        )

                # Status info
                status_y = box_y + box_height - 2
                status_text = (
                    f"Slot {idx + 1} of {len(lines)} • {len(lines)} total slots"
                )
                status_centered = center_string(status_text, box_width - 4)
                stdscr.addstr(
                    status_y, box_x + 2, status_centered, curses.color_pair(Colors.INFO)
                )

            except curses.error:
                pass

            # Create status bar
            show_status(
                stdscr,
                f"Editing Transport Order • Use arrow keys to navigate slots",
                "info",
            )

            stdscr.refresh()
            key = stdscr.getch()

            # Handle navigation
            if key in (curses.KEY_UP, ord("k")) and idx > 0:
                idx -= 1
            elif key in (curses.KEY_DOWN, ord("j")) and idx < len(lines) - 1:
                idx += 1
            elif key in (ord("a"), ord("A")):  # Add new slot
                new_slot = (
                    lines[-1].copy()
                    if lines
                    else DEFAULT_ORDER_VALUES[OrderMode.TRANSPORT][0].copy()
                )
                new_slot["Slot Number"] = str(len(lines) + 1)
                lines.append(new_slot)
                idx = len(lines) - 1
                show_status(stdscr, "New slot added", "success")
                stdscr.refresh()
                time.sleep(0.3)
            elif key in (ord("d"), ord("D")) and lines:  # Delete slot
                if len(lines) > 1:
                    lines.pop(idx)
                    # Renumber remaining slots
                    for i, line in enumerate(lines):
                        line["Slot Number"] = str(i + 1)
                    if idx >= len(lines):
                        idx = len(lines) - 1
                    show_status(stdscr, "Slot deleted", "warning")
                    stdscr.refresh()
                    time.sleep(0.3)
                else:
                    show_status(stdscr, "Cannot delete the last slot", "error")
                    stdscr.refresh()
                    time.sleep(0.5)
            elif key in (curses.KEY_ENTER, 10, 13, ord("l")):  # Enter
                result = self._edit_transport_slot(stdscr, lines[idx], mode, lines)
                if result is True:
                    return True
            elif key == ord("s") or key == ord("S"):
                return True  # Save/send
            elif key in (ord("h"), ord("b"), ord("B")):
                return False  # Back

    def _edit_transport_slot(
        self,
        stdscr,
        slot: Dict,
        mode: Optional[str] = None,
        all_lines: List[Dict] = None,
    ) -> Optional[bool]:
        """Edit a single slot in the transport order with database lookups."""
        from config.constants import OrderMode

        fields = FIELD_ORDER.get(OrderMode.TRANSPORT, [])

        # Store original processing mode to detect changes
        original_processing_mode = slot.get("Processing Mode")

        # Use the enhanced form with database lookup enabled
        updated_values = edit_form(
            stdscr,
            fields,
            slot,
            title=f"Edit Transport Slot {slot.get('Slot Number', '')}",
            enable_db_lookup=True,
        )
        if updated_values is not None:
            # Check if processing mode was changed and apply to all slots
            new_processing_mode = updated_values.get("Processing Mode")
            if (
                all_lines
                and new_processing_mode
                and new_processing_mode != original_processing_mode
            ):
                # Apply new processing mode to all slots
                for line in all_lines:
                    line["Processing Mode"] = new_processing_mode
                show_status(
                    stdscr,
                    f"Processing mode '{new_processing_mode}' applied to all slots",
                    "success",
                )
                stdscr.refresh()
                time.sleep(0.8)
            else:
                slot.update(updated_values)  # Update only the changed fields
            return None  # Continue editing
        return None

    def edit_inventory_order(self, stdscr, mode: str, values: Dict) -> bool:
        """Edit inventory order with enhanced UI."""
        from config.constants import Colors, Symbols

        # Use the enhanced form editor for consistent UI
        fields = FIELD_ORDER.get(mode, list(values.keys()))
        result = edit_form(
            stdscr, fields, values, title=f"Edit {mode} Order", enable_db_lookup=True
        )
        return result is not None

    def edit_goods_in_order(self, stdscr, mode: str, values: Dict) -> bool:
        """Edit goods-in order with enhanced UI."""
        from config.constants import Colors, Symbols

        # Use the enhanced form editor for consistent UI
        fields = FIELD_ORDER.get(mode, list(values.keys()))
        result = edit_form(
            stdscr, fields, values, title=f"Edit {mode} Order", enable_db_lookup=True
        )
        return result is not None

    def edit_goods_add_order(self, stdscr, mode: str, values: Dict) -> bool:
        """Edit goods-add order with enhanced UI."""
        from config.constants import Colors, Symbols

        # Use the enhanced form editor for consistent UI
        fields = FIELD_ORDER.get(mode, list(values.keys()))
        result = edit_form(
            stdscr, fields, values, title=f"Edit {mode} Order", enable_db_lookup=True
        )
        return result is not None
