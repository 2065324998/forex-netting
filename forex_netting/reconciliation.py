"""Nostro account position reconciliation.

Computes expected nostro account balance changes based on
settlement instructions. A nostro account is a bank's account
held at a correspondent bank in a foreign currency.
"""

from collections import defaultdict
from .trade import SettlementInstruction


def compute_nostro_positions(instructions, party):
    """Compute expected nostro position changes for a party.

    For each currency, calculates the net change in the party's
    nostro account based on settlement instructions where the
    party is either payer or receiver.

    Args:
        instructions: List of SettlementInstruction objects
        party: The party whose nostro positions to compute

    Returns:
        Dict mapping (currency, value_date) to position change.
        Positive means the party receives (nostro balance increases).
        Negative means the party pays (nostro balance decreases).
    """
    positions = defaultdict(float)

    for instr in instructions:
        if instr.payer == party:
            # Party pays: nostro decreases
            positions[(instr.currency, instr.value_date)] -= instr.amount
        elif instr.receiver == party:
            # Party receives: nostro increases
            positions[(instr.currency, instr.value_date)] += instr.amount

    return {k: round(v, 2) for k, v in positions.items() if abs(v) > 0.005}
