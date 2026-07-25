from scripts.bch_solo_rental_strike_engine import (
    analyze_metric,
    build_trend_confidence_section,
    calculate_metric_trend,
    calculate_metric_volatility,
    calculate_numeric_trend,
    calculate_trend_confidence,
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

def test_analyze_metric_improving():
    history = [
        {"score": 40},
        {"score": 30},
        {"score": 20},
        {"score": 10},
    ]

    analysis = analyze_metric(history, "score")

    assert analysis["metric"] == "score"
    assert analysis["trend"]["direction"] == "IMPROVING"
    assert analysis["persistence"]["consecutive_moves"] == 3

def test_analyze_metric_empty():
    analysis = analyze_metric([], "score")

    assert analysis["metric"] == "score"
    assert analysis["trend"]["direction"] == "UNKNOWN"
    assert analysis["persistence"]["direction"] == "UNKNOWN"

def test_analyze_metric_missing_values():
    history = [
        {"score": 20},
        {"score": None},
        {"score": 10},
        {"score": None},
    ]

    analysis = analyze_metric(history, "score")

    assert analysis["trend"]["direction"] == "IMPROVING"

def test_calculate_trend_confidence_high():
    analysis = {
        "trend": {
            "count": 10,
            "direction": "IMPROVING",
        },
        "persistence": {
            "consecutive_moves": 6,
        },
    }

    confidence = calculate_trend_confidence(analysis)

    assert confidence["level"] == "HIGH"

def test_calculate_trend_confidence_medium():
    analysis = {
        "trend": {
            "count": 5,
            "direction": "IMPROVING",
        },
        "persistence": {
            "consecutive_moves": 3,
        },
    }

    confidence = calculate_trend_confidence(analysis)

    assert confidence["level"] == "MEDIUM"

def test_calculate_trend_confidence_low():
    analysis = {
        "trend": {
            "count": 1,
            "direction": "UNKNOWN",
        },
        "persistence": {
            "consecutive_moves": 0,
        },
    }

    confidence = calculate_trend_confidence(analysis)

    assert confidence["level"] == "LOW"

def test_build_trend_confidence_section_high():
    confidence = {
        "level": "HIGH",
        "direction": "IMPROVING",
        "history_count": 10,
        "consecutive_moves": 6,
    }

    text = build_trend_confidence_section(confidence)

    assert "Trend Confidence" in text
    assert "HIGH" in text
    assert "IMPROVING" in text
    assert "10" in text
    assert "6" in text

def test_calculate_metric_volatility_low():
    history_rows = [
        {"opportunity_score": 70},
        {"opportunity_score": 71},
        {"opportunity_score": 70},
        {"opportunity_score": 71},
        {"opportunity_score": 70},
    ]

    volatility = calculate_metric_volatility(
        history_rows,
        "opportunity_score",
    )

    assert volatility["count"] == 5
    assert volatility["level"] == "LOW"

def test_calculate_metric_volatility_high():
    history_rows = [
        {"opportunity_score": 30},
        {"opportunity_score": 90},
        {"opportunity_score": 25},
        {"opportunity_score": 95},
        {"opportunity_score": 35},
    ]

    volatility = calculate_metric_volatility(
        history_rows,
        "opportunity_score",
    )

    assert volatility["count"] == 5
    assert volatility["level"] == "HIGH"
    assert "range" in volatility

def test_calculate_metric_volatility_medium():
    history_rows = [
        {"opportunity_score": 55},
        {"opportunity_score": 65},
        {"opportunity_score": 60},
        {"opportunity_score": 68},
        {"opportunity_score": 58},
    ]

    volatility = calculate_metric_volatility(
        history_rows,
        "opportunity_score",
    )

    assert volatility["count"] == 5
    assert volatility["level"] == "MEDIUM"

def test_calculate_metric_volatility_empty_history():
    volatility = calculate_metric_volatility(
        [],
        "opportunity_score",
    )

    assert volatility["count"] == 0
    assert volatility["range"] == 0.0
    assert volatility["level"] == "LOW"