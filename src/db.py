"""SQLite database layer for FII/DII data storage."""

import sqlite3
from datetime import datetime
from typing import Optional
from pathlib import Path

from src.config import DB_PATH


def _dict_factory(cursor, row):
    """Row factory that returns dicts instead of tuples."""
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}


def init_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Initialize SQLite database and return connection."""
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = _dict_factory
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fii_dii_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            buy_value REAL NOT NULL,
            sell_value REAL NOT NULL,
            net_value REAL NOT NULL,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, category)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_fii_dii_date
        ON fii_dii_data(date)
    """)
    conn.commit()
    return conn


def insert_record(conn: sqlite3.Connection, date: str, category: str,
                  buy_value: float, sell_value: float, net_value: float) -> None:
    """Insert or update a FII/DII record (upsert on date+category)."""
    conn.execute("""
        INSERT INTO fii_dii_data (date, category, buy_value, sell_value, net_value)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(date, category) DO UPDATE SET
            buy_value = excluded.buy_value,
            sell_value = excluded.sell_value,
            net_value = excluded.net_value,
            fetched_at = CURRENT_TIMESTAMP
    """, (date, category, buy_value, sell_value, net_value))
    conn.commit()


def query_all(conn: sqlite3.Connection) -> list[dict]:
    """Return all records ordered by date ascending."""
    return conn.execute(
        "SELECT date, category, buy_value, sell_value, net_value "
        "FROM fii_dii_data ORDER BY date ASC"
    ).fetchall()


def query_by_date_range(conn: sqlite3.Connection, start_date: str, end_date: str) -> list[dict]:
    """Return records within date range (inclusive)."""
    return conn.execute(
        "SELECT date, category, buy_value, sell_value, net_value "
        "FROM fii_dii_data WHERE date >= ? AND date <= ? ORDER BY date ASC",
        (start_date, end_date)
    ).fetchall()


def get_today_snapshot(conn: sqlite3.Connection, today: Optional[str] = None) -> list[dict]:
    """Return today's records if they exist."""
    today = today or datetime.now().strftime("%d-%b-%Y")
    return conn.execute(
        "SELECT date, category, buy_value, sell_value, net_value "
        "FROM fii_dii_data WHERE date = ? ORDER BY category",
        (today,)
    ).fetchall()


def get_monthly_rollup(conn: sqlite3.Connection, year: int, month: int) -> list[dict]:
    """Aggregate FII/DII data for a given month (month-to-date)."""
    records = query_all(conn)
    groups: dict[str, dict] = {}
    for r in records:
        d = datetime.strptime(r["date"], "%d-%b-%Y")
        if d.year != year or d.month != month:
            continue
        cat = r["category"]
        if cat not in groups:
            groups[cat] = {"category": cat, "buy_value": 0.0, "sell_value": 0.0, "net_value": 0.0}
        groups[cat]["buy_value"] += r["buy_value"]
        groups[cat]["sell_value"] += r["sell_value"]
        groups[cat]["net_value"] += r["net_value"]
    return list(groups.values())
