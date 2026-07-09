# Module 5: Strategic Intelligence — NSE FII/DII Data Dashboard

> AEOS v1.0 — Research, Product Discovery & Strategic Intelligence

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROBLEM:
CUSTOMER:
MARKET:
COMPETITION:
TECHNOLOGY:
BUSINESS:
MOATS:
RISKS:
VALIDATION:
RECOMMENDATION:
PRIORITY:
NEXT ACTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Executive Summary

**Problem:** Indian retail equity investors check FII/DII data daily as a market sentiment indicator, but have no dedicated tool to track historical trends. NSE website shows only the current day. Moneycontrol and TradingView offer limited history behind paywalls.

**Solution:** A free, open-source Streamlit dashboard that scrapes daily FII/DII from NSE India, persists to SQLite, and visualizes trends with interactive Plotly charts, Nifty overlay, and rolling averages.

**Why now:** FII/DII data has become a mainstream sentiment indicator for Indian retail. X/Reddit discourse around "FII selling" and "DII buying" is at an all-time high. Yet no free tool exists to answer "what was the 30-day trend?" — everyone checks today in isolation.

---

## Market

| Dimension | Assessment |
|-----------|------------|
| **TAM** | ~15M active Indian retail equity investors (NSE, 2025) |
| **SAM** | ~2M who actively track FII/DII data (based on X/Discourse volume) |
| **SOM** | ~50K dev/users who would use a free OSS tool |
| **Growth** | Indian retail demat accounts growing 30% YoY (NSE data) |
| **Timing** | Next bull cycle sentiment — FII/DII tracking peaks in volatile markets |

---

## Customers

**Primary persona:** Indian retail equity investor, 25-40, tech-savvy, uses Groww/Zerodha, active on X/Reddit finance communities.

**Pain points:**
- Opens NSE website daily to check FII/DII — no history visible
- Checks Moneycontrol — shows current day only, cluttered UI
- Tries TradingView — needs paid subscription for NSE FII/DII data
- Tracks manually in spreadsheets (high friction, low adoption)

**Willingness to pay:** Zero for this segment. They use free tools. Monetization must come via OSS community adoption, not direct charges.

---

## Competition

| Competitor | FII/DII | History | Free | Weakness |
|------------|---------|---------|------|----------|
| NSE India website | ✅ Current day | ❌ | ✅ | No history, no trends |
| Moneycontrol | ✅ Summary | ❌ | ✅ | Cluttered, limited |
| TradingView | ✅ With their data feed | ✅ | ❌ | Paid plan required |
| Upstox/Zerodha apps | ✅ Basic | ❌ | ✅ | Limited to holdings view |
| **FII/DII Dashboard** | **✅ Full** | **✅ SQLite** | **✅ OSS** | **No real-time, no mobile app** |

---

## Technology

| Dimension | Assessment |
|-----------|------------|
| **Feasibility** | ✅ Proven — nsepython.nse_fiidii() works (verified Jun 2026) |
| **Stack** | Streamlit + SQLite + Plotly — all free, zero infra |
| **Data source risk** | Medium — nsepython relies on NSE unofficial API, could break |
| **Scalability** | SQLite handles 10+ years of daily data (~7KB/yr) |
| **Maintenance** | Zero — no servers, no cron, no API keys |

---

## Business Model

**Revenue:** $0. Pure open-source (AGPL v3). Audience-building tool for the creator's OSS portfolio.

**Costs:** $0 — Streamlit Cloud free tier, no paid deps.

**Strategic value:** Demonstrates Indian-market data engineering skills. Feeds into the broader portfolio of finance OSS tools (NSE Portfolio Risk Scanner, NSE Sentiment Analyzer).

---

## Moats

| Moat | Assessment | Durability |
|------|------------|------------|
| **Data accumulation** | Historical SQLite grows over time | Medium — copyable by starting earlier |
| **AGPL v3** | Prevents closed-source monetization | High — legally enforced |
| **Zero-maintenance infra** | Free hosting, no ops | Low — anyone can do same |

No strong moat exists for this project. It is a utility tool, not a business.

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| nsepython breaks (NSE API changes) | Data source lost | Fallback: Upstox API browser scrape |
| Streamlit Cloud sunset | Hosting lost | Migrate to Render free tier |
| Low adoption | Wasted effort | Accept — utility tool by nature |
| yfinance rate-limited | Nifty overlay breaks | Google Finance browser fallback |

---

## Validation Plan

**Cheapest test:** Already validated — nse_fiidii() output confirmed on Jul 9 2026.

**Success signal:** Active users on Streamlit Cloud, GitHub stars, contributions.

**No further validation needed** for a utility tool of this scope.

---

## Recommendation

| Dimension | Score |
|-----------|-------|
| Business Impact | 3/10 — non-monetizable utility |
| User Impact | 7/10 — fills real gap for Indian investors |
| Engineering Cost | 9/10 (inverted) — ~550 LOC |
| Technical Risk | 7/10 (inverted) — nsepython single point of failure |
| Strategic Importance | 6/10 — portfolio credibility, not revenue |
| Moat Contribution | 2/10 — low defensibility |
| **Overall** | **6/10** |

**Verdict: Build** — valid utility tool, zero cost to maintain, fills a genuine gap. Keep scope tight, ship fast.

**Investment memo:** This is not a business. It is a portfolio piece and community utility. Engineer it for zero maintenance, not for scale. The AGPL license ensures that if anyone builds a business on top of it, the source stays open.
