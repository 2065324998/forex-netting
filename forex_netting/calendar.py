"""Business day calendar and settlement date calculations.

Provides utilities for determining T+2 settlement dates and
checking business day status across different currency calendars.
"""

from datetime import date, timedelta

# Standard weekend days
_WEEKEND = {5, 6}  # Saturday, Sunday

# Known holidays by currency (simplified — major holidays only)
_HOLIDAYS = {
    "USD": {
        date(2024, 1, 1),   # New Year
        date(2024, 1, 15),  # MLK Day
        date(2024, 2, 19),  # Presidents Day
        date(2024, 5, 27),  # Memorial Day
        date(2024, 6, 19),  # Juneteenth
        date(2024, 7, 4),   # Independence Day
        date(2024, 9, 2),   # Labor Day
        date(2024, 11, 28), # Thanksgiving
        date(2024, 12, 25), # Christmas
    },
    "EUR": {
        date(2024, 1, 1),   # New Year
        date(2024, 3, 29),  # Good Friday
        date(2024, 4, 1),   # Easter Monday
        date(2024, 5, 1),   # Labour Day
        date(2024, 12, 25), # Christmas
        date(2024, 12, 26), # St Stephen
    },
    "GBP": {
        date(2024, 1, 1),   # New Year
        date(2024, 3, 29),  # Good Friday
        date(2024, 4, 1),   # Easter Monday
        date(2024, 5, 6),   # Early May
        date(2024, 5, 27),  # Spring Bank Holiday
        date(2024, 8, 26),  # Summer Bank Holiday
        date(2024, 12, 25), # Christmas
        date(2024, 12, 26), # Boxing Day
    },
    "JPY": {
        date(2024, 1, 1),   # New Year
        date(2024, 1, 2),   # Bank Holiday
        date(2024, 1, 3),   # Bank Holiday
        date(2024, 1, 8),   # Coming of Age
        date(2024, 2, 11),  # National Foundation
        date(2024, 2, 12),  # Observed
        date(2024, 2, 23),  # Emperor's Birthday
        date(2024, 3, 20),  # Vernal Equinox
        date(2024, 4, 29),  # Showa Day
        date(2024, 5, 3),   # Constitution Day
        date(2024, 5, 6),   # Observed
        date(2024, 7, 15),  # Marine Day
        date(2024, 8, 12),  # Mountain Day Observed
        date(2024, 9, 16),  # Respect for Aged
        date(2024, 9, 22),  # Autumnal Equinox
        date(2024, 9, 23),  # Observed
        date(2024, 10, 14), # Sports Day
        date(2024, 11, 3),  # Culture Day
        date(2024, 11, 4),  # Observed
        date(2024, 11, 23), # Labor Thanksgiving
        date(2024, 12, 31), # Bank Holiday
    },
    "CHF": {
        date(2024, 1, 1),   # New Year
        date(2024, 1, 2),   # Berchtold
        date(2024, 3, 29),  # Good Friday
        date(2024, 4, 1),   # Easter Monday
        date(2024, 5, 1),   # Labour Day
        date(2024, 5, 9),   # Ascension
        date(2024, 5, 20),  # Whit Monday
        date(2024, 8, 1),   # National Day
        date(2024, 12, 25), # Christmas
        date(2024, 12, 26), # St Stephen
    },
}


def is_business_day(d, currency=None):
    """Check if a date is a business day.

    Args:
        d: Date to check
        currency: If provided, also check currency-specific holidays

    Returns:
        True if d is a business day
    """
    if d.weekday() in _WEEKEND:
        return False
    if currency and currency in _HOLIDAYS:
        if d in _HOLIDAYS[currency]:
            return False
    return True


def next_business_day(d, currency=None):
    """Find the next business day on or after d.

    Args:
        d: Starting date
        currency: Currency calendar to use

    Returns:
        The next business day
    """
    while not is_business_day(d, currency):
        d += timedelta(days=1)
    return d


def compute_value_date(trade_date, settlement_lag=2, currency=None):
    """Compute the settlement (value) date for an FX trade.

    Standard FX spot trades settle T+2 (two business days after
    the trade date).

    Args:
        trade_date: Date the trade was executed
        settlement_lag: Number of business days (default 2 for spot)
        currency: Currency calendar for holiday checking

    Returns:
        Settlement date
    """
    d = trade_date
    days_counted = 0
    while days_counted < settlement_lag:
        d += timedelta(days=1)
        if is_business_day(d, currency):
            days_counted += 1
    return d
