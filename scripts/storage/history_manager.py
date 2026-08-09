from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from scripts.storage.storage_manager import (
    get_database_size_bytes,
    initialize_history_database,
    vacuum_database,
)


def get_history_rows(
    db_path: Path,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Return the most recent history rows, newest first.
    """
    initialize_history_database(db_path)

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            """
            SELECT *
            FROM run_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]

ALLOWED_LATEST_COLUMNS = {
    "opportunity_score",
    "opportunity_action",
}


def get_latest_value(
    db_path: Path,
    column_name: str,
) -> Any | None:
    """
    Return the latest value for an allowed run_history column.

    The column name is validated because SQLite parameters cannot be used
    for identifiers such as column names.
    """
    if column_name not in ALLOWED_LATEST_COLUMNS:
        raise ValueError(
            f"Unsupported history column: {column_name!r}"
        )

    initialize_history_database(db_path)

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            f"""
            SELECT {column_name}
            FROM run_history
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

    if row is None:
        return None

    return row[0]


RUN_HISTORY_INSERT_COLUMNS = (
    "timestamp",
    "btc_usd",
    "bch_usd",
    "bch_btc",
    "bch_difficulty",
    "bch_network_hashrate_eh",
    "best_source",
    "best_name",
    "best_hashrate_ph",
    "best_duration_hours",
    "best_cost_usd",
    "best_prob_1plus",
    "best_prob_2plus",
    "best_expected_profit_usd",
    "best_roi_pct",
    "best_risk_adjusted_roi_pct",
    "best_fair_value_ratio",
    "best_premium_discount_pct",
    "best_alert_tier",
    "best_recommendation",
    "market_regime",
    "opportunity_score",
    "opportunity_action",
    "canonical_decision",
    "budget_min_usd",
    "budget_max_usd",
    "budget_step_usd",
    "braiins_price_btc_per_ph_day",
    "best_mrr_price_btc_per_ph_day",
    "scenario_count",
)


def insert_history_row(
    db_path: Path,
    record: dict[str, Any],
) -> int:
    """
    Insert one execution record into run_history.

    Returns the newly created row ID.
    """
    initialize_history_database(db_path)

    missing_columns = [
        column
        for column in RUN_HISTORY_INSERT_COLUMNS
        if column not in record
    ]

    if missing_columns:
        raise ValueError(
            "History record is missing required columns: "
            + ", ".join(missing_columns)
        )

    column_sql = ", ".join(RUN_HISTORY_INSERT_COLUMNS)
    placeholder_sql = ", ".join(
        "?" for _ in RUN_HISTORY_INSERT_COLUMNS
    )
    values = tuple(
        record[column]
        for column in RUN_HISTORY_INSERT_COLUMNS
    )

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            f"""
            INSERT INTO run_history ({column_sql})
            VALUES ({placeholder_sql})
            """,
            values,
        )
        conn.commit()

        row_id = cursor.lastrowid

    if row_id is None:
        raise RuntimeError("SQLite did not return a history row ID.")

    return int(row_id)


def get_history_trend_windows(
    db_path: Path,
    windows: dict[str, int],
    metrics: list[str],
) -> dict[str, Any]:
    """
    Return start, end, and percentage-change values for each metric
    across the requested history windows.
    """
    initialize_history_database(db_path)

    allowed_metrics = set(RUN_HISTORY_INSERT_COLUMNS)

    unsupported_metrics = [
        metric
        for metric in metrics
        if metric not in allowed_metrics
    ]

    if unsupported_metrics:
        raise ValueError(
            "Unsupported history metrics: "
            + ", ".join(unsupported_metrics)
        )

    trends: dict[str, Any] = {}

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        metric_sql = ", ".join(metrics)

        for label, row_limit in windows.items():
            rows = conn.execute(
                f"""
                SELECT {metric_sql}
                FROM run_history
                ORDER BY id DESC
                LIMIT ?
                """,
                (row_limit,),
            ).fetchall()

            rows = list(reversed(rows))

            trends[label] = {
                "rows": len(rows),
                "metrics": {},
            }

            if len(rows) < 2:
                continue

            first = rows[0]
            last = rows[-1]

            for metric in metrics:
                start = first[metric]
                end = last[metric]

                if start is None or end is None or start == 0:
                    change_pct = None
                else:
                    change_pct = ((end - start) / start) * 100

                trends[label]["metrics"][metric] = {
                    "start": start,
                    "end": end,
                    "change_pct": change_pct,
                }

    return trends

def get_history_statistics(
    db_path: Path,
) -> dict[str, Any]:
    """
    Return basic execution-history statistics.

    This function is read-only and does not initialize or migrate the
    database. Schema initialization and migration are owned by engine
    startup.
    """
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS record_count,
                MIN(timestamp) AS oldest_timestamp,
                MAX(timestamp) AS newest_timestamp
            FROM run_history
            """
        ).fetchone()

    if row is None:
        return {
            "record_count": 0,
            "oldest_timestamp": None,
            "newest_timestamp": None,
            "database_size_bytes": get_database_size_bytes(
                db_path
            ),
        }

    return {
        "record_count": int(row[0]),
        "oldest_timestamp": row[1],
        "newest_timestamp": row[2],
        "database_size_bytes": get_database_size_bytes(
            db_path
        ),
    }

def prune_oldest_history_rows(
    db_path: Path,
    *,
    row_count: int,
) -> int:
    """
    Delete up to row_count oldest history records.

    Returns the number of rows deleted.
    """
    if row_count <= 0:
        return 0

    initialize_history_database(db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
            DELETE FROM run_history
            WHERE id IN (
                SELECT id
                FROM run_history
                ORDER BY id ASC
                LIMIT ?
            )
            """,
            (row_count,),
        )

        conn.commit()

        deleted_count = cursor.rowcount

    return max(0, int(deleted_count))

def enforce_history_size_limit(
    db_path: Path,
    *,
    max_size_bytes: int,
) -> dict[str, Any]:
    """
    Enforce the configured maximum history database size.

    Oldest history rows are removed in batches until the database is
    within the configured size limit or no history rows remain.
    """
    initialize_history_database(db_path)

    size_before = get_database_size_bytes(db_path)

    if size_before <= max_size_bytes:
        return {
            "pruned": False,
            "rows_deleted": 0,
            "size_before_bytes": size_before,
            "size_after_bytes": size_before,
        }

    total_deleted = 0

    while True:
        stats = get_history_statistics(db_path)
        record_count = int(stats["record_count"])

        if record_count <= 0:
            break

        batch_size = max(
            1,
            record_count // 10,
        )

        deleted = prune_oldest_history_rows(
            db_path,
            row_count=batch_size,
        )

        if deleted <= 0:
            break

        total_deleted += deleted

        vacuum_database(db_path)

        current_size = get_database_size_bytes(
            db_path
        )

        if current_size <= max_size_bytes:
            break

    size_after = get_database_size_bytes(
        db_path
    )

    return {
        "pruned": total_deleted > 0,
        "rows_deleted": total_deleted,
        "size_before_bytes": size_before,
        "size_after_bytes": size_after,
    }