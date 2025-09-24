"""
Database management for the OSR Order GUI.
"""

import time
from typing import List, Tuple, Optional, Dict

# Import oracle module (assuming it's available)
try:
    import oracle
except ImportError:
    oracle = None

from utils.exceptions import DatabaseConnectionError


class Database:
    """Handles Oracle database connections and query operations."""

    def __init__(self, osrid: str, retries: int = 3, delay: int = 2):
        self.osrid = osrid
        self.retries = retries
        self.delay = delay

    def connect(self):
        """Connect to Oracle database with retry logic."""
        if oracle is None:
            raise DatabaseConnectionError("Oracle module not available")

        for attempt in range(self.retries):
            try:
                return oracle.login(self.osrid)
            except Exception as e:
                if attempt < self.retries - 1:
                    time.sleep(self.delay)
                else:
                    raise DatabaseConnectionError(
                        f"Failed to connect to Oracle database after {self.retries} attempts: {e}"
                    )

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Tuple]:
        """Execute database query with error handling."""
        try:
            db = self.connect()
            cursor = db.cursor()
            cursor.execute(query, params or {})
            results = cursor.fetchall()
            db.close()
            return results
        except Exception as e:
            raise DatabaseConnectionError(f"Database query error: {e}")

    def get_products_for_pick(self) -> List[Tuple]:
        """Get products available for picking orders."""
        query = """
            SELECT DISTINCT p.pri_name, p.pri_code, SUM(s.scnt_unreserved)
            FROM slot_contents s
            JOIN product_infos p ON s.scnt_pri_id = p.pri_id
            WHERE s.scnt_slot_tray_osr_id = :osrid
            AND s.scnt_unreserved > 0
            GROUP BY p.pri_name, p.pri_code
            ORDER BY p.pri_name
        """
        return self.execute_query(query, {"osrid": self.osrid})

    def get_products_for_inventory(self) -> List[Tuple]:
        """Get products available for inventory orders."""
        query = """
            SELECT p.pri_name, p.pri_code, s.scnt_slot_tray_id, s.scnt_slot_type
            FROM slot_contents s
            JOIN trays t ON s.scnt_slot_tray_id = t.tray_id
            JOIN product_infos p ON s.scnt_pri_id = p.pri_id
            WHERE s.scnt_slot_tray_osr_id = :osrid
            AND s.scnt_unreserved > 0
            ORDER BY p.pri_name
        """
        return self.execute_query(query, {"osrid": self.osrid})

    def get_products_for_goods_in(self) -> List[Tuple]:
        """Get products available for goods-in orders."""
        query = (
            "SELECT DISTINCT pri_name, pri_code FROM product_infos ORDER BY pri_name"
        )
        return self.execute_query(query)
