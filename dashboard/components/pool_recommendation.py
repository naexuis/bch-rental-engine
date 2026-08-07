from __future__ import annotations

import streamlit as st

from dashboard.ui_utils import (
    fmt_hashrate_from_ph,
    safe_num,
)


def render_recommended_pool(
    recommended_pool: dict,
    pool_rankings: list[dict],
) -> None:
    """
    Render the recommended mining pool and alternative routing options.
    """
    st.subheader("Recommended Pool")

    pool_name = recommended_pool.get("pool_name")
    routing_score = safe_num(
        recommended_pool.get("routing_score", 0)
    )

    if pool_name:
        st.success(
            f"Recommended Route: {pool_name} currently has the highest "
            f"routing score at {routing_score:.1f}/100."
        )
    else:
        st.warning(
            "No pool recommendation is currently available."
        )

    pool_col1, pool_col2, pool_col3, pool_col4 = st.columns(4)

    pool_col1.metric(
        "Pool",
        recommended_pool.get("pool_name", "N/A"),
    )

    pool_col2.metric(
        "Routing Score",
        f"{safe_num(recommended_pool.get('routing_score', 0)):.1f}/100",
    )

    pool_col3.metric(
        "Dominance",
        f"{safe_num(recommended_pool.get('pool_dominance_pct', 0)):.2f}%",
    )

    pool_col4.metric(
        "Existing Pool",
        fmt_hashrate_from_ph(
            recommended_pool.get("existing_pool_hashrate_ph", 0)
        ),
    )

    if not pool_name:
        return

    pool_dominance_pct = safe_num(
        recommended_pool.get("pool_dominance_pct", 0)
    )
    network_share_pct = safe_num(
        recommended_pool.get("post_rental_network_share_pct", 0)
    )
    fee_pct = safe_num(
        recommended_pool.get("fee_pct", 0)
    )

    st.markdown("### Why this pool?")

    st.write(
        f"Routing to **{pool_name}** gives the current strike an estimated "
        f"**{pool_dominance_pct:.1f}% share of that pool's hashrate** while "
        f"the pool would represent about **{network_share_pct:.2f}% of the BCH network** "
        f"after the rental. The current pool fee is **{fee_pct:.2f}%**."
    )

    if len(pool_rankings) > 1:
        st.markdown("### Alternative Pools")

        for rank, pool in enumerate(
            pool_rankings[1:4],
            start=2,
        ):
            st.info(
                f"#{rank} • {pool.get('pool_name', 'Unknown')}\n\n"
                f"Routing Score: "
                f"{safe_num(pool.get('routing_score', 0)):.1f}/100\n"
                f"Dominance: "
                f"{safe_num(pool.get('pool_dominance_pct', 0)):.1f}%"
            )
