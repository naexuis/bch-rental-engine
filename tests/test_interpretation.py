from scripts.bch_solo_rental_strike_engine import (
    build_opportunity_history_section,
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