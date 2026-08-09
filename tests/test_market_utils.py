import pandas as pd
import pytest

from dashboard.market_utils import (
    calculate_technical_indicators,
    get_candle_settings,
    summarize_technical_indicators,
)


def test_calculate_technical_indicators_empty_dataframe():
    df = pd.DataFrame()

    result = calculate_technical_indicators(df)

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_calculate_technical_indicators_adds_expected_columns():
    periods = 220

    df = pd.DataFrame(
        {
            "time": pd.date_range(
                "2026-01-01",
                periods=periods,
                freq="h",
            ),
            "open": range(100, 100 + periods),
            "high": range(101, 101 + periods),
            "low": range(99, 99 + periods),
            "close": range(100, 100 + periods),
            "volume": [1000] * periods,
        }
    )

    result = calculate_technical_indicators(df)

    for column in [
        "ema20",
        "ema50",
        "ema200",
        "rsi14",
        "atr14",
    ]:
        assert column in result.columns


def test_calculate_technical_indicators_sorts_by_time():
    df = pd.DataFrame(
        {
            "time": pd.to_datetime(
                [
                    "2026-08-08 12:00:00",
                    "2026-08-08 10:00:00",
                    "2026-08-08 11:00:00",
                ]
            ),
            "open": [102, 100, 101],
            "high": [103, 101, 102],
            "low": [101, 99, 100],
            "close": [102, 100, 101],
            "volume": [1000, 1000, 1000],
        }
    )

    result = calculate_technical_indicators(df)

    assert result["time"].is_monotonic_increasing
    assert result.index.tolist() == [0, 1, 2]


def test_calculate_technical_indicators_coerces_numeric_columns():
    periods = 25

    df = pd.DataFrame(
        {
            "time": pd.date_range(
                "2026-01-01",
                periods=periods,
                freq="h",
            ),
            "open": [str(100 + i) for i in range(periods)],
            "high": [str(101 + i) for i in range(periods)],
            "low": [str(99 + i) for i in range(periods)],
            "close": [str(100 + i) for i in range(periods)],
            "volume": ["1000"] * periods,
        }
    )

    result = calculate_technical_indicators(df)

    for column in [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]:
        assert pd.api.types.is_numeric_dtype(
            result[column]
        )


def test_summarize_technical_indicators_empty_dataframe():
    result = summarize_technical_indicators(
        pd.DataFrame()
    )

    assert result == {
        "trend": "Insufficient Data",
        "momentum": "Insufficient Data",
        "technical_score": 0.0,
        "close": None,
        "ema20": None,
        "ema50": None,
        "ema200": None,
        "rsi14": None,
        "atr14": None,
    }


def test_summarize_technical_indicators_strong_bullish():
    df = pd.DataFrame(
        {
            "close": [105, 106, 107, 108, 109, 110],
            "ema20": [100, 101, 102, 103, 104, 105],
            "ema50": [95, 96, 97, 98, 99, 100],
            "ema200": [90, 91, 92, 93, 94, 95],
            "rsi14": [60] * 6,
            "atr14": [2] * 6,
        }
    )

    result = summarize_technical_indicators(df)

    assert result["trend"] == "Strong Bullish"
    assert result["momentum"] == "Positive"
    assert result["technical_score"] == pytest.approx(
        95.0
    )


def test_summarize_technical_indicators_strong_bearish():
    df = pd.DataFrame(
        {
            "close": [105, 104, 103, 102, 101, 100],
            "ema20": [110, 109, 108, 107, 106, 105],
            "ema50": [115, 114, 113, 112, 111, 110],
            "ema200": [120, 119, 118, 117, 116, 115],
            "rsi14": [40] * 6,
            "atr14": [2] * 6,
        }
    )

    result = summarize_technical_indicators(df)

    assert result["trend"] == "Strong Bearish"
    assert result["momentum"] == "Negative"
    assert result["technical_score"] == pytest.approx(
        10.0
    )


@pytest.mark.parametrize(
    (
        "range_label",
        "left_interval",
        "right_interval",
    ),
    [
        ("Past 24 Hours", "15m", "5m"),
        ("Past 3 Days", "1h", "15m"),
        ("Past 7 Days", "4h", "1h"),
        ("Past 30 Days", "1d", "4h"),
        ("Past Year", "1wk", "1d"),
    ],
)
def test_get_candle_settings_known_ranges(
    range_label,
    left_interval,
    right_interval,
):
    result = get_candle_settings(range_label)

    assert result["left_interval"] == left_interval
    assert result["right_interval"] == right_interval


def test_get_candle_settings_unknown_range_defaults_to_seven_days():
    result = get_candle_settings("Unknown Range")
    expected = get_candle_settings("Past 7 Days")

    assert result == expected
