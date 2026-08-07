from dashboard.app import canonical_decision_from_state


def test_uses_current_canonical_decision():
    opportunity = {
        "canonical_decision": "WATCH_CLOSELY",
    }

    result = canonical_decision_from_state(
        opportunity=opportunity,
        recommendation="DO NOT RENT",
    )

    assert result == "WATCH_CLOSELY"


def test_falls_back_to_legacy_rent_recommendation():
    result = canonical_decision_from_state(
        opportunity={},
        recommendation="RENT",
    )

    assert result == "READY"


def test_falls_back_to_legacy_near_strike_recommendation():
    result = canonical_decision_from_state(
        opportunity={},
        recommendation="NEAR_STRIKE",
    )

    assert result == "WATCH_CLOSELY"


def test_falls_back_to_unavailable_for_legacy_wait():
    result = canonical_decision_from_state(
        opportunity={},
        recommendation="WAIT",
    )

    assert result == "UNAVAILABLE"


def test_unknown_legacy_value_defaults_to_wait():
    result = canonical_decision_from_state(
        opportunity={},
        recommendation="UNKNOWN",
    )

    assert result == "WAIT"
