"""Tests for FX trade data structures."""

import pytest
from datetime import date
from forex_netting import FXTrade


class TestFXTrade:
    def test_create_trade(self):
        t = FXTrade("T001", date(2024, 3, 15), date(2024, 3, 19),
                    "BankA", "BankB", "USD", "JPY", 1_000_000, 150_000_000)
        assert t.trade_id == "T001"
        assert t.buy_amount == 1_000_000
        assert t.sell_amount == 150_000_000

    def test_rate_property(self):
        t = FXTrade("T001", date(2024, 3, 15), date(2024, 3, 19),
                    "BankA", "BankB", "USD", "JPY", 1_000_000, 150_000_000)
        assert t.rate == pytest.approx(150.0, abs=0.01)

    def test_negative_amount_rejected(self):
        with pytest.raises(ValueError):
            FXTrade("T001", date(2024, 3, 15), date(2024, 3, 19),
                    "BankA", "BankB", "USD", "JPY", -100, 150_000_000)

    def test_same_party_rejected(self):
        with pytest.raises(ValueError):
            FXTrade("T001", date(2024, 3, 15), date(2024, 3, 19),
                    "BankA", "BankA", "USD", "JPY", 1_000_000, 150_000_000)

    def test_same_currency_rejected(self):
        with pytest.raises(ValueError):
            FXTrade("T001", date(2024, 3, 15), date(2024, 3, 19),
                    "BankA", "BankB", "USD", "USD", 1_000_000, 150_000_000)

    def test_value_before_trade_rejected(self):
        with pytest.raises(ValueError):
            FXTrade("T001", date(2024, 3, 15), date(2024, 3, 14),
                    "BankA", "BankB", "USD", "JPY", 1_000_000, 150_000_000)
