"""SQLite database layer for FII/DII data storage."""

import sqlite3
from datetime import datetime
from typing import Optional
from pathlib import Path

from src.config import DB_PATH

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS fii_dii_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    buy_value REAL NOT NULL,
    sell_value REAL NOT NULL,
    net_value REAL NOT NULL,
    source TEXT NOT NULL DEFAULT 'live',
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, category)
)
"""

_MIGRATE_SOURCE_COL = """
ALTER TABLE fii_dii_data ADD COLUMN source TEXT NOT NULL DEFAULT 'live'
"""


def _dict_factory(cursor, row):
    """Row factory that returns dicts instead of tuples."""
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}


def init_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Initialize SQLite database and return connection."""
    path = db_path or DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = _dict_factory
    conn.execute(_SCHEMA_SQL)
    # Migration: add source column if it doesn't exist
    try:
        conn.execute(_MIGRATE_SOURCE_COL)
        conn.commit()
    except sqlite3.OperationalError:
        pass  # column already exists
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_fii_dii_date
        ON fii_dii_data(date)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_fii_dii_source
        ON fii_dii_data(source)
    """)
    conn.commit()
    return conn


def insert_record(conn: sqlite3.Connection, date: str, category: str,
                  buy_value: float, sell_value: float, net_value: float,
                  source: str = "live") -> None:
    """Insert or update a FII/DII record (upsert on date+category)."""
    conn.execute("""
        INSERT INTO fii_dii_data (date, category, buy_value, sell_value, net_value, source)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(date, category) DO UPDATE SET
            buy_value = excluded.buy_value,
            sell_value = excluded.sell_value,
            net_value = excluded.net_value,
            source = excluded.source,
            fetched_at = CURRENT_TIMESTAMP
    """, (date, category, buy_value, sell_value, net_value, source))
    conn.commit()


def query_all(conn: sqlite3.Connection) -> list[dict]:
    """Return all records ordered by date ascending."""
    return conn.execute(
        "SELECT date, category, buy_value, sell_value, net_value, source "
        "FROM fii_dii_data ORDER BY date ASC"
    ).fetchall()


def query_by_date_range(conn: sqlite3.Connection, start_date: str, end_date: str) -> list[dict]:
    """Return records within date range (inclusive)."""
    return conn.execute(
        "SELECT date, category, buy_value, sell_value, net_value, source "
        "FROM fii_dii_data WHERE date >= ? AND date <= ? ORDER BY date ASC",
        (start_date, end_date)
    ).fetchall()


def get_today_snapshot(conn: sqlite3.Connection, today: Optional[str] = None) -> list[dict]:
    """Return today's records if they exist."""
    today = today or datetime.now().strftime("%d-%b-%Y")
    return conn.execute(
        "SELECT date, category, buy_value, sell_value, net_value, source "
        "FROM fii_dii_data WHERE date = ? ORDER BY category",
        (today,)
    ).fetchall()


def has_mock_data(conn: sqlite3.Connection) -> bool:
    """Return True if any records in the DB have source='sample'."""
    row = conn.execute("SELECT 1 FROM fii_dii_data WHERE source = 'sample' LIMIT 1").fetchone()
    return row is not None


def get_monthly_rollup(conn: sqlite3.Connection, year: int, month: int) -> list[dict]:
    """Return aggregated FII/DII data for a given month."""
    month_abbr = datetime(year, month, 1).strftime("%b")
    return conn.execute(
        "SELECT category, SUM(buy_value) AS buy_value, SUM(sell_value) AS sell_value, "
        "SUM(net_value) AS net_value FROM fii_dii_data "
        "WHERE date LIKE ? GROUP BY category ORDER BY category",
        (f"%-{month_abbr}-{year}",)
    ).fetchall()
