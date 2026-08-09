import math

import pandas as pd
import pytest

from dashboard.ui_utils import (
    build_success_probability_curve,
    fmt_hashrate_from_ph,
    fmt_large_number,
    progress_pct,
    safe_num,
)


def test_safe_num_returns_value_when_present():
    assert safe_num(42.5) == 42.5


def test_safe_num_uses_default_for_nan():
    assert safe_num(float("nan"), default=7) == 7


def test_safe_num_uses_default_for_none():
    assert safe_num(None, default=9) == 9


def test_probability_curve_empty_when_expected_blocks_nonpositive():
    result = build_success_probability_curve(
        expected_blocks=0,
        duration_hours=2,
    )

    assert result.empty
    assert list(result.columns) == [
        "hours",
        "probability_pct",
    ]


def test_probability_curve_empty_when_duration_nonpositive():
    result = build_success_probability_curve(
        expected_blocks=1,
        duration_hours=0,
    )

    assert result.empty


def test_probability_curve_has_requested_number_of_points():
    result = build_success_probability_curve(
        expected_blocks=1,
        duration_hours=2,
        points=25,
    )

    assert len(result) == 25


def test_probability_curve_starts_at_zero():
    result = build_success_probability_curve(
        expected_blocks=1,
        duration_hours=2,
    )

    assert result.iloc[0]["hours"] == pytest.approx(0.0)
    assert result.iloc[0]["probability_pct"] == pytest.approx(0.0)


def test_probability_at_recommended_duration_matches_poisson_formula():
    expected_blocks = 0.8
    duration_hours = 2.0

    result = build_success_probability_curve(
        expected_blocks=expected_blocks,
        duration_hours=duration_hours,
        max_multiplier=1.0,
        points=2,
    )

    expected_probability = (
        1 - math.exp(-expected_blocks)
    ) * 100

    assert result.iloc[-1]["hours"] == pytest.approx(
        duration_hours
    )
    assert result.iloc[-1][
        "probability_pct"
    ] == pytest.approx(expected_probability)


def test_probability_curve_is_monotonic_increasing():
    result = build_success_probability_curve(
        expected_blocks=1,
        duration_hours=2,
    )

    assert result["hours"].is_monotonic_increasing
    assert result["probability_pct"].is_monotonic_increasing


@pytest.mark.parametrize(
    ("value_ph", "expected"),
    [
        (250, "250.00 PH/s"),
        (1, "1.00 PH/s"),
        (0.5, "500.00 TH/s"),
        (0.0005, "500.00 GH/s"),
        (0.0000005, "500.00 MH/s"),
        (None, "0.00 MH/s"),
    ],
)
def test_fmt_hashrate_from_ph(
    value_ph,
    expected,
):
    assert fmt_hashrate_from_ph(value_ph) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (999, "999"),
        (1_000, "1.00 K"),
        (1_000_000, "1.00 M"),
        (1_000_000_000, "1.00 B"),
        (1_000_000_000_000, "1.00 T"),
        (-1_500_000, "-1.50 M"),
        (None, "0"),
    ],
)
def test_fmt_large_number(
    value,
    expected,
):
    assert fmt_large_number(value) == expected


@pytest.mark.parametrize(
    ("value", "max_value", "expected"),
    [
        (50, 100, 50),
        (25, 50, 50),
        (150, 100, 100),
        (-10, 100, 0),
        (0, 100, 0),
        (100, 0, 0),
        (100, -1, 0),
    ],
)
def test_progress_pct(
    value,
    max_value,
    expected,
):
    assert progress_pct(
        value,
        max_value,
    ) == expected


def test_progress_pct_uses_default_max_for_nan():
    result = progress_pct(
        50,
        float("nan"),
    )

    assert result == 50
