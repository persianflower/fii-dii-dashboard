"""NSE FII/DII Data Dashboard — Track institutional investor flows."""

import io
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from src.config import DB_PATH
from src.db import init_db, insert_record, query_all, get_today_snapshot, get_monthly_rollup
from src.fetch import get_fiidii_data, get_nifty_history
from src.charts import (
    build_trend_chart,
    build_comparison_chart,
    build_rolling_avg_chart,
    build_fii_nifty_overlay,
)
from src.ai import generate_summary

# ─── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="FII/DII Dashboard",
    page_icon=(
        '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" '
        'viewBox="0 0 24 24" fill="none" stroke="#22C55E" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"/>'
        '<path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>'
        '<path d="M2 12h20"/>'
        '<path d="M12 6v6l4 2"/></svg>'
    ),
    layout="wide",
)

# ─── Lucide SVGs (compact, inline) ─────────────────────────
_II = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>'  # globe
_IN = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9 9 3 15 9 21 9 15 15 9 15Z"/><path d="M9 21V9"/></svg>'  # building
_CA = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2v4M16 2v4M3 10h18"/><rect x="3" y="4" width="18" height="18" rx="2"/></svg>'  # calendar
_RF = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M21 21v-5h-5"/></svg>'  # refresh-cw
_DL = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'  # download

# ─── Custom CSS (minimal, premium) ─────────────────────────
# ─── Custom CSS (minimal, premium, theme-aware) ────────────
st.markdown("""<style>
    :root {
        --bg-card: #f8fafc;
        --border-card: #e2e8f0;
        --text-muted: #64748b;
        --text-caption: #94a3b8;
        --bg-info: #f0f4ff;
        --border-info: #dbeafe;
        --accent: #22C55E;
        --danger: #dc2626;
    }
    @media (prefers-color-scheme: dark) {
        .stApp { background: #0f172a; }
        :root {
            --bg-card: #1e293b;
            --border-card: #334155;
            --text-muted: #94a3b8;
            --text-caption: #64748b;
            --bg-info: #1e3a5f;
            --border-info: #2563eb;
        }
        div[data-testid="column"] { background: #1e293b; border-color: #334155; }
        div[data-testid="metric-container"] > label { color: #94a3b8 !important; }
        .st-b7, .st-b6, .st-b5, .st-b4 { color: #e2e8f0 !important; }
    }
    .stApp { max-width: 1200px; margin: 0 auto; }
    div[data-testid="column"] {
        background: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 12px;
        padding: 16px 14px;
    }
    div[data-testid="metric-container"] {
        background: transparent !important;
        padding: 0 !important;
    }
    div[data-testid="metric-container"] > label {
        font-size: 0.75rem !important;
        color: var(--text-muted) !important;
        font-weight: 500 !important;
    }
    div[data-testid="metric-container"] > div {
        font-size: 1.35rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stInfo"] {
        background: var(--bg-info) !important;
        border: 1px solid var(--border-info) !important;
        border-radius: 10px !important;
    }
    .ml { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; font-size: 0.78rem; font-weight: 500; }
    .mc { font-size: 0.7rem; color: var(--text-caption); margin-top: 2px; }
    .hdr { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 1.05rem; margin: 24px 0 4px; }
    .empty { text-align: center; padding: 32px 20px; border: 1px dashed var(--border-card); border-radius: 12px; color: var(--text-caption); font-size: 0.85rem; }
    hr { margin: 4px 0 16px; }
    .stButton button, .stDownloadButton button { border-radius: 8px; font-size: 0.8rem; width: 100%; }
    .stButton button:hover { opacity: 0.85; transition: opacity 0.15s; }
    section[data-testid="stSidebar"] .stMarkdown { font-size: 0.85rem; }
</style>""", unsafe_allow_html=True)


# ─── Helper ────────────────────────────────────────────────
def _section(icon_svg: str, label: str):
    st.markdown(f'<div class="hdr">{icon_svg} {label}</div><hr>', unsafe_allow_html=True)


