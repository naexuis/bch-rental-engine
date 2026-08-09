import pytest

from dashboard.decision_utils import (
    canonical_decision_from_state,
)


@pytest.mark.parametrize(
    "canonical_decision",
    [
        "RENT_NOW",
        "READY",
        "WATCH_CLOSELY",
        "WATCH",
        "WAIT",
        "UNAVAILABLE",
    ],
)
def test_valid_canonical_decision_is_preserved(
    canonical_decision,
):
    result = canonical_decision_from_state(
        opportunity={
            "canonical_decision": canonical_decision,
        },
        recommendation="DO NOT RENT",
    )

    assert result == canonical_decision


@pytest.mark.parametrize(
    ("recommendation", "expected"),
    [
        ("STRONG RENT", "RENT_NOW"),
        ("RENT", "READY"),
        ("NEAR STRIKE", "WATCH_CLOSELY"),
        ("WATCH", "WATCH"),
        ("DO NOT RENT", "WAIT"),
        ("WAIT", "UNAVAILABLE"),
    ],
)
def test_legacy_recommendation_mapping(
    recommendation,
    expected,
):
    result = canonical_decision_from_state(
        opportunity={},
        recommendation=recommendation,
    )

    assert result == expected


@pytest.mark.parametrize(
    ("recommendation", "expected"),
    [
        ("strong_rent", "RENT_NOW"),
        ("near_strike", "WATCH_CLOSELY"),
        ("do_not_rent", "WAIT"),
        (" watch ", "WATCH"),
    ],
)
def test_legacy_recommendation_is_normalized(
    recommendation,
    expected,
):
    result = canonical_decision_from_state(
        opportunity={},
        recommendation=recommendation,
    )

    assert result == expected


def test_invalid_canonical_decision_falls_back_to_legacy_mapping():
    result = canonical_decision_from_state(
        opportunity={
            "canonical_decision": "UNKNOWN",
        },
        recommendation="RENT",
    )

    assert result == "READY"


def test_unknown_recommendation_defaults_to_wait():
    result = canonical_decision_from_state(
        opportunity={},
        recommendation="SOMETHING ELSE",
    )

    assert result == "WAIT"
