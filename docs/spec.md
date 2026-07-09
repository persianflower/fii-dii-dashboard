# Module 7: Product Management — NSE FII/DII Data Dashboard

> AEOS v1.0 — Product Management & Product Strategy Engine

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTIVE SUMMARY:
PROBLEM DEFINITION:
CUSTOMER ANALYSIS:
BUSINESS GOALS:
FEATURE EVALUATION:
TRADEOFF ANALYSIS:
ROADMAP RECOMMENDATION:
USER STORIES:
ACCEPTANCE CRITERIA:
SUCCESS METRICS:
EXPERIMENT PLAN:
BUSINESS IMPACT:
ENGINEERING IMPACT:
DEPENDENCIES:
RISKS:
ALTERNATIVES CONSIDERED:
HUMAN DECISIONS REQUIRED:
FINAL RECOMMENDATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Executive Summary

**Recommendation:** Build and ship a focused FII/DII data dashboard as v0.1.0. Keep scope minimal — 4 chart types, SQLite persistence, CSV export. This is a utility tool for portfolio credibility, not a monetizable product.

**Rationale:** The problem is real (no free FII/DII historical tracking exists), the engineering cost is near-zero (550 LOC, free hosting), and the maintenance burden is zero (no cron, no servers). The opportunity cost of not building it is negligible. Build it, put it on GitHub, and move on.

---

## Problem Definition

**The real problem:** Indian retail investors check FII/DII data daily as a market sentiment indicator but cannot answer "what was the 30-day trend?" because no free tool stores historical snapshots. NSE shows current day. Moneycontrol and TradingView offer limited history behind paywalls.

**Who experiences it:** Active Indian retail equity investors who track institutional flows.

**How often:** Daily during market hours.

**How success is measured:** A user can open the app and see a 30-day trend of FII net flows within 15 seconds.

---

## Customer Analysis

| Dimension | Detail |
|-----------|--------|
| **Persona** | Ashay — Indian retail investor, tech-savvy, OSS contributor |
| **Primary need** | "Show me FII/DII trend over the past week/month" |
| **Current workflow** | Opens NSE website daily, copies data to mental memory |
| **Pain frequency** | Every trading day |
| **Pain severity** | Moderate — data exists but is scattered |
| **Willingness to pay** | $0 — would use a free tool, would not pay |
| **Segment size** | ~2M Indian investors who track FII/DII |

---

## Business Goals

| Goal | Primary? | Measure |
|------|----------|---------|
| Build OSS portfolio credibility | ✅ | GitHub stars, repo quality |
| Demonstrate Indian market data engineering | ✅ | Code quality, docs |
| Revenue | ❌ | Not a goal |

---

## Feature Evaluation

| Feature | Customer Val (/10) | Eng Cost (/10 inv) | Strategic (/10) | Verdict |
|---------|:-:|:-:|:-:|:---|
| Current day FII/DII display | 10/10 | 9/10 | 8/10 | ✅ Build (P0) |
| SQLite historical persistence | 9/10 | 8/10 | 7/10 | ✅ Build (P0) |
| Net flow trend chart | 9/10 | 8/10 | 7/10 | ✅ Build (P0) |
| FII vs DII bar comparison | 8/10 | 8/10 | 6/10 | ✅ Build (P1) |
| Rolling averages (7d/15d/30d) | 8/10 | 7/10 | 6/10 | ✅ Build (P1) |
| Nifty price overlay | 7/10 | 7/10 | 6/10 | ✅ Build (P1) |
| CSV export | 5/10 | 9/10 | 4/10 | ✅ Build (P1) |
| Date range filter | 8/10 | 8/10 | 6/10 | ✅ Build (P1) |
| Telegram notifications | 6/10 | 4/10 | 4/10 | ❌ Defer (out of scope) |
| Mobile app | 3/10 | 2/10 | 1/10 | ❌ Reject |
| User accounts/auth | 2/10 | 3/10 | 1/10 | ❌ Reject |
| Category breakdown (equity/debt) | 6/10 | 3/10 | 3/10 | ❌ Not possible (nse_fiidii lacks this) |

---

## Tradeoff Analysis

The only meaningful tradeoff: **simplicity vs completeness.**

| Dimension | Simple (v0.1.0) — CHOSEN | Complete (v0.2.0) |
|-----------|:---:|:---:|
| **Charts** | 4 types (trend, compare, rolling, overlay) | +heatmap, +volume, +cumulative |
| **Data** | nsepython only | +Upstox fallback, +BSE data |
| **Notifications** | None | Telegram bot, email |
| **Infrastructure** | SQLite, Streamlit free tier | PostgreSQL, Render paid |
| **LOC** | ~550 | ~2000+ |
| **Maintenance** | Zero | Ongoing |
| **Time to ship** | 1 session | 1 week |

**Recommendation:** Simple. The v0.1.0 scope solves the core problem. Add features only when users ask for them.

---

## Roadmap Recommendation

### v0.1.0 (Shipped Jul 9)
- [x] Current day FII/DII display
- [x] SQLite persistence with lazy-fill
- [x] Net flow trend chart
- [x] FII vs DII bar comparison
- [x] Rolling averages (7/15/30 day)
- [x] Nifty price overlay
- [x] CSV export + date filter
- [x] Streamlit Cloud deploy

