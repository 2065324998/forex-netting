# FX Settlement Netting Engine

A Python library for computing bilateral net positions and generating
settlement instructions for foreign exchange trades.

## Features

- FX trade representation with T+2 settlement date calculation
- Business day calendar with holiday support
- Bilateral netting engine (aggregates obligations by counterparty and currency)
- Settlement instruction generation from net positions
- Nostro account position tracking

## Usage

```python
from datetime import date
from forex_netting import FXTrade, compute_bilateral_nets, generate_settlement_instructions

trades = [
    FXTrade(
        trade_id="T001",
        trade_date=date(2024, 3, 15),
        value_date=date(2024, 3, 19),
        buyer="BankA",
        seller="BankB",
        buy_currency="USD",
        sell_currency="JPY",
        buy_amount=1_000_000.0,
        sell_amount=150_000_000.0,
    ),
]

nets = compute_bilateral_nets(trades)
instructions = generate_settlement_instructions(nets)
```

## Concepts

- **Bilateral netting**: Aggregation of multiple FX obligations between two
  parties into a single net amount per currency and settlement date.
- **Value date**: The date on which settlement occurs (typically T+2 for
  spot FX trades).
- **Settlement instruction**: A directive to pay or receive a specific
  amount of currency on a given date.
- **Nostro account**: A bank's account held at a correspondent bank in
  a foreign currency.
