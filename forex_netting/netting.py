"""Bilateral and multilateral FX netting engine.

Computes net obligations between counterparties by aggregating individual
trade-level currency flows into bilateral net positions. Each FX trade
generates two obligations — one for each currency leg — which are then
netted across all trades between a given pair of counterparties.

The netting process reduces the number of settlement payments required,
lowering operational risk and liquidity requirements.
"""

from collections import defaultdict
from .trade import FXTrade, NetPosition


def _ordered_pair(party1, party2):
    """Return parties in canonical alphabetical order."""
    if party1 <= party2:
        return party1, party2
    return party2, party1


def compute_bilateral_nets(trades):
    """Compute bilateral net positions from a list of FX trades.

    For each pair of counterparties, aggregates all currency obligations
    across their trades to produce a single net amount per currency.
    The net amount represents the delivery obligation from the
    alphabetically-first party to the second party.

    A positive net_amount means party_a must deliver to party_b.
    A negative net_amount means party_b must deliver to party_a.

    Args:
        trades: List of FXTrade objects

    Returns:
        List of NetPosition objects with non-zero net amounts
    """
    # Accumulate net flows: key is (party_a, party_b, currency)
    # Value is net amount party_a must deliver to party_b
    flows = defaultdict(float)

    for trade in trades:
        party_a, party_b = _ordered_pair(trade.buyer, trade.seller)

        # Determine delivery direction relative to party_a
        # The SELLER delivers buy_currency to the buyer
        if trade.seller == party_a:
            # party_a is seller: party_a delivers buy_currency
            buy_direction = 1
        else:
            # party_b is seller: party_a receives buy_currency
            buy_direction = -1

        # For the sell_currency leg, the seller receives sell_currency
        # (equivalently, the buyer delivers sell_currency)
        sell_direction = buy_direction

        # Accumulate both legs of the trade
        key_buy = (party_a, party_b, trade.buy_currency)
        flows[key_buy] += buy_direction * trade.buy_amount

        key_sell = (party_a, party_b, trade.sell_currency)
        flows[key_sell] += sell_direction * trade.sell_amount

    # Convert to NetPosition objects, filtering out near-zero positions
    positions = []
    for (pa, pb, ccy), amount in flows.items():
        if abs(amount) > 0.005:
            positions.append(NetPosition(
                party_a=pa,
                party_b=pb,
                currency=ccy,
                value_date=_latest_value_date(trades, pa, pb),
                net_amount=round(amount, 2),
            ))

    return positions


def _latest_value_date(trades, party_a, party_b):
    """Get the latest value date among trades between two parties."""
    dates = []
    for t in trades:
        pa, pb = _ordered_pair(t.buyer, t.seller)
        if pa == party_a and pb == party_b:
            dates.append(t.value_date)
    return max(dates) if dates else None


def compute_multilateral_nets(trades):
    """Compute each party's multilateral net position per currency.

    The multilateral net is the sum of all bilateral net positions
    for a given party across all counterparties. This represents
    the total amount each party must deliver to (or receive from)
    the group as a whole.

    Args:
        trades: List of FXTrade objects

    Returns:
        Dict mapping (party, currency) to net amount.
        Positive means the party is a net deliverer.
    """
    bilateral = compute_bilateral_nets(trades)
    multi = defaultdict(float)

    for pos in bilateral:
        # party_a's delivery to party_b
        multi[(pos.party_a, pos.currency)] += pos.net_amount
        # party_b's delivery to party_a (opposite sign)
        multi[(pos.party_b, pos.currency)] -= pos.net_amount

    return {k: round(v, 2) for k, v in multi.items() if abs(v) > 0.005}
