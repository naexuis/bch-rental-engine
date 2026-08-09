import sqlite3

import pandas as pd
import pytest

from dashboard.history_data import (
    load_history_dataframe,
)


def create_run_history_db(
    db_path,
    rows,
    *,
    include_probability=True,
):
    with sqlite3.connect(db_path) as conn:
        if include_probability:
            conn.execute(
                """
                CREATE TABLE run_history (
                    timestamp TEXT,
                    best_recommendation TEXT,
                    best_prob_1plus REAL
                )
                """
            )

            conn.executemany(
                """
                INSERT INTO run_history (
                    timestamp,
                    best_recommendation,
                    best_prob_1plus
                )
                VALUES (?, ?, ?)
                """,
                rows,
            )

        else:
            conn.execute(
                """
                CREATE TABLE run_history (
                    timestamp TEXT,
                    best_recommendation TEXT
                )
                """
            )

            conn.executemany(
                """
                INSERT INTO run_history (
                    timestamp,
                    best_recommendation
                )
                VALUES (?, ?)
                """,
                rows,
            )

        conn.commit()


def test_missing_database_returns_empty_dataframe(
    tmp_path,
):
    db_path = tmp_path / "missing.db"

    result = load_history_dataframe(db_path)

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_empty_run_history_table_returns_empty_dataframe(
    tmp_path,
):
    db_path = tmp_path / "history.db"

    create_run_history_db(
        db_path,
        [],
    )

    result = load_history_dataframe(db_path)

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_history_rows_are_sorted_by_timestamp(
    tmp_path,
):
    db_path = tmp_path / "history.db"

    create_run_history_db(
        db_path,
        [
            (
                "2026-08-08 12:00:00",
                "WATCH",
                0.40,
            ),
            (
                "2026-08-08 10:00:00",
                "WAIT",
                0.20,
            ),
            (
                "2026-08-08 11:00:00",
                "RENT",
                0.30,
            ),
        ],
    )

    result = load_history_dataframe(db_path)

    assert list(
        result["best_recommendation"]
    ) == [
        "WAIT",
        "RENT",
        "WATCH",
    ]

    assert result.index.tolist() == [0, 1, 2]


def test_invalid_timestamps_are_removed(
    tmp_path,
):
    db_path = tmp_path / "history.db"

    create_run_history_db(
        db_path,
        [
            (
                "2026-08-08 10:00:00",
                "RENT",
                0.50,
            ),
            (
                "not-a-timestamp",
                "WATCH",
                0.25,
            ),
        ],
    )

    result = load_history_dataframe(db_path)

    assert len(result) == 1
    assert result.iloc[0]["best_recommendation"] == "RENT"
    assert pd.notna(result.iloc[0]["timestamp"])


def test_probability_fraction_is_converted_to_percent(
    tmp_path,
):
    db_path = tmp_path / "history.db"

    create_run_history_db(
        db_path,
        [
            (
                "2026-08-08 10:00:00",
                "RENT",
                0.55,
            ),
        ],
    )

    result = load_history_dataframe(db_path)

    assert (
        result.iloc[0]["best_prob_1plus_pct"]
        == pytest.approx(55.0)
    )


def test_probability_percent_column_is_optional(
    tmp_path,
):
    db_path = tmp_path / "history.db"

    create_run_history_db(
        db_path,
        [
            (
                "2026-08-08 10:00:00",
                "WATCH",
            ),
        ],
        include_probability=False,
    )

    result = load_history_dataframe(db_path)

    assert len(result) == 1
    assert "best_prob_1plus_pct" not in result.columns


def test_timestamp_column_is_datetime_after_loading(
    tmp_path,
):
    db_path = tmp_path / "history.db"

    create_run_history_db(
        db_path,
        [
            (
                "2026-08-08 10:00:00",
                "RENT",
                0.50,
            ),
        ],
    )

    result = load_history_dataframe(db_path)

    assert pd.api.types.is_datetime64_any_dtype(
        result["timestamp"]
    )
