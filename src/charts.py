"""Plotly chart builders for the FII/DII dashboard."""

from __future__ import annotations

from typing import Optional


def _records_to_df(records: list[dict]) -> "pd.DataFrame":
    """Convert DB records to a pivoted DataFrame with dates as index."""
    import pandas as pd  # lazy — avoids numpy/pandas version conflicts at import time

    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    df["date_parsed"] = pd.to_datetime(df["date"], format="%d-%b-%Y")
    return df.sort_values("date_parsed")


def _pivot_net(df: "pd.DataFrame") -> "pd.DataFrame":
    """Pivot for net values: columns = categories, index = date."""
    return df.pivot_table(
        index="date_parsed", columns="category", values="net_value", aggfunc="first"
    )


def _empty_figure(title: str = "No data available") -> "go.Figure":
    """Return an empty figure with a title."""
    import plotly.graph_objects as go  # lazy import

    return go.Figure().update_layout(title=title)


def build_trend_chart(records: list[dict]) -> "go.Figure":
    """Build a net FII/DII trend line chart."""
    import plotly.graph_objects as go  # lazy import

    df = _records_to_df(records)
    if df.empty:
        return _empty_figure()

    pivoted = _pivot_net(df)
    fig = go.Figure()

    colors = {"FII/FPI": "#22C55E", "DII": "#EF4444"}

    for category in ["FII/FPI", "DII"]:
        if category in pivoted.columns:
            fig.add_trace(go.Scatter(
                x=pivoted.index,
                y=pivoted[category],
                mode="lines+markers",
                name=category,
                line=dict(color=colors.get(category, "#636363"), width=2),
                hovertemplate="%{y:,.2f}",
            ))

    fig.update_layout(
        title="FII/DII Net Flow (₹ Crores)",
        xaxis_title="Date",
        yaxis_title="Net Value (₹ Cr)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig


def build_comparison_chart(records: list[dict]) -> "go.Figure":
    """Build a grouped bar chart comparing FII vs DII net values."""
    import plotly.graph_objects as go  # lazy import

    df = _records_to_df(records)
    if df.empty:
        return _empty_figure()

    pivoted = _pivot_net(df)
    fig = go.Figure()

    for category in ["FII/FPI", "DII"]:
        if category in pivoted.columns:
            fig.add_trace(go.Bar(
                x=pivoted.index,
                y=pivoted[category],
                name=category,
                marker_color="#22C55E" if category == "FII/FPI" else "#EF4444",
            ))

    fig.update_layout(
        title="FII vs DII Daily Net Comparison",
        xaxis_title="Date",
        yaxis_title="Net Value (₹ Cr)",
        barmode="group",
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig


def build_rolling_avg_chart(records: list[dict], window: int = 7) -> "go.Figure":
    """Build a rolling average chart for FII and DII net flows."""
    import plotly.graph_objects as go  # lazy import

    df = _records_to_df(records)
    if df.empty:
        return _empty_figure()

    pivoted = _pivot_net(df)
    fig = go.Figure()
    colors = {"FII/FPI": "#22C55E", "DII": "#EF4444"}

    for category in ["FII/FPI", "DII"]:
        if category in pivoted.columns and len(pivoted) >= window:
            rolling = pivoted[category].rolling(window=window, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=pivoted.index,
                y=rolling,
                mode="lines",
                name=f"{category} ({window}D MA)",
                line=dict(color=colors.get(category, "#636363"), width=2, dash="dash"),
                hovertemplate="%{y:,.2f}",
            ))

    fig.update_layout(
        title=f"{window}-Day Rolling Average Net Flow (₹ Crores)",
        xaxis_title="Date",
        yaxis_title="Net Value (₹ Cr)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig


def build_fii_nifty_overlay(records: list[dict], nifty_prices: Optional[dict[str, float]] = None) -> "go.Figure":
    """Dual-axis chart: FII net flow + Nifty closing price."""
    import plotly.graph_objects as go  # lazy import
    from plotly.subplots import make_subplots  # lazy import

    df = _records_to_df(records)
    if df.empty:
        return _empty_figure()

    fii_data = df[df["category"] == "FII/FPI"]
    if fii_data.empty:
        return _empty_figure("No FII data available")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=fii_data["date_parsed"],
            y=fii_data["net_value"],
            mode="lines+markers",
            name="FII Net (₹ Cr)",
            line=dict(color="#22C55E", width=2),
        ),
        secondary_y=False,
    )

    if nifty_prices:
        import pandas as pd  # lazy import

        dates = pd.to_datetime(list(nifty_prices.keys()), format="%d-%b-%Y")
        prices = list(nifty_prices.values())
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=prices,
                mode="lines",
                name="Nifty 50",
                line=dict(color="#636363", width=2, dash="dot"),
            ),
            secondary_y=True,
        )

    fig.update_layout(
        title="FII Net Flow vs Nifty 50",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=40, r=20, t=40, b=40),
    )
    fig.update_yaxes(title_text="FII Net (₹ Cr)", secondary_y=False)
    fig.update_yaxes(title_text="Nifty 50", secondary_y=True)
    return fig
