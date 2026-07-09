━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROBLEM STATEMENT:    Add AI summary, Telegram alerts, monthly rollup, F&O tab, and sector breakdown to existing FII/DII dashboard
REQUIREMENTS:
  - AI summary: LLM-generated one-liner from latest FII/DII data, with rule-based fallback
  - Telegram alert: Cron-based notification when FII net crosses ±₹1,000 Cr
  - Monthly rollup: SQLite aggregate query, displayed as st.metric
  - F&O tab: New tab in the dashboard, fetch from separate NSE endpoint
  - Sector breakdown: Map top stocks to sectors, show FII flow by sector

CONSTRAINTS:
  - No new backend services — all runs in Streamlit+dependencies
  - No cron — lazy-fill pattern for all data (alert uses existing Telegram cron infra)
  - No new external APIs beyond what's already used (yfinance, nsepython)
  - LLM calls use existing Groq API key

ARCHITECTURE OPTIONS:
  Option A: Inline — add all new code into existing app.py and src/ modules
  Option B: Plugin — create a src/plugins/ directory with feature-specific modules
  Option C: Duplicate app — no, overkill for 4 features

RECOMMENDED: Option A (inline)
  Rationale: Each feature is <50 lines of new code. Creating a plugin system for 4
  small additions is over-engineering. Ponytail principle — simplest thing that works.

COMPONENT DIAGRAM:
  app.py — 3 new tabs (Monthly Rollup, F&O Data → future, Sector Breakdown → future)
  src/fetch.py — 2 new functions (get_fii_fno_data, get_sector_map)
  src/ai.py — NEW file for AI summary generation (wraps LLM call)
  src/alerts.py — NEW file for Telegram alert logic
  internals/orchestrator.md — update with Phase 2 progress

DATA FLOW:
  AI summary: fetch.get_fiidii_data() → latest row → ai.generate_summary() → app.py display
  Telegram: cron → src/alerts/check_threshold() → telegram.send_message()
  Monthly: fetch data (all) → SQL GROUP BY month → app.py metric display

DATA MODEL: No schema changes required

RISKS:
  Top 1: LLM API may fail or return nonsense — fallback to rule-based summary
  Top 2: Telegram key not configured — feature silently disabled
  Top 3: NSE API for F&O may differ from cash endpoint — treat as unknown

TRADEOFFS:
  Accepted: F&O and sector breakdown deferred to follow-up session
  Deferred: CI/CD pipeline, monitoring
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
