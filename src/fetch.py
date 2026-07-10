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

    nse_fiidii() returns a pandas DataFrame. Retries up to 2 times
    with 2s backoff. Returns empty list on all failures.
    """
    import time
    for attempt in range(3):
        try:
            import nsepython as nse
            raw = nse.nse_fiidii()
            if raw.empty:
                return []
            parsed = []
            for row in raw.to_dict("records"):
                p = parse_fiidii_row(row)
                if p:
                    parsed.append(p)
            return parsed
        except Exception:
            if attempt < 2:
                time.sleep(2)
                continue
            return []


def get_nifty_history(start_date: str, end_date: str) -> Optional[dict[str, float]]:
    """Fetch historical Nifty 50 closing prices for a date range.

    Returns dict mapping 'DD-Mon-YYYY' -> close price, or None on failure.
    """
    try:
        import yfinance as yf
        ticker = yf.Ticker(NIFTY_TICKER)
        hist = ticker.history(start=start_date, end=end_date)
        if hist.empty:
            return None
        return {d.strftime("%d-%b-%Y"): float(r["Close"])
                for d, r in hist.iterrows()}
    except Exception:
        return None


def generate_sample_data(days: int = 30) -> list[dict]:
    """Generate realistic-looking mock FII/DII data for the past N trading days.

    Skips weekends. Returns list of records ready for insert_record().
    """
    import random
    from datetime import date, timedelta

    random.seed(42)
    records = []
    today = date.today()

    # Base parameters — seeded for reproducibility
    fii_base_buy = 16000.0
    fii_base_sell = 15500.0
    dii_base_buy = 14000.0
    dii_base_sell = 13500.0

    for offset in range(days, 0, -1):
        d = today - timedelta(days=offset)
        if d.weekday() >= 5:  # skip Sat/Sun
            continue

        date_str = d.strftime("%d-%b-%Y")

        # FII: mostly selling with some buying days
        fii_drift = random.uniform(-2000, 1800)
        fii_net = fii_base_buy - fii_base_sell + fii_drift
        fii_buy = fii_base_buy + random.uniform(-800, 800)
        fii_sell = fii_buy - fii_net

        # DII: tends to counterbalance FII
        dii_drift = random.uniform(-1200, 1200)
        dii_net = -fii_net * random.uniform(-0.4, 0.6) + dii_drift
        dii_buy = dii_base_buy + random.uniform(-600, 600)
        dii_sell = dii_buy - dii_net

        records.append({"date": date_str, "category": "FII/FPI",
                        "buy_value": round(fii_buy, 2),
                        "sell_value": round(fii_sell, 2),
                        "net_value": round(fii_net, 2),
                        "source": "sample"})
        records.append({"date": date_str, "category": "DII",
                        "buy_value": round(dii_buy, 2),
                        "sell_value": round(dii_sell, 2),
                        "net_value": round(dii_net, 2),
                        "source": "sample"})

    return records
