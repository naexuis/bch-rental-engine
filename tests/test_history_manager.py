import sqlite3
from pathlib import Path

from scripts.storage.history_manager import (
    get_history_statistics,
)
from scripts.storage.storage_manager import (
    RUN_HISTORY_TABLE,
    initialize_history_database,
    get_database_size_bytes,
)


def test_get_history_statistics_reports_count_and_timestamp_range(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "state" / "history.db"

    initialize_history_database(db_path)

    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            f"""
            INSERT INTO {RUN_HISTORY_TABLE} (
                timestamp
            )
            VALUES (?)
            """,
            [
                ("2026-08-08T12:00:00Z",),
                ("2026-08-08T10:00:00Z",),
                ("2026-08-08T14:00:00Z",),
            ],
        )
        conn.commit()

    stats = get_history_statistics(db_path)

    assert stats["record_count"] == 3
    assert stats["oldest_timestamp"] == "2026-08-08T10:00:00Z"
    assert stats["newest_timestamp"] == "2026-08-08T14:00:00Z"

def test_get_history_statistics_handles_empty_history(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "state" / "history.db"

    initialize_history_database(db_path)

    stats = get_history_statistics(db_path)

    assert stats["record_count"] == 0
    assert stats["oldest_timestamp"] is None
    assert stats["newest_timestamp"] is None
    assert stats["database_size_bytes"] == get_database_size_bytes(
        db_path
    )
    assert stats["database_size_bytes"] > 0

def test_get_history_statistics_reports_database_size(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "state" / "history.db"

    initialize_history_database(db_path)

    stats = get_history_statistics(db_path)

    assert stats["database_size_bytes"] == get_database_size_bytes(
        db_path
    )
    assert stats["database_size_bytes"] > 0