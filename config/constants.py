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


ORDER_TYPES = [
    OrderMode.PICK_STANDARD,
    OrderMode.PICK_MANUAL,
    OrderMode.INVENTORY,
    OrderMode.GOODS_IN,
    OrderMode.GOODS_ADD,
]


class ServerType:
    """Enumeration of server types."""

    LIVE = "Live"
    TEST = "Test"


SERVER_TYPES = [
    ServerType.LIVE,
    ServerType.TEST,
]


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


class Symbols:
    """ASCII-safe symbols for universal terminal compatibility."""

    # Navigation
    ARROW_RIGHT = ">"
    ARROW_LEFT = "<"
    ARROW_UP = "^"
    ARROW_DOWN = "v"

    # Status indicators
    CHECK = "+"
    CROSS = "-"
    SUCCESS = "OK"
    ERROR = "ERR"
    WARNING = "!"
    INFO = "i"

    # UI elements
    BULLET = "*"
    STAR = "*"
    CONFIRM = "?"
    KEY = ">"
    EDIT = "="
    MENU = "="
    SETTINGS = "@"

    # Selection boxes
    BOX_EMPTY = "[ ]"
    BOX_CHECKED = "[*]"

    # Order tracking
    CLOCK = "T"
    BACK = "<"
    REFRESH = "R"
    ID = "#"
    TYPE = "T"
    OSR = "O"
    STATUS = "S"
    TIME = "@"
    QUESTION = "?"

    # Box drawing
    HORIZONTAL_LINE = "─"
    VERTICAL_LINE = "│"
    TOP_LEFT = "┌"
    TOP_RIGHT = "┐"
    BOTTOM_LEFT = "└"
    BOTTOM_RIGHT = "┘"
