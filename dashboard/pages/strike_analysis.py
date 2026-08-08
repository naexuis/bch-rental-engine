from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.ui_utils import (
    fmt_hashrate_from_ph,
    progress_pct,
    safe_num,
)


def render_strike_analysis_page(
    *,
    state: dict,
) -> None:
    st.subheader("Strike Analysis")

    winners = state.get("winners", {})
    best = winners.get("best_strike", {}) or {}

    if not best:
        st.warning("No strike analysis data available yet.")
        st.stop()

    strike_recommendation = str(best.get("recommendation", "N/A")).upper()
    strike_grade = str(best.get("strike_grade", "N/A")).upper()
    strike_score = safe_num(best.get("strike_score", 0))
    strike_fvr = safe_num(best.get("fair_value_ratio", 0))
    strike_risk_roi = safe_num(best.get("risk_adjusted_roi_pct", 0))
    strike_expected_profit = safe_num(best.get("expected_profit_usd", 0))
    strike_prob = safe_num(best.get("prob_1plus", 0)) * 100

    if strike_recommendation in ["RENT", "STRONG_RENT"]:
        st.success(f"🟢 Recommendation: {strike_recommendation}")
    elif strike_recommendation in ["WATCH", "MONITOR"]:
        st.warning(f"🟡 Recommendation: {strike_recommendation}")
    else:
        st.error(f"🔴 Recommendation: {strike_recommendation}")

    st.write(
        f"Current setup is **{strike_grade} grade** with a **{strike_score:.1f}/100** strike score. "
        f"FVR is **{strike_fvr:.3f}**, risk-adjusted ROI is **{strike_risk_roi:.2f}%**, "
        f"and expected profit is **${strike_expected_profit:,.2f}**."
    )

    st.divider()


    st.markdown("### Selected Strike")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Budget", f"${safe_num(best.get('budget_usd', 0)):,.0f}")
    c2.metric("Hashrate", fmt_hashrate_from_ph(best.get("hashrate_ph", 0)))
    c3.metric("Duration", f"{safe_num(best.get('duration_hours', 0)):.2f}h")
    c4.metric("Strike Grade", strike_grade)

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("P(1+ Block)", f"{safe_num(best.get('prob_1plus', 0)) * 100:.2f}%")
    c6.metric("P(2+ Blocks)", f"{safe_num(best.get('prob_2plus', 0)) * 100:.2f}%")
    c7.metric("FVR", f"{safe_num(best.get('fair_value_ratio', 0)):.3f}")
    c8.metric("Risk ROI", f"{safe_num(best.get('risk_adjusted_roi_pct', 0)):.2f}%")

    st.caption(f"Strike Score: {strike_score:.1f}/100")
    st.progress(progress_pct(strike_score, 100))

    pb1, pb2 = st.columns(2)

    with pb1:
        st.caption(f"P(1+ Block): {strike_prob:.2f}% / 70% target")
        st.progress(progress_pct(strike_prob, 70))

    with pb2:
        st.caption(f"FVR: {strike_fvr:.3f} / 0.900 target")
        st.progress(progress_pct(strike_fvr, 0.90))

    st.divider()

    st.subheader("Expected Outcomes")

    o1, o2, o3, o4 = st.columns(4)

    o1.metric("Expected Revenue", f"${safe_num(best.get('expected_revenue_usd', 0)):,.2f}")
    o2.metric("Expected Profit", f"${safe_num(best.get('expected_profit_usd', 0)):,.2f}")
    o3.metric("Risk-Adjusted Profit", f"${safe_num(best.get('risk_adjusted_profit_usd', 0)):,.2f}")
    o4.metric("Expected BCH Net", f"{safe_num(best.get('expected_bch_net', 0)):.4f} BCH")

    st.divider()

    st.subheader("Block Outcome Scenarios")

    p0 = safe_num(best.get("prob_0_blocks", 0))
    p1plus = safe_num(best.get("prob_1plus", 0))
    p2plus = safe_num(best.get("prob_2plus", 0))

    p1_exact = max(0, p1plus - p2plus)

    outcome_rows = [
        {
            "Outcome": "0 Blocks",
            "Probability": f"{p0 * 100:.2f}%",
            "Profit": f"${safe_num(best.get('profit_if_0_blocks', 0)):,.2f}",
        },
        {
            "Outcome": "1 Block",
            "Probability": f"{p1_exact * 100:.2f}%",
            "Profit": f"${safe_num(best.get('profit_if_1_block', 0)):,.2f}",
        },
        {
            "Outcome": "2+ Blocks",
            "Probability": f"{p2plus * 100:.2f}%",
            "Profit": f"${safe_num(best.get('profit_if_2_blocks', 0)):,.2f}",
        },
    ]

    st.dataframe(pd.DataFrame(outcome_rows), use_container_width=True)

    st.divider()

    st.subheader("Why this strike?")

    st.write(
        f"The engine selected this strike because it provides the strongest overall tradeoff "
        f"within the current budget and hashrate constraints. It uses **{fmt_hashrate_from_ph(best.get('hashrate_ph', 0))}** "
        f"for **{safe_num(best.get('duration_hours', 0)):.2f} hours**, producing a "
        f"**{safe_num(best.get('prob_1plus', 0)) * 100:.2f}%** chance of finding at least one block. "
        f"However, the economics are still unfavorable: FVR is **{safe_num(best.get('fair_value_ratio', 0)):.3f}** "
        f"and risk-adjusted ROI is **{safe_num(best.get('risk_adjusted_roi_pct', 0)):.2f}%**, "
        f"so the recommendation remains **{best.get('recommendation', 'N/A')}**."
    )

    st.divider()

    st.subheader("Alternative Winners")

    cards = [
        ("Highest Probability", "best_probability"),
        ("Best Fair Value", "best_fair_value"),
        ("Best Risk ROI", "best_risk_adjusted_roi"),
        ("Lowest Cost", "lowest_cost_per_probability"),
    ]

    cols = st.columns(2)

    for i, (title, key) in enumerate(cards):

        strike = winners.get(key)

        if not strike:
            continue

        with cols[i % 2]:

            st.markdown(f"#### {title}")

            st.metric(
                "Budget",
                f"${safe_num(strike.get('budget_usd',0)):,.0f}"
            )

            st.metric(
                "Probability",
                f"{safe_num(strike.get('prob_1plus',0)*100):.1f}%"
            )

            st.metric(
                "Duration",
                f"{safe_num(strike.get('duration_hours',0)):.2f} h"
            )

            st.metric(
                "Expected Profit",
                f"${safe_num(strike.get('expected_profit_usd',0)):,.2f}"
            )

            st.caption(
                f"FVR {safe_num(strike.get('fair_value_ratio',0)):.3f} • "
                f"Risk ROI {safe_num(strike.get('risk_adjusted_roi_pct',0)):.1f}%"
            )

    st.divider()

    st.subheader("Optimization Surface")

    surface = state.get("optimization_surface", [])

    if surface:
        surface_df = pd.DataFrame(surface)

        heatmap_metric = st.selectbox(
            "Heatmap Metric",
            [
                "strike_score",
                "prob_1plus",
                "risk_adjusted_roi_pct",
                "fair_value_ratio",
            ],
            format_func=lambda x: {
                "strike_score": "Strike Score",
                "prob_1plus": "P(1+ Block)",
                "risk_adjusted_roi_pct": "Risk ROI %",
                "fair_value_ratio": "FVR",
            }.get(x, x),
        )

        plot_df = surface_df.copy()

        if heatmap_metric == "prob_1plus":
            plot_df[heatmap_metric] = plot_df[heatmap_metric] * 100

        heat_df = plot_df.pivot_table(
            index="hashrate_ph",
            columns="budget_usd",
            values=heatmap_metric,
            aggfunc="max",
        )

        hover_df = plot_df.copy()

        hover_df["prob_1plus_pct"] = hover_df["prob_1plus"] * 100
        hover_df["prob_2plus_pct"] = hover_df["prob_2plus"] * 100

        fig = px.imshow(
            heat_df,
            aspect="auto",
            title="Budget × Hashrate Optimization Surface",
            labels={
                "x": "Budget USD",
                "y": "Hashrate PH/s",
                "color": heatmap_metric,
            },
        )

        fig.update_traces(
            hovertemplate=(
                "Budget: $%{x}<br>"
                "Hashrate: %{y} PH/s<br>"
                f"{heatmap_metric}: %{{z:.2f}}<br>"
                "<extra></extra>"
            )
        )

        selected = state.get("winners", {}).get("best_strike", {})

        selected_budget = selected.get("budget_usd")
        selected_hashrate = selected.get("hashrate_ph")

        if selected_budget is not None and selected_hashrate is not None:
            fig.add_scatter(
                x=[selected_budget],
                y=[selected_hashrate],
                mode="markers+text",
                marker=dict(
                    size=18,
                    symbol="star",
                    color="red",
                    line=dict(width=2, color="white"),
                ),
                text=["Selected"],
                textposition="top center",
                name="Selected Strike",
            )

        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "This heatmap shows how the engine scored each budget and hashrate combination."
        )
    else:
        st.info("No optimization surface data available yet.")
