"""Data Agent for Order History, Tracking, and Fulfillment lookups.

Executes strictly parameterized SQLite queries to protect against SQL injection.
Never executes raw or model-generated SQL strings.
"""

import re
from pathlib import Path
from typing import Any

from app.db.models import get_db_connection

ORDER_ID_REGEX = re.compile(r"\bORD-\d{5}\b", re.IGNORECASE)
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")


class DataAgent:
    """Agent executing safe parameterized database queries for order data."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path

    def lookup_order_by_id(self, order_id: str) -> dict[str, Any] | None:
        """Fetch a single order by Order ID using parameterized SQL."""
        clean_id = order_id.strip().upper()
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT order_id, customer_name, email, product_title, price_usd,
                   status, order_date, expected_delivery, carrier
            FROM orders
            WHERE UPPER(order_id) = ?
        """, (clean_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def lookup_orders_by_email(self, email: str, limit: int = 5) -> list[dict[str, Any]]:
        """Fetch orders associated with a customer email using parameterized SQL."""
        clean_email = email.strip().lower()
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT order_id, customer_name, email, product_title, price_usd,
                   status, order_date, expected_delivery, carrier
            FROM orders
            WHERE LOWER(email) = ?
            ORDER BY order_date DESC
            LIMIT ?
        """, (clean_email, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def handle_query(self, query: str) -> dict[str, Any]:
        """Parse order identifiers from query, query SQLite, and formulate response.

        Returns:
            Dict containing answer, order_data, tool_name, and confidence.
        """
        # Try extracting Order ID first
        id_match = ORDER_ID_REGEX.search(query)
        if id_match:
            order_id = id_match.group(0).upper()
            order = self.lookup_order_by_id(order_id)
            if order:
                answer = (
                    f"Order **{order['order_id']}** for **{order['product_title']}** (${order['price_usd']:.2f}) "
                    f"is currently **{order['status']}**. "
                    f"It was placed on {order['order_date']} with carrier **{order['carrier']}**. "
                    f"Estimated delivery date is **{order['expected_delivery']}**."
                )
                return {
                    "answer": answer,
                    "order_data": [order],
                    "tool_called": "lookup_order_by_id",
                    "confidence": 1.0,
                    "found": True
                }
            else:
                return {
                    "answer": f"I checked our database, but could not find an order matching **{order_id}**. Please double-check your Order ID.",
                    "order_data": [],
                    "tool_called": "lookup_order_by_id",
                    "confidence": 0.90,
                    "found": False
                }

        # Try extracting Email
        email_match = EMAIL_REGEX.search(query)
        if email_match:
            email = email_match.group(0).lower()
            orders = self.lookup_orders_by_email(email)
            if orders:
                summary_lines = [
                    f"- **{o['order_id']}**: {o['product_title']} (${o['price_usd']:.2f}) — Status: **{o['status']}** (Carrier: {o['carrier']})"
                    for o in orders
                ]
                answer = f"Found {len(orders)} order(s) for **{email}**:\n" + "\n".join(summary_lines)
                return {
                    "answer": answer,
                    "order_data": orders,
                    "tool_called": "lookup_orders_by_email",
                    "confidence": 0.98,
                    "found": True
                }
            else:
                return {
                    "answer": f"No orders found matching the email address **{email}**.",
                    "order_data": [],
                    "tool_called": "lookup_orders_by_email",
                    "confidence": 0.85,
                    "found": False
                }

        return {
            "answer": "To look up your order details, please provide your **Order ID** (e.g. `ORD-10025`) or your registered **account email address**.",
            "order_data": [],
            "tool_called": "none",
            "confidence": 0.70,
            "found": False
        }
