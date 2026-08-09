from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Final
from dataclasses import dataclass


RUN_HISTORY_TABLE: Final[str] = "run_history"
CURRENT_SCHEMA_VERSION: Final[int] = 1

@dataclass(frozen=True)
class StorageHealth:
    """
    Summary of the current SQLite database health.
    """

    database_exists: bool
    database_size_bytes: int
    row_count: int
    integrity_ok: bool


def migrate_schema_v0_to_v1(
    conn: sqlite3.Connection,
) -> None:
    """
    Upgrade a legacy version-0 history database to schema version 1.

    Existing history rows are preserved while missing version-1 columns
    are added.
    """
    existing_columns = {
        row[1]
        for row in conn.execute(
            f"PRAGMA table_info({RUN_HISTORY_TABLE})"
        ).fetchall()
    }

    required_columns = {
        "market_regime": "TEXT",
        "opportunity_score": "REAL",
        "opportunity_action": "TEXT",
        "canonical_decision": "TEXT",
        "budget_min_usd": "REAL",
        "budget_max_usd": "REAL",
        "budget_step_usd": "REAL",
    }

    for column_name, column_type in required_columns.items():
        if column_name not in existing_columns:
            conn.execute(
                f"""
                ALTER TABLE {RUN_HISTORY_TABLE}
                ADD COLUMN {column_name} {column_type}
                """
            )

    conn.execute("PRAGMA user_version = 1")


def initialize_history_database(db_path: Path) -> None:
    """
    Create the history database and apply all currently supported schema
    migrations.

    This function is safe to call multiple times.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        current_user_version = conn.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

        if current_user_version > CURRENT_SCHEMA_VERSION:
            raise RuntimeError(
                "Database uses a newer schema version "
                f"({current_user_version}) than this application supports "
                f"({CURRENT_SCHEMA_VERSION})."
            )
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {RUN_HISTORY_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,

                btc_usd REAL,
                bch_usd REAL,
                bch_btc REAL,
                bch_difficulty REAL,
                bch_network_hashrate_eh REAL,

                best_source TEXT,
                best_name TEXT,
                best_hashrate_ph REAL,
                best_duration_hours REAL,
                best_cost_usd REAL,

                best_prob_1plus REAL,
                best_prob_2plus REAL,
                best_expected_profit_usd REAL,
                best_roi_pct REAL,
                best_risk_adjusted_roi_pct REAL,

                best_fair_value_ratio REAL,
                best_premium_discount_pct REAL,
                best_alert_tier TEXT,
                best_recommendation TEXT,

                market_regime TEXT,
                opportunity_score REAL,
                opportunity_action TEXT,
                canonical_decision TEXT,

                budget_min_usd REAL,
                budget_max_usd REAL,
                budget_step_usd REAL,

                braiins_price_btc_per_ph_day REAL,
                best_mrr_price_btc_per_ph_day REAL,

                scenario_count INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        if current_user_version == 0:
            migrate_schema_v0_to_v1(conn)

        conn.commit()


def get_database_size_bytes(
    db_path: Path,
) -> int:
    """
    Return the current SQLite database size in bytes.

    Returns zero if the database does not yet exist.
    """
    if not db_path.exists():
        return 0

    return db_path.stat().st_size


def get_database_row_count(
    db_path: Path,
) -> int:
    """
    Return the number of history rows currently stored.

    Returns zero if the database does not yet exist.
    """
    if not db_path.exists():
        return 0

    with sqlite3.connect(db_path) as conn:
        result = conn.execute(
            f"SELECT COUNT(*) FROM {RUN_HISTORY_TABLE}"
        ).fetchone()

    return int(result[0]) if result else 0

def check_database_integrity(
    db_path: Path,
) -> bool:
    """
    Run SQLite's integrity check.

    Returns:
        True if the database passes the integrity check or does not yet exist.
        False if corruption is detected.
    """
    if not db_path.exists():
        return True

    with sqlite3.connect(db_path) as conn:
        result = conn.execute("PRAGMA integrity_check").fetchone()

    return bool(result and result[0] == "ok")

def vacuum_database(
    db_path: Path,
) -> bool:
    """
    Run SQLite VACUUM to reclaim unused space.

    Returns:
        True if the operation completed successfully.
        False if the database does not yet exist.
    """
    if not db_path.exists():
        return False

    with sqlite3.connect(db_path) as conn:
        conn.execute("VACUUM")

    return True

def get_storage_health(
    db_path: Path,
) -> StorageHealth:
    """
    Return a summary of the current storage health.
    """
    exists = db_path.exists()

    return StorageHealth(
        database_exists=exists,
        database_size_bytes=get_database_size_bytes(db_path),
        row_count=get_database_row_count(db_path),
        integrity_ok=check_database_integrity(db_path),
    )
