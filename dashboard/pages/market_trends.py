from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.ui_utils import safe_num


def render_market_trends_page(
    *,
    df: pd.DataFrame,
    latest: dict,
) -> None:
    st.subheader("Market Trends")

    if df.empty:
        st.warning("No history data available yet.")
        st.stop()

    trend_df = df.copy()
    trend_df["timestamp"] = pd.to_datetime(trend_df["timestamp"], errors="coerce")
    trend_df = trend_df.dropna(subset=["timestamp"]).sort_values("timestamp")

    st.caption(f"Showing {len(trend_df)} historical engine runs.")

    latest = trend_df.iloc[-1]

    current_fvr = safe_num(latest.get("best_fair_value_ratio", 0))
    current_risk_roi = safe_num(latest.get("best_risk_adjusted_roi_pct", 0))
    current_prob = safe_num(latest.get("best_prob_1plus", 0)) * 100
    current_bch = safe_num(latest.get("bch_usd", 0))

    TARGET_FVR = 0.90
    TARGET_RISK_ROI = 0.0
    TARGET_PROB = 70.0

    fvr_gap = TARGET_FVR - current_fvr
    risk_gap = TARGET_RISK_ROI - current_risk_roi
    prob_gap = TARGET_PROB - current_prob

    fvr_delta = "✓ Fair value met" if current_fvr >= TARGET_FVR else f"+{fvr_gap:.3f} needed"

    risk_delta = "✓ Profitable" if current_risk_roi >= 0 else f"+{risk_gap:.1f}% needed"

    prob_delta = "✓ Target met" if current_prob >= TARGET_PROB else f"+{prob_gap:.1f}% needed"

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("FVR", f"{current_fvr:.3f}", delta=fvr_delta, delta_color="inverse")
    c2.metric("Risk ROI", f"{current_risk_roi:.1f}%", delta=risk_delta, delta_color="inverse")
    c3.metric("P(1+ Block)", f"{current_prob:.1f}%", delta=prob_delta, delta_color="inverse")
    c4.metric("BCH Price", f"${current_bch:,.2f}", )

    st.divider()

    # -------------------------------------------------
    # FVR Trend
    # -------------------------------------------------
    if "best_fair_value_ratio" in trend_df.columns:
        fig = px.line(
            trend_df,
            x="timestamp",
            y="best_fair_value_ratio",
            markers=True,
            title="Fair Value Ratio Over Time",
            labels={
                "timestamp": "Time",
                "best_fair_value_ratio": "FVR",
            },
        )
        fig.add_hline(y=0.90, line_dash="dash", annotation_text="Rent target: 0.90")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # Probability Trend
    # -------------------------------------------------
    if "best_prob_1plus" in trend_df.columns:
        prob_df = trend_df.copy()
        prob_df["best_prob_1plus_pct"] = prob_df["best_prob_1plus"] * 100

        fig = px.line(
            prob_df,
            x="timestamp",
            y="best_prob_1plus_pct",
            markers=True,
            title="P(1+ Block) Over Time",
            labels={
                "timestamp": "Time",
                "best_prob_1plus_pct": "P(1+ Block) %",
            },
        )
        fig.add_hline(y=70, line_dash="dash", annotation_text="Target: 70%")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # Risk ROI Trend
    # -------------------------------------------------
    if "best_risk_adjusted_roi_pct" in trend_df.columns:
        fig = px.line(
            trend_df,
            x="timestamp",
            y="best_risk_adjusted_roi_pct",
            markers=True,
            title="Risk-Adjusted ROI Over Time",
            labels={
                "timestamp": "Time",
                "best_risk_adjusted_roi_pct": "Risk ROI %",
            },
        )
        fig.add_hline(y=0, line_dash="dash", annotation_text="Break-even")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # BCH Price
    # -------------------------------------------------
    if "bch_usd" in trend_df.columns:

        fig = px.line(
            trend_df,
            x="timestamp",
            y="bch_usd",
            markers=True,
            title="BCH Price",
            labels={
                "timestamp": "Time",
                "bch_usd": "USD"
            }
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
