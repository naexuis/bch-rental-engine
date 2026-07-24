from scripts.bch_solo_rental_strike_engine import (
    calculate_opportunity_score,
)


def test_calculate_opportunity_score_perfect_inputs():
    result = calculate_opportunity_score(
        fair_value_ratio=1.10,
        prob_1plus=0.50,
        risk_adjusted_roi_pct=10.0,
        market_regime="FAIR",
    )

    assert result["score"] == 100.0
    assert result["action"] == "STRIKE_NOW"

    assert result["components"]["fvr_score"] == 65.0
    assert result["components"]["prob_score"] == 20.0
    assert result["components"]["roi_score"] == 15.0

def test_calculate_opportunity_score_applies_fvr_hard_cap():
    result = calculate_opportunity_score(
        fair_value_ratio=0.84,
        prob_1plus=1.00,
        risk_adjusted_roi_pct=100.0,
        market_regime="BEARISH",
    )

    assert result["score"] == 39.0
    assert result["action"] == "WAIT"

def test_calculate_opportunity_score_applies_negative_roi_cap():
    result = calculate_opportunity_score(
        fair_value_ratio=1.10,
        prob_1plus=1.00,
        risk_adjusted_roi_pct=-11.0,
        market_regime="FAIR",
    )

    assert result["score"] == 54.0
    assert result["action"] == "WEAK_WATCH"

def test_probability_score_reaches_maximum_at_fifty_percent():
    low = calculate_opportunity_score(
        fair_value_ratio=1.10,
        prob_1plus=0.50,
        risk_adjusted_roi_pct=10.0,
        market_regime="FAIR",
    )

    high = calculate_opportunity_score(
        fair_value_ratio=1.10,
        prob_1plus=0.70,
        risk_adjusted_roi_pct=10.0,
        market_regime="FAIR",
    )

    assert low["components"]["prob_score"] == 20.0
    assert high["components"]["prob_score"] == 20.0