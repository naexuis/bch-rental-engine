from scripts.bch_solo_rental_strike_engine import (
    calculate_metric_trend,
    calculate_numeric_trend,
    calculate_trend_persistence,
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

def test_calculate_metric_trend_uses_chronological_order():
    history_rows = [
        {"opportunity_score": 55.0},
        {"opportunity_score": 52.0},
        {"opportunity_score": 50.0},
    ]

    trend = calculate_metric_trend(
        history_rows,
        "opportunity_score",
    )

    assert trend["count"] == 3
    assert trend["previous"] == 52.0
    assert trend["current"] == 55.0
    assert trend["change"] == 3.0
    assert trend["direction"] == "IMPROVING"


def test_calculate_metric_trend_drops_missing_values():
    history_rows = [
        {"opportunity_score": 55.0},
        {"opportunity_score": None},
        {"opportunity_score": 50.0},
    ]

    trend = calculate_metric_trend(
        history_rows,
        "opportunity_score",
    )

    assert trend["count"] == 2
    assert trend["previous"] == 50.0
    assert trend["current"] == 55.0
    assert trend["change"] == 5.0
    assert trend["direction"] == "IMPROVING"


def test_calculate_metric_trend_returns_unknown_for_missing_metric():
    history_rows = [
        {"opportunity_score": 55.0},
        {"opportunity_score": 50.0},
    ]

    trend = calculate_metric_trend(
        history_rows,
        "best_risk_adjusted_roi_pct",
    )

    assert trend["count"] == 0
    assert trend["current"] is None
    assert trend["previous"] is None
    assert trend["change"] is None
    assert trend["direction"] == "UNKNOWN"


def test_calculate_metric_trend_handles_empty_history():
    trend = calculate_metric_trend(
        [],
        "opportunity_score",
    )

    assert trend["count"] == 0
    assert trend["direction"] == "UNKNOWN"

def test_calculate_trend_persistence_improving():
    result = calculate_trend_persistence(
        [50, 52, 54, 56],
    )

    assert result["direction"] == "IMPROVING"
    assert result["consecutive_moves"] == 3


def test_calculate_trend_persistence_declining():
    result = calculate_trend_persistence(
        [60, 58, 55, 51],
    )

    assert result["direction"] == "DECLINING"
    assert result["consecutive_moves"] == 3


def test_calculate_trend_persistence_stops_at_reversal():
    result = calculate_trend_persistence(
        [50, 55, 53, 56],
    )

    assert result["direction"] == "IMPROVING"
    assert result["consecutive_moves"] == 1


def test_calculate_trend_persistence_stable():
    result = calculate_trend_persistence(
        [54, 54, 54],
    )

    assert result["direction"] == "STABLE"
    assert result["consecutive_moves"] == 2


def test_calculate_trend_persistence_single_value():
    result = calculate_trend_persistence([54])

    assert result["direction"] == "UNKNOWN"
    assert result["consecutive_moves"] == 0


def test_calculate_trend_persistence_empty():
    result = calculate_trend_persistence([])

    assert result["direction"] == "UNKNOWN"
    assert result["consecutive_moves"] == 0