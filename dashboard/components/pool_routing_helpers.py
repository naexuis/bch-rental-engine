from __future__ import annotations

import streamlit as st

from dashboard.ui_utils import (
    fmt_hashrate_from_ph,
    safe_num,
)


def pool_rank_label(index: int) -> str:
    labels = [
        "🥇 Recommended",
        "🥈 Strong Alternative",
        "🥉 Backup Option",
    ]

    if index < len(labels):
        return labels[index]

    return "Additional Pool"


def render_pool_card(
    pool: dict,
    index: int,
) -> None:
    score = safe_num(
        pool.get("routing_score", 0)
    )

    dominance = safe_num(
        pool.get("pool_dominance_pct", 0)
    )

    existing_pool = pool.get(
        "existing_pool_hashrate_ph",
        0,
    )

    fee_pct = safe_num(
        pool.get("fee_pct", 0)
    )

    st.markdown(
        f"### {pool.get('pool_name', 'Unknown Pool')}"
    )

    st.caption(
        pool_rank_label(index)
    )

    st.metric(
        "Routing Score",
        f"{score:.1f}/100",
    )

    st.metric(
        "Dominance",
        f"{dominance:.2f}%",
    )

    st.metric(
        "Existing Pool",
        fmt_hashrate_from_ph(existing_pool),
    )

    st.metric(
        "Fee",
        f"{fee_pct:.2f}%",
    )