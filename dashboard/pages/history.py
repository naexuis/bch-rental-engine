from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.history_data import (
    load_history_dataframe,
)
from dashboard.ui_utils import (
    safe_num,
)


def render_history_page(
    *,
    db_path: Path,
) -> None:
    st.subheader("Historical Performance")

    hist_df = load_history_dataframe(db_path)

    if hist_df.empty:
        st.warning("History database not found or no history records are available yet.")
        st.stop()

    latest_hist = hist_df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Runs", f"{len(hist_df):,}")
    col2.metric("Latest Recommendation", str(latest_hist.get("best_recommendation", "N/A")))
    col3.metric("Latest FVR", f"{safe_num(latest_hist.get('best_fair_value_ratio', 0)):.3f}")
    col4.metric("Latest Risk ROI", f"{safe_num(latest_hist.get('best_risk_adjusted_roi_pct', 0)):.2f}%")

    st.divider()

    st.subheader("Recommendation Timeline")

    timeline_df = hist_df[
        [
            "timestamp",
            "best_recommendation",
            "opportunity_action",
            "opportunity_score",
            "best_prob_1plus_pct",
            "best_risk_adjusted_roi_pct",
            "best_fair_value_ratio",
            "best_hashrate_ph",
            "best_cost_usd",
            "best_duration_hours",
        ]
    ].tail(100).copy()

    timeline_df["timestamp"] = timeline_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    timeline_df["best_prob_1plus_pct"] = timeline_df["best_prob_1plus_pct"].round(2)
    timeline_df["best_risk_adjusted_roi_pct"] = timeline_df["best_risk_adjusted_roi_pct"].round(2)
    timeline_df["best_fair_value_ratio"] = timeline_df["best_fair_value_ratio"].round(3)
    timeline_df["best_hashrate_ph"] = timeline_df["best_hashrate_ph"].round(0)
    timeline_df["best_cost_usd"] = timeline_df["best_cost_usd"].round(2)
    timeline_df["best_duration_hours"] = timeline_df["best_duration_hours"].round(2)

    st.dataframe(timeline_df, use_container_width=True)

    st.divider()

    st.subheader("Key Metric Trends")

    fig = px.line(
        hist_df,
        x="timestamp",
        y="opportunity_score",
        markers=True,
        title="Opportunity Score Over Time",
        labels={"timestamp": "Time", "opportunity_score": "Opportunity Score"},
    )
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        hist_df,
        x="timestamp",
        y="best_prob_1plus_pct",
        markers=True,
        title="P(1+ Block) Over Time",
        labels={"timestamp": "Time", "best_prob_1plus_pct": "P(1+ Block) %"},
    )
    fig.add_hline(y=70, line_dash="dash", annotation_text="Target: 70%")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        hist_df,
        x="timestamp",
        y="best_risk_adjusted_roi_pct",
        markers=True,
        title="Risk-Adjusted ROI Over Time",
        labels={"timestamp": "Time", "best_risk_adjusted_roi_pct": "Risk ROI %"},
    )
    fig.add_hline(y=0, line_dash="dash", annotation_text="Break-even")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        hist_df,
        x="timestamp",
        y="best_fair_value_ratio",
        markers=True,
        title="Fair Value Ratio Over Time",
        labels={"timestamp": "Time", "best_fair_value_ratio": "FVR"},
    )
    fig.add_hline(y=0.90, line_dash="dash", annotation_text="Watch target: 0.90")
    fig.add_hline(y=1.00, line_dash="dash", annotation_text="Fair value: 1.00")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Raw History")

    with st.expander("Show raw history table"):
        st.dataframe(hist_df.tail(500), use_container_width=True)
