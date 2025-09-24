"""
XML generation for OSR orders.
"""

from typing import Dict, Any, List

from config.constants import OrderMode
from config.defaults import XML_TEMPLATES, LINE_TEMPLATES
from utils.exceptions import OrderValidationError


class OrderXML:
    """Handles XML generation for different order types."""

    @staticmethod
    def generate(order_data: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Generate XML for an order based on order data and configuration."""
        mode = order_data.get("mode")
        values = order_data.get("values")
        lines = order_data.get("lines")

        if not mode or mode not in XML_TEMPLATES:
            raise OrderValidationError(f"Invalid or missing order mode: {mode}")
        if not values:
            raise OrderValidationError("Order values are required")

        try:
            if mode in [OrderMode.PICK_STANDARD, OrderMode.PICK_MANUAL]:
                return OrderXML._generate_pick_order(mode, values, lines)
            elif mode == OrderMode.INVENTORY:
                return OrderXML._generate_inventory_order(values)
            elif mode == OrderMode.GOODS_IN:
                return OrderXML._generate_goods_in_order(values, config)
            elif mode == OrderMode.GOODS_ADD:
                return OrderXML._generate_goods_add_order(values, config)
            elif mode == OrderMode.TRANSPORT:
                return OrderXML._generate_transport_order(mode, values, lines)
        except KeyError as e:
            raise OrderValidationError(f"Missing required field in order data: {e}")
        except Exception as e:
            raise OrderValidationError(f"Error generating XML: {e}")

    @staticmethod
    def _generate_pick_order(
        mode: str, values_list: List[Dict], lines: List[Dict] = None
    ) -> str:
        """Generate XML for pick orders."""
        if not values_list or not isinstance(values_list, list):
            raise OrderValidationError("Pick orders require a list of values")

        lines_xml = ""
        template = LINE_TEMPLATES[mode]

        for values in values_list:
            lines_xml += template.format(**values)

        order_values = values_list[0]
        return XML_TEMPLATES[mode].format(lines=lines_xml, **order_values).strip()

    @staticmethod
    def _generate_inventory_order(values: Dict) -> str:
        """Generate XML for inventory orders."""
        return XML_TEMPLATES[OrderMode.INVENTORY].format(**values).strip()

    @staticmethod
    def _generate_goods_in_order(values: Dict, config: Dict) -> str:
        """Generate XML for goods-in orders."""
        values = values.copy()
        values["cont_type"] = values.get("Container Type", "full")
        capacity_specs = OrderXML._generate_capacity_specs(values, config)
        values["capacity_specs"] = capacity_specs
        return XML_TEMPLATES[OrderMode.GOODS_IN].format(**values).strip()

    @staticmethod
    def _generate_goods_add_order(values: Dict, config: Dict) -> str:
        """Generate XML for goods-add orders."""
        capacity_specs = OrderXML._generate_capacity_specs(values, config)
        values["capacity_specs"] = capacity_specs
        return XML_TEMPLATES[OrderMode.GOODS_ADD].format(**values).strip()

    @staticmethod
    def _generate_capacity_specs(values: Dict, config: Dict) -> str:
        """Generate capacity specifications XML from configuration."""
        capacity_specs = ""
        config_capacity_specs = config.get("capacity_specs", {})

        if config_capacity_specs:
            for spec, max_qty in config_capacity_specs.items():
                capacity_specs += f'<capacity_spec compartment_type="{spec}" maximum_quantity="{max_qty}"/>'

        return capacity_specs

    @staticmethod
    def _generate_transport_order(
        mode: str, values_list: List[Dict], lines: List[Dict] = None
    ) -> str:
        """Generate XML for transport orders with multi-slot support."""
        if not values_list or not isinstance(values_list, list):
            raise OrderValidationError("Transport orders require a list of values")

        slot_contents_xml = ""
        template = LINE_TEMPLATES[mode]

        for values in values_list:
            slot_contents_xml += template.format(**values)

        order_values = values_list[0]
        order_values["slot_contents"] = slot_contents_xml
        return XML_TEMPLATES[mode].format(**order_values).strip()
