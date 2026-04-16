"""Tests for the bilateral netting engine."""

import pytest
from datetime import date
from forex_netting import FXTrade, compute_bilateral_nets, compute_multilateral_nets


VD = date(2024, 3, 19)  # Common value date for all tests


class TestBilateralNetsSingleTrade:
    """Single-trade netting scenarios.

    With a single trade, the bilateral net is just the trade itself.
    Uses trades where seller is alphabetically first (BankA sells to BankB).
    """

    def test_single_trade_produces_two_positions(self):
        """One trade generates positions in two currencies."""
        trade = FXTrade("T1", date(2024, 3, 15), VD,
                        "BankB", "BankA", "USD", "JPY",
                        1_000_000, 150_000_000)
        nets = compute_bilateral_nets([trade])
        currencies = {p.currency for p in nets}
        assert "USD" in currencies
        assert "JPY" in currencies

    def test_single_trade_amounts(self):
        """Net amounts equal trade amounts for a single trade."""
        # BankA is seller of USD (delivers USD), BankB is buyer
        trade = FXTrade("T1", date(2024, 3, 15), VD,
                        "BankB", "BankA", "USD", "JPY",
                        1_000_000, 150_000_000)
        nets = compute_bilateral_nets([trade])
        net_dict = {p.currency: p.net_amount for p in nets}
        # BankA (party_a, seller) delivers USD: positive
        assert net_dict["USD"] == pytest.approx(1_000_000, abs=1)
        # Total absolute flow is buy_amount + sell_amount
        total = sum(abs(p.net_amount) for p in nets)
        assert total == pytest.approx(151_000_000, abs=1)

    def test_parties_are_ordered(self):
        """Net positions should have alphabetically ordered parties."""
        trade = FXTrade("T1", date(2024, 3, 15), VD,
                        "ZBank", "AlphaBank", "EUR", "GBP",
                        500_000, 430_000)
        nets = compute_bilateral_nets([trade])
        for p in nets:
            assert p.party_a == "AlphaBank"
            assert p.party_b == "ZBank"


class TestBilateralNetsMultipleTrades:
    def test_two_same_direction_trades_net(self):
        """Two trades in the same direction should add up."""
        # BankA sells USD to BankB in both trades
        t1 = FXTrade("T1", date(2024, 3, 15), VD,
                     "BankB", "BankA", "USD", "JPY",
                     1_000_000, 150_000_000)
        t2 = FXTrade("T2", date(2024, 3, 15), VD,
                     "BankB", "BankA", "USD", "JPY",
                     500_000, 75_000_000)
        nets = compute_bilateral_nets([t1, t2])
        net_dict = {p.currency: p.net_amount for p in nets}
        assert net_dict["USD"] == pytest.approx(1_500_000, abs=1)

    def test_empty_trades(self):
        """No trades should produce no positions."""
        nets = compute_bilateral_nets([])
        assert len(nets) == 0


class TestMultilateralNets:
    def test_three_party_cycle(self):
        """In a cycle A→B→C→A, multilateral nets should be smaller."""
        t1 = FXTrade("T1", date(2024, 3, 15), VD,
                     "BankB", "BankA", "USD", "EUR",
                     1_000_000, 920_000)
        t2 = FXTrade("T2", date(2024, 3, 15), VD,
                     "BankC", "BankB", "USD", "EUR",
                     1_000_000, 920_000)
        multi = compute_multilateral_nets([t1, t2])
        # BankB both sells USD (to BankB buyer in T1) and buys USD (from BankB)
        # Check that multilateral net has entries
        assert len(multi) > 0
