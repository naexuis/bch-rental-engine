from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.ui_utils import (
    fmt_hashrate_from_ph,
    safe_num,
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

    rows = []

    for item in frontier:
        frontier_best = (
            item.get("best_score", {})
            or item.get("best_probability", {})
        )

        rows.append(
            {
                "budget_usd": safe_num(
                    item.get(
                        "budget_usd",
                        frontier_best.get("cost_usd", 0),
                    )
                ),
                "cost_usd": safe_num(
                    frontier_best.get("cost_usd", 0)
                ),
                "hashrate": fmt_hashrate_from_ph(
                    frontier_best.get("hashrate_ph", 0)
                ),
                "duration_hours": safe_num(
                    frontier_best.get("duration_hours", 0)
                ),
                "prob_1plus_pct": (
                    safe_num(frontier_best.get("prob_1plus", 0)) * 100
                ),
                "prob_2plus_pct": (
                    safe_num(frontier_best.get("prob_2plus", 0)) * 100
                ),
                "fvr": safe_num(
                    frontier_best.get("fair_value_ratio", 0)
                ),
                "risk_roi_pct": safe_num(
                    frontier_best.get("risk_adjusted_roi_pct", 0)
                ),
                "recommendation": frontier_best.get(
                    "recommendation",
                    "N/A",
                ),
                "source": str(
                    frontier_best.get("source", "N/A")
                ).upper(),
            }
        )

    frontier_df = pd.DataFrame(rows)

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

        fig = px.line(
            chart_df,
            x="budget_usd",
            y="prob_1plus_pct",
            markers=True,
            labels={
                "budget_usd": "Budget USD",
                "prob_1plus_pct": "P(1+ Block) %",
            },
        )

        fig.update_traces(
            hovertemplate=(
                "Budget: $%{x:,.0f}<br>"
                "P(1+): %{y:.2f}%"
                "<extra></extra>"
            )
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )
