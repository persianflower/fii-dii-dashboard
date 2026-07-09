"""Tests for the database layer."""

import pytest
from pathlib import Path
import tempfile
import os

from src.db import init_db, insert_record, query_all, query_by_date_range, get_monthly_rollup


@pytest.fixture
def db_path():
    """Temporary in-memory-equivalent file DB for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        p = Path(f.name)
    yield p
    os.unlink(p)


def test_init_db_creates_table(db_path):
    conn = init_db(db_path)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fii_dii_data'")
    assert cursor.fetchone() is not None
    conn.close()


def test_insert_and_query_all(db_path):
    conn = init_db(db_path)
    insert_record(conn, "09-Jul-2026", "FII/FPI", 1000.0, 800.0, 200.0)
    insert_record(conn, "09-Jul-2026", "DII", 500.0, 600.0, -100.0)
    rows = query_all(conn)
    assert len(rows) == 2
    assert rows[0]["category"] == "FII/FPI"
    assert rows[0]["net_value"] == 200.0
    conn.close()


def test_unique_constraint(db_path):
    """Same date+category should not create duplicate."""
    conn = init_db(db_path)
    insert_record(conn, "09-Jul-2026", "FII/FPI", 1000.0, 800.0, 200.0)
    insert_record(conn, "09-Jul-2026", "FII/FPI", 2000.0, 1500.0, 500.0)  # should update/ignore
    rows = query_all(conn)
    assert len(rows) == 1  # no duplicate
    conn.close()


def test_query_by_date_range(db_path):
    conn = init_db(db_path)
    insert_record(conn, "08-Jul-2026", "FII/FPI", 17463.95, 15501.15, 1962.8)
    insert_record(conn, "09-Jul-2026", "FII/FPI", 1000.0, 800.0, 200.0)
    insert_record(conn, "10-Jul-2026", "FII/FPI", 2000.0, 1500.0, 500.0)
    rows = query_by_date_range(conn, "09-Jul-2026", "10-Jul-2026")
    assert len(rows) == 2
    assert rows[0]["date"] == "09-Jul-2026"
    assert rows[1]["date"] == "10-Jul-2026"
    conn.close()


def test_empty_db_returns_empty_list(db_path):
    conn = init_db(db_path)
    assert query_all(conn) == []
    conn.close()


def test_monthly_rollup_aggregation(db_path):
    conn = init_db(db_path)
    insert_record(conn, "01-Jul-2026", "FII/FPI", 1000.0, 800.0, 200.0)
    insert_record(conn, "01-Jul-2026", "DII", 500.0, 600.0, -100.0)
    insert_record(conn, "15-Jul-2026", "FII/FPI", 2000.0, 1500.0, 500.0)
    insert_record(conn, "15-Jul-2026", "DII", 800.0, 900.0, -100.0)
    insert_record(conn, "01-Aug-2026", "FII/FPI", 3000.0, 2000.0, 1000.0)

    result = get_monthly_rollup(conn, 2026, 7)
    assert len(result) == 2  # FII and DII
    fii = next(r for r in result if r["category"] == "FII/FPI")
    dii = next(r for r in result if r["category"] == "DII")
    assert fii["net_value"] == 700.0  # 200 + 500
    assert dii["net_value"] == -200.0  # -100 + -100
    conn.close()


def test_monthly_rollup_empty_month(db_path):
    conn = init_db(db_path)
    insert_record(conn, "01-Jul-2026", "FII/FPI", 1000.0, 800.0, 200.0)
    result = get_monthly_rollup(conn, 2026, 8)
    assert result == []
    conn.close()
