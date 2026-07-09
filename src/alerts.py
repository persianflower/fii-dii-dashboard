"""Telegram alerting for FII/DII thresholds.

Checks if FII net crosses a configured threshold and
produces a formatted message ready for delivery.
"""

import os
from datetime import datetime
from typing import Optional

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
DEFAULT_THRESHOLD_CR = 1000.0


def _format_cr(value: float) -> str:
    prefix = "−" if value < 0 else "+"
    return f"{prefix}₹{abs(value):,.0f} Cr"


def check_threshold(
    records: list[dict],
    threshold: float = DEFAULT_THRESHOLD_CR,
) -> Optional[str]:
    """Check if FII/DII net crosses threshold and return alert message.

    Returns a formatted Telegram message if threshold is breached,
    None otherwise.
    """
    today_str = datetime.now().strftime("%d-%b-%Y")

    fii_net = None
    dii_net = None
    for r in records:
        if r["category"] == "FII/FPI":
            fii_net = r["net_value"]
        elif r["category"] == "DII":
            dii_net = r["net_value"]

    if fii_net is None:
        return None

    if abs(fii_net) < threshold:
        return None

    direction = "net sellers" if fii_net < 0 else "net buyers"
    intensity = "heavily" if abs(fii_net) >= threshold * 2 else ""

    lines = [
        f"🚨 *FII Flow Alert* — {today_str}",
        "",
        f"FIIs were {intensity} {direction}: {_format_cr(fii_net)}",
    ]

    if dii_net is not None:
        dii_direction = "buyers" if dii_net >= 0 else "sellers"
        lines.append(f"DIIs were net {dii_direction}: {_format_cr(dii_net)}")

    if fii_net < 0 and dii_net and dii_net > 0:
        lines.append("")
        lines.append("DIIs absorbed FII selling — market support detected.")
    elif fii_net < 0 and dii_net and dii_net < 0:
        lines.append("")
        lines.append("Both FII and DII selling — broad institutional caution.")

    lines.append("")
    lines.append("Source: FII/DII Dashboard (open-source)")

    return "\n".join(lines)


def send_alert(message: str) -> bool:
    """Send a message via Telegram bot API.

    Returns True if sent successfully, False otherwise.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    import httpx

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown",
            })
        resp.raise_for_status()
        return True
    except Exception:
        return False
