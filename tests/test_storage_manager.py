from pathlib import Path
import sqlite3

from scripts.storage.storage_manager import (
    RUN_HISTORY_TABLE,
    get_database_row_count,
    get_database_size_bytes,
    initialize_history_database,
    check_database_integrity,
    vacuum_database,
    StorageHealth,
    get_storage_health,
    CURRENT_SCHEMA_VERSION,
)


def test_database_metrics_return_zero_when_database_is_missing(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "history.db"

    assert get_database_size_bytes(db_path) == 0
    assert get_database_row_count(db_path) == 0


def test_database_metrics_report_initialized_database(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "state" / "history.db"

    initialize_history_database(db_path)

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            f"""
            INSERT INTO {RUN_HISTORY_TABLE} (
                timestamp
            )
            VALUES (?)
            """,
            ("2026-07-27T12:00:00Z",),
        )
        conn.commit()

    assert get_database_size_bytes(db_path) > 0
    assert get_database_row_count(db_path) == 1

def test_database_integrity_returns_true_when_database_is_missing(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "history.db"

    assert check_database_integrity(db_path) is True


def test_database_integrity_passes_for_initialized_database(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "state" / "history.db"

    initialize_history_database(db_path)

    assert check_database_integrity(db_path) is True

def test_vacuum_database_returns_false_when_database_is_missing(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "history.db"

    assert vacuum_database(db_path) is False


def test_vacuum_database_completes_for_initialized_database(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "state" / "history.db"

    initialize_history_database(db_path)

    assert vacuum_database(db_path) is True
    assert check_database_integrity(db_path) is True

def test_get_storage_health_for_missing_database(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "missing" / "history.db"

    health = get_storage_health(db_path)

    assert isinstance(health, StorageHealth)
    assert health.database_exists is False
    assert health.database_size_bytes == 0
    assert health.row_count == 0
    assert health.integrity_ok is True


def test_get_storage_health_for_initialized_database(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "state" / "history.db"

    initialize_history_database(db_path)

    health = get_storage_health(db_path)

    assert isinstance(health, StorageHealth)
    assert health.database_exists is True
    assert health.database_size_bytes > 0
    assert health.row_count == 0
    assert health.integrity_ok is True


def test_initialize_history_database_adds_canonical_decision_column(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "state" / "history.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            f"""
            CREATE TABLE {RUN_HISTORY_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                opportunity_action TEXT
            )
            """
        )
        conn.execute(
            f"""
            INSERT INTO {RUN_HISTORY_TABLE} (
                timestamp,
                opportunity_action
            )
            VALUES (?, ?)
            """,
            (
                "2026-08-06T12:00:00Z",
                "WATCH",
            ),
        )
        conn.commit()

    initialize_history_database(db_path)

    with sqlite3.connect(db_path) as conn:
        columns = {
            row[1]
            for row in conn.execute(
                f"PRAGMA table_info({RUN_HISTORY_TABLE})"
            ).fetchall()
        }

        row = conn.execute(
            f"""
            SELECT
                timestamp,
                opportunity_action,
                canonical_decision
            FROM {RUN_HISTORY_TABLE}
            """
        ).fetchone()

    assert "canonical_decision" in columns
    assert row == (
        "2026-08-06T12:00:00Z",
        "WATCH",
        None,
    )

def test_initialize_history_database_sets_current_schema_version(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "state" / "history.db"

    initialize_history_database(db_path)

    with sqlite3.connect(db_path) as conn:
        user_version = conn.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

    assert user_version == CURRENT_SCHEMA_VERSION