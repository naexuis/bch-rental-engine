from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def load_history_dataframe(
    db_path: Path,
) -> pd.DataFrame:
    """
    Load and normalize dashboard history data from SQLite.
    """
    if not db_path.exists():
        return pd.DataFrame()

    with sqlite3.connect(db_path) as conn:
        hist_df = pd.read_sql_query(
            "SELECT * FROM run_history ORDER BY timestamp ASC",
            conn,
        )

    if hist_df.empty:
        return hist_df

    hist_df["timestamp"] = pd.to_datetime(
        hist_df["timestamp"],
        errors="coerce",
    )

    hist_df = (
        hist_df
        .dropna(subset=["timestamp"])
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    if "best_prob_1plus" in hist_df.columns:
        hist_df["best_prob_1plus_pct"] = (
            hist_df["best_prob_1plus"] * 100
        )

    return hist_df
