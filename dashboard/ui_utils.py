from __future__ import annotations

import math

import pandas as pd

import streamlit as st


def safe_num(value, default=0.0):
    if pd.isna(value):
        return default
    return value


def build_success_probability_curve(
    expected_blocks: float,
    duration_hours: float,
    max_multiplier: float = 4.0,
    points: int = 200,
) -> pd.DataFrame:
    """
    Build cumulative probability of finding at least one block over time.

    The recommended strike defines the Poisson rate:
        expected_blocks = lambda * duration_hours

    Therefore:
        P(1+ block by time t) = 1 - exp(-lambda * t)
    """
    expected_blocks = safe_num(expected_blocks)
    duration_hours = safe_num(duration_hours)

    if expected_blocks <= 0 or duration_hours <= 0:
        return pd.DataFrame(
            columns=["hours", "probability_pct"]
        )

    block_rate_per_hour = expected_blocks / duration_hours
    max_hours = duration_hours * max_multiplier

    hours = [
        max_hours * i / (points - 1)
        for i in range(points)
    ]

    probability_pct = [
        (1 - math.exp(-block_rate_per_hour * hour)) * 100
        for hour in hours
    ]

    return pd.DataFrame(
        {
            "hours": hours,
            "probability_pct": probability_pct,
        }
    )


def fmt_hashrate_from_ph(value_ph):
    value_ph = safe_num(value_ph)

    if value_ph >= 1:
        return f"{value_ph:,.2f} PH/s"

    value_th = value_ph * 1_000
    if value_th >= 1:
        return f"{value_th:,.2f} TH/s"

    value_gh = value_th * 1_000
    if value_gh >= 1:
        return f"{value_gh:,.2f} GH/s"

    value_mh = value_gh * 1_000
    return f"{value_mh:,.2f} MH/s"


def fmt_large_number(value):
    value = safe_num(value)

    if abs(value) >= 1_000_000_000_000:
        return f"{value/1_000_000_000_000:.2f} T"

    if abs(value) >= 1_000_000_000:
        return f"{value/1_000_000_000:.2f} B"

    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:.2f} M"

    if abs(value) >= 1_000:
        return f"{value/1_000:.2f} K"

    return f"{value:,.0f}"


def progress_pct(
    value: float,
    max_value: float = 100.0,
) -> int:
    value = safe_num(value)
    max_value = safe_num(max_value, 100.0)

    if max_value <= 0:
        return 0

    pct = int(round((value / max_value) * 100))
    return max(0, min(100, pct))


def render_decision_status(
    action: str,
) -> None:
    action = str(
        action or "WAIT"
    ).upper()

    if action in [
        "RENT",
        "STRONG_RENT",
    ]:
        st.success("🟢 RENT")

    elif action in [
        "WATCH",
        "WEAK_WATCH",
        "MONITOR",
    ]:
        st.warning("🟡 WATCH")

    else:
        st.error("🔴 WAIT")