from __future__ import annotations

import math

import streamlit as st

from dashboard.ui_utils import (
    build_success_probability_curve,
    fmt_hashrate_from_ph,
    safe_num,
)
from dashboard.charts.probability import (
    build_mission_probability_chart,
)


def render_mission_timeline(
    best: dict,
    strike_cost: float,
) -> None:
    """
    Render the recommended strike probability timeline.

    The timeline uses the engine's expected_blocks and duration_hours
    to show the cumulative probability of finding at least one BCH block.
    """
    expected_blocks = safe_num(best.get("expected_blocks", 0))
    duration_hours = safe_num(best.get("duration_hours", 0))

    probability_curve = build_success_probability_curve(
        expected_blocks=expected_blocks,
        duration_hours=duration_hours,
    )

    if probability_curve.empty:
        return

    recommended_probability_pct = (
        1 - math.exp(-expected_blocks)
    ) * 100

    block_rate_per_hour = expected_blocks / duration_hours

    median_hours = math.log(2) / block_rate_per_hour
    expected_time_hours = 1 / block_rate_per_hour

    st.subheader("Mission Timeline")

    st.caption(
        "Shows how the probability of finding at least one BCH block "
        "accumulates over time for the recommended hashrate. "
        "The shaded area represents the recommended rental window."
    )

    if recommended_probability_pct >= 70:
        st.success(
            f"Mission Status: The recommended strike finishes with a "
            f"{recommended_probability_pct:.1f}% chance of finding at least one BCH block."
        )
    elif recommended_probability_pct >= 50:
        st.warning(
            f"Mission Status: The recommended strike finishes with a "
            f"{recommended_probability_pct:.1f}% chance of finding at least one BCH block. "
            "The probability is meaningful, but still below the 70% target."
        )
    else:
        st.error(
            f"Mission Status: The recommended strike finishes with only a "
            f"{recommended_probability_pct:.1f}% chance of finding at least one BCH block. "
            "Current conditions remain below the preferred success threshold."
        )

    m1, m2, m3, m4, m5, m6 = st.columns(6)

    m1.metric("Mission Budget", f"${strike_cost:,.0f}")
    m2.metric(
        "Rental Hashrate",
        fmt_hashrate_from_ph(best.get("hashrate_ph", 0)),
    )
    m3.metric("Mission Duration", f"{duration_hours:.2f} h")
    m4.metric(
        "Final Success Chance",
        f"{recommended_probability_pct:.1f}%",
    )
    m5.metric("Median Success Time", f"{median_hours:.2f} h")
    m6.metric(
        "Expected Success Time",
        f"{expected_time_hours:.2f} h",
    )

    probability_fig = build_mission_probability_chart(
        probability_curve=probability_curve,
        duration_hours=duration_hours,
        recommended_probability_pct=recommended_probability_pct,
        median_hours=median_hours,
        expected_time_hours=expected_time_hours,
        strike_cost=strike_cost,
        hashrate_ph=safe_num(best.get("hashrate_ph", 0)),
        expected_blocks=expected_blocks,
    )

    st.plotly_chart(
        probability_fig,
        width="stretch",
    )
