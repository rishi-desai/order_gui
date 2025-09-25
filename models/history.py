"""
Order history management.
"""

import json
import os
import time
from typing import List, Dict

from config.constants import ORDERS_HISTORY_FILE


class History:
    """Manages order history tracking and persistence."""

    @staticmethod
    def load() -> List[Dict[str, str]]:
        """Load order history from file."""
        try:
            if os.path.exists(ORDERS_HISTORY_FILE):
                with open(ORDERS_HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return []

    @staticmethod
    def save(orders: List[Dict[str, str]]) -> None:
        """Save order history to file."""
        try:
            with open(ORDERS_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(orders, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    @staticmethod
    def add_order(
        order_id: str, order_type: str, osrid: str, status: str = "sent"
    ) -> None:
        """Add new order to history."""
        orders = History.load()

        order_record = {
            "order_id": order_id,
            "type": order_type,
            "osrid": osrid,
            "status": status,
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        orders.insert(0, order_record)  # Most recent first
        orders = orders[:100]  # Keep only last 100 orders
        History.save(orders)

    @staticmethod
    def update_status(order_id: str, new_status: str) -> None:
        """Update order status in history."""
        orders = History.load()

        for order in orders:
            if order.get("order_id") == order_id:
                order["status"] = new_status
                order["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
                break

        History.save(orders)

    @staticmethod
    def get_active_orders(osrid: str) -> List[Dict[str, str]]:
        """Get active orders that can be cancelled."""
        orders = History.load()
        return [
            order
            for order in orders
            if (
                order.get("osrid") == osrid
                and order.get("status") in ["sent", "processing", "pending"]
                and order.get("status")
                not in ["cancelled", "cancelled_dry_run", "completed", "failed"]
            )
        ]

    @staticmethod
    def get_orders_for_osr(osrid: str) -> List[Dict[str, str]]:
        """Get all orders for a specific OSR ID."""
        orders = History.load()
        return [order for order in orders if order.get("osrid") == osrid]

    @staticmethod
    def get_last_order() -> Dict[str, str]:
        """Get the most recent order from history."""
        orders = History.load()
        if orders:
            last_order = orders[0]  # Most recent first
            return {
                "order_id": last_order.get("order_id"),
                "order_type": last_order.get("type"),
                "osrid": last_order.get("osrid"),
                "status": last_order.get("status"),
                "created": last_order.get("created"),
                "updated": last_order.get("updated"),
            }
        return {}
