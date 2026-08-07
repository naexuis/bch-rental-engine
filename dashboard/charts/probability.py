from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def build_mission_probability_chart(
    *,
    probability_curve: pd.DataFrame,
    duration_hours: float,
    recommended_probability_pct: float,
    median_hours: float,
    expected_time_hours: float,
    strike_cost: float,
    hashrate_ph: float,
    expected_blocks: float,
) -> go.Figure:
    """
    Build the Mission Timeline probability chart.
    """
    fig = px.line(
        probability_curve,
        x="hours",
        y="probability_pct",
        labels={
            "hours": "Mission Time (Hours)",
            "probability_pct": "Mission Success Probability (%)",
        },
    )

    fig.update_traces(
        line={"width": 3},
        hovertemplate=(
            "<b>Mission Timeline</b><br>"
            "Mission Time: %{x:.2f} h<br>"
            "Success Probability: %{y:.2f}%"
            "<extra></extra>"
        ),
    )

    fig.add_vrect(
        x0=0,
        x1=duration_hours,
        opacity=0.24,
        line_width=0,
        annotation_text="Recommended Rental Window",
        annotation_position="top left",
    )

    fig.add_vline(
        x=median_hours,
        line_dash="dot",
        annotation_text="Median",
    )

    fig.add_vline(
        x=expected_time_hours,
        line_dash="dot",
        annotation_text="Expected",
    )

    fig.add_scatter(
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
                hashrate_ph,
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

    fig.update_layout(
        height=620,
        yaxis_range=[0, 100],
        showlegend=False,
        margin=dict(l=40, r=20, t=30, b=40),
    )

    return fig
