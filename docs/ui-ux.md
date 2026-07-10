# UI/UX Design Decisions — FII/DII Dashboard v2

## Color Palette

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--bg-primary` | `#ffffff` | `#0f172a` | Page background |
| `--bg-card` | `#f8fafc` | `#1e293b` | Card backgrounds |
| `--border-card` | `#e2e8f0` | `#334155` | Card borders |
| `--text-primary` | `#0f172a` | `#f1f5f9` | Headings |
| `--text-muted` | `#64748b` | `#94a3b8` | Labels, captions |
| `--text-caption` | `#94a3b8` | `#64748b` | Footer, extras |
| `--accent-green` | `#22C55E` | `#22C55E` | FII positive |
| `--accent-red` | `#EF4444` | `#EF4444` | DII / negative |
| `--bg-info` | `#f0f4ff` | `#1e3a5f` | Info boxes |

FII = green (foreign capital inflow = market bullish)
DII = red (domestic institutions as counterbalance)

## Typography
- Metric values: 1.35rem, 600 weight
- Labels: 0.75rem, 500 weight
- Headers: 1.05rem, 600 weight
- Captions: 0.7-0.78rem, 400 weight
- Font: system stack (Inter fallback via CSS)

## Layout Architecture
- Max content width: 1200px centered
- Sidebar: filters, actions, about
- Main: 3 sections (Today → MTD → Charts)
- Charts: 4 tabs (Trend → FII vs DII → Rolling Avg → Nifty Overlay)
- Responsive: column cards auto-stack on mobile

## Component States
Every section handles:
1. **Loading** — `st.spinner` during data fetch
2. **Empty** — Dashed border placeholder with guidance text
3. **Error** — try/except wrapped, shows fallback message, doesn't crash app
4. **Data** — Normal rendering

## Error Boundaries
- `app.py` split into 4 independent try/except blocks:
  1. Today's Snapshot
  2. Month-to-Date
  3. Charts section
  4. Sidebar actions
- A crash in any section shows "⚠️ Could not load [section]" instead of killing the app

## Session State Caching
- `SESSION["nifty_prices"]` — cached yfinance fetch, cleared on refresh
- `SESSION["today_snapshot"]` — avoid double DB query

## Accessibility (WCAG)
- Color is not the only indicator — metric labels include text descriptors
- SVGs use `stroke="currentColor"` for proper contrast inheritance
- Layout works at 1200px and narrow

## What's NOT in Scope
- Mobile PWA — Streamlit's responsive layout handles basic mobile
- Chart animations — Plotly defaults are sufficient
- Custom font — system stack avoids extra HTTP requests
