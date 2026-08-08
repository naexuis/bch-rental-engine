from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.components.alternative_strike_plans import (
    render_alternative_strike_plans,
)
from dashboard.components.mission_timeline import (
    render_mission_timeline,
)
from dashboard.components.pool_recommendation import (
    render_recommended_pool,
)
from dashboard.decision_utils import (
    canonical_decision_from_state,
)
from dashboard.ui_utils import (
    fmt_hashrate_from_ph,
    safe_num,
)

def render_dashboard_page(
    *,
    state: dict,
    df: pd.DataFrame,
    latest: dict,
    has_history: bool,
    history_rows: int,
    last_updated,
) -> None:
    """
    Render the Dashboard page.
    """
    best_strike = (
        state.get("winners", {}).get("best_strike")
        or {}
    )

    recommended_pool = (
        state.get("recommended_pool")
        or {}
    )

    pool_rankings = (
        state.get("pool_routing", {}).get("rankings", [])
        or []
    )


    if not has_history and not state:
        st.subheader("Decision Center")
        st.info(
            "The dashboard is installed and ready. "
            "Waiting for the first successful engine run."
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("History Rows", "0")
        c2.metric("Latest Run", "Waiting")
        c3.metric("Engine State", "Not available yet")

        st.caption(
            "Strike recommendations, opportunity metrics, and pool routing "
            "will appear after the engine writes its first state and history records."
        )

        st.stop()

    winners = state.get("winners", {})
    best = winners.get("best_strike", {}) or {}
    opportunity = state.get("opportunity", {}) or {}

    recommendation = str(
        best.get("recommendation", state.get("recommendation", "N/A"))
    ).upper()
    recommendation = recommendation.replace("_", " ")
    canonical_decision = canonical_decision_from_state(
        opportunity=opportunity,
        recommendation=recommendation,
    )
    market_regime = str(state.get("market_regime", "N/A")).upper()

    opportunity_score = safe_num(opportunity.get("score", 0))
    prob_1plus = safe_num(best.get("prob_1plus", 0)) * 100
    risk_roi = safe_num(best.get("risk_adjusted_roi_pct", 0))
    fvr = safe_num(best.get("fair_value_ratio", 0))
    premium = safe_num(best.get("premium_discount_pct", 0))

    strike_cost = safe_num(best.get("cost_usd", best.get("budget_usd", 0)))
    expected_profit = safe_num(best.get("expected_profit_usd", 0))
    expected_roi = (
        (expected_profit / strike_cost) * 100
        if strike_cost > 0
        else 0.0
    )

    # Operator-facing rendering derived from the canonical engine decision.
    operator_action = {
        "RENT_NOW": "RENT NOW",
        "READY": "RENT",
        "WATCH_CLOSELY": "WATCH",
        "WATCH": "WATCH",
        "WAIT": "DO NOT RENT",
        "UNAVAILABLE": "WAITING",
    }.get(canonical_decision, "DO NOT RENT")

    recommendation_title = {
        "RENT_NOW": "Excellent Rental Opportunity",
        "READY": "Rental Opportunity",
        "WATCH_CLOSELY": "Near Strike Opportunity",
        "WATCH": "Continue Monitoring",
        "WAIT": "Unfavorable Rental Conditions",
        "UNAVAILABLE": "Waiting for Pricing Data",
    }.get(
        canonical_decision,
        "Unfavorable Rental Conditions",
    )

    recommendation_message = {
        "RENT_NOW": (
            "Multiple indicators align. Conditions favor executing a rental."
        ),
        "READY": "Current conditions support renting hashpower.",
        "WATCH_CLOSELY": (
            "Conditions are close to the strike threshold. "
            "Continue monitoring before renting."
        ),
        "WATCH": (
            "Conditions may be improving but do not justify a rental yet."
        ),
        "WAIT": (
            "Current market conditions do not support renting hashpower."
        ),
        "UNAVAILABLE": (
            "Live BCH market data was retrieved successfully, but no hashpower "
            "pricing source is currently available. Strike recommendations will "
            "resume automatically once pricing data becomes available."
        ),
    }.get(
        canonical_decision,
        "Current market conditions do not support renting hashpower.",
    )

    st.subheader("Decision Center")

    banner_text = (
        f"### {operator_action}\n\n"
        f"**Market State:** {recommendation_title}\n\n"
        f"{recommendation_message}"
    )

    if operator_action in ["RENT", "RENT NOW"]:
        st.success(banner_text)
    elif operator_action in ["WATCH", "MONITOR", "WAITING"]:
        st.warning(banner_text)
    else:
        st.error(banner_text)

    if opportunity_score >= 90:
        confidence_label = "Very High"
    elif opportunity_score >= 75:
        confidence_label = "High"
    elif opportunity_score >= 60:
        confidence_label = "Moderate"
    elif opportunity_score >= 40:
        confidence_label = "Low"
    else:
        confidence_label = "Very Low"

    d1, d2, d3 = st.columns(3)
    d1.metric("Confidence", confidence_label)
    d2.metric("Opportunity Score", f"{opportunity_score:.1f}/100")
    d3.metric("Market Regime", market_regime)

    st.divider()
    st.subheader("Key Decision Drivers")

    d5, d6, d7, d8 = st.columns(4)
    d5.metric("P(1+ Block)", f"{prob_1plus:.2f}%")
    d6.metric("Risk-Adjusted ROI", f"{risk_roi:.2f}%")
    d7.metric("FVR", f"{fvr:.3f}")
    d8.metric("Rental Premium", f"{premium:+.2f}%")

    reasons = []

    if fvr >= 0.90:
        reasons.append("✅ FVR is above the 0.90 watch threshold.")
    else:
        reasons.append("❌ FVR is below the 0.90 watch threshold.")

    if prob_1plus >= 70:
        reasons.append("✅ P(1+ Block) is above the 70% target.")
    else:
        reasons.append(f"❌ P(1+ Block) is below target at {prob_1plus:.2f}%.")

    if risk_roi >= 0:
        reasons.append("✅ Risk-adjusted ROI is positive.")
    else:
        reasons.append(
            f"❌ Risk-adjusted ROI is still negative at {risk_roi:.2f}%."
        )

    if premium <= 0:
        reasons.append("✅ Rental pricing is at or below break-even fair value.")
    else:
        reasons.append(
            f"❌ Rental pricing is still {premium:.2f}% above break-even."
        )

    for reason in reasons:
        st.write(reason)

    st.divider()
    st.subheader("Recommended Strike")

    c1, c2, c3 = st.columns(3)
    c1.metric("Budget", f"${strike_cost:,.0f}")
    c2.metric(
        "Hashrate",
        fmt_hashrate_from_ph(best.get("hashrate_ph", 0)),
    )
    c3.metric(
        "Duration",
        f"{safe_num(best.get('duration_hours', 0)):.2f} h",
    )

    c4, c5, c6 = st.columns(3)
    c4.metric("Success Probability", f"{prob_1plus:.2f}%")
    c5.metric("Expected ROI", f"{expected_roi:.2f}%")
    c6.metric("Rental Premium", f"{premium:+.2f}%")

    if operator_action in ["RENT", "RENT NOW"]:
        execution_plan = (
            "**Recommended Execution Plan**\n\n"
            f"Rent approximately **{fmt_hashrate_from_ph(best.get('hashrate_ph', 0))}** "
            f"for **{safe_num(best.get('duration_hours', 0)):.2f} hours** "
            f"at a projected cost of **${strike_cost:,.0f}**. "
            f"The modeled expected profit is **${expected_profit:,.2f}** "
            f"({expected_roi:.2f}% expected ROI)."
        )

    elif operator_action == "WATCH":
        execution_plan = (
            "**Recommended Execution Plan**\n\n"
            "Continue monitoring the market. Current conditions are close to a "
            "rental opportunity.\n\n"
            f"If conditions improve, the engine would recommend approximately "
            f"**{fmt_hashrate_from_ph(best.get('hashrate_ph', 0))}** "
            f"for **{safe_num(best.get('duration_hours', 0)):.2f} hours** "
            f"at an estimated cost of **${strike_cost:,.0f}**."
        )

    else:
        execution_plan = (
            "**Recommended Execution Plan**\n\n"
            "No rental is recommended under current market conditions. "
            "Continue monitoring until the key decision drivers improve."
        )

    st.info(execution_plan)

    render_mission_timeline(
        best=best,
        strike_cost=strike_cost,
    )

    st.divider()

    render_recommended_pool(
        recommended_pool=recommended_pool,
        pool_rankings=pool_rankings,
    )

    st.divider()

    render_alternative_strike_plans(
        state=state,
    )

    st.divider()
    with st.expander("Current Blockers", expanded=False):

        blockers = []

        if fvr < 0.90:
            blockers.append("Hashpower is still priced above fair value.")

        if risk_roi < 0:
            blockers.append("Risk-adjusted ROI must improve to at least break-even (0%).")

        if prob_1plus < 70:
            blockers.append("Probability must exceed the 70% deployment threshold.")

        if not blockers:
            st.success("No major blockers detected.")
        else:
            for blocker in blockers:
                st.error(blocker)

    with st.expander("Conditions Needed for a RENT Signal", expanded=False):

        cond1, cond2, cond3 = st.columns(3)
        cond1.metric("FVR Target", ">= 0.90", f"Current: {fvr:.3f}")
        cond2.metric(
            "Risk ROI Target",
            ">= 0%",
            f"Current: {risk_roi:.2f}%",
        )
        cond3.metric(
            "Probability Target",
            ">= 70%",
            f"Current: {prob_1plus:.2f}%",
        )

#####################################################################
#####################################################################

