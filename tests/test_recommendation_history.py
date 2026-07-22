from scripts.bch_solo_rental_strike_engine import (
    normalize_operator_action,
    normalize_opportunity_action,
    recommendation_changed,
)


def test_normalize_operator_action():
    assert normalize_operator_action("rent") == "RENT"
    assert normalize_operator_action(" WATCH ") == "WATCH"
    assert normalize_operator_action("do_not_rent") == "DO NOT RENT"
    assert normalize_operator_action("DO-NOT-RENT") == "DO NOT RENT"


def test_normalize_operator_action_handles_missing_values():
    assert normalize_operator_action(None) == "UNKNOWN"
    assert normalize_operator_action("") == "UNKNOWN"


def test_recommendation_changed_returns_false_for_same_action():
    assert recommendation_changed("WATCH", "WATCH") is False
    assert recommendation_changed("watch", " WATCH ") is False


def test_recommendation_changed_returns_true_for_transition():
    assert recommendation_changed("WATCH", "RENT") is True
    assert recommendation_changed("DO NOT RENT", "WATCH") is True


def test_recommendation_changed_returns_false_without_previous_action():
    assert recommendation_changed(None, "WATCH") is False
    assert recommendation_changed("", "WATCH") is False

def test_normalize_opportunity_action():
    assert normalize_opportunity_action("strike_now") == "STRIKE_NOW"
    assert normalize_opportunity_action(" STRONG WATCH ") == "STRONG_WATCH"
    assert normalize_opportunity_action("weak-watch") == "WEAK_WATCH"
    assert normalize_opportunity_action("watch") == "WATCH"
    assert normalize_opportunity_action("wait") == "WAIT"



def test_normalize_opportunity_action_handles_missing_or_invalid_values():
    assert normalize_opportunity_action(None) == "UNKNOWN"
    assert normalize_opportunity_action("") == "UNKNOWN"
    assert normalize_opportunity_action("RENT") == "UNKNOWN"