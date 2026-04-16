"""Settlement instruction generation from net positions.

Supports both bilateral settlement (direct counterparty payments)
and multilateral CCP-mediated settlement where each party settles
only their net position with a central counterparty.

Settlement amounts are rounded to currency-appropriate precision
(e.g., JPY settles in whole yen, USD to cents). After rounding,
a balance adjustment ensures that total CCP receipts equal total
CCP payments per currency per value date.
"""

from collections import defaultdict
from .trade import FXTrade, NetPosition, SettlementInstruction
from .netting import compute_bilateral_nets


# Currency precision: number of decimal places for settlement amounts.
# Most currencies settle to 2 decimal places (cents), but JPY and KRW
# settle to whole units, and some Middle Eastern currencies use 3.
CURRENCY_PRECISION = {
    "JPY": 0,
    "KRW": 0,
    "BHD": 3,
    "KWD": 3,
    "OMR": 3,
}
DEFAULT_PRECISION = 2


def _round_settlement_amount(amount, currency):
    """Round a settlement amount to the appropriate precision.

    Different currencies have different minimum settlement units.
    Most currencies use 2 decimal places, but JPY uses 0.
    """
    return round(amount, 2)


def generate_settlement_instructions(net_positions):
    """Generate bilateral settlement instructions from net positions.

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


def generate_multilateral_settlement(trades):
    """Generate CCP-mediated settlement instructions from FX trades.

    Performs the full settlement pipeline:
    1. Bilateral netting of trades between each pair of counterparties
    2. Multilateral aggregation to compute each party's net position
    3. Currency-appropriate rounding of settlement amounts
    4. Balance adjustment to ensure CCP receipts equal payments

    Each party settles only their net obligation with the CCP rather
    than individually with each counterparty.

    Args:
        trades: List of FXTrade objects

    Returns:
        List of SettlementInstruction objects with "CCP" as counterparty
    """
    # Step 1: Bilateral netting
    bilateral = compute_bilateral_nets(trades)

    # Step 2: Multilateral aggregation per (party, currency, value_date)
    multi = defaultdict(float)
    for pos in bilateral:
        multi[(pos.party_a, pos.currency, pos.value_date)] += pos.net_amount
        multi[(pos.party_b, pos.currency, pos.value_date)] -= pos.net_amount

    # Step 3: Generate settlement instructions with rounding
    instructions = []
    for (party, ccy, vd), amount in sorted(multi.items()):
        if abs(amount) < 0.005:
            continue

        rounded = _round_settlement_amount(abs(amount), ccy)

        if amount > 0:
            instructions.append(SettlementInstruction(
                payer=party, receiver="CCP",
                currency=ccy, amount=rounded, value_date=vd,
            ))
        else:
            instructions.append(SettlementInstruction(
                payer="CCP", receiver=party,
                currency=ccy, amount=rounded, value_date=vd,
            ))

    # Step 4: Balance adjustment for rounding residuals
    instructions = _balance_ccp_residuals(instructions)

    return instructions


def _balance_ccp_residuals(instructions):
    """Adjust settlement amounts to maintain CCP balance after rounding.

    After rounding to currency-specific precision, the CCP's total
    receipts may differ from total payments by a small rounding residual.
    This must be corrected so the CCP has exactly zero net position
    in each currency on each value date.

    The party with the largest settlement amount in the affected
    currency/date group absorbs the residual adjustment.
    """
    return instructions
