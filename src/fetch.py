"""Data fetching module — wraps nsepython and yfinance."""

from typing import Optional

from src.config import NIFTY_TICKER


def parse_fiidii_row(raw: dict) -> Optional[dict]:
    """Parse a raw nse_fiidii() row into clean types.

    Returns None if the row is empty or malformed.
    """
    if not raw or not raw.get("category") or not raw.get("buyValue"):
        return None
    try:
        return {
            "date": str(raw["date"]),
            "category": str(raw["category"]),
            "buy_value": float(raw["buyValue"]),
            "sell_value": float(raw["sellValue"]),
            "net_value": float(raw["netValue"]),
        }
    except (ValueError, TypeError, KeyError):
        return None


def get_fiidii_data() -> list[dict]:
    """Fetch current FII/DII data from NSE and return parsed records.

    Returns empty list on failure.
    """
    try:
        import nsepython as nse  # lazy import — nsepython's deps may not install cleanly
        raw_rows = nse.nse_fiidii()
        if not raw_rows:
            return []
        parsed = []
        for row in raw_rows:
            p = parse_fiidii_row(row)
            if p:
                parsed.append(p)
        return parsed
    except Exception:
        return []


def get_nifty_history(start_date: str, end_date: str) -> Optional[dict[str, float]]:
    """Fetch historical Nifty 50 closing prices for a date range.

    Returns dict mapping 'DD-Mon-YYYY' → close price, or None on failure.
    """
    try:
        import yfinance as yf  # lazy import — avoids numpy/pandas version conflicts
        ticker = yf.Ticker(NIFTY_TICKER)
        hist = ticker.history(start=start_date, end=end_date)
        if hist.empty:
            return None
        return {d.strftime("%d-%b-%Y"): float(r["Close"])
                for d, r in hist.iterrows()}
    except Exception:
        return None
