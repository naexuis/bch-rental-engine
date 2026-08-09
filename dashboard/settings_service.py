from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def load_config_override(
    config_override_path: Path,
) -> dict:
    if not config_override_path.exists():
        return {}

    try:
        with config_override_path.open(
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    except Exception:
        return {}


def save_config_override(
    config: dict,
    *,
    config_dir: Path,
    config_override_path: Path,
) -> None:
    config_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    tmp = config_override_path.with_suffix(".tmp")

    with tmp.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            config,
            f,
            indent=2,
            sort_keys=True,
        )

    tmp.replace(config_override_path)


def request_engine_run(
    config_dir: Path,
) -> None:
    """
    Request an immediate engine run through the shared config directory.
    """
    config_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    run_now_trigger_path = (
        config_dir / "run_now.trigger"
    )

    run_now_trigger_path.touch()


def resolve_setting_value(
    key: str,
    override: dict,
    state_config: dict,
    latest: pd.Series,
    default: int | float,
) -> int | float:
    """
    Resolve one dashboard setting using the configured priority order.

    Priority:
        1. Dashboard override file
        2. Latest JSON state config
        3. Latest history row
        4. Hardcoded default
    """
    if key in override:
        return override[key]

    if key in state_config:
        return state_config[key]

    latest_value = latest.get(key)

    if pd.notna(latest_value):
        return latest_value

    return default
