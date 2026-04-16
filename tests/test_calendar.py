"""Tests for business day calendar and settlement dates."""

import pytest
from datetime import date
from forex_netting import compute_value_date, is_business_day


class TestBusinessDay:
    def test_weekday_is_business(self):
        assert is_business_day(date(2024, 3, 18))  # Monday

    def test_saturday_not_business(self):
        assert not is_business_day(date(2024, 3, 16))

    def test_sunday_not_business(self):
        assert not is_business_day(date(2024, 3, 17))

    def test_usd_holiday(self):
        assert not is_business_day(date(2024, 7, 4), "USD")

    def test_jpy_holiday(self):
        assert not is_business_day(date(2024, 1, 2), "JPY")

    def test_non_holiday_weekday(self):
        assert is_business_day(date(2024, 3, 18), "USD")


class TestValueDate:
    def test_t_plus_2_simple(self):
        """Monday trade -> Wednesday settlement."""
        vd = compute_value_date(date(2024, 3, 18))
        assert vd == date(2024, 3, 20)

    def test_t_plus_2_over_weekend(self):
        """Thursday trade -> Monday settlement (skip weekend)."""
        vd = compute_value_date(date(2024, 3, 14))
        assert vd == date(2024, 3, 18)

    def test_t_plus_2_friday(self):
        """Friday trade -> Tuesday settlement."""
        vd = compute_value_date(date(2024, 3, 15))
        assert vd == date(2024, 3, 19)

    def test_t_plus_1(self):
        """T+1 settlement."""
        vd = compute_value_date(date(2024, 3, 18), settlement_lag=1)
        assert vd == date(2024, 3, 19)
