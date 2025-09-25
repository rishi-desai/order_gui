"""Form component for field editing."""

import curses
import time
from typing import List, Dict, Any, Optional

from .utils import (
    get_screen_size,
    center_string,
    truncate_text,
    draw_border,
    show_status,
)
from .menu import display_menu
from config.constants import Colors, Symbols


def edit_form(
    stdscr,
    fields: List[str],
    values: Dict[str, Any],
    title: str = "Edit Fields",
    enable_db_lookup: bool = False,
) -> Optional[Dict[str, Any]]:
    """Enhanced field editing with improved visual design and dynamic sizing."""
    current_row = 0
    height, width = get_screen_size(stdscr)

    while True:
        stdscr.clear()

        max_field_len = max(len(field) for field in fields) if fields else 20
        max_value_len = (
            max(len(str(values.get(field, ""))) for field in fields) if fields else 20
        )

        if enable_db_lookup:
            instruction_text = (
                "[S]end Order  •  [B]ack  •  [Enter] Edit Field  •  [D] Database Lookup"
            )
        else:
            instruction_text = "[S]end Order  •  [B]ack  •  [Enter] Edit Field"

        content_width = max(
            max_field_len + max_value_len + 20,
            len(title) + 10,  # Title
            len(instruction_text) + 10,  # Instructions
        )

        box_width = min(width - 6, max(70, content_width))
        box_height = min(height - 4, len(fields) + 12)  # More space for better layout
        box_x = (width - box_width) // 2
        box_y = (height - box_height) // 2

        # Draw main box with enhanced border
        draw_border(stdscr, box_y, box_x, box_height, box_width, title, Colors.HEADER)

        # Header section with improved spacing
        try:
            # Instructions with better visibility
            instructions_y = box_y + 2
            instruction_color = curses.color_pair(Colors.INFO) | curses.A_BOLD
            instructions_centered = center_string(instruction_text, box_width - 4)
            stdscr.addstr(
                instructions_y, box_x + 2, instructions_centered, instruction_color
            )

            # Separator line for visual separation
            separator_y = box_y + 3
            stdscr.addstr(
                separator_y,
                box_x + 1,
                Symbols.HORIZONTAL_LINE * (box_width - 2),
                curses.color_pair(Colors.BORDER),
            )
        except curses.error:
            pass

        # Enhanced field display section
        field_start_y = box_y + 5  # More space after header
        for idx, field in enumerate(fields):
            y_pos = field_start_y + idx
            if y_pos >= box_y + box_height - 5:  # Leave more space for footer
                break

            value = str(values.get(field, ""))

            # Enhanced field formatting with better visual hierarchy
            field_num = f"{idx + 1:2d}"
            field_name = field

            # Calculate available space more intelligently
            field_section_width = (box_width - 8) // 2
            value_section_width = box_width - field_section_width - 12

            field_display = truncate_text(field_name, field_section_width - 5)
            value_display = truncate_text(value, value_section_width) if value else "─"

            if idx == current_row:
                # Enhanced highlighting for selected field
                try:
                    # Selection indicator with number
                    stdscr.addstr(
                        y_pos,
                        box_x + 2,
                        f"{Symbols.ARROW_RIGHT}",
                        curses.color_pair(Colors.SELECTED) | curses.A_BOLD,
                    )
                    stdscr.addstr(
                        y_pos,
                        box_x + 4,
                        field_num,
                        curses.color_pair(Colors.SELECTED) | curses.A_BOLD,
                    )
                    stdscr.addstr(
                        y_pos,
                        box_x + 7,
                        f". {field_display}:",
                        curses.color_pair(Colors.SELECTED) | curses.A_BOLD,
                    )
                    # Value with different color for better contrast
                    stdscr.addstr(
                        y_pos,
                        box_x + 11 + len(field_display),  # Added more spacing
                        f" {value_display}",  # Added space before value
                        curses.color_pair(Colors.WARNING) | curses.A_BOLD,
                    )
                except curses.error:
                    pass
            else:
                # Normal field display with improved readability
                try:
                    # Field number in subdued color
                    stdscr.addstr(
                        y_pos, box_x + 4, field_num, curses.color_pair(Colors.INFO)
                    )
                    # Field name
                    stdscr.addstr(
                        y_pos,
                        box_x + 7,
                        f". {field_display}:",
                        curses.color_pair(Colors.TEXT),
                    )
                    # Value with slight emphasis
                    stdscr.addstr(
                        y_pos,
                        box_x + 11 + len(field_display),  # Added more spacing
                        f" {value_display}",  # Added space before value
                        curses.color_pair(Colors.HEADER),
                    )
                except curses.error:
                    pass

        # Enhanced footer section with better spacing and visibility
        footer_start_y = box_y + box_height - 4

        # Separator line before footer
        try:
            stdscr.addstr(
                footer_start_y - 1,
                box_x + 1,
                Symbols.HORIZONTAL_LINE * (box_width - 2),
                curses.color_pair(Colors.BORDER),
            )
        except curses.error:
            pass

        # Enhanced database indicator with better positioning
        if enable_db_lookup and current_row < len(fields):
            field = fields[current_row]
            # Define which fields support database lookup
            db_lookup_fields = {
                "Container Type": "Database lookup: Container types",
                "Product Code": "Database lookup: Product codes and names",
                "Product Name": "Database lookup: Product codes and names",
                "Processing Mode": "Select processing mode",
            }

            if field in db_lookup_fields:
                # Special handling for Processing Mode in transport orders
                if field == "Processing Mode" and "Transport" in title:
                    db_indicator = (
                        "Press [Enter] to select processing mode (standard pre-filled)"
                    )
                else:
                    db_indicator = (
                        f"[D] {db_lookup_fields[field]} • [Enter] Edit manually"
                    )

                db_indicator_truncated = truncate_text(db_indicator, box_width - 4)
                try:
                    stdscr.addstr(
                        footer_start_y,
                        box_x + 2,
                        db_indicator_truncated,
                        curses.color_pair(Colors.INFO) | curses.A_DIM,
                    )
                except curses.error:
                    pass
                except curses.error:
                    pass

        # Status bar
        show_status(stdscr, f"Editing field: {fields[current_row]}", "info")
        stdscr.refresh()

        key = stdscr.getch()

        if key in (curses.KEY_UP, ord("k")) and current_row > 0:
            current_row -= 1
        elif key in (curses.KEY_DOWN, ord("j")) and current_row < len(fields) - 1:
            current_row += 1
        elif key == ord("s") or key == ord("S"):
            show_status(stdscr, "Saving configuration...", "success")
            stdscr.refresh()
            time.sleep(0.5)
            return values
        elif key in (ord("b"), ord("B"), ord("h")):
            return None
        elif key in (ord("d"), ord("D")) and enable_db_lookup:
            # Handle database lookup
            field = fields[current_row]
            # Disable D key for Processing Mode in transport orders
            if field == "Processing Mode" and "Transport" in title:
                show_status(
                    stdscr,
                    "Use [Enter] to select processing mode for transport orders",
                    "info",
                )
                stdscr.refresh()
                time.sleep(1.5)
            else:
                _handle_database_lookup(stdscr, field, values)
        elif key in (curses.KEY_ENTER, 10, 13, ord("l")):  # Enter
            field_name = fields[current_row]

            # Special handling for Processing Mode field
            if field_name == "Processing Mode":
                _handle_processing_mode_selection(stdscr, values)
                continue

            current_value = str(values.get(field_name, ""))

            # Show input prompt
            show_status(stdscr, f"Editing {field_name} - Enter new value:", "info")
            stdscr.refresh()

            # Enable input
            curses.curs_set(1)
            curses.echo()

            try:
                prompt_y = box_y + box_height - 2
                prompt_x = box_x + 2

                # Clear input area
                stdscr.addstr(
                    prompt_y,
                    prompt_x,
                    " " * (box_width - 4),
                    curses.color_pair(Colors.TEXT),
                )
                stdscr.addstr(
                    prompt_y,
                    prompt_x,
                    f"{field_name}: ",
                    curses.color_pair(Colors.TEXT),
                )
                stdscr.addstr(
                    prompt_y,
                    prompt_x + len(field_name) + 2,
                    current_value,
                    curses.A_REVERSE,
                )
                stdscr.move(
                    prompt_y, prompt_x + len(field_name) + 2 + len(current_value)
                )
                stdscr.refresh()

                # Get user input
                new_value = (
                    stdscr.getstr(prompt_y, prompt_x + len(field_name) + 2, 40)
                    .decode("utf-8")
                    .strip()
                )

                if new_value or new_value == "":  # Allow empty values
                    values[field_name] = new_value
                    show_status(stdscr, f"Updated {field_name}", "success")
                    stdscr.refresh()
                    time.sleep(0.3)

            except KeyboardInterrupt:
                show_status(stdscr, "Edit cancelled", "warning")
                stdscr.refresh()
                time.sleep(0.3)
            finally:
                curses.noecho()
                curses.curs_set(0)


