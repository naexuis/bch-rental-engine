from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.ui_utils import (
    fmt_hashrate_from_ph,
    safe_num,
)
from dashboard.frontier_data import (
    build_frontier_dataframe,
)
from dashboard.charts.frontier import (
    build_frontier_probability_chart,
)


def render_alternative_strike_plans(
    state: dict,
) -> None:
    """
    Render alternative strike plans from the budget frontier.
    """
    st.subheader("Alternative Strike Plans")

    frontier = state.get("budget_frontier", [])

    if not frontier:
        st.info("No alternative strike plans are available yet.")
        return

    frontier_df = build_frontier_dataframe(frontier)

    display_frontier_df = frontier_df.copy()

    display_frontier_df["budget_usd"] = (
        display_frontier_df["budget_usd"]
        .map(lambda x: f"${x:,.0f}")
    )

    display_frontier_df["cost_usd"] = (
        display_frontier_df["cost_usd"]
        .map(lambda x: f"${x:,.0f}")
    )

    display_frontier_df["duration_hours"] = (
        display_frontier_df["duration_hours"]
        .map(lambda x: f"{x:.2f}h")
    )

    display_frontier_df["prob_1plus_pct"] = (
        display_frontier_df["prob_1plus_pct"]
        .map(lambda x: f"{x:.2f}%")
    )

    display_frontier_df["prob_2plus_pct"] = (
        display_frontier_df["prob_2plus_pct"]
        .map(lambda x: f"{x:.2f}%")
    )

    display_frontier_df["fvr"] = (
        display_frontier_df["fvr"]
        .map(lambda x: f"{x:.3f}")
    )

    display_frontier_df["risk_roi_pct"] = (
        display_frontier_df["risk_roi_pct"]
        .map(lambda x: f"{x:.2f}%")
    )

    display_frontier_df = display_frontier_df[
        [
            "budget_usd",
            "hashrate",
            "duration_hours",
            "prob_1plus_pct",
            "prob_2plus_pct",
            "fvr",
            "risk_roi_pct",
            "recommendation",
            "source",
        ]
    ]

    with st.expander(
        "View all candidate plans",
        expanded=False,
    ):
        st.dataframe(
            display_frontier_df,
            width="stretch",
        )

        chart_df = frontier_df.copy()
        chart_df["budget_usd"] = (
            chart_df["budget_usd"].round(0)
        )
        chart_df["prob_1plus_pct"] = (
            chart_df["prob_1plus_pct"].round(2)
        )

        fig = build_frontier_probability_chart(
            chart_df
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )
