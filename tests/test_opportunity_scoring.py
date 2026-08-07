from scripts.bch_solo_rental_strike_engine import (
    calculate_opportunity_score,
)


def test_calculate_opportunity_score_perfect_inputs():
    result = calculate_opportunity_score(
        fair_value_ratio=1.10,
        prob_1plus=0.70,
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
    assert result["action"] == "WATCH"
    assert result["canonical_decision"] == "WATCH_CLOSELY"

def test_probability_score_reaches_maximum_at_seventy_percent():
    below_target = calculate_opportunity_score(
        fair_value_ratio=1.10,
        prob_1plus=0.50,
        risk_adjusted_roi_pct=10.0,
        market_regime="FAIR",
    )

    at_target = calculate_opportunity_score(
        fair_value_ratio=1.10,
        prob_1plus=0.70,
        risk_adjusted_roi_pct=10.0,
        market_regime="FAIR",
    )

    above_target = calculate_opportunity_score(
        fair_value_ratio=1.10,
        prob_1plus=0.90,
        risk_adjusted_roi_pct=10.0,
        market_regime="FAIR",
    )

    assert below_target["components"]["prob_score"] == 14.3
    assert at_target["components"]["prob_score"] == 20.0
    assert above_target["components"]["prob_score"] == 20.0

def test_probability_score_sensitivity(capsys):
    """
    Diagnostic test to visualize how Opportunity Score changes as
    P(1+) increases while holding all other inputs constant.

    This is primarily intended as a characterization test for the
    current scoring model.
    """

    print("\n")
    print("=" * 72)
    print("Opportunity Score Sensitivity to P(1+)")
    print("=" * 72)
    print(
        f"{'P(1+)':>8} "
        f"{'Prob Score':>12} "
        f"{'Total Score':>12} "
        f"{'Action':>15}"
    )
    print("-" * 72)

    probabilities = [
        0.00,
        0.10,
        0.20,
        0.30,
        0.40,
        0.50,
        0.60,
        0.70,
        0.80,
        0.90,
        1.00,
    ]

    for p in probabilities:
        result = calculate_opportunity_score(
            fair_value_ratio=1.10,
            prob_1plus=p,
            risk_adjusted_roi_pct=10.0,
            market_regime="FAIR",
        )

        print(
            f"{p:8.2%} "
            f"{result['components']['prob_score']:12.1f} "
            f"{result['score']:12.1f} "
            f"{result['action']:>15}"
        )

    print("=" * 72)

    # The purpose of this test is diagnostic. It always passes.
    assert True