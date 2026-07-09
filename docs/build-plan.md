━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTIVE SUMMARY
  Goal: Ship 3 features (AI summary, Telegram alerts, monthly rollup) in one session
  Scope: ~100 lines of new code across src/ai.py, src/alerts.py, app.py, cron job
  Timeline: Single session

PROJECT GOAL
  Objective: Add interpretation layer + proactive delivery + aggregate view
  Success criteria: All 3 features visible in dashboard, alerts fireable by cron

MILESTONES
  M1: AI summary — src/ai.py + app.py display
  M2: Monthly rollup — SQL query + app.py display
  M3: Telegram alert — src/alerts.py + cron registration

TASK LIST
  # | Task | Effort | Risk | Depends On
  --- | --- | --- | --- | ---
  1 | Create src/ai.py with generate_ai_summary() + fallback | Low | Low | —
  2 | Wire AI summary into app.py (st.info before charts) | Low | Low | 1
  3 | Add monthly rollup query to src/fetch.py | Low | None | —
  4 | Display monthly rollup in app.py (st.metric row) | Low | None | 3
  5 | Create src/alerts.py with check_fii_threshold() | Low | Low | —
  6 | Cron job: register Telegram alert | Low | Medium (needs user's key) | 5
  7 | Update docs (CHANGELOG, spec done during planning) | Low | None | 1-6

DEPENDENCY GRAPH
  Critical path: 1→2, 3→4, 5→6 (all independent of each other)
  Parallel work: 1, 3, 5 can happen simultaneously

RISK REGISTER
  Risk | Likelihood | Impact | Mitigation
  LLM API failure | Medium | Medium | Hardcoded fallback summary
  Telegram key not available | High | Low | Silent skip, feature doc

APPROVAL GATES
  Gate | Required
  Telegram cron setup | User provides bot token

DEFINITION OF DONE
  Checklist:
    [ ] AI summary renders on all 4 tabs
    [ ] Monthly rollup shows correct SUM from SQLite
    [ ] alert.py fires formatted Telegram message
    [ ] All existing 26 tests pass + new tests for new features
    [ ] docs updated
    [ ] git commit

NEXT ACTION
  Build feature 1: src/ai.py with AI summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