def _handle_database_lookup(stdscr, field: str, values: Dict[str, Any]) -> None:
    """Handle database lookups for specific fields."""
    from models.database import Database
    from models.config import Config

    # Special handling for Processing Mode field
    if field == "Processing Mode":
        _handle_processing_mode_selection(stdscr, values)
        return

    try:
        config_manager = Config()
        config = config_manager.load()
        osrid = config_manager.resolve_osr(config)

        # Check if OSR ID is configured, if not prompt to configure it
        if not osrid:
            from ui.dialog import display_dialog

            # Ask user if they want to configure OSR ID now
            dialog_result = display_dialog(
                stdscr,
                "OSR ID is required for database access.\n\nWould you like to configure it now?",
                "Configuration Required",
                "question",
                show_yes_no=True,
            )

            if dialog_result:  # User chose Yes
                from controllers.config_controller import ConfigController

                config_controller = ConfigController()
                config_controller.configure_osr_id(stdscr, config, config_manager)

                # Reload config to get the new OSR ID
                config = config_manager.load()
                osrid = config_manager.resolve_osr(config)

                if not osrid:
                    show_status(stdscr, "OSR ID configuration cancelled", "warning")
                    stdscr.refresh()
                    time.sleep(2)
                    return
            else:
                show_status(
                    stdscr, "Database access requires OSR ID configuration", "info"
                )
                stdscr.refresh()
                time.sleep(2)
                return

        db = Database(osrid)

        if field == "Container Type":
            try:
                container_types = db.get_container_types()
                if container_types:
                    options = [ct[0] for ct in container_types]
                    selected_idx = display_menu(
                        stdscr,
                        options,
                        title="Select Container Type:",
                        instructions="Choose from available container types",
                    )
                    if selected_idx is not None:
                        values[field] = options[selected_idx]
                else:
                    show_status(
                        stdscr, "No container types found in database", "warning"
                    )
                    stdscr.refresh()
                    time.sleep(2)
            except Exception as e:
                show_status(stdscr, f"Database error: {str(e)}", "error")
                stdscr.refresh()
                time.sleep(2)

        elif field in ["Product Code", "Product Name"]:
            try:
                products = db.get_products_for_goods_in()  # Using the combined method
                if products:
                    # Create display options showing both name and code
                    options = [f"{prod[0]} ({prod[1]})" for prod in products]
                    selected_idx = display_menu(
                        stdscr,
                        options,
                        title="Select Product:",
                        instructions="Choose from available products",
                    )
                    if selected_idx is not None:
                        selected_product = products[selected_idx]
                        values["Product Name"] = selected_product[0]
                        values["Product Code"] = selected_product[1]
                else:
                    show_status(stdscr, "No products found in database", "warning")
                    stdscr.refresh()
                    time.sleep(2)
            except Exception as e:
                show_status(stdscr, f"Database error: {str(e)}", "error")
                stdscr.refresh()
                time.sleep(2)
        else:
            show_status(stdscr, f"No database lookup available for {field}", "info")
            stdscr.refresh()
            time.sleep(1.5)

    except Exception as e:
        show_status(stdscr, f"Database connection error: {str(e)}", "error")
        stdscr.refresh()
        time.sleep(2)


