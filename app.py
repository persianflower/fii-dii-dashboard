"""NSE FII/DII Data Dashboard — Streamlit app."""

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

st.set_page_config(
    page_title="FII/DII Data Dashboard",
    page_icon="📊",
    layout="centered",
)

st.title("NSE FII/DII Data Dashboard")
st.caption("Daily institutional investor flows — FII (Foreign) vs DII (Domestic)")


# ─── Init ─────────────────────────────────────────────────
conn = init_db(DB_PATH)


# ─── Data fetching (lazy-fill) ────────────────────────────
@st.cache_resource(ttl=3600)
def get_db_path():
    return DB_PATH


today_str = datetime.now().strftime("%d-%b-%Y")
today_snapshot = get_today_snapshot(conn)

if not today_snapshot:
    with st.spinner("Fetching today's FII/DII data from NSE..."):
        records = get_fiidii_data()
        if records:
            for r in records:
                insert_record(conn, r["date"], r["category"],
                              r["buy_value"], r["sell_value"], r["net_value"])
            st.success(f"Fetched data for {today_str}")
        else:
            st.info("Could not fetch today's data (market hours or NSE API). Showing historical data.")
else:
    st.caption(f"Latest data: {today_str} (cached)")


all_records = query_all(conn)
df_all = pd.DataFrame(all_records)

# Parse dates for filtering
if not df_all.empty:
    df_all["date_parsed"] = pd.to_datetime(df_all["date"], format="%d-%b-%Y", errors="coerce")
    min_date = df_all["date_parsed"].min().date()
    max_date = df_all["date_parsed"].max().date()
else:
    min_date = datetime.now().date() - timedelta(days=30)
    max_date = datetime.now().date()


# ─── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.header("Controls")

    date_range = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if st.button("🔄 Refresh today's data"):
        st.cache_resource.clear()
        st.rerun()

    st.divider()
    st.subheader("Export")

    if not df_all.empty:
        csv_buffer = io.StringIO()
        df_all.to_csv(csv_buffer, index=False)
        st.download_button(
            label="Download CSV",
            data=csv_buffer.getvalue(),
            file_name=f"fiidii_data_{today_str}.csv",
            mime="text/csv",
        )

    st.divider()
    st.caption("Data source: NSE India via nsepython")
    st.caption("License: AGPL v3")


# ─── Filter data ──────────────────────────────────────────
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = [r for r in all_records
            if start_date <= pd.to_datetime(r["date"], format="%d-%b-%Y").date() <= end_date]


# ─── Current Day Metrics ──────────────────────────────────
st.header("Today's Snapshot")

today_data = get_today_snapshot(conn)
if today_data:
    cols = st.columns(2)
    for i, record in enumerate(today_data):
        with cols[i]:
            delta = f"+{record['net_value']:,.0f}" if record['net_value'] >= 0 else f"{record['net_value']:,.0f}"
            st.metric(
                label=f"{record['category']} Net (₹ Cr)",
                value=f"₹{record['net_value']:,.0f}",
                delta=delta,
            )
            st.caption(f"Buy: ₹{record['buy_value']:,.0f} | Sell: ₹{record['sell_value']:,.0f}")

    # ─── AI Interpretation ─────────────────────────────────
    fii_row = next((r for r in today_data if r['category'] == 'FII/FPI'), None)
    dii_row = next((r for r in today_data if r['category'] == 'DII'), None)
    if fii_row:
        fii_net = fii_row['net_value']
        dii_net = dii_row['net_value'] if dii_row else 0.0
        # Trend detection: how many consecutive FII days in same direction?
        all_records_recent = query_all(conn)[-10:]
        trend_days = 0
        for r in reversed(all_records_recent):
            if r['category'] != 'FII/FPI':
                continue
            if (r['net_value'] >= 0 and fii_net >= 0) or (r['net_value'] < 0 and fii_net < 0):
                trend_days += 1
            else:
                break
        summary = generate_summary(fii_net, dii_net, today_str, trend_days)
        st.info(f"💡 {summary}")
else:
    st.info("No data for today. Data auto-fetches during market hours.")


# ─── Monthly Rollup ───────────────────────────────────────
st.header("Month-to-Date")
now = datetime.now()
monthly = get_monthly_rollup(conn, now.year, now.month)
if monthly:
    cols = st.columns(len(monthly))
    for i, row in enumerate(monthly):
        with cols[i]:
            delta = f"+{row['net_value']:,.0f}" if row['net_value'] >= 0 else f"{row['net_value']:,.0f}"
            st.metric(
                label=f"{row['category']} MTD (₹ Cr)",
                value=f"₹{row['net_value']:,.0f}",
                delta=delta,
            )
            st.caption(f"Buy: ₹{row['buy_value']:,.0f} | Sell: ₹{row['sell_value']:,.0f}")


# ─── Charts ───────────────────────────────────────────────
st.header("Historical Trends")

if len(filtered) >= 2:
    tab1, tab2, tab3, tab4 = st.tabs([
        "Net Flow Trend", "FII vs DII", "Rolling Averages", "FII vs Nifty"
    ])

    with tab1:
        fig1 = build_trend_chart(filtered)
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        fig2 = build_comparison_chart(filtered)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        window = st.selectbox("Rolling window", [7, 15, 30], index=0)
        fig3 = build_rolling_avg_chart(filtered, window=window)
        st.plotly_chart(fig3, use_container_width=True)

    with tab4:
        nifty_prices = get_nifty_history(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
        )
        fig4 = build_fii_nifty_overlay(filtered, nifty_prices=nifty_prices)
        st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("Need at least 2 days of data to display charts. Data accumulates daily.")
