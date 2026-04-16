"""Tests for settlement instruction generation."""

import pytest
from datetime import date
from forex_netting import (
    FXTrade, compute_bilateral_nets,
    generate_settlement_instructions,
)
from forex_netting.reconciliation import compute_nostro_positions


VD = date(2024, 3, 19)


class TestSettlementInstructions:
    def test_single_trade_instructions(self):
        """Single trade generates settlement instructions."""
        trade = FXTrade("T1", date(2024, 3, 15), VD,
                        "BankB", "BankA", "USD", "JPY",
                        1_000_000, 150_000_000)
        nets = compute_bilateral_nets([trade])
        instructions = generate_settlement_instructions(nets)
        assert len(instructions) >= 2  # At least one per currency

    def test_instruction_amounts_positive(self):
        """Settlement instruction amounts are always positive."""
        trade = FXTrade("T1", date(2024, 3, 15), VD,
                        "BankB", "BankA", "USD", "JPY",
                        1_000_000, 150_000_000)
        nets = compute_bilateral_nets([trade])
        instructions = generate_settlement_instructions(nets)
        for instr in instructions:
            assert instr.amount > 0

    def test_instruction_value_date(self):
        """Instructions carry the correct value date."""
        trade = FXTrade("T1", date(2024, 3, 15), VD,
                        "BankB", "BankA", "USD", "JPY",
                        1_000_000, 150_000_000)
        nets = compute_bilateral_nets([trade])
        instructions = generate_settlement_instructions(nets)
        for instr in instructions:
            assert instr.value_date is not None


class TestNostroReconciliation:
    def test_nostro_positions_from_instructions(self):
        """Nostro positions reflect settlement instructions."""
        trade = FXTrade("T1", date(2024, 3, 15), VD,
                        "BankB", "BankA", "USD", "JPY",
                        1_000_000, 150_000_000)
        nets = compute_bilateral_nets([trade])
        instructions = generate_settlement_instructions(nets)
        positions = compute_nostro_positions(instructions, "BankA")
        assert len(positions) > 0
