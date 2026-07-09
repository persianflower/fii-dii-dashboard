━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTIVE SUMMARY:
  4 features to implement, ordered by effort-to-value ratio. Feature 1 (AI summary) and Feature 2 (Telegram alert) are the highest
  leverage — they turn raw data into actionable insight and proactive notifications. Feature 3-4 are nice additions.

PROBLEM DEFINITION:
  Users need institutional flow context (what does the data mean?) not just raw numbers. And they need it delivered, not just
  available on a website they have to visit.

CUSTOMER ANALYSIS:
  Persona: Indian retail swing trader with 5-20 holdings. Checks FII/DII daily. Currently uses Trendlyne or ScanX.
  Pain points: (1) Raw numbers without interpretation, (2) No proactive alerts when FII flow shifts,
    (3) No sector-level view, (4) No F&O context.
  Sources: Reddit r/IndianStreetBets threads, YouTube FII/DII tutorial comments.

FEATURE EVALUATION:

  | Feature | Value (1-10) | Effort (1-10, inverted) | Risk | Moat | Total |
  |---------|-------------|------------------------|------|------|-------|
  | AI summary | 8 | 9 (easy) | Low - API cost | 5 | 30 |
  | Telegram alerts | 9 | 6 (medium) | Low | 7 | 28 |
  | Monthly rollup | 6 | 9 (easy) | None | 3 | 18 |
  | F&O data tab | 7 | 5 (medium-hard) | NSE API reliability | 5 | 17 |
  | Sector breakdown | 8 | 4 (hard) | Data mapping | 6 | 16 |

TRADEOFF ANALYSIS:

  | Dimension | AI summary | Telegram alert | Monthly rollup | F&O tab | Sector breakdown |
  |-----------|-----------|----------------|---------------|---------|-----------------|
  | User value | High | High | Medium | Medium-High | High |
  | Effort | ~15 lines | ~40 lines | ~20 lines | ~100 lines | ~150 lines |
  | Risk | LLM cost, latency | Telegram key, cron infra | None | NSE API format changes | Stock-to-sector mapping |
  | Maintainability | Trivial | Trivial | Trivial | Medium | Medium-High (mapping drift) |

ROADMAP RECOMMENDATION:
  Build order: AI summary → Telegram alerts → Monthly rollup → F&O tab → Sector breakdown
  Each is independently shippable.

USER STORIES:

  1. AI summary:
     As a retail trader, I want to see a one-line interpretation of FII/DII data ("FIIs sold ₹X Cr for 3rd day —
     bearish signal for large-caps") so I don't have to interpret raw numbers.

  2. Telegram alert:
     As a swing trader, I want a Telegram notification when FII net crosses ±₹1,000 Cr so I can react
     without checking the dashboard daily.

  3. Monthly rollup:
     As an investor, I want a month-to-date summary table showing accumulated FII/DII flows so I can
     see the trend beyond daily noise.

ACCEPTANCE CRITERIA:

  AI summary:
    [] Generate one-line summary using LLM from latest FII/DII data
    [] Fall back to rule-based summary if LLM fails
    [] Display in a st.info before the charts
    [] No API key → show fallback summary only

  Telegram alert:
    [] Check FII net against threshold (configurable, default ±₹1,000 Cr)
    [] Send formatted alert with FII/DII net, date, and trend
    [] Works via cron (daily at 3:30 PM IST)
    [] No Telegram key → silently skip

  Monthly rollup:
    [] Compute total FII buy/sell/net for current month from SQLite data
    [] Display as a st.metric row or mini table
    [] Update automatically as new days arrive

SUCCESS METRICS:
  AI summary: Users spend 5 fewer seconds interpreting the dashboard
  Telegram alerts: User checks FII data after receiving alert (verifiable: user told us)
  Monthly rollup: Users reference the monthly figure (revisit signal)

HUMAN DECISIONS REQUIRED:
  [] Approve build order (AI summary → Telegram → rollup → F&O → sector)
  [] Provide Telegram bot token (alert feature needs it)
  [] Choose LLM provider for AI summary (your existing keys: Groq, Gemini)

FINAL RECOMMENDATION:
  Build the first 3 features (AI summary, Telegram alerts, Monthly rollup) in this session.
  F&O tab and Sector breakdown as follow-up.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
