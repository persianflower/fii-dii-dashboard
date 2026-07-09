"""Tests for src/ai.py — AI summary generation."""

import pytest
from src.ai import generate_summary, _rule_based_summary


class TestRuleBasedSummary:

    def test_fii_buying_dii_buying(self):
        result = _rule_based_summary(1500.0, 800.0, 1)
        assert "bought" in result
        assert "Both FII and DII" in result

    def test_fii_selling_dii_buying(self):
        result = _rule_based_summary(-2000.0, 1000.0, 1)
        assert "sold" in result
        assert "DIIs stepped in" in result

    def test_fii_buying_dii_selling(self):
        result = _rule_based_summary(1000.0, -500.0, 1)
        assert "bought" in result
        assert "divergence" in result

    def test_both_selling(self):
        result = _rule_based_summary(-1500.0, -800.0, 1)
        assert "sold" in result
        assert "broad institutional caution" in result

    def test_consecutive_bearish_3_days(self):
        result = _rule_based_summary(-1200.0, 500.0, 3)
        assert "consecutive sessions" in result
        assert "bearish" in result

    def test_consecutive_bullish_3_days(self):
        result = _rule_based_summary(1200.0, -300.0, 3)
        assert "consecutive sessions" in result
        assert "bullish" in result


class TestGenerateSummary:

    def test_returns_string(self):
        result = generate_summary(1000.0, 500.0, "09-Jul-2026", 0, force_llm=False)
        assert isinstance(result, str)
        assert len(result) > 10

    def test_rule_based_formatting(self):
        result = generate_summary(-1234.56, 789.12, "09-Jul-2026", 0, force_llm=False)
        assert "₹" in result
        assert "Cr" in result

    def test_zero_values(self):
        result = generate_summary(0.0, 0.0, "09-Jul-2026", 0, force_llm=False)
        assert isinstance(result, str)
        assert len(result) > 0
