from __future__ import annotations


def canonical_decision_from_state(
    opportunity: dict,
    recommendation: str,
) -> str:
    """
    Return the canonical decision from current engine state.

    Older state files may not contain canonical_decision, so preserve
    compatibility by translating the legacy recommendation.
    """
    canonical_decision = str(
        opportunity.get("canonical_decision", "")
    ).strip().upper()

    valid_decisions = {
        "RENT_NOW",
        "READY",
        "WATCH_CLOSELY",
        "WATCH",
        "WAIT",
        "UNAVAILABLE",
    }

    if canonical_decision in valid_decisions:
        return canonical_decision

    legacy_recommendation = (
        str(recommendation)
        .strip()
        .upper()
        .replace("_", " ")
    )

    legacy_mapping = {
        "STRONG RENT": "RENT_NOW",
        "RENT": "READY",
        "NEAR STRIKE": "WATCH_CLOSELY",
        "WATCH": "WATCH",
        "DO NOT RENT": "WAIT",
        "WAIT": "UNAVAILABLE",
    }

    return legacy_mapping.get(
        legacy_recommendation,
        "WAIT",
    )
