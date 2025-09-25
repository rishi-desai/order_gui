"""
Constants and enumerations for the OSR Order GUI application.
"""

import os


# Application metadata
APP_NAME = "OSR Order GUI"
APP_VERSION = "1.0.0"

# File paths
CONFIG_FILE = os.path.expanduser("./.orders_config.json")
ORDERS_HISTORY_FILE = os.path.expanduser("./.orders_history.json")


class OrderMode:
    """Enumeration of available order processing modes."""

    PICK_STANDARD = "Pick Standard"
    PICK_MANUAL = "Pick Manual"
    INVENTORY = "Inventory"
    GOODS_IN = "Goods In"
    GOODS_ADD = "Goods Add"
    TRANSPORT = "Transport"


ORDER_TYPES = [
    OrderMode.PICK_STANDARD,
    OrderMode.PICK_MANUAL,
    OrderMode.INVENTORY,
    OrderMode.GOODS_IN,
    OrderMode.GOODS_ADD,
    OrderMode.TRANSPORT,
]


class ServerType:
    """Enumeration of server types."""

    LIVE = "Live"
    TEST = "Test"


SERVER_TYPES = [
    ServerType.LIVE,
    ServerType.TEST,
]


class TransportProcessingMode:
    """Enumeration of available transport order processing modes."""

    STANDARD = "standard"
    DISPATCH = "dispatch"
    EMPTY_TRAY = "empty_tray"
    FIRST_HIT_IN_SEQUENCE = "first_hit_in_sequence"


TRANSPORT_PROCESSING_MODES = [
    TransportProcessingMode.STANDARD,
    TransportProcessingMode.DISPATCH,
    TransportProcessingMode.EMPTY_TRAY,
    TransportProcessingMode.FIRST_HIT_IN_SEQUENCE,
]

# User-friendly descriptions for transport processing modes
TRANSPORT_MODE_DESCRIPTIONS = {
    TransportProcessingMode.STANDARD: "Standard processing (default)",
    TransportProcessingMode.DISPATCH: "Dispatch mode - for outbound orders",
    TransportProcessingMode.EMPTY_TRAY: "Empty tray transport",
    TransportProcessingMode.FIRST_HIT_IN_SEQUENCE: "First hit in sequence processing",
}


class Colors:
    """Color constants for terminal display."""

    HEADER = 1
    TEXT = 2
    SELECTED = 3
    SUCCESS = 4
    ERROR = 5
    WARNING = 6
    INFO = 7
    BORDER = 8
    INPUT_BG = 9
    SECTION_HEADER = 10


class Symbols:
    """ASCII-safe symbols for universal terminal compatibility."""

    # Navigation arrows
    ARROW_RIGHT = ">"
    ARROW_LEFT = "<"
    ARROW_UP = "^"
    ARROW_DOWN = "v"

    # Selection boxes
    BOX_EMPTY = "[ ]"
    BOX_CHECKED = "[*]"

    # Box drawing
    HORIZONTAL_LINE = "─"
    VERTICAL_LINE = "│"
    TOP_LEFT = "╭"
    TOP_RIGHT = "╮"
    BOTTOM_LEFT = "╰"
    BOTTOM_RIGHT = "╯"
