import json

import pandas as pd

from dashboard.settings_service import (
    load_config_override,
    request_engine_run,
    resolve_setting_value,
    save_config_override,
)


def test_load_missing_override_returns_empty_dict(
    tmp_path,
):
    path = tmp_path / "missing.json"

    result = load_config_override(path)

    assert result == {}


def test_load_valid_override_returns_json_contents(
    tmp_path,
):
    path = tmp_path / "override.json"

    path.write_text(
        json.dumps(
            {
                "budget_min_usd": 250,
                "budget_max_usd": 900,
            }
        ),
        encoding="utf-8",
    )

    result = load_config_override(path)

    assert result == {
        "budget_min_usd": 250,
        "budget_max_usd": 900,
    }


def test_load_malformed_override_returns_empty_dict(
    tmp_path,
):
    path = tmp_path / "override.json"

    path.write_text(
        "{not-valid-json",
        encoding="utf-8",
    )

    result = load_config_override(path)

    assert result == {}


def test_save_config_override_creates_directory_and_file(
    tmp_path,
):
    config_dir = tmp_path / "config"
    config_path = config_dir / "dashboard_config_override.json"

    config = {
        "budget_min_usd": 100,
        "budget_max_usd": 1000,
        "budget_step_usd": 25,
    }

    save_config_override(
        config,
        config_dir=config_dir,
        config_override_path=config_path,
    )

    assert config_dir.exists()
    assert config_path.exists()

    saved = json.loads(
        config_path.read_text(
            encoding="utf-8",
        )
    )

    assert saved == config


def test_save_config_override_removes_tmp_file_after_replace(
    tmp_path,
):
    config_dir = tmp_path / "config"
    config_path = config_dir / "dashboard_config_override.json"

    save_config_override(
        {
            "hashrate_min_ph": 300,
        },
        config_dir=config_dir,
        config_override_path=config_path,
    )

    tmp_file = config_path.with_suffix(".tmp")

    assert config_path.exists()
    assert not tmp_file.exists()


def test_request_engine_run_creates_trigger_file(
    tmp_path,
):
    config_dir = tmp_path / "config"

    request_engine_run(config_dir)

    trigger = config_dir / "run_now.trigger"

    assert config_dir.exists()
    assert trigger.exists()
    assert trigger.is_file()


def test_resolve_setting_value_prefers_override():
    latest = pd.Series(
        {
            "budget_min_usd": 400,
        }
    )

    result = resolve_setting_value(
        key="budget_min_usd",
        override={
            "budget_min_usd": 100,
        },
        state_config={
            "budget_min_usd": 200,
        },
        latest=latest,
        default=300,
    )

    assert result == 100


def test_resolve_setting_value_uses_state_config_when_no_override():
    latest = pd.Series(
        {
            "budget_min_usd": 400,
        }
    )

    result = resolve_setting_value(
        key="budget_min_usd",
        override={},
        state_config={
            "budget_min_usd": 200,
        },
        latest=latest,
        default=300,
    )

    assert result == 200


def test_resolve_setting_value_uses_latest_when_no_override_or_state():
    latest = pd.Series(
        {
            "budget_min_usd": 400,
        }
    )

    result = resolve_setting_value(
        key="budget_min_usd",
        override={},
        state_config={},
        latest=latest,
        default=300,
    )

    assert result == 400


def test_resolve_setting_value_uses_default_when_latest_missing():
    latest = pd.Series(dtype=float)

    result = resolve_setting_value(
        key="budget_min_usd",
        override={},
        state_config={},
        latest=latest,
        default=300,
    )

    assert result == 300


def test_resolve_setting_value_uses_default_when_latest_nan():
    latest = pd.Series(
        {
            "budget_min_usd": float("nan"),
        }
    )

    result = resolve_setting_value(
        key="budget_min_usd",
        override={},
        state_config={},
        latest=latest,
        default=300,
    )

    assert result == 300
