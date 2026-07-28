from pathlib import Path
import sqlite3

from scripts.storage.storage_manager import (
    RUN_HISTORY_TABLE,
    get_database_row_count,
    get_database_size_bytes,
    initialize_history_database,
    check_database_integrity,
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