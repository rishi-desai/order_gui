"""
Sandbox command generation for test server operations.
"""

import re
from typing import Optional, Dict, Any
from enum import Enum
import os
import subprocess


class SandboxAction(Enum):
    """Available sandbox actions."""

    INSERT_CARRIER = "insert"
    REMOVE_CARRIER = "remove"
    ENABLE_ELEMENT = "enable"
    DISABLE_ELEMENT = "disable"


class SandboxCommandGenerator:
    """Generates sandbox commands for test server operations."""

    def __init__(self, osrid: str):
        """Initialize with OSR ID (e.g., 'osr1', 'osr2')."""
        self.osrid = osrid.lower()
        if not self.osrid.startswith("osr"):
            self.osrid = f"osr{self.osrid}"

    def get_sim_prefix(self) -> str:
        """Get the simulator command prefix (e.g., 'simosr1', 'simosr2')."""
        return f"sim{self.osrid}"

    def generate_insert_command(self, element: str, carrier: str) -> str:
        """Generate command to insert a carrier into an element.

        Args:
            element: Qualified name of workflow element (e.g., 'workflow.element')
            carrier: Carrier identifier to insert

        Returns:
            Complete sandbox command string
        """
        sim_prefix = self.get_sim_prefix()
        return f"{sim_prefix} -i {element} {carrier}"

    def generate_remove_command(self, element: str, carrier: str) -> str:
        """Generate command to remove a carrier from an element.

        Args:
            element: Qualified name of workflow element
            carrier: Carrier identifier to remove

        Returns:
            Complete sandbox command string
        """
        sim_prefix = self.get_sim_prefix()
        return f"{sim_prefix} -r {element} {carrier}"

    def generate_enable_command(
        self, element: str, element_type: str = "element"
    ) -> str:
        """Generate command to enable an element, station, or gateway.

        Args:
            element: Qualified name of workflow element
            element_type: Type - 'element'/'e', 'station'/'s', or 'gateway'/'g'

        Returns:
            Complete sandbox command string
        """
        sim_prefix = self.get_sim_prefix()
        type_map = {
            "element": "e",
            "station": "s",
            "gateway": "g",
            "e": "e",
            "s": "s",
            "g": "g",
        }
        type_flag = type_map.get(element_type.lower(), "e")
        return f"{sim_prefix} --enable-element {type_flag} {element}"

    def generate_disable_command(
        self, element: str, element_type: str = "element"
    ) -> str:
        """Generate command to disable an element, station, or gateway.

        Args:
            element: Qualified name of workflow element
            element_type: Type - 'element'/'e', 'station'/'s', or 'gateway'/'g'

        Returns:
            Complete sandbox command string
        """
        sim_prefix = self.get_sim_prefix()
        type_map = {
            "element": "e",
            "station": "s",
            "gateway": "g",
            "e": "e",
            "s": "s",
            "g": "g",
        }
        type_flag = type_map.get(element_type.lower(), "e")
        return f"{sim_prefix} --disable-element {type_flag} {element}"

    def extract_carrier_from_xml(self, xml_content: str) -> Optional[str]:
        """Extract carrier/container/tray information from order XML for insertion commands.

        Args:
            xml_content: XML content of the order

        Returns:
            Carrier identifier if found, None otherwise
        """
        # Look for container/tray/carrier references in XML
        # Prioritize most specific patterns first
        patterns = [
            r'container_id="([^"]+)"',  # Direct container_id attribute
            r'tray_id="([^"]+)"',  # Direct tray_id attribute
            r'carrier_id="([^"]+)"',  # Direct carrier_id attribute
            r'<container[^>]*id="([^"]+)"',  # Container with id attribute
            r'<tray[^>]*id="([^"]+)"',  # Tray with id attribute
            r'<carrier[^>]*id="([^"]+)"',  # Carrier with id attribute
            r"<container[^>]*>([^<]+)</container>",  # Container content
            r"<tray[^>]*>([^<]+)</tray>",  # Tray content
            r"<carrier[^>]*>([^<]+)</carrier>",  # Carrier content
            r'id="([^"]+)".*(?:container|tray|carrier)',  # ID near container/tray/carrier
        ]

        for pattern in patterns:
            match = re.search(pattern, xml_content, re.IGNORECASE)
            if match:
                carrier_id = match.group(1).strip()
                # Skip empty or placeholder values
                if carrier_id and carrier_id.lower() not in [
                    "",
                    "none",
                    "null",
                    "undefined",
                ]:
                    return carrier_id

        return None

    def generate_insertion_commands_for_order(
        self, xml_content: str, default_element: str = None
    ) -> Dict[str, str]:
        """Generate insertion commands for an order.

        Args:
            xml_content: XML content of the order
            default_element: Default element to use if not extractable from XML

        Returns:
            Dictionary with command types as keys and commands as values
        """
        commands = {}

        # Extract carrier ID
        carrier = self.extract_carrier_from_xml(xml_content)
        if not carrier:
            # Generate a default carrier ID based on order
            order_id_match = re.search(r'order_number="([^"]+)"', xml_content)
            if order_id_match:
                carrier = f"carrier_{order_id_match.group(1)}"
            else:
                carrier = "carrier_test"

        # Use provided element or a reasonable default
        element = default_element or "workflow.input.station.01"

        # Generate basic insertion command
        commands["insert_now"] = self.generate_insert_command(element, carrier)

        # Generate remove command (for cleanup)
        commands["remove_later"] = self.generate_remove_command(element, carrier)

        return commands


def copy_to_clipboard(text):
    """
    Copy text to clipboard on Linux server.
    Returns True on success, False otherwise.
    """
    try:
        # Try xclip first (most common)
        if os.system("which xclip > /dev/null 2>&1") == 0:
            proc = subprocess.Popen(
                ["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE
            )
            proc.communicate(input=text.encode("utf-8"))
            return proc.returncode == 0

        # Try xsel as fallback
        if os.system("which xsel > /dev/null 2>&1") == 0:
            proc = subprocess.Popen(
                ["xsel", "--clipboard", "--input"], stdin=subprocess.PIPE
            )
            proc.communicate(input=text.encode("utf-8"))
            return proc.returncode == 0

        # Try wl-copy for Wayland
        if os.system("which wl-copy > /dev/null 2>&1") == 0:
            proc = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
            proc.communicate(input=text.encode("utf-8"))
            return proc.returncode == 0

        return False

    except Exception:
        return False
