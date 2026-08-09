import json

from scripts.config_manager import (
    get_config_value,
    load_config_override,
)


def test_load_config_override_returns_empty_when_missing(
    tmp_path,
):
    path = tmp_path / "missing.json"

    assert load_config_override(path) == {}


def test_load_config_override_returns_dict_contents(
    tmp_path,
):
    path = tmp_path / "override.json"

    path.write_text(
        json.dumps(
            {
                "history_max_size_bytes": 123,
            }
        ),
        encoding="utf-8",
    )

    result = load_config_override(path)

    assert result == {
        "history_max_size_bytes": 123,
    }


def test_load_config_override_rejects_non_object_json(
    tmp_path,
):
    path = tmp_path / "override.json"

    path.write_text(
        json.dumps(
            [
                1,
                2,
                3,
            ]
        ),
        encoding="utf-8",
    )

    assert load_config_override(path) == {}


def test_load_config_override_returns_empty_for_malformed_json(
    tmp_path,
):
    path = tmp_path / "override.json"

    path.write_text(
        "{not-valid-json",
        encoding="utf-8",
    )

    assert load_config_override(path) == {}


def test_get_config_value_prefers_override(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "override.json"

    path.write_text(
        json.dumps(
            {
                "history_max_size_bytes": 500,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv(
        "BCH_HISTORY_MAX_SIZE_BYTES",
        "700",
    )

    result = get_config_value(
        key="history_max_size_bytes",
        env_key="BCH_HISTORY_MAX_SIZE_BYTES",
        default=1000,
        config_override_path=path,
        cast_type=int,
    )

    assert result == 500


def test_get_config_value_uses_environment_when_override_missing(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "missing.json"

    monkeypatch.setenv(
        "BCH_HISTORY_MAX_SIZE_BYTES",
        "700",
    )

    result = get_config_value(
        key="history_max_size_bytes",
        env_key="BCH_HISTORY_MAX_SIZE_BYTES",
        default=1000,
        config_override_path=path,
        cast_type=int,
    )

    assert result == 700


def test_get_config_value_uses_default_when_missing_everywhere(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "missing.json"

    monkeypatch.delenv(
        "BCH_HISTORY_MAX_SIZE_BYTES",
        raising=False,
    )

    result = get_config_value(
        key="history_max_size_bytes",
        env_key="BCH_HISTORY_MAX_SIZE_BYTES",
        default=1000,
        config_override_path=path,
        cast_type=int,
    )

    assert result == 1000


def test_get_config_value_returns_default_for_invalid_override(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "override.json"

    path.write_text(
        json.dumps(
            {
                "history_max_size_bytes": "not-an-int",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv(
        "BCH_HISTORY_MAX_SIZE_BYTES",
        "700",
    )

    result = get_config_value(
        key="history_max_size_bytes",
        env_key="BCH_HISTORY_MAX_SIZE_BYTES",
        default=1000,
        config_override_path=path,
        cast_type=int,
    )

    assert result == 1000


def test_get_config_value_returns_default_for_invalid_environment(
    tmp_path,
    monkeypatch,
):
    path = tmp_path / "missing.json"

    monkeypatch.setenv(
        "BCH_HISTORY_MAX_SIZE_BYTES",
        "not-an-int",
    )

    result = get_config_value(
        key="history_max_size_bytes",
        env_key="BCH_HISTORY_MAX_SIZE_BYTES",
        default=1000,
        config_override_path=path,
        cast_type=int,
    )

    assert result == 1000


def test_get_config_value_allows_zero_for_unlimited_history(
    tmp_path,
):
    path = tmp_path / "override.json"

    path.write_text(
        json.dumps(
            {
                "history_max_size_bytes": 0,
            }
        ),
        encoding="utf-8",
    )

    result = get_config_value(
        key="history_max_size_bytes",
        env_key="BCH_HISTORY_MAX_SIZE_BYTES",
        default=1_073_741_824,
        config_override_path=path,
        cast_type=int,
    )

    assert result == 0
