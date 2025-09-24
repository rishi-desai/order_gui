"""
Default configuration and templates for the OSR Order GUI application.
"""

from .constants import OrderMode, ServerType


# Default values for order fields
DEFAULT_ORDER_VALUES = {
    "first_run": True,
    "name": "src",
    "server_type": ServerType.LIVE,
    "sandbox_custom_elements": [],
    OrderMode.PICK_STANDARD: [
        {
            "Order Number": "1",
            "Container / Tray Number": "T925001",
            "Quantity": "10",
            "Product Code": "test01",
            "Product Name": "Test-Product-1",
        }
    ],
    OrderMode.PICK_MANUAL: [
        {
            "Order Number": "1",
            "Quantity": "10",
            "Product Code": "test01",
            "Product Name": "Test-Product-1",
        }
    ],
    OrderMode.INVENTORY: {
        "Order Number": "1",
        "Container / Tray Number": "T925001",
        "Product Code": "test01",
    },
    OrderMode.GOODS_IN: {
        "Order Number": "1",
        "Container / Tray Number": "T925001",
        "Container Type": "full",
        "Quantity": "10",
        "Product Code": "test01",
        "Product Name": "Test-Product-1",
    },
    OrderMode.GOODS_ADD: {
        "Order Number": "1",
        "Quantity": "10",
        "Product Code": "test01",
        "Product Name": "Test-Product-1",
    },
    OrderMode.TRANSPORT: [
        {
            "Order Number": "1",
            "New Owner": "SRC",
            "Owner": "SRC",
            "Target Zone": "CIRCULATION",
            "Container Number": "T925001",
            "Container Type": "OSR_EVO",
            "Compartment Type": "full",
            "Slot Number": "1",
            "Quantity": "10",
            "Product Code": "test01",
            "Product Name": "Test-Product-1",
        }
    ],
}

# Field ordering for different order types
FIELD_ORDER = {
    OrderMode.PICK_STANDARD: [
        "Quantity",
        "Container / Tray Number",
        "Product Code",
        "Product Name",
        "Order Number",
        "name",
    ],
    OrderMode.PICK_MANUAL: [
        "Quantity",
        "Product Code",
        "Product Name",
        "Order Number",
        "name",
    ],
    OrderMode.INVENTORY: [
        "Container / Tray Number",
        "Product Code",
        "Order Number",
        "name",
    ],
    OrderMode.GOODS_IN: [
        "Quantity",
        "Container / Tray Number",
        "Product Code",
        "Product Name",
        "Container Type",
        "Order Number",
        "name",
    ],
    OrderMode.GOODS_ADD: [
        "Quantity",
        "Product Code",
        "Product Name",
        "Order Number",
        "name",
    ],
    OrderMode.TRANSPORT: [
        "Quantity",
        "Container Number",
        "Product Code",
        "Product Name",
        "Target Zone",
        "Container Type",
        "Compartment Type",
        "New Owner",
        "Owner",
        "Slot Number",
        "Order Number",
        "name",
    ],
}

# XML Templates for order generation
XML_TEMPLATES = {
    OrderMode.PICK_STANDARD: """
    <host2osr>
        <pick_order order_number="{name}-pick-{Order Number}" container_number="{Container / Tray Number}" processing_mode="standard">
            {lines}
        </pick_order>
    </host2osr>
    """,
    OrderMode.PICK_MANUAL: """
    <host2osr>
        <pick_order order_number="{name}-pick-manual-{Order Number}" processing_mode="manual">
            {lines}
        </pick_order>
    </host2osr>
    """,
    OrderMode.INVENTORY: """
    <host2osr>
        <inventory_order order_number="{name}-inv-{Order Number}" processing_mode="standard" container_number="{Container / Tray Number}">
            <product product_code="{Product Code}" />
        </inventory_order>
    </host2osr>
    """,
    OrderMode.GOODS_IN: """
    <host2osr>
        <goods_in_order order_number="{name}-goods-in-{Order Number}" compartment_number="{Container / Tray Number}" compartment_type="{cont_type}" processing_mode="standard">
            <goods_in_order_line quantity_advertised="{Quantity}">
                <product product_code="{Product Code}" name="{Product Name}" returned="false" bundle_size="1">
                    {capacity_specs}
                </product>
            </goods_in_order_line>
        </goods_in_order>
    </host2osr>
    """,
    OrderMode.GOODS_ADD: """
    <host2osr>
        <goods_in_order order_number="{name}-goods-add-{Order Number}" processing_mode="renewal">
            <goods_in_order_line quantity_advertised="{Quantity}">
                <product product_code="{Product Code}" name="{Product Name}" returned="false" bundle_size="1">
                    {capacity_specs}
                </product>
            </goods_in_order_line>
        </goods_in_order>
    </host2osr>
    """,
    OrderMode.TRANSPORT: """
    <host2osr>
        <transport_order order_number="{name}-transport-{Order Number}" processing_mode="standard" preannouncement="true" new_owner="{New Owner}" requires_route_assistance="false">
            <transport_order_line target_zone="{Target Zone}"/>
            <container container_number="{Container Number}" container_type="{Container Type}" compartment_type="{Compartment Type}" owner="{Owner}">
                {slot_contents}
            </container>
        </transport_order>
    </host2osr>
    """,
}

# Line templates for pick orders
LINE_TEMPLATES = {
    OrderMode.PICK_STANDARD: """
            <pick_order_line quantity="{Quantity}" target_slot="1">
                <product product_code="{Product Code}" name="{Product Name}" returned="false"/>
            </pick_order_line>
        """,
    OrderMode.PICK_MANUAL: """
            <pick_order_line quantity="{Quantity}">
                <product product_code="{Product Code}" name="{Product Name}" />
            </pick_order_line>
        """,
    OrderMode.TRANSPORT: """
                <slot_contents slot_number="{Slot Number}">
                    <inventory_order_line current_expected_quantity="{Quantity}">
                        <product product_code="{Product Code}" name="{Product Name}" bundle_size="1">
                        </product>
                    </inventory_order_line>
                </slot_contents>
        """,
}
