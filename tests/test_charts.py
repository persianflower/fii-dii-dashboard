"""Tests for the charts module."""

import pytest
import pandas as pd
import plotly.graph_objects as go

from src.charts import build_trend_chart, build_comparison_chart, build_rolling_avg_chart


@pytest.fixture
def sample_data():
    """Realistic FII/DII sample data spanning 5 days."""
    return [
        {"date": "06-Jul-2026", "category": "FII/FPI", "buy_value": 17000.0, "sell_value": 15500.0, "net_value": 1500.0},
        {"date": "06-Jul-2026", "category": "DII", "buy_value": 8000.0, "sell_value": 9000.0, "net_value": -1000.0},
        {"date": "07-Jul-2026", "category": "FII/FPI", "buy_value": 16500.0, "sell_value": 15000.0, "net_value": 1500.0},
        {"date": "07-Jul-2026", "category": "DII", "buy_value": 7500.0, "sell_value": 8500.0, "net_value": -1000.0},
        {"date": "08-Jul-2026", "category": "FII/FPI", "buy_value": 17463.95, "sell_value": 15501.15, "net_value": 1962.8},
        {"date": "08-Jul-2026", "category": "DII", "buy_value": 19165.13, "sell_value": 18374.97, "net_value": 790.16},
        {"date": "09-Jul-2026", "category": "FII/FPI", "buy_value": 18000.0, "sell_value": 16000.0, "net_value": 2000.0},
        {"date": "09-Jul-2026", "category": "DII", "buy_value": 9000.0, "sell_value": 10000.0, "net_value": -1000.0},
        {"date": "10-Jul-2026", "category": "FII/FPI", "buy_value": 17500.0, "sell_value": 15800.0, "net_value": 1700.0},
        {"date": "10-Jul-2026", "category": "DII", "buy_value": 8500.0, "sell_value": 9200.0, "net_value": -700.0},
    ]


class TestTrendChart:
    def test_returns_plotly_figure(self, sample_data):
        fig, err = build_trend_chart(sample_data)
        assert err is None
        assert isinstance(fig, go.Figure)

    def test_has_two_traces(self, sample_data):
        fig, err = build_trend_chart(sample_data)
        assert err is None
        assert len(fig.data) >= 2

    def test_fii_trace_has_correct_values(self, sample_data):
        fig, err = build_trend_chart(sample_data)
        assert err is None
        fii_net = [1500.0, 1500.0, 1962.8, 2000.0, 1700.0]
        for trace in fig.data[:2]:
            if list(trace.y) == fii_net:
                return
        for trace in fig.data[:2]:
            if all(abs(a - b) < 1 for a, b in zip(list(trace.y), fii_net)):
                return
        pytest.fail("FII trace with correct values not found")

    def test_empty_data_returns_figure(self):
        fig, err = build_trend_chart([])
        assert err is None
        assert isinstance(fig, go.Figure)

    def test_single_day_returns_figure(self, sample_data):
        fig, err = build_trend_chart(sample_data[:2])
        assert err is None
        assert isinstance(fig, go.Figure)


class TestComparisonChart:
    def test_returns_plotly_figure(self, sample_data):
        fig, err = build_comparison_chart(sample_data)
        assert err is None
        assert isinstance(fig, go.Figure)

    def test_has_traces(self, sample_data):
        fig, err = build_comparison_chart(sample_data)
        assert err is None
        assert len(fig.data) > 0


class TestRollingAvgChart:
    def test_returns_plotly_figure(self, sample_data):
        fig, err = build_rolling_avg_chart(sample_data, window=3)
        assert err is None
        assert isinstance(fig, go.Figure)

    def test_has_two_traces(self, sample_data):
        fig, err = build_rolling_avg_chart(sample_data, window=3)
        assert err is None
        assert len(fig.data) == 2

    def test_empty_data_returns_figure(self):
        fig, err = build_rolling_avg_chart([], window=3)
        assert err is None
        assert isinstance(fig, go.Figure)
