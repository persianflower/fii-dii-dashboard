"""NSE FII/DII Data Dashboard — Track institutional investor flows."""

import html
import io
import logging
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

log = logging.getLogger(__name__)

from src.config import DB_PATH
from src.db import init_db, insert_record, query_all, get_today_snapshot, get_monthly_rollup, has_mock_data
from src.fetch import get_fiidii_data, get_nifty_history, generate_sample_data
from src.charts import (
    build_trend_chart,
    build_comparison_chart,
    build_rolling_avg_chart,
    build_fii_nifty_overlay,
)
from src.ai import generate_summary
from src.styles import render_css

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

# ─── Lucide SVGs ───────────────────────────────────────────
_II = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>'
_IN = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9 9 3 15 9 21 9 15 15 9 15Z"/><path d="M9 21V9"/></svg>'
_CA = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2v4M16 2v4M3 10h18"/><rect x="3" y="4" width="18" height="18" rx="2"/></svg>'
_RF = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M21 21v-5h-5"/></svg>'
_DL = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'
_WARN = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'

# ─── CSS ───────────────────────────────────────────────────
render_css()


# ─── Helpers ───────────────────────────────────────────────
def _section(icon_svg: str, label: str):
    st.markdown(f'<div class="hdr">{icon_svg} {html.escape(label)}</div><hr>', unsafe_allow_html=True)


def _metric_card(icon_svg: str, label: str, value: str, caption: str,
                 delta: str | None = None, color: str = "#64748b"):
    st.markdown(
        f'<div class="ml" style="color:{color}">{icon_svg} {label}</div>',
        unsafe_allow_html=True,
    )
    st.metric(label=label, value=value, delta=delta, label_visibility="collapsed")
    st.markdown(f'<div class="mc">{caption}</div>', unsafe_allow_html=True)


def _error_placeholder(section: str):
    st.markdown(
        f'<div class="error-placeholder">{_WARN} Could not load {section}. '
        f'Try refreshing the page.</div>',
        unsafe_allow_html=True,
    )


def _chart_unavailable():
    st.markdown(
        '<div class="empty">Chart unavailable — plotting library not loaded.</div>',
        unsafe_allow_html=True,
    )


# ─── Init DB ───────────────────────────────────────────────
conn = init_db(DB_PATH)
today_str = datetime.now().strftime("%d-%b-%Y")

# ─── Session state defaults ────────────────────────────────
if "nifty_prices" not in st.session_state:
    st.session_state.nifty_prices = None
if "data_fetched" not in st.session_state:
    st.session_state.data_fetched = False
if "seeded_sample" not in st.session_state:
    st.session_state.seeded_sample = False

# ─── Lazy-fill data ────────────────────────────────────────
today_snapshot = get_today_snapshot(conn)
if not today_snapshot:
    with st.spinner("Fetching today's FII/DII data from NSE..."):
        records = get_fiidii_data()
        if records:
            for r in records:
                insert_record(conn, r["date"], r["category"],
                              r["buy_value"], r["sell_value"], r["net_value"])
            st.session_state.data_fetched = True

all_records = query_all(conn)

# ─── Auto-seed sample data when DB is too thin ─────────────
_unique_dates = len(set(r["date"] for r in all_records))
if _unique_dates < 3 and not today_snapshot:
    sample = generate_sample_data(30)
    for r in sample:
        insert_record(conn, r["date"], r["category"],
                      r["buy_value"], r["sell_value"], r["net_value"],
                      source=r.get("source", "sample"))
    all_records = query_all(conn)
    st.session_state.seeded_sample = True

df_all = pd.DataFrame(all_records) if all_records else pd.DataFrame()