def _handle_processing_mode_selection(stdscr, values: Dict[str, Any]) -> None:
    """Handle processing mode selection for transport orders."""
    from config.constants import TRANSPORT_PROCESSING_MODES, TRANSPORT_MODE_DESCRIPTIONS

    # Create user-friendly options with descriptions
    options = []
    current_mode = values.get("Processing Mode", "standard")

    # Ensure the field is set to default if empty
    if not current_mode:
        current_mode = "standard"
        values["Processing Mode"] = current_mode

    for mode in TRANSPORT_PROCESSING_MODES:
        description = TRANSPORT_MODE_DESCRIPTIONS.get(mode, mode)
        if mode == current_mode:
            option_text = f"● {description}"  # Mark current selection
        else:
            option_text = f"  {description}"
        options.append(option_text)

    # Show processing mode selection menu
    selected_idx = display_menu(
        stdscr,
        options=options,
        title="🚚 Select Transport Processing Mode",
        instructions="Choose processing mode • Current selection marked with ●",
    )

    if selected_idx is not None:
        selected_mode = TRANSPORT_PROCESSING_MODES[selected_idx]
        values["Processing Mode"] = selected_mode
        show_status(stdscr, f"Processing mode set to: {selected_mode}", "success")
        stdscr.refresh()
        time.sleep(0.8)
