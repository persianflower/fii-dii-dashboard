"""AI-powered summary generation for FII/DII data.

Generates a plain-language interpretation of institutional flows
using Groq API, with a deterministic rule-based fallback.
"""

import os
from typing import Optional
from datetime import datetime
import httpx


GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


def _format_number(value: float) -> str:
    """Format a crore figure for display."""
    prefix = "−" if value < 0 else ""
    return f"{prefix}₹{abs(value):,.0f} Cr"


def _rule_based_summary(fii_net: float, dii_net: float, trend_days: int = 0) -> str:
    """Generate deterministic summary without an LLM call."""
    parts = []

    # Consecutive trend
    if trend_days >= 3 and fii_net < 0:
        parts.append(f"FIIs have been net sellers for {trend_days} consecutive sessions — sustained bearish signal for large-caps.")
    elif trend_days >= 3 and fii_net > 0:
        parts.append(f"FIIs have been net buyers for {trend_days} consecutive sessions — sustained bullish signal.")
    elif trend_days >= 2 and fii_net < 0:
        parts.append(f"FIIs net sold for a second straight session — increasing caution.")
    elif trend_days >= 2 and fii_net > 0:
        parts.append(f"FIIs net bought for a second straight session — momentum building.")

    # Direction
    direction = "bought" if fii_net >= 0 else "sold"
    fii_part = f"FIIs {direction} {_format_number(abs(fii_net))} in cash market."
    parts.append(fii_part)

    # DII counterbalance
    if dii_net > 0 and fii_net < 0:
        parts.append("DIIs stepped in as buyers, partially offsetting FII outflows.")
    elif dii_net < 0 and fii_net > 0:
        parts.append("DIIs were net sellers on this FII buying day — divergence worth watching.")
    elif dii_net > 0 and fii_net > 0:
        parts.append("Both FII and DII were net buyers — broad institutional confidence.")
    elif dii_net < 0 and fii_net < 0:
        parts.append("Both FII and DII were net sellers — broad institutional caution.")

    return " ".join(parts)


def _llm_summary(fii_net: float, dii_net: float, today_str: str) -> Optional[str]:
    """Call Groq API to generate a one-line summary."""
    if not GROQ_API_KEY:
        return None

    prompt = (
        f"Today ({today_str}): FII net = ₹{fii_net:+.0f} Cr, DII net = ₹{dii_net:+.0f} Cr "
        f"in Indian cash equity market. Generate exactly ONE concise sentence explaining "
        f"what this means for retail traders. Use natural language. "
        f"Be direct — no hedging, no 'suggests', no 'indicates'. "
        f"If FIIs sold heavily, say 'FIIs sold off'. If they bought, say 'FIIs bought in'."
    )

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a concise market commentator. "
                                       "Respond in ONE sentence. Use plain English. No fluff.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 80,
                    "temperature": 0.5,
                },
            )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()
        # Strip quotes if LLM wraps the response
        return content.strip('"\'')
    except Exception:
        return None


def generate_summary(
    fii_net: float,
    dii_net: float,
    today_str: Optional[str] = None,
    trend_days: int = 0,
    force_llm: bool = False,
) -> str:
    """Generate a market interpretation summary.

    Uses LLM (Groq) when available, falls back to rule-based.
    """
    if force_llm or GROQ_API_KEY:
        llm_result = _llm_summary(fii_net, dii_net, today_str or datetime.now().strftime("%d-%b-%Y"))
        if llm_result:
            return llm_result

    return _rule_based_summary(fii_net, dii_net, trend_days)
