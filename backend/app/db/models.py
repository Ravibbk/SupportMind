"""SQLite Database connection and table schemas for SupportMind.

Tables:
1. orders: Synchronized e-commerce orders from orders.csv
2. tickets: Customer support tickets
3. actions: Pending and executed agentic actions (requiring human approval)
4. traces: Observability traces of agent execution, tools called, latency, and cost
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "supportmind.db"


def get_db_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Create and return a SQLite database connection with row factory."""
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path | None = None) -> None:
    """Initialize database tables with strict parameterized schemas."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # 1. Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            product_title TEXT NOT NULL,
            price_usd REAL NOT NULL,
            status TEXT NOT NULL,
            order_date TEXT NOT NULL,
            expected_delivery TEXT NOT NULL,
            carrier TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_email ON orders(email)")

    # 2. Tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            customer_email TEXT,
            category TEXT NOT NULL,
            urgency TEXT NOT NULL,
            status TEXT NOT NULL, -- 'open', 'pending_approval', 'resolved'
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Actions table (Human-in-the-loop approval workflow)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            action_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            action_type TEXT NOT NULL, -- 'start_refund_request', 'create_ticket', 'draft_email_reply'
            status TEXT NOT NULL,      -- 'pending_approval', 'approved', 'rejected', 'completed'
            payload_json TEXT NOT NULL,
            requires_approval INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP
        )
    """)

    # 4. Observability Traces table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traces (
            trace_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            agent_chosen TEXT NOT NULL,
            tools_called TEXT,
            prompt_version TEXT,
            retrieved_chunks_count INTEGER DEFAULT 0,
            latency_ms REAL NOT NULL,
            token_count INTEGER DEFAULT 0,
            estimated_cost_usd REAL DEFAULT 0.0,
            critic_flagged INTEGER DEFAULT 0,
            critic_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully.")
