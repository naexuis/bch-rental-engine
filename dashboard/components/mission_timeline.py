from __future__ import annotations

import math

import plotly.express as px
import streamlit as st

from dashboard.ui_utils import (
    build_success_probability_curve,
    fmt_hashrate_from_ph,
    safe_num,
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

    probability_fig = px.line(
        probability_curve,
        x="hours",
        y="probability_pct",
        labels={
            "hours": "Mission Time (Hours)",
            "probability_pct": "Mission Success Probability (%)",
        },
    )

    probability_fig.update_traces(
        line={"width": 3},
        hovertemplate=(
            "<b>Mission Timeline</b><br>"
            "Mission Time: %{x:.2f} h<br>"
            "Success Probability: %{y:.2f}%"
            "<extra></extra>"
        ),
    )

    probability_fig.add_vrect(
        x0=0,
        x1=duration_hours,
        opacity=0.24,
        line_width=0,
        annotation_text="Recommended Rental Window",
        annotation_position="top left",
    )

    probability_fig.add_vline(
        x=median_hours,
        line_dash="dot",
        annotation_text="Median",
    )

    probability_fig.add_vline(
        x=expected_time_hours,
        line_dash="dot",
        annotation_text="Expected",
    )

    probability_fig.add_scatter(
        x=[duration_hours],
        y=[recommended_probability_pct],
        mode="markers+text",
        name="Recommended Strike",
        text=[
            (
                f"Recommended Strike<br>"
                f"{duration_hours:.2f} h<br>"
                f"{recommended_probability_pct:.1f}%"
            )
        ],
        textposition="top center",
        marker={
            "size": 26,
            "symbol": "star",
            "color": "gold",
            "line": {
                "width": 2,
                "color": "black",
            },
        },
        customdata=[
            [
                strike_cost,
                safe_num(best.get("hashrate_ph", 0)),
                expected_blocks,
            ]
        ],
        hovertemplate=(
            "<b>Recommended Strike</b><br>"
            "Duration: %{x:.2f} h<br>"
            "Success Probability: %{y:.2f}%<br>"
            "Budget: $%{customdata[0]:,.0f}<br>"
            "Hashrate: %{customdata[1]:,.0f} PH/s<br>"
            "Expected Blocks: %{customdata[2]:.3f}"
            "<extra></extra>"
        ),
    )

    probability_fig.update_layout(
        height=620,
        yaxis_range=[0, 100],
        showlegend=False,
        margin=dict(l=40, r=20, t=30, b=40),
    )

    st.plotly_chart(
        probability_fig,
        width="stretch",
    )