# ─── Date range bounds ─────────────────────────────────────
if not df_all.empty:
    df_all["date_parsed"] = pd.to_datetime(df_all["date"], format="%d-%b-%Y", errors="coerce")
    valid_dates = df_all["date_parsed"].dropna()
    min_date = valid_dates.min().date() if not valid_dates.empty else datetime.now().date() - timedelta(days=30)
    max_date = valid_dates.max().date() if not valid_dates.empty else datetime.now().date()
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
        min_value=datetime.now().date() - timedelta(days=60),
        max_value=datetime.now().date(),
        label_visibility="collapsed",
    )
    st.divider()

    st.markdown(f"**Actions** {_RF}", unsafe_allow_html=True)
    if st.button("Refresh data", width='stretch'):
        st.session_state.nifty_prices = None
        st.cache_resource.clear()
        st.rerun()

    if st.button("Load sample data (30d)", width='stretch'):
        sample = generate_sample_data(30)
        conn.execute("DELETE FROM fii_dii_data")
        for r in sample:
            insert_record(conn, r["date"], r["category"],
                          r["buy_value"], r["sell_value"], r["net_value"],
                          source=r.get("source", "sample"))
        st.session_state.nifty_prices = None
        st.session_state.seeded_sample = True
        st.rerun()
    st.caption("Replaces existing data with 30 days of mock data.")

    if not df_all.empty:
        buf = io.StringIO()
        df_all.to_csv(buf, index=False)
        st.markdown(f"{_DL}", unsafe_allow_html=True)
        st.download_button(
            label="Download CSV",
            data=buf.getvalue(),
            file_name=f"fiidii_data_{today_str}.csv",
            mime="text/csv",
            width='stretch',
        )
    st.divider()

    st.markdown("**About**")
    st.caption("Data: NSE India via nsepython")
    st.caption("License: AGPL v3")
    if today_snapshot:
        st.caption(f"Today's data loaded — {today_str}")
    elif st.session_state.data_fetched:
        st.caption(f"Fresh data fetched — {today_str}")
    elif st.session_state.seeded_sample or has_mock_data(conn):
        st.caption("Sample data — click Refresh for live NSE data")
    else:
        st.caption("Historical only (no new data)")
    st.caption(f"Records: {len(all_records)}")

# ─── Filter dates ──────────────────────────────────────────
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = (
    [r for r in all_records
     if start_date <= pd.to_datetime(r["date"], format="%d-%b-%Y").date() <= end_date]
    if not df_all.empty else []
)

# ─── Aggregate helpers ─────────────────────────────────────
def _range_aggregate(records: list[dict]) -> dict:
    """Aggregate filtered records into per-category totals."""
    groups: dict[str, dict] = {}
    for r in records:
        cat = r["category"]
        if cat not in groups:
            groups[cat] = {"buy_value": 0.0, "sell_value": 0.0, "net_value": 0.0}
        groups[cat]["buy_value"] += r["buy_value"]
        groups[cat]["sell_value"] += r["sell_value"]
        groups[cat]["net_value"] += r["net_value"]
    return groups


def _render_flow_cards(groups: dict, prefix: str = ""):
    """Render FII + DII metric cards from an aggregated group dict."""
    cols = st.columns(len(groups))
    cat_order = ["FII/FPI", "DII"]
    for i, cat in enumerate(cat_order):
        if cat not in groups:
            continue
        vals = groups[cat]
        with cols[i]:
            is_fii = cat == "FII/FPI"
            color = "#22C55E" if is_fii else "#EF4444"
            _metric_card(
                icon_svg=_II if is_fii else _IN,
                label=f"{cat}{prefix}",
                value=f"₹{vals['net_value']:,.0f} Cr",
                caption=f"Buy: ₹{vals['buy_value']:,.0f} Cr | Sell: ₹{vals['sell_value']:,.0f} Cr",
                color=color,
            )


_is_single_day = start_date == end_date
_range_label = start_date.strftime("%d-%b-%Y") if _is_single_day else f"{start_date.strftime('%d-%b')} – {end_date.strftime('%d-%b-%Y')}"

# ─── Section 1: Date Range Summary ─────────────────────────
_section(_II, _range_label)

if st.session_state.seeded_sample or has_mock_data(conn):
    st.warning(
        "**Sample data mode** — The values shown include mock data, not live NSE figures. "
        "Click **Refresh data** in the sidebar to fetch real NSE data."
    )

try:
    if filtered:
        groups = _range_aggregate(filtered)
        _render_flow_cards(groups)

        # AI Summary — inside try so `groups` is guaranteed to exist
        _fii_records = [r for r in filtered if r["category"] == "FII/FPI"]
        _fii_records.sort(key=lambda r: r["date"], reverse=True)
        _trend_days = 0
        if _fii_records:
            _sign = 1 if _fii_records[0]["net_value"] >= 0 else -1
            for _r in _fii_records:
                if (_r["net_value"] >= 0 and _sign > 0) or (_r["net_value"] < 0 and _sign < 0):
                    _trend_days += 1
                else:
                    break
        _fii_net = groups.get("FII/FPI", {}).get("net_value", 0)
        _dii_net = groups.get("DII", {}).get("net_value", 0)
        _summary = generate_summary(_fii_net, _dii_net, trend_days=_trend_days)
        st.info(_summary)
    else:
        st.markdown(
            '<div class="empty">No data for this date range. Adjust the filter or load sample data.</div>',
            unsafe_allow_html=True,
        )
except Exception as exc:
    log.warning("range summary render failed: %s", exc)
    _error_placeholder("range summary")

