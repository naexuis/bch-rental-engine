from scripts.bch_solo_rental_strike_engine import (
    calculate_numeric_trend,
)

def test_calculate_numeric_trend_improving():
    trend = calculate_numeric_trend(
        [50, 52, 55],
    )

    assert trend["count"] == 3
    assert trend["current"] == 55
    assert trend["previous"] == 52
    assert trend["change"] == 3
    assert trend["direction"] == "IMPROVING"

def test_calculate_numeric_trend_declining():
    trend = calculate_numeric_trend(
        [60, 58, 55],
    )

    assert trend["direction"] == "DECLINING"
    assert trend["change"] == -3

def test_calculate_numeric_trend_stable():
    trend = calculate_numeric_trend(
        [54, 54],
    )

    assert trend["direction"] == "STABLE"
    assert trend["change"] == 0

def test_calculate_numeric_trend_single_value():
    trend = calculate_numeric_trend(
        [54],
    )

    assert trend["count"] == 1
    assert trend["current"] == 54
    assert trend["previous"] is None
    assert trend["change"] is None
    assert trend["direction"] == "UNKNOWN"

def test_calculate_numeric_trend_empty():
    trend = calculate_numeric_trend([])

    assert trend["count"] == 0
    assert trend["current"] is None
    assert trend["previous"] is None
    assert trend["change"] is None
    assert trend["direction"] == "UNKNOWN"