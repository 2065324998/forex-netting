"""FX trade and settlement data structures."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class FXTrade:
    """Represents a single FX spot or forward trade.

    The buyer purchases buy_amount of buy_currency and delivers
    sell_amount of sell_currency to the seller.

    Attributes:
        trade_id: Unique trade identifier
        trade_date: Date the trade was executed
        value_date: Settlement date for the trade
        buyer: Party buying the buy_currency
        seller: Party selling the buy_currency
        buy_currency: Currency the buyer receives
        sell_currency: Currency the buyer delivers
        buy_amount: Amount of buy_currency exchanged
        sell_amount: Amount of sell_currency exchanged
    """
    trade_id: str
    trade_date: date
    value_date: date
    buyer: str
    seller: str
    buy_currency: str
    sell_currency: str
    buy_amount: float
    sell_amount: float

    def __post_init__(self):
        if self.buy_amount <= 0:
            raise ValueError(f"buy_amount must be positive, got {self.buy_amount}")
        if self.sell_amount <= 0:
            raise ValueError(f"sell_amount must be positive, got {self.sell_amount}")
        if self.buyer == self.seller:
            raise ValueError("buyer and seller must be different parties")
        if self.buy_currency == self.sell_currency:
            raise ValueError("buy_currency and sell_currency must differ")
        if self.value_date < self.trade_date:
            raise ValueError("value_date cannot be before trade_date")

    @property
    def rate(self):
        """Implied exchange rate (sell_currency per unit of buy_currency)."""
        return self.sell_amount / self.buy_amount


@dataclass(frozen=True)
class NetPosition:
    """A bilateral net obligation between two parties in a single currency.

    Attributes:
        party_a: First party (alphabetically ordered)
        party_b: Second party (alphabetically ordered)
        currency: Settlement currency
        value_date: Settlement date
        net_amount: Net amount party_a must deliver to party_b.
                    Positive means party_a pays party_b.
                    Negative means party_b pays party_a.
    """
    party_a: str
    party_b: str
    currency: str
    value_date: date
    net_amount: float


@dataclass(frozen=True)
class SettlementInstruction:
    """A payment instruction for settling a net FX position.

    Attributes:
        payer: Party making the payment
        receiver: Party receiving the payment
        currency: Payment currency
        amount: Payment amount (always positive)
        value_date: Payment date
    """
    payer: str
    receiver: str
    currency: str
    amount: float
    value_date: date
