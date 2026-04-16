"""Settlement instruction generation from bilateral net positions.

Converts net positions into actionable settlement instructions that
specify the payer, receiver, currency, amount, and settlement date
for each payment.
"""

from .trade import FXTrade, NetPosition, SettlementInstruction


def generate_settlement_instructions(net_positions):
    """Generate settlement instructions from bilateral net positions.

    For each net position, creates a settlement instruction directing
    the net payer to deliver the net amount to the net receiver.

    Args:
        net_positions: List of NetPosition objects from the netting engine

    Returns:
        List of SettlementInstruction objects
    """
    instructions = []

    for pos in net_positions:
        if abs(pos.net_amount) < 0.01:
            continue

        instructions.append(SettlementInstruction(
            payer=pos.party_a,
            receiver=pos.party_b,
            currency=pos.currency,
            amount=abs(pos.net_amount),
            value_date=pos.value_date,
        ))

    return instructions