# ─── Section 2: Per-day breakdown (when range > 1 day) ─────
if not _is_single_day and filtered:
    _section(_CA, "Daily Cash Flow")
    try:
        # Group by date, show per-day FII/DII data in a compact table
        dates = sorted(set(r["date"] for r in filtered), reverse=True)
        for d in dates:
            day_records = [r for r in filtered if r["date"] == d]
            day_groups = _range_aggregate(day_records)
            summary = ", ".join(f"{k}: ₹{v['net_value']:,.0f} Cr" for k, v in day_groups.items())
            with st.expander(f"**{d}** — {summary}", expanded=False):
                _render_flow_cards(day_groups)
    except Exception as exc:
        log.warning("daily breakdown render failed: %s", exc)
        _error_placeholder("daily breakdown")

# ─── Section 3: Month-to-Date ──────────────────────────────
_section(_CA, "Month-to-Date")
try:
    now = datetime.now()
    monthly = get_monthly_rollup(conn, now.year, now.month)
    if monthly:
        monthly_groups = {r["category"]: r for r in monthly}
        _render_flow_cards(monthly_groups)
    else:
        st.markdown(
            '<div class="empty">No monthly data yet. Data accumulates daily.</div>',
            unsafe_allow_html=True,
        )
except Exception as exc:
    log.warning("monthly data render failed: %s", exc)
    _error_placeholder("monthly data")

# ─── Section 4: Charts ─────────────────────────────────────
_section(_RF, "Historical Trends")

if filtered:
    st.caption(f"Charting {len(filtered)} records across {len(set(r['date'] for r in filtered))} trading days")
    t1, t2, t3, t4 = st.tabs(["Net Flow Trend", "FII vs DII", "Rolling Averages", "FII vs Nifty"])

    with t1:
        try:
            fig, err = build_trend_chart(filtered)
            if fig is not None:
                st.altair_chart(fig, use_container_width=True)
            elif err:
                st.markdown(
                    f'<div class="empty">{_WARN} Chart library error: {err}</div>',
                    unsafe_allow_html=True,
                )
            else:
                _chart_unavailable()
        except Exception as exc:
            log.warning("trend chart render failed: %s", exc)
            _error_placeholder("trend chart")
    with t2:
        try:
            fig, err = build_comparison_chart(filtered)
            if fig is not None:
                st.altair_chart(fig, use_container_width=True)
            elif err:
                st.markdown(
                    f'<div class="empty">{_WARN} Chart library error: {err}</div>',
                    unsafe_allow_html=True,
                )
            else:
                _chart_unavailable()
        except Exception as exc:
            log.warning("comparison chart render failed: %s", exc)
            _error_placeholder("comparison chart")
    with t3:
        try:
            window = st.selectbox("Rolling window", [7, 15, 30], index=0, label_visibility="collapsed")
            fig, err = build_rolling_avg_chart(filtered, window=window)
            if fig is not None:
                st.altair_chart(fig, use_container_width=True)
            elif err:
                st.markdown(
                    f'<div class="empty">{_WARN} Chart library error: {err}</div>',
                    unsafe_allow_html=True,
                )
            else:
                _chart_unavailable()
        except Exception as exc:
            log.warning("rolling average chart render failed: %s", exc)
            _error_placeholder("rolling average chart")
    with t4:
        try:
            nifty_cache_key = (start_date.isoformat(), end_date.isoformat())
            if st.session_state.nifty_prices is None or st.session_state.get("nifty_cache_key") != nifty_cache_key:
                with st.spinner("Fetching Nifty prices..."):
                    st.session_state.nifty_prices = get_nifty_history(
                        start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
                    )
                    st.session_state.nifty_cache_key = nifty_cache_key
            fig, err = build_fii_nifty_overlay(filtered, nifty_prices=st.session_state.nifty_prices)
            if fig is not None:
                st.altair_chart(fig, use_container_width=True)
            elif err:
                st.markdown(
                    f'<div class="empty">{_WARN} Chart library error: {err}</div>',
                    unsafe_allow_html=True,
                )
            else:
                _chart_unavailable()
        except Exception as exc:
            log.warning("Nifty overlay chart render failed: %s", exc)
            _error_placeholder("Nifty overlay chart")

# ─── Footer ────────────────────────────────────────────────
sample_tag = " · Sample mode" if st.session_state.seeded_sample else ""
st.markdown(
    f'<div class="footer">'
    f'<span>FII/DII Dashboard · {_CA} {today_str}</span>'
    f'<span>{sample_tag}'
    f'AGPL v3 | '
    f'<a href="https://github.com/AshayK003/fii-dii-dashboard">GitHub</a></span></div>',
    unsafe_allow_html=True,
)
