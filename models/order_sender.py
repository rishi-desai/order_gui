"""Order sending via CORBA to OSR system."""

import sys
import subprocess
import re
from typing import Tuple

try:
    from omniORB import CORBA, PortableServer
    import OSR, OSR__POA
    import GCS, GCS__POA
    import CosNaming

    CORBA_AVAILABLE = True
except ImportError:
    CORBA_AVAILABLE = False

from utils.exceptions import ORBConnectionError, OrderValidationError


class OrderSender:
    """Handles sending orders via CORBA to OSR system."""

    def __init__(self, osrid: str, dry_run: bool = False):
        self.osrid = osrid
        self.dry_run = dry_run

    def send(self, xml: str) -> None:
        """Send order XML to OSR system via CORBA."""
        if not xml or not xml.strip():
            raise OrderValidationError("Order XML cannot be empty")

        if self.dry_run:
            return

        if not CORBA_AVAILABLE:
            raise ORBConnectionError("CORBA libraries not available")

        try:
            orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
            obj = orb.resolve_initial_references("NameService")
            rootContext = obj._narrow(CosNaming.NamingContext)

            gcsName = [CosNaming.NameComponent("GCS", "")]
            gcs_obj = rootContext.resolve(gcsName)
            gcs = gcs_obj._narrow(GCS.NamingContext)

            # Get Oracle configuration
            ocfg = gcs.resolve([self.osrid, "oracle"])

            # Resolve service port
            name = [
                CosNaming.NameComponent(self.osrid, ""),
                CosNaming.NameComponent("ServicePorts", ""),
                CosNaming.NameComponent("Hio", ""),
            ]
            sobj = rootContext.resolve(name)
            servant = sobj._narrow(OSR.Hio.ServicePort)

            # Send the order
            servant.sendOrder(xml)

        except Exception as e:
            raise ORBConnectionError(f"Failed to send order: {e}")


class OrderCanceller:
    """Handles order cancellation operations."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    def cancel_order(self, order_type: str, order_id: str) -> Tuple[bool, str]:
        """Cancel an order using the shell command."""
        if self.dry_run:
            return True, "Dry run - order would be cancelled"

        try:
            # Build the shell command using global send_cancel command
            command = (
                f"send_cancel --typ {order_type} --order-id {order_id} --really-send"
            )

            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            # Check if command succeeded
            if result.returncode == 0:
                return True, "Success"
            else:
                error_msg = f"Command failed (exit code {result.returncode})"
                if result.stderr.strip():
                    error_msg += f": {result.stderr.strip()}"
                if result.stdout.strip():
                    error_msg += f" | stdout: {result.stdout.strip()}"
                return False, error_msg

        except Exception as e:
            return False, f"Exception: {str(e)}"


def extract_order_id_from_xml(xml_content: str) -> str:
    """Extract order ID from XML content."""
    match = re.search(r'order_number="([^"]+)"', xml_content)
    return match.group(1) if match else "unknown"


def get_order_type_from_xml(xml_content: str) -> str:
    """Extract order type from XML content and return proper OrderMode constant."""
    from config.constants import OrderMode

    # Make order type detection more robust by checking for main order elements
    # Check more specific patterns first, then more general ones
    # Use space or > to ensure we're matching actual element starts

    if "<transport_order " in xml_content or "<transport_order>" in xml_content:
        return OrderMode.TRANSPORT
    elif "<pick_order " in xml_content or "<pick_order>" in xml_content:
        # Determine if it's standard or manual pick based on container presence
        if "container_number=" in xml_content:
            return OrderMode.PICK_STANDARD
        else:
            return OrderMode.PICK_MANUAL
    elif (
        "<goods_in_order " in xml_content and 'processing_mode="renewal"' in xml_content
    ):
        return OrderMode.GOODS_ADD
    elif "<goods_in_order " in xml_content or "<goods_in_order>" in xml_content:
        return OrderMode.GOODS_IN
    elif "<inventory_order " in xml_content or "<inventory_order>" in xml_content:
        return OrderMode.INVENTORY
    else:
        return "unknown"