def _metric_card(icon_svg: str, label: str, value: str, delta: str,
                 caption: str, color: str = "#64748b"):
    st.markdown(
        f'<div class="ml" style="color:{color}">{icon_svg} {label}</div>',
        unsafe_allow_html=True,
    )
    st.metric(label=label, value=value, delta=delta, label_visibility="collapsed")
    st.markdown(f'<div class="mc">{caption}</div>', unsafe_allow_html=True)


# ─── Init ──────────────────────────────────────────────────
conn = init_db(DB_PATH)

# ─── Lazy-fill data ────────────────────────────────────────
today_str = datetime.now().strftime("%d-%b-%Y")
today_snapshot = get_today_snapshot(conn)
data_fetched = False

if not today_snapshot:
    with st.spinner("Fetching today's FII/DII data from NSE..."):
        records = get_fiidii_data()
        if records:
            for r in records:
                insert_record(conn, r["date"], r["category"],
                              r["buy_value"], r["sell_value"], r["net_value"])
            data_fetched = True

all_records = query_all(conn)
df_all = pd.DataFrame(all_records)

if not df_all.empty:
    df_all["date_parsed"] = pd.to_datetime(df_all["date"], format="%d-%b-%Y", errors="coerce")
    valid_dates = df_all["date_parsed"].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
    else:
        min_date = datetime.now().date() - timedelta(days=30)
        max_date = datetime.now().date()
else:
    min_date = datetime.now().date() - timedelta(days=30)
    max_date = datetime.now().date()

