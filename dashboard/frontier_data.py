from __future__ import annotations

import pandas as pd

from dashboard.ui_utils import (
    fmt_hashrate_from_ph,
    safe_num,
)


def build_frontier_dataframe(
    frontier: list[dict],
) -> pd.DataFrame:
    """
    Convert engine budget-frontier records into a normalized DataFrame.
    """
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

    return pd.DataFrame(rows)