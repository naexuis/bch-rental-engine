import pandas as pd
import pytest

from dashboard.frontier_data import (
    build_frontier_dataframe,
)


def test_build_frontier_dataframe_uses_best_score_first():
    frontier = [
        {
            "budget_usd": 500,
            "best_score": {
                "cost_usd": 480,
                "hashrate_ph": 250,
                "duration_hours": 2.5,
                "prob_1plus": 0.72,
                "prob_2plus": 0.31,
                "fair_value_ratio": 0.98,
                "risk_adjusted_roi_pct": 4.5,
                "recommendation": "RENT",
                "source": "braiins",
            },
            "best_probability": {
                "cost_usd": 999,
                "hashrate_ph": 999,
                "duration_hours": 9.9,
                "prob_1plus": 0.99,
            },
        }
    ]

    result = build_frontier_dataframe(frontier)

    assert len(result) == 1

    row = result.iloc[0]

    assert row["budget_usd"] == 500
    assert row["cost_usd"] == 480
    assert row["hashrate"] == "250.00 PH/s"
    assert row["duration_hours"] == 2.5
    assert row["prob_1plus_pct"] == 72.0
    assert row["prob_2plus_pct"] == 31.0
    assert row["fvr"] == 0.98
    assert row["risk_roi_pct"] == 4.5
    assert row["recommendation"] == "RENT"
    assert row["source"] == "BRAIINS"


def test_build_frontier_dataframe_falls_back_to_best_probability():
    frontier = [
        {
            "budget_usd": 300,
            "best_score": {},
            "best_probability": {
                "cost_usd": 300,
                "hashrate_ph": 0.5,
                "duration_hours": 1.25,
                "prob_1plus": 0.55,
                "prob_2plus": 0.12,
                "fair_value_ratio": 1.01,
                "risk_adjusted_roi_pct": -2.0,
                "recommendation": "WATCH",
                "source": "mrr",
            },
        }
    ]

    result = build_frontier_dataframe(frontier)

    row = result.iloc[0]

    assert row["cost_usd"] == 300
    assert row["hashrate"] == "500.00 TH/s"
    assert row["duration_hours"] == 1.25
    assert row["prob_1plus_pct"] == pytest.approx(55.0)
    assert row["prob_2plus_pct"] == pytest.approx(12.0)
    assert row["source"] == "MRR"


def test_budget_defaults_to_cost_when_budget_missing():
    frontier = [
        {
            "best_score": {
                "cost_usd": 420,
            },
        }
    ]

    result = build_frontier_dataframe(frontier)

    assert result.iloc[0]["budget_usd"] == 420


def test_missing_fields_receive_safe_defaults():
    frontier = [
        {}
    ]

    result = build_frontier_dataframe(frontier)

    row = result.iloc[0]

    assert row["budget_usd"] == 0
    assert row["cost_usd"] == 0
    assert row["hashrate"] == "0.00 MH/s"
    assert row["duration_hours"] == 0
    assert row["prob_1plus_pct"] == 0
    assert row["prob_2plus_pct"] == 0
    assert row["fvr"] == 0
    assert row["risk_roi_pct"] == 0
    assert row["recommendation"] == "N/A"
    assert row["source"] == "N/A"


def test_empty_frontier_returns_empty_dataframe():
    result = build_frontier_dataframe([])

    assert isinstance(result, pd.DataFrame)
    assert result.empty
