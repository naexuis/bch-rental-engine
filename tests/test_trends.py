from scripts.bch_solo_rental_strike_engine import (
    StrikeScenario,
    analyze_metric,
    build_interpretation_text,
    build_trend_confidence_section,
    build_trend_strength_section,
    build_volatility_section,
    calculate_metric_trend,
    calculate_metric_volatility,
    calculate_numeric_trend,
    calculate_trend_confidence,
    calculate_trend_persistence,
    calculate_trend_strength,
    calculate_trend_velocity,
)
import pytest

def test_calculate_numeric_trend_improving():
    trend = calculate_numeric_trend(
        [50, 52, 55],
    )

    assert trend["count"] == 3
    assert trend["current"] == 55
    assert trend["previous"] == 52
    assert trend["change"] == 3
    assert trend["velocity"] == 2.5
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
    assert "confidence" in analysis
    assert "volatility" in analysis
    assert analysis["volatility"]["level"] == "HIGH"
    assert "trend_strength" in analysis

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
    assert volatility["std_dev"] == pytest.approx(
        0.4898979485566356,
        rel=1e-6,
    )
    assert volatility["mean"] == pytest.approx(
        70.4,
        rel=1e-6,
    )
    assert volatility["coefficient_of_variation"] == pytest.approx(
        0.006958777678361301,
        rel=1e-6,
    )
    assert volatility["coefficient_of_variation"] < 0.01

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
    assert volatility["std_dev"] == 0.0
    assert volatility["mean"] == 0.0
    assert volatility["coefficient_of_variation"] == 0.0
    assert volatility["level"] == "LOW"

def test_calculate_metric_volatility_uses_relative_variability():
    history_rows = [
        {"opportunity_score": 1000},
        {"opportunity_score": 1015},
        {"opportunity_score": 990},
        {"opportunity_score": 1010},
        {"opportunity_score": 995},
    ]

    volatility = calculate_metric_volatility(
        history_rows,
        "opportunity_score",
    )

    assert volatility["range"] == 25.0
    assert volatility["coefficient_of_variation"] < 0.02
    assert volatility["level"] == "LOW"

def test_build_volatility_section_low():
    volatility = {
        "count": 5,
        "range": 1.0,
        "std_dev": 0.49,
        "mean": 70.4,
        "coefficient_of_variation": 0.006958777678361301,
        "level": "LOW",
    }

    text = build_volatility_section(volatility)

    assert "LOW" in text
    assert "Volatility" in text
    assert "0.49" in text
    assert "CV" in text
    assert "0.70%" in text
    assert "stable" in text.lower()
    assert "recent history" in text.lower()

def test_build_volatility_section_medium():
    volatility = {
        "count": 5,
        "range": 13.0,
        "std_dev": 4.45,
        "level": "MEDIUM",
    }

    text = build_volatility_section(volatility)

    assert "MEDIUM" in text
    assert "moderate" in text.lower()

def test_build_volatility_section_high():
    volatility = {
        "count": 5,
        "range": 70.0,
        "std_dev": 30.27,
        "level": "HIGH",
    }

    text = build_volatility_section(volatility)

    assert "HIGH" in text
    assert "highly volatile" in text.lower()

def test_build_interpretation_text_includes_volatility():
    best = StrikeScenario(
        source="mrr",
        name="Test Rig",
        budget_usd=300.0,
        budget_btc=0.003,
        hashrate_ph=300.0,
        hashrate_eh=0.300,
        duration_hours=1.0,
        cost_btc=0.003,
        cost_usd=300.0,
        expected_blocks=0.75,
        prob_0_blocks=0.47,
        prob_1plus=0.53,
        prob_2plus=0.10,
        expected_bch_gross=3.125,
        expected_bch_net=3.078,
        expected_revenue_usd=620.0,
        expected_profit_usd=320.0,
        roi_pct=106.7,
        risk_adjusted_profit_usd=150.0,
        risk_adjusted_roi_pct=50.0,
        profit_if_0_blocks=-300.0,
        profit_if_1_block=320.0,
        profit_if_2_blocks=940.0,
        break_even_price_btc_per_ph_day=0.40,
        current_price_btc_per_ph_day=0.35,
        fair_value_ratio=1.10,
        premium_discount_pct=-12.5,
        strike_score=90.0,
        strike_grade="A",
        alert_tier="HIGH",
        recommendation="RENT",
        strike_type="TEST",
    )

def test_calculate_trend_velocity_improving():
    velocity = calculate_trend_velocity(
        [10, 20, 30, 40],
    )

    assert velocity["count"] == 4
    assert velocity["change"] == 30.0
    assert velocity["velocity"] == 10.0
    assert velocity["direction"] == "IMPROVING"

def test_calculate_trend_velocity_declining():
    velocity = calculate_trend_velocity(
        [40, 30, 20, 10],
    )

    assert velocity["count"] == 4
    assert velocity["change"] == -30.0
    assert velocity["velocity"] == -10.0
    assert velocity["direction"] == "DECLINING"

def test_calculate_trend_velocity_stable():
    velocity = calculate_trend_velocity(
        [25, 25, 25, 25],
    )

    assert velocity["count"] == 4
    assert velocity["change"] == 0.0
    assert velocity["velocity"] == 0.0
    assert velocity["direction"] == "STABLE"

def test_calculate_trend_velocity_single_value():
    velocity = calculate_trend_velocity(
        [25],
    )

    assert velocity["count"] == 1
    assert velocity["change"] is None
    assert velocity["velocity"] is None
    assert velocity["direction"] == "UNKNOWN"

def test_calculate_trend_velocity_empty():
    velocity = calculate_trend_velocity(
        [],
    )

    assert velocity["count"] == 0
    assert velocity["change"] is None
    assert velocity["velocity"] is None
    assert velocity["direction"] == "UNKNOWN"

def test_calculate_trend_strength_strong():
    strength = calculate_trend_strength(
        confidence="HIGH",
        volatility="LOW",
        persistence=8,
        direction="IMPROVING",
    )

    assert strength["strength"] == "VERY_STRONG"

def test_build_trend_strength_section_very_strong():
    text = build_trend_strength_section(
        {
            "strength": "VERY_STRONG",
        }
    )

    assert "Trend Strength" in text
    assert "VERY_STRONG" in text