# ─── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"**FII/DII Dashboard**  \n{_CA} {today_str}", unsafe_allow_html=True)
    st.divider()

    st.markdown("**Filters**")
    date_range = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed",
    )
    st.divider()

    st.markdown(f"**Actions** {_RF}", unsafe_allow_html=True)
    if st.button("Refresh data", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

    if not df_all.empty:
        buf = io.StringIO()
        df_all.to_csv(buf, index=False)
        st.markdown(f"{_DL}", unsafe_allow_html=True)
        st.download_button(
            label="Download CSV",
            data=buf.getvalue(),
            file_name=f"fiidii_data_{today_str}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    st.divider()

    st.markdown("**About**")
    st.caption("Data: NSE India via nsepython")
    st.caption("License: AGPL v3")
    if today_snapshot:
        st.caption(f"Today's data loaded — {today_str}")
    elif data_fetched:
        st.caption(f"Fresh data fetched — {today_str}")
    else:
        st.caption("Historical only (no new data)")
    st.caption(f"Records: {len(all_records)}")

# ─── Filter ────────────────────────────────────────────────
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = (
    [r for r in all_records
     if start_date <= pd.to_datetime(r["date"], format="%d-%b-%Y").date() <= end_date]
    if not df_all.empty else []
)

# ─── Today's Snapshot ─────────────────────────────────────
_section(_II, "Today's Snapshot")

today_data = get_today_snapshot(conn)
if today_data:
    cols = st.columns(2)
    for i, rec in enumerate(today_data):
        with cols[i]:
            is_fii = rec["category"] == "FII/FPI"
            color = "#16a34a" if is_fii else "#dc2626"
            delta = f"+{rec['net_value']:,.0f}" if rec['net_value'] >= 0 else f"{rec['net_value']:,.0f}"
            _metric_card(
                icon_svg=_II if is_fii else _IN,
                label=rec["category"],
                value=f"₹{rec['net_value']:,.0f}",
                delta=delta,
                caption=f"Buy: ₹{rec['buy_value']:,.0f} | Sell: ₹{rec['sell_value']:,.0f}",
                color=color,
            )

    fii = next((r for r in today_data if r["category"] == "FII/FPI"), None)
    dii = next((r for r in today_data if r["category"] == "DII"), None)
    if fii:
        recent = query_all(conn)[-10:]
        trend_days = 0
        for r in reversed(recent):
            if r["category"] != "FII/FPI":
                continue
            if (r["net_value"] >= 0 and fii["net_value"] >= 0) or (r["net_value"] < 0 and fii["net_value"] < 0):
                trend_days += 1
            else:
                break
        summary = generate_summary(fii["net_value"], dii["net_value"] if dii else 0.0, today_str, trend_days)
        st.info(summary)
elif data_fetched:
    st.info("Today's data fetched but NSE returned nothing yet (market hours).")
else:
    st.markdown(
        '<div class="empty"><div style="font-weight:600;margin-bottom:4px">No Data Today</div>'
        'Use <b>Refresh data</b> in the sidebar during market hours to pull the latest '
        'FII/DII snapshot from NSE.</div>',
        unsafe_allow_html=True,
    )

# ─── MTD ──────────────────────────────────────────────────
_section(_CA, "Month-to-Date")
now = datetime.now()
monthly = get_monthly_rollup(conn, now.year, now.month)
if monthly:
    cols = st.columns(len(monthly))
    for i, row in enumerate(monthly):
        with cols[i]:
            is_fii = row["category"] == "FII/FPI"
            color = "#16a34a" if is_fii else "#dc2626"
            delta = f"+{row['net_value']:,.0f}" if row['net_value'] >= 0 else f"{row['net_value']:,.0f}"
            _metric_card(
                icon_svg=_II if is_fii else _IN,
                label=f"{row['category']} MTD",
                value=f"₹{row['net_value']:,.0f}",
                delta=delta,
                caption=f"Buy: ₹{row['buy_value']:,.0f} | Sell: ₹{row['sell_value']:,.0f}",
                color=color,
            )
else:
    st.markdown(
        '<div class="empty">No monthly data yet. Data accumulates daily.</div>',
        unsafe_allow_html=True,
    )

# ─── Charts ────────────────────────────────────────────────
_section(_RF, "Historical Trends")

if len(filtered) >= 2:
    t1, t2, t3, t4 = st.tabs(["Net Flow Trend", "FII vs DII", "Rolling Averages", "FII vs Nifty"])

    with t1:
        fig = build_trend_chart(filtered)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="empty">Plotly unavailable — charts cannot render.</div>', unsafe_allow_html=True)
    with t2:
        fig = build_comparison_chart(filtered)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="empty">Plotly unavailable — charts cannot render.</div>', unsafe_allow_html=True)
    with t3:
        window = st.selectbox("Rolling window", [7, 15, 30], index=0, label_visibility="collapsed")
        fig = build_rolling_avg_chart(filtered, window=window)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="empty">Plotly unavailable — charts cannot render.</div>', unsafe_allow_html=True)
    with t4:
        with st.spinner("Fetching Nifty prices..."):
            nifty_prices = get_nifty_history(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        fig = build_fii_nifty_overlay(filtered, nifty_prices=nifty_prices)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="empty">Plotly unavailable — charts cannot render.</div>', unsafe_allow_html=True)
else:
    msg = "Need at least 2 days of data to display charts." if not filtered else (
        f"Only {len(filtered)} record(s) in the selected range. Expand the date range."
    )
    st.markdown(f'<div class="empty">{msg}</div>', unsafe_allow_html=True)

# ─── Footer ────────────────────────────────────────────────
st.markdown(
    f'<div style="margin-top:32px;padding:12px 0;border-top:1px solid #e2e8f0;'
    f'font-size:0.7rem;color:#94a3b8;display:flex;justify-content:space-between">'
    f'<span>FII/DII Dashboard &mdash; {_CA} {today_str}</span>'
    f'<span>AGPL v3 &middot; '
    f'<a href="https://github.com/AshayK003/fii-dii-dashboard" style="color:#94a3b8">GitHub</a></span></div>',
    unsafe_allow_html=True,
)
