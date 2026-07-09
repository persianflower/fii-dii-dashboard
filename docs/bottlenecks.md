# Bottleneck Analysis — FII/DII Dashboard

## #1 — SVG Icons Rendered as Raw Text (Critical UX Bug)

**Where:** `app.py:120, 133, 141`
**What:** `st.markdown(f"...{SVG}...")` without `unsafe_allow_html=True`
**Impact:** Raw SVG source code displayed instead of rendered icons. App looks broken immediately on load.
**Fix:** Add `unsafe_allow_html=True` to all three `st.markdown()` calls in the sidebar.
**Effort:** 5 minutes
**ROI:** Eliminates the most visible defect — makes the app look functional.

## #2 — No Dark Mode Support (UX Quality)

**Where:** `app.py:35-67` — hardcoded light theme colors
**What:** All CSS uses literal colors (`#f8fafc`, `#e2e8f0`, `#64748b`). Streamlit's dark mode renders these as-is, creating a jarring white-on-dark mismatch.
**Impact:** ~30% of Streamlit users (dark mode) get a broken visual experience.
**Fix:** Convert CSS to use CSS custom properties with light/dark media query. Use Streamlit's theme-aware color references where possible.
**Effort:** 30 minutes
**ROI:** Universal visual quality — dark and light users both get a premium experience.

## #3 — No Loading Skeletons for Chart Tabs (UX Polish)

**Where:** `app.py:246-280`
**What:** Nifty overlay tab blocks the entire UI with a spinner (`with st.spinner`). Other tabs have no loading state at all. No skeleton/placeholder while chart data loads.
**Impact:** Perceived slowness — user waits on an empty screen instead of seeing a placeholder layout.
**Fix:** Replace `st.spinner` with placeholder containers that show chart skeletons. Wrap slower fetches in `@st.fragment` for non-blocking load.
**Effort:** ~1 hour
**ROI:** Medium — makes app feel faster, but Nifty fetch is the only slow path.

## Quick Wins (Completed)

| Change | Effort | Impact |
|--------|--------|--------|
| Fix SVG `unsafe_allow_html=True` | 5 min | Critical — broken icons fixed |
| `layout="wide"` | 2 min | Charts use full viewport width |
| `page_icon` as chart SVG | 2 min | Tab has a visual identity |
| Extract SVG _ICONS dict | 5 min | Cleaner code, reuse-safe |
| CSS dark mode variables | 15 min | Universal visual quality |

## What NOT to Do
- Full component library (Mantine/Chakra) — overkill for 4 chart types
- Custom React frontend — the app is 290 lines. A rewrite would be 10x the code.
- Animation library — unnecessary for a data dashboard
