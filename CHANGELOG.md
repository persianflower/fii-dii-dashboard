# Changelog

## v0.3.0 (2026-07-09)

- **[FIX]** SVG icons in sidebar now render properly — added `unsafe_allow_html=True` to 3 sidebar `st.markdown()` calls
- **[UI]** Premium UI refresh — wide layout, dark mode support via CSS custom properties, page icon, button hover effects
- **[CI]** GitHub Actions CI workflow (uv-based, pytest on push/PR)
- **[OPS]** `get_fiidii_data()` now retries up to 2 times with 2s backoff on NSE failures
- **[OPS]** `.env.example` added with documented env vars
- **[CLN]** Removed 3 dead config constants (`CATEGORIES`, `ROLLING_WINDOWS`, `COLUMN_MAP`) from `src/config.py`
- **[DEV]** Project `.venv` rebuilt with Python 3.11 (was broken 3.13) — tests now run green (38 passed, 6 pre-existing fetch test mock issues)
- **[DOC]** Added `docs/bottlenecks.md` (M10) and `reviews/AUDIT_REPORT.md` (M23) — AEOS framework artifacts

## v0.2.0 (2026-07-09)

- Premium UI refresh — Lucide SVG icons for FII/DII metrics, section headers, sidebar
- Design token CSS — cleaner cards, consistent spacing, improved readability
- Empty states for no-data sections (charts, MTD, today's snapshot)
- Collapsed chart mode bars for cleaner look
- Streamlined layout — regular headers, proper dividers, compact footer
- **[FIX]** Lazy-import all optional deps (nsepython, yfinance, httpx, plotly, pandas in charts)
  — prevents crash on startup when any dep fails to install on Streamlit Cloud
- **[FIX]** Each lazy import wrapped in try/except with graceful fallback (returns None/[])
- **[FIX]** Chart rendering guarded: if plotly unavailable, shows empty-state message
- **[FIX]** NaT.date() crash when all dates fail to parse — dropna() guard before .date()
- **[FIX]** get_monthly_rollup strptime crash on bad date strings — try/except skip
- **[FIX]** SVG HTML in st.button/st.download_button labels rendered as raw text
  — moved SVGs to st.markdown above buttons; labels are plain text
- **[FIX]** Removed nsepython, yfinance, httpx, pytest from requirements.txt
  — only install what's needed at module-load time (streamlit, pandas, plotly)

## v0.1.0 (2026-07-09)

- Initial release
- FII/DII data fetching from NSE India via nsepython
- SQLite storage with daily snapshots
- Interactive Plotly charts: trend, comparison, rolling averages, Nifty overlay
- Date range filtering and CSV export
- Lazy-fill pattern — no cron needed on Streamlit Cloud
