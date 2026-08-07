import pandas as pd

from dashboard.app import resolve_setting_value


def test_setting_prefers_dashboard_override():
    result = resolve_setting_value(
        key="hashrate_min_ph",
        override={"hashrate_min_ph": 150},
        state_config={"hashrate_min_ph": 200},
        latest=pd.Series({"hashrate_min_ph": 250}),
        default=300,
    )

    assert result == 150


def test_setting_falls_back_to_state_config():
    result = resolve_setting_value(
        key="hashrate_min_ph",
        override={},
        state_config={"hashrate_min_ph": 200},
        latest=pd.Series({"hashrate_min_ph": 250}),
        default=300,
    )

    assert result == 200


def test_setting_falls_back_to_history():
    result = resolve_setting_value(
        key="budget_min_usd",
        override={},
        state_config={},
        latest=pd.Series({"budget_min_usd": 225}),
        default=100,
    )

    assert result == 225


def test_setting_falls_back_to_default_when_missing():
    result = resolve_setting_value(
        key="hashrate_step_ph",
        override={},
        state_config={},
        latest=pd.Series(dtype="object"),
        default=50,
    )

    assert result == 50


def test_setting_ignores_nan_history_value():
    result = resolve_setting_value(
        key="budget_step_usd",
        override={},
        state_config={},
        latest=pd.Series({"budget_step_usd": float("nan")}),
        default=10,
    )

    assert result == 10
