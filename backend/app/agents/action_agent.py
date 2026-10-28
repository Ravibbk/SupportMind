"""Action Agent managing tool calling and Human-in-the-Loop approvals.

Supported Tools:
1. start_refund_request: Issues refund approval request (ALWAYS requires human approval).
2. create_ticket: Logs formal support escalation ticket (requires approval if urgency == 'high').
3. draft_email_reply: Formulates outbound communication to the customer.
"""

import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.db.models import get_db_connection


@dataclass
class ActionItem:
    """Represents an agent action requiring or completing execution."""

    action_id: str
    session_id: str
    action_type: str
    status: str  # 'pending_approval', 'approved', 'rejected', 'completed'
    requires_approval: bool
    payload: dict[str, Any]
    created_at: str
    resolved_at: str | None = None


class ActionAgent:
    """Agent executing tools with human-in-the-loop safeguards."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path

    def start_refund_request(
        self,
        session_id: str,
        order_id: str,
        amount: float,
        reason: str
    ) -> ActionItem:
        """Initiate a refund request. Mandates human approval before fund disbursement."""
        action_id = f"ACT-REF-{uuid.uuid4().hex[:8].upper()}"
        payload = {
            "order_id": order_id,
            "refund_amount_usd": round(amount, 2),
            "reason": reason,
            "initiated_by": "SupportMind ActionAgent"
        }
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        action = ActionItem(
            action_id=action_id,
            session_id=session_id,
            action_type="start_refund_request",
            status="pending_approval",
            requires_approval=True,
            payload=payload,
            created_at=now
        )
        self._save_action(action)
        return action

    def create_ticket(
        self,
        session_id: str,
        category: str,
        urgency: str,
        subject: str,
        description: str,
        customer_email: str | None = None
    ) -> ActionItem:
        """Create a customer support ticket. High urgency escalations mandate human approval."""
        ticket_id = f"TCK-{uuid.uuid4().hex[:8].upper()}"
        action_id = f"ACT-TCK-{uuid.uuid4().hex[:8].upper()}"
        requires_approval = urgency.lower() == "high"
        status = "pending_approval" if requires_approval else "completed"
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        payload = {
            "ticket_id": ticket_id,
            "category": category,
            "urgency": urgency,
            "subject": subject,
            "description": description,
            "customer_email": customer_email or "guest@novacart.com"
        }

        # 1. Insert into tickets table
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tickets (ticket_id, session_id, customer_email, category, urgency, status, subject, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ticket_id, session_id, customer_email, category, urgency, status, subject, description))
            conn.commit()
            conn.close()
        except Exception:
            pass

        # 2. Insert into actions table
        action = ActionItem(
            action_id=action_id,
            session_id=session_id,
            action_type="create_ticket",
            status=status,
            requires_approval=requires_approval,
            payload=payload,
            created_at=now
        )
        self._save_action(action)
        return action

    def draft_email_reply(
        self,
        session_id: str,
        recipient: str,
        subject: str,
        body: str
    ) -> ActionItem:
        """Draft a formal customer email response."""
        action_id = f"ACT-EML-{uuid.uuid4().hex[:8].upper()}"
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        payload = {
            "recipient": recipient,
            "subject": subject,
            "body": body
        }
        action = ActionItem(
            action_id=action_id,
            session_id=session_id,
            action_type="draft_email_reply",
            status="completed",
            requires_approval=False,
            payload=payload,
            created_at=now
        )
        self._save_action(action)
        return action

    def approve_action(self, action_id: str) -> dict[str, Any]:
        """Human approval callback: transitions action status to approved."""
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE actions
            SET status = 'approved', resolved_at = ?
            WHERE action_id = ?
        """, (now, action_id))
        conn.commit()

        # Fetch updated action
        cursor.execute("SELECT * FROM actions WHERE action_id = ?", (action_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {"status": "success", "action": dict(row)}
        return {"status": "error", "message": f"Action ID {action_id} not found."}

    def reject_action(self, action_id: str, reason: str | None = None) -> dict[str, Any]:
        """Human rejection callback: transitions action status to rejected."""
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE actions
            SET status = 'rejected', resolved_at = ?
            WHERE action_id = ?
        """, (now, action_id))
        conn.commit()

        cursor.execute("SELECT * FROM actions WHERE action_id = ?", (action_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {"status": "success", "action": dict(row), "reason": reason or "Rejected by human agent"}
        return {"status": "error", "message": f"Action ID {action_id} not found."}

    def get_pending_actions(self) -> list[dict[str, Any]]:
        """Fetch all currently pending actions requiring human decision."""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM actions
            WHERE status = 'pending_approval'
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _save_action(self, action: ActionItem) -> None:
        """Persist action state to SQLite."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO actions (
                    action_id, session_id, action_type, status,
                    payload_json, requires_approval, created_at, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                action.action_id,
                action.session_id,
                action.action_type,
                action.status,
                json.dumps(action.payload),
                1 if action.requires_approval else 0,
                action.created_at,
                action.resolved_at
            ))
            conn.commit()
            conn.close()
        except Exception:
            pass
