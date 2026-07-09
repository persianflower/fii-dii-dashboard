# FII/DII Dashboard — Engineering Memory

## Import Stability Architecture

**Problem:** Streamlit Cloud crash on startup whenever ANY third-party package
fails to install or import (numpy version conflicts cascade to pandas, plotly,
nsepython, yfinance, httpx — all depend on numpy).

**Solution:** Layered defense:
1. **Layer 1 — Minimal module-level imports:** Only `streamlit`, `pandas`,
   `plotly` in requirements.txt. Everything else is optional and lazy-imported.
2. **Layer 2 — Lazy imports with try/except:** Every function that needs a
   third-party lib does the import inside the function body, wrapped in
   `try/except ImportError`. If the import fails, returns a graceful fallback
   (None for chart builders, [] for data fetchers).
3. **Layer 3 — Caller-side None guards:** `app.py` checks if chart builders
   return None before calling `st.plotly_chart()`. Shows empty-state message
   instead of crashing.

**Pattern (lazy import with fallback):**
```python
def _import_go():
    try:
        import plotly.graph_objects as go
        return go
    except ImportError:
        return None

def build_trend_chart(records):
    go = _import_go()
    if go is None:
        return None  # caller handles
    ...
```

**Guard pattern for None returns:**
```python
fig = build_trend_chart(filtered)
if fig is not None:
    st.plotly_chart(fig, ...)
else:
    st.markdown('<div class="empty">Chart lib unavailable</div>', ...)
```

## Anti-Patterns Found & Fixed

1. **SVG in st.button labels:** Streamlit escapes HTML in button labels.
   SVGs render as raw `<svg>...</svg>` text. Fix: put SVG in `st.markdown()`
   above the button, use plain text for the button label.

2. **NaT.date() crash:** `df["date"].min().date()` crashes when ALL values
   are NaT (parsing failures). NaT (Not-a-Time) has no `.date()` method.
   Fix: `valid_dates = df["date_parsed"].dropna()` then check `.empty` before
   calling `.date()`.

3. **datetime.strptime on user data:** `datetime.strptime(r["date"], fmt)`
   raises ValueError on any format mismatch. Fix: wrap in try/except.

## Bug Taxonomy (Streamlit Cloud Deploys)

All bugs found: **Import timing** — module-level imports of third-party deps
execute before any error handling is possible. The fix is always:
1. Move import inside the function that uses it
2. Wrap in try/except ImportError
3. Return graceful fallback value
4. Guard the call site

## Latent Risks

- `init_db(DB_PATH)` runs at module level — could fail if `data/` directory
  isn't writable. Mitigation: Streamlit Cloud filesystem is writable in /mount.
- Test suite imports pandas/plotly at module level — if numpy breaks locally,
  tests can't run. Mitigation: non-issue for CI (clean environment).