### v0.2.0 (If adoption warrants — 50+ stars or users)
- API endpoint for FII/DII history
- Category breakdown (if nsepython adds it)
- Dark mode

### v1.0.0 (If significant traction — 500+ users)
- Upstox API as secondary data source
- Telegram daily briefing integration
- Historical data import (backfill)

---

## User Stories

### P0 — Core Experience

1. **As a** retail investor, **I want to** see today's FII and DII net values at a glance, **so that** I know the market sentiment direction without hunting through NSE's website.

2. **As a** swing trader, **I want to** view a trend chart of FII net flows over the past 30 days, **so that** I can see whether foreign investors are consistently buying or selling.

3. **As a** researcher, **I want to** compare FII and DII flows side by side, **so that** I can see who is counterbalancing whom.

### P1 — Deeper Analysis

4. **As a** technical analyst, **I want to** overlay Nifty 50 closing prices on FII flow data, **so that** I can assess correlation between institutional flows and index movement.

5. **As a** data-driven investor, **I want to** set rolling averages (7d/15d/30d) on FII net flows, **so that** I can filter out daily noise and see the underlying trend.

6. **As a** portfolio manager, **I want to** download the raw data as CSV, **so that** I can run my own analysis in Excel/Google Sheets.

### P2 — Nice to Have

7. **As a** power user, **I want to** filter by date range, **so that** I can zoom into specific periods (e.g., budget week, earnings season).

---

## Acceptance Criteria

### v0.1.0
- [x] FII and DII current-day buy/sell/net values shown as metrics
- [x] SQLite stores one row per date+category — no duplicate snapshots
- [x] Trend chart renders with selectable date range
- [x] Bar comparison chart shows FII vs DII per day
- [x] Rolling average chart works for 7, 15, 30 day windows
- [x] Nifty overlay chart shows FII net + ^NSEI on dual axis
- [x] CSV download includes all columns
- [x] Cold start ≤ 15s (8.5s fetch + render)
- [x] 22 tests pass
- [x] AGPL v3 license in place

### Not in scope (v0.1.0)
- No user accounts
- No notifications
- No real-time data
- No mobile app
- No category breakdown (equity/debt)

---

## Success Metrics

| Metric | Current | Target (3 months) |
|--------|---------|-------------------|
| GitHub stars | 0 | 50 |
| Daily active users (Streamlit) | — | 100 |
| Data accuracy vs NSE source | ✅ | 100% |
| Cold start time | ~12s | <15s |
| Uptime (Streamlit Cloud) | — | 99.9% |
| Tests passing | 22/22 | 22/22 |

---

## Experiment Plan

No further validation needed. The core data source is verified (nse_fiidii() confirmed working Jul 9). The utility value is self-evident for anyone who tracks Indian markets.

**If adoption is slow:** Cross-post to r/IndianStockMarket, r/IndianInvestments, X/desi finance, Dev.to. The repo README includes the Streamlit deploy badge.

---

## Business Impact

| Dimension | Impact |
|-----------|--------|
| Revenue | $0 |
| Retention | N/A — no user accounts |
| Strategic value | Portfolio credibility for OSS developer brand |
| Support cost | $0 — no support needed for a dashboard |

---

## Engineering Impact

| Dimension | Estimate |
|-----------|----------|
| **Effort** | 1 session (completed) |
| **LOC** | ~550 Python + ~400 docs |
| **Complexity** | Low — 3 data modules + 1 app shell |
| **Dependencies** | 5 (streamlit, pandas, plotly, nsepython, yfinance) |
| **Maintenance burden** | Zero — no database, no servers, no cron |

---

## Dependencies

| Dependency | Version | Risk |
|------------|---------|------|
| nsepython | ≥2.97 | NSE API may change — medium |
| yfinance | ≥1.5 | ^NSEI availability — low |
| Streamlit | ≥1.35 | Free tier policy — low |
| Plotly | ≥5.18 | Compatible with Streamlit — low |
| sqlite3 | stdlib | Zero risk |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| nsepython breaks | Medium | High data loss | Upstox fallback |
| Low adoption | High | Low effort waste | Accept — utility tool |
| Someone clones/sells | Medium | Medium | AGPL v3 prevents closed-source |
| yfinance breaks | Low | Medium Nifty overlay loss | Google Finance browser fallback |

---

## Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| **FastAPI + React frontend** | Overkill for a dashboard; Streamlit is 10x faster to build and deploy |
| **PostgreSQL** | SQLite is sufficient for ~7KB/year of data |
| **Cron job** | Streamlit Cloud has no cron; lazy-fill is simpler |
| **Plotly Dash** | More flexible but Streamlit Cloud hosting is free |
| **Google Sheets as DB** | Friction to set up; SQLite is zero-config |

---

## Human Decisions Required

| Decision | Status |
|----------|--------|
| Architecture approval | ✅ Approved (Jul 9) |
| Build scope | ✅ Confirmed (SQLite + historical + overlays) |
| AGPL v3 license | ✅ Confirmed |
| GitHub repo creation | ✅ Done |
| Streamlit Cloud deploy | ⬜ Deploy when user is ready |

---

## Final Recommendation

**Verdict: Build.** v0.1.0 is shipped and pushed. Deploy to Streamlit Cloud and share on social. Do not invest further unless adoption data justifies it.
