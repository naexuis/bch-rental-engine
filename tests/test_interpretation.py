from scripts.bch_solo_rental_strike_engine import (
    build_opportunity_history_section,
    build_score_limiter_section,
)


def test_build_opportunity_history_text_changed():
    opportunity = {
        "previous_action": "WATCH",
        "action": "STRONG_WATCH",
        "change_type": "UPGRADE",
    }

    text = build_opportunity_history_section(opportunity)

    assert "Previous Action: WATCH" in text
    assert "Current Action: STRONG_WATCH" in text
    assert "Status: Changed" in text
    assert "Classification: UPGRADE" in text


def test_build_opportunity_history_text_unchanged():
    opportunity = {
        "previous_action": "WATCH",
        "action": "WATCH",
        "change_type": "UNCHANGED",
    }

    text = build_opportunity_history_section(opportunity)

    assert "Status: Unchanged" in text
    assert "Classification: UNCHANGED" in text


def test_build_opportunity_history_text_initial_run():
    opportunity = {
        "previous_action": None,
        "action": "WATCH",
        "change_type": "INITIAL_RUN",
    }

    text = build_opportunity_history_section(opportunity)

    assert "Status: Initial Run" in text
    assert "Classification: INITIAL_RUN" in text

def test_build_score_limiter_section_for_low_fvr():
    opportunity = {
        "components": {
            "fair_value_ratio": 0.84,
            "risk_adjusted_roi_pct": 10.0,
        }
    }

    result = build_score_limiter_section(opportunity)

    assert "below 0.850" in result
    assert "capped at 39" in result


def test_build_score_limiter_section_for_fvr_below_ninety():
    opportunity = {
        "components": {
            "fair_value_ratio": 0.89,
            "risk_adjusted_roi_pct": 10.0,
        }
    }

    result = build_score_limiter_section(opportunity)

    assert "below 0.900" in result
    assert "capped at 49" in result


def test_build_score_limiter_section_for_roi_below_negative_ten():
    opportunity = {
        "components": {
            "fair_value_ratio": 0.95,
            "risk_adjusted_roi_pct": -11.0,
        }
    }

    result = build_score_limiter_section(opportunity)

    assert "below -10%" in result
    assert "capped at 54" in result


def test_build_score_limiter_section_for_negative_roi():
    opportunity = {
        "components": {
            "fair_value_ratio": 0.95,
            "risk_adjusted_roi_pct": -1.0,
        }
    }

    result = build_score_limiter_section(opportunity)

    assert "still negative" in result
    assert "capped at 69" in result


def test_build_score_limiter_section_without_active_cap():
    opportunity = {
        "components": {
            "fair_value_ratio": 1.00,
            "risk_adjusted_roi_pct": 1.0,
        }
    }

    result = build_score_limiter_section(opportunity)

    assert "No active Opportunity Score cap" in result


def test_build_score_limiter_section_handles_missing_components():
    assert build_score_limiter_section({}) == ""
    assert build_score_limiter_section({"components": {}}) == ""