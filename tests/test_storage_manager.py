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
