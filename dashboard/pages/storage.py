from __future__ import annotations

from pathlib import Path

import streamlit as st

from dashboard.settings_service import (
    load_config_override,
)
from scripts.storage.history_manager import (
    get_history_statistics,
)
from scripts.storage.storage_manager import (
    get_storage_health,
    vacuum_database,
)


def render_storage_page(
    *,
    db_path: Path,
    config_override_path: Path,
) -> None:
    """
    Render storage health, usage, retention, and maintenance controls.
    """
    st.subheader("Storage")

    health = get_storage_health(
        db_path,
    )

    stats = get_history_statistics(
        db_path,
    )

    override = load_config_override(
        config_override_path,
    )

    history_max_size_bytes = int(
        override.get(
            "history_max_size_bytes",
            1_073_741_824,
        )
    )

    database_size_bytes = int(
        stats.get(
            "database_size_bytes",
            0,
        )
    )

    database_size_mib = (
        database_size_bytes / (1024 ** 2)
    )

    if history_max_size_bytes == 0:
        retention_label = "Unlimited"
        usage_label = "N/A"
    else:
        retention_gib = (
            history_max_size_bytes
            / (1024 ** 3)
        )

        usage_pct = (
            database_size_bytes
            / history_max_size_bytes
            * 100
        )

        retention_label = (
            f"{retention_gib:.2f} GiB"
        )

        usage_label = (
            f"{usage_pct:.2f}%"
        )

    st.markdown("### Storage Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Database Size",
        f"{database_size_mib:.2f} MiB",
    )

    c2.metric(
        "Retention Limit",
        retention_label,
    )

    c3.metric(
        "Storage Used",
        usage_label,
    )

    c4.metric(
        "History Records",
        f"{stats['record_count']:,}",
    )

    st.markdown("### History Range")

    h1, h2 = st.columns(2)

    h1.metric(
        "Oldest Record",
        stats["oldest_timestamp"]
        or "N/A",
    )

    h2.metric(
        "Newest Record",
        stats["newest_timestamp"]
        or "N/A",
    )

    st.markdown("### Database Health")

    if health.integrity_ok:
        st.success(
            "Database integrity check passed."
        )
    else:
        st.error(
            "Database integrity check failed."
        )

    st.divider()

    st.markdown("### Database Maintenance")

    st.caption(
        "Compacting the database runs SQLite VACUUM to reclaim unused "
        "space after history pruning or long-term operation."
    )

    if st.button(
        "Compact Database",
        type="secondary",
    ):
        size_before = db_path.stat().st_size if db_path.exists() else 0

        compacted = vacuum_database(
            db_path,
        )

        size_after = db_path.stat().st_size if db_path.exists() else 0

        if compacted:
            reclaimed_bytes = max(
                0,
                size_before - size_after,
            )

            reclaimed_mib = (
                reclaimed_bytes / (1024 ** 2)
            )

            st.success(
                "Database compacted successfully. "
                f"Reclaimed {reclaimed_mib:.2f} MiB."
            )

            st.cache_data.clear()
        else:
            st.warning(
                "Database does not exist yet, so there was nothing to compact."
            )