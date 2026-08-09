from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard.components.pool_routing_helpers import (
    render_pool_card,
)
from dashboard.ui_utils import (
    fmt_hashrate_from_ph,
    render_decision_status,
    safe_num,
)


def render_pool_routing_page(
    *,
    state: dict,
) -> None:
    st.subheader("Pool Routing")

    opportunity = state.get("opportunity") or {}
    action = opportunity.get("action", "WAIT")

    render_decision_status(action)

    recommended_pool = state.get("recommended_pool")
    rankings = state.get(
        "pool_routing",
        {},
    ).get(
        "rankings",
        [],
    )

    if not recommended_pool:
        st.warning("No pool routing data available yet.")
        st.stop()

    pool_name = recommended_pool.get("pool_name", "N/A") if recommended_pool else "N/A"
    pool_score = safe_num(recommended_pool.get("routing_score", 0)) if recommended_pool else 0

    if pool_score >= 85:
        st.success(f"🟢 Recommended Route: {pool_name}")
    elif pool_score >= 70:
        st.warning(f"🟡 Acceptable Route: {pool_name}")
    else:
        st.error(f"🔴 Weak Route: {pool_name}")

    st.write(
        f"Route rented hashrate to **{pool_name}**. "
        f"It has the highest current routing score at **{pool_score:.1f}/100**."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Recommended Pool", recommended_pool.get("pool_name", "N/A"))
    col2.metric("Routing Score", f"{recommended_pool.get('routing_score', 0):.1f}/100")
    col3.metric("Dominance", f"{recommended_pool.get('pool_dominance_pct', 0):.2f}%")
    col4.metric(
    "Existing Pool",
    fmt_hashrate_from_ph(recommended_pool.get("existing_pool_hashrate_ph", 0)),
    )

    st.subheader("Why this pool?")

    dominance = safe_num(recommended_pool.get("pool_dominance_pct", 0))
    existing_pool = recommended_pool.get("existing_pool_hashrate_ph", 0)
    fee_pct = safe_num(recommended_pool.get("fee_pct", 0))
    network_share = safe_num(
        recommended_pool.get("post_rental_network_share_pct", 0)
    )

    st.write(
        f"**{recommended_pool.get('pool_name', 'This pool')}** is currently the best routing choice. "
        f"After adding your rental, you would control approximately **{dominance:.2f}%** of that pool's hashrate. "
        f"The pool currently has **{fmt_hashrate_from_ph(existing_pool)}** of existing hashrate, "
        f"charges a **{fee_pct:.2f}%** fee, "
        f"and your rental would represent approximately **{network_share:.2f}%** of the entire BCH network."
    )

    st.divider()

    st.subheader("Pool Rankings")

    if rankings:
        top_pools = rankings[:4]
        card_cols = st.columns(len(top_pools))

        for idx, pool in enumerate(top_pools):
            with card_cols[idx]:
                render_pool_card(pool, idx)

        st.divider()

        pool_df = pd.DataFrame(rankings)

        display_df = pool_df.copy()

        display_df["existing_pool"] = display_df["existing_pool_hashrate_ph"].apply(fmt_hashrate_from_ph)
        display_df["post_rental_pool"] = display_df["post_rental_pool_hashrate_ph"].apply(fmt_hashrate_from_ph)

        display_df["routing_score"] = display_df["routing_score"].round(1)
        display_df["pool_dominance_pct"] = display_df["pool_dominance_pct"].round(2)
        display_df["post_rental_network_share_pct"] = display_df["post_rental_network_share_pct"].round(2)
        display_df["fee_pct"] = display_df["fee_pct"].round(2)

        display_df = display_df[
            [
                "pool_name",
                "routing_score",
                "pool_dominance_pct",
                "existing_pool",
                "post_rental_pool",
                "post_rental_network_share_pct",
                "fee_pct",
                "status",
            ]
        ]

        st.dataframe(display_df, use_container_width=True)

        chart_df = pool_df.copy()
        chart_df["routing_score"] = chart_df["routing_score"].round(1)

        fig = px.bar(
            chart_df,
            x="pool_name",
            y="routing_score",
            text="routing_score",
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="inside")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No pool rankings available.")
