from scripts.bch_solo_rental_strike_engine import (
    calculate_opportunity_score,
    classify_alert_tier,
    recommendation_from_tier,
    determine_canonical_decision,
)


def test_classify_alert_tier_strong_rent():
    assert (
        classify_alert_tier(
            fair_value_ratio=1.10,
            risk_adjusted_roi_pct=10.0,
            prob_1plus=0.70,
        )
        == "STRONG_RENT"
    )


def test_classify_alert_tier_deploy_now():
    assert (
        classify_alert_tier(
            fair_value_ratio=1.03,
            risk_adjusted_roi_pct=0.1,
            prob_1plus=0.70,
        )
        == "DEPLOY_NOW"
    )


def test_classify_alert_tier_near_strike():
    assert (
        classify_alert_tier(
            fair_value_ratio=0.98,
            risk_adjusted_roi_pct=-5.0,
            prob_1plus=0.50,
        )
        == "NEAR_STRIKE"
    )


def test_classify_alert_tier_watch_improving():
    assert (
        classify_alert_tier(
            fair_value_ratio=0.90,
            risk_adjusted_roi_pct=-15.0,
            prob_1plus=0.25,
        )
        == "WATCH_IMPROVING"
    )


def test_classify_alert_tier_do_not_rent():
    assert (
        classify_alert_tier(
            fair_value_ratio=0.89,
            risk_adjusted_roi_pct=20.0,
            prob_1plus=0.90,
        )
        == "DO_NOT_RENT"
    )


def test_recommendation_from_tier_mapping():
    assert recommendation_from_tier("STRONG_RENT") == "RENT"
    assert recommendation_from_tier("DEPLOY_NOW") == "RENT"
    assert recommendation_from_tier("NEAR_STRIKE") == "NEAR STRIKE"
    assert recommendation_from_tier("WATCH_IMPROVING") == "WATCH"
    assert recommendation_from_tier("DO_NOT_RENT") == "DO NOT RENT"


def test_opportunity_score_negative_roi_is_capped_below_strong_watch():
    opportunity = calculate_opportunity_score(
        fair_value_ratio=1.00,
        prob_1plus=0.70,
        risk_adjusted_roi_pct=-1.0,
        market_regime="VALUE",
    )

    assert opportunity["score"] <= 69.0
    assert opportunity["action"] in {"WATCH", "WEAK_WATCH", "WAIT"}

def test_near_strike_requires_minimum_block_probability():
    tier = classify_alert_tier(
        fair_value_ratio=0.99,
        risk_adjusted_roi_pct=-3.0,
        prob_1plus=0.20,
    )

    assert tier == "WATCH_IMPROVING"

def test_canonical_decision_unavailable():
    assert (
        determine_canonical_decision(
            fair_value_ratio=1.20,
            risk_adjusted_roi_pct=20.0,
            prob_1plus=0.90,
            executable=False,
        )
        == "UNAVAILABLE"
    )


def test_canonical_decision_rent_now():
    assert (
        determine_canonical_decision(
            fair_value_ratio=1.10,
            risk_adjusted_roi_pct=10.0,
            prob_1plus=0.70,
            executable=True,
        )
        == "RENT_NOW"
    )


def test_canonical_decision_ready():
    assert (
        determine_canonical_decision(
            fair_value_ratio=1.03,
            risk_adjusted_roi_pct=0.1,
            prob_1plus=0.70,
            executable=True,
        )
        == "READY"
    )


def test_canonical_decision_watch_closely():
    assert (
        determine_canonical_decision(
            fair_value_ratio=0.98,
            risk_adjusted_roi_pct=-5.0,
            prob_1plus=0.50,
            executable=True,
        )
        == "WATCH_CLOSELY"
    )


def test_canonical_decision_watch():
    assert (
        determine_canonical_decision(
            fair_value_ratio=0.90,
            risk_adjusted_roi_pct=-15.0,
            prob_1plus=0.20,
            executable=True,
        )
        == "WATCH"
    )


def test_canonical_decision_wait():
    assert (
        determine_canonical_decision(
            fair_value_ratio=0.89,
            risk_adjusted_roi_pct=20.0,
            prob_1plus=0.90,
            executable=True,
        )
        == "WAIT"
    )

def test_strong_rent_downgrades_to_watch_when_probability_is_low():
    tier = classify_alert_tier(
        fair_value_ratio=1.12,
        risk_adjusted_roi_pct=12.0,
        prob_1plus=0.40,
    )

    assert tier == "WATCH_IMPROVING"
