import sqlite3
from pathlib import Path
import pytest

from scripts.storage.history_manager import (
    get_history_statistics,
    prune_oldest_history_rows,
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

def test_prune_oldest_history_rows_removes_oldest_records(
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
                ("2026-08-08T10:00:00Z",),
                ("2026-08-08T11:00:00Z",),
                ("2026-08-08T12:00:00Z",),
                ("2026-08-08T13:00:00Z",),
                ("2026-08-08T14:00:00Z",),
            ],
        )
        conn.commit()

    deleted_count = prune_oldest_history_rows(
        db_path,
        row_count=2,
    )

    with sqlite3.connect(db_path) as conn:
        remaining_rows = conn.execute(
            f"""
            SELECT timestamp
            FROM {RUN_HISTORY_TABLE}
            ORDER BY id ASC
            """
        ).fetchall()

    assert deleted_count == 2

    assert remaining_rows == [
        ("2026-08-08T12:00:00Z",),
        ("2026-08-08T13:00:00Z",),
        ("2026-08-08T14:00:00Z",),
    ]

def test_prune_oldest_history_rows_caps_at_available_rows(
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
                ("2026-08-08T10:00:00Z",),
                ("2026-08-08T11:00:00Z",),
                ("2026-08-08T12:00:00Z",),
            ],
        )
        conn.commit()

    deleted_count = prune_oldest_history_rows(
        db_path,
        row_count=10,
    )

    stats = get_history_statistics(db_path)

    assert deleted_count == 3
    assert stats["record_count"] == 0
    assert stats["oldest_timestamp"] is None
    assert stats["newest_timestamp"] is None


@pytest.mark.parametrize(
    "row_count",
    [
        0,
        -1,
        -100,
    ],
)
def test_prune_oldest_history_rows_noops_for_nonpositive_count(
    tmp_path: Path,
    row_count: int,
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
            ("2026-08-08T10:00:00Z",),
        )
        conn.commit()

    deleted_count = prune_oldest_history_rows(
        db_path,
        row_count=row_count,
    )

    stats = get_history_statistics(db_path)

    assert deleted_count == 0
    assert stats["record_count"] == 1