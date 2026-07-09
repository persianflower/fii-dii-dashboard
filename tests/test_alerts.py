"""Tests for src/alerts.py — Telegram alert logic."""

import pytest
from src.alerts import check_threshold


class TestCheckThreshold:

    def test_no_alert_below_threshold(self):
        records = [
            {"category": "FII/FPI", "net_value": 500.0},
            {"category": "DII", "net_value": 300.0},
        ]
        result = check_threshold(records, threshold=1000.0)
        assert result is None

    def test_alert_above_threshold(self):
        records = [
            {"category": "FII/FPI", "net_value": 1500.0},
            {"category": "DII", "net_value": -500.0},
        ]
        result = check_threshold(records, threshold=1000.0)
        assert result is not None
        assert "buyers" in result
        assert "₹" in result

    def test_alert_above_threshold_negative(self):
        records = [
            {"category": "FII/FPI", "net_value": -2500.0},
            {"category": "DII", "net_value": 1200.0},
        ]
        result = check_threshold(records, threshold=1000.0)
        assert result is not None
        assert "sellers" in result
        assert "DIIs absorbed" in result

    def test_both_selling_alert(self):
        records = [
            {"category": "FII/FPI", "net_value": -3000.0},
            {"category": "DII", "net_value": -500.0},
        ]
        result = check_threshold(records, threshold=1000.0)
        assert result is not None
        assert "broad institutional caution" in result

    def test_no_fii_data_returns_none(self):
        records = [{"category": "DII", "net_value": 500.0}]
        result = check_threshold(records)
        assert result is None

    def test_empty_records_returns_none(self):
        result = check_threshold([])
        assert result is None

    def test_heavy_flow_uses_intensity(self):
        records = [
            {"category": "FII/FPI", "net_value": 3500.0},
            {"category": "DII", "net_value": -1000.0},
        ]
        result = check_threshold(records, threshold=1000.0)
        assert result is not None
        assert "heavily" in result  # >= 2x threshold
