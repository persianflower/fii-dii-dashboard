"""Constants and configuration for the FII/DII dashboard."""

from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "fiidii.db"
NIFTY_TICKER = "^NSEI"
