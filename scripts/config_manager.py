from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def load_config_override(
    config_override_path: Path,
) -> dict[str, Any]:
    """
    Load the dashboard configuration override file.

    Returns an empty dictionary if the file is missing, malformed,
    or does not contain a JSON object.
    """
    if not config_override_path.exists():
        return {}

    try:
        with config_override_path.open(
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {}

        return data

    except Exception:
        return {}


def get_config_value(
    *,
    key: str,
    env_key: str,
    default: Any,
    config_override_path: Path,
    cast_type: type = float,
) -> Any:
    """
    Resolve a configuration value using:

        1. Dashboard override JSON
        2. Environment variable
        3. Default value
    """
    override = load_config_override(
        config_override_path
    )

    if key in override:
        try:
            return cast_type(
                override[key]
            )
        except Exception:
            return default

    value = os.getenv(env_key)

    if value is None:
        return default

    try:
        return cast_type(value)
    except Exception:
        return default
