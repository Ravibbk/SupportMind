import csv
import sys
from pathlib import Path

# Ensure backend directory is in sys.path for direct CLI script execution
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.models import get_db_connection, init_db

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ORDERS_CSV = BASE_DIR / "data" / "orders.csv"


def seed_orders(csv_path: Path | None = None, db_path: Path | None = None) -> int:
    """Read orders.csv and insert into SQLite orders table using safe parameterized queries."""
    init_db(db_path)
    path = csv_path or ORDERS_CSV

    if not path.exists():
        raise FileNotFoundError(f"orders.csv not found at {path}")

    orders = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            orders.append((
                row["order_id"],
                row["customer_name"],
                row["email"],
                row["product_title"],
                float(row["price_usd"]),
                row["status"],
                row["order_date"],
                row["expected_delivery"],
                row["carrier"]
            ))

    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT OR REPLACE INTO orders (
            order_id, customer_name, email, product_title, price_usd,
            status, order_date, expected_delivery, carrier
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, orders)

    conn.commit()
    conn.close()
    return len(orders)


if __name__ == "__main__":
    count = seed_orders()
    print(f"Successfully seeded {count} orders into SQLite database.")
