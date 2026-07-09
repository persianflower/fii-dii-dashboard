"""Tests for the fetch layer."""

import pytest
from unittest.mock import patch, MagicMock

from src.fetch import parse_fiidii_row, get_fiidii_data, get_nifty_price


class TestParseFiidiiRow:
    """String → float parsing with NSE format."""

    def test_basic_parse(self):
        raw = {"category": "FII/FPI", "date": "09-Jul-2026",
               "buyValue": "17463.95", "sellValue": "15501.15", "netValue": "1962.8"}
        parsed = parse_fiidii_row(raw)
        assert parsed["category"] == "FII/FPI"
        assert parsed["buy_value"] == 17463.95
        assert parsed["sell_value"] == 15501.15
        assert parsed["net_value"] == 1962.8
        assert parsed["date"] == "09-Jul-2026"

    def test_negative_net(self):
        raw = {"category": "DII", "date": "09-Jul-2026",
               "buyValue": "500", "sellValue": "700", "netValue": "-200"}
        parsed = parse_fiidii_row(raw)
        assert parsed["net_value"] == -200.0

    def test_large_values(self):
        raw = {"category": "FII/FPI", "date": "01-Jan-2026",
               "buyValue": "123456.78", "sellValue": "98765.43", "netValue": "24691.35"}
        parsed = parse_fiidii_row(raw)
        assert parsed["buy_value"] == 123456.78
        assert parsed["net_value"] == 24691.35

    def test_empty_string_returns_none(self):
        raw = {"category": "", "date": "", "buyValue": "", "sellValue": "", "netValue": ""}
        parsed = parse_fiidii_row(raw)
        assert parsed is None

    def test_missing_keys_returns_none(self):
        assert parse_fiidii_row({"category": "FII/FPI"}) is None
        assert parse_fiidii_row({}) is None


class TestGetFiidiiData:
    """Integration-adjacent: mocking nsepython."""

    @patch("src.fetch.nse")
    def test_returns_parsed_records(self, mock_nse):
        mock_nse.nse_fiidii.return_value = [
            {"category": "FII/FPI", "date": "09-Jul-2026",
             "buyValue": "17463.95", "sellValue": "15501.15", "netValue": "1962.8"},
            {"category": "DII", "date": "09-Jul-2026",
             "buyValue": "5000.0", "sellValue": "6000.0", "netValue": "-1000.0"},
        ]
        result = get_fiidii_data()
        assert len(result) == 2
        assert result[0]["category"] == "FII/FPI"
        assert result[0]["net_value"] == 1962.8

    @patch("src.fetch.nse")
    def test_handles_empty_response(self, mock_nse):
        mock_nse.nse_fiidii.return_value = []
        assert get_fiidii_data() == []

    @patch("src.fetch.nse")
    def test_handles_nse_error(self, mock_nse):
        mock_nse.nse_fiidii.side_effect = Exception("NSE API unavailable")
        assert get_fiidii_data() == []


class TestGetNiftyPrice:

    @patch("src.fetch.yf")
    def test_returns_close_price(self, mock_yf):
        import pandas as pd
        hist = pd.DataFrame({"Close": [24400.0, 24450.0, 24500.50]})
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = hist
        mock_yf.Ticker.return_value = mock_ticker

        price = get_nifty_price()
        assert price == 24500.50

    @patch("src.fetch.yf")
    def test_returns_none_on_failure(self, mock_yf):
        mock_yf.Ticker.side_effect = Exception("yfinance error")
        assert get_nifty_price() is None
