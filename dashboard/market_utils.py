from __future__ import annotations

import pandas as pd
import yfinance as yf

from dashboard.ui_utils import safe_num


def summarize_technical_indicators(df: pd.DataFrame) -> dict:
    """
    Summarize the latest technical state for display in the dashboard.
    """
    empty_summary = {
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

    if df.empty:
        return empty_summary

    valid_rows = df.dropna(subset=["close"])

    if valid_rows.empty:
        return empty_summary

    latest_row = valid_rows.iloc[-1]

    close = safe_num(latest_row.get("close"), None)
    ema20 = latest_row.get("ema20")
    ema50 = latest_row.get("ema50")
    ema200 = latest_row.get("ema200")
    rsi14 = latest_row.get("rsi14")
    atr14 = latest_row.get("atr14")

    score = 50.0

    if pd.notna(ema20) and close is not None:
        score += 10 if close > ema20 else -10

    if pd.notna(ema20) and pd.notna(ema50):
        score += 15 if ema20 > ema50 else -15

    if pd.notna(ema50) and pd.notna(ema200):
        score += 10 if ema50 > ema200 else -10

    if pd.notna(rsi14):
        if 50 <= rsi14 <= 70:
            score += 10
        elif 30 <= rsi14 < 50:
            score -= 5
        elif rsi14 > 70:
            score -= 5
        elif rsi14 < 30:
            score += 5

    score = max(0.0, min(100.0, score))

    if close is None or pd.isna(ema20):
        trend = "Insufficient Data"

    elif pd.isna(ema50):
        recent_window = df.tail(min(6, len(df)))

        ema20_slope = (
            recent_window["ema20"].iloc[-1]
            - recent_window["ema20"].iloc[0]
            if recent_window["ema20"].notna().all()
            else 0.0
        )

        if close > ema20 and ema20_slope > 0:
            trend = "Bullish"
        elif close < ema20 and ema20_slope < 0:
            trend = "Bearish"
        else:
            trend = "Neutral"

    else:
        recent_window = df.tail(min(6, len(df)))

        ema20_slope = (
            recent_window["ema20"].iloc[-1]
            - recent_window["ema20"].iloc[0]
            if recent_window["ema20"].notna().all()
            else 0.0
        )

        ema50_slope = (
            recent_window["ema50"].iloc[-1]
            - recent_window["ema50"].iloc[0]
            if recent_window["ema50"].notna().all()
            else 0.0
        )

        bullish_signals = 0
        bearish_signals = 0

        if close > ema20:
            bullish_signals += 1
        elif close < ema20:
            bearish_signals += 1

        if ema20 > ema50:
            bullish_signals += 1
        elif ema20 < ema50:
            bearish_signals += 1

        if ema20_slope > 0:
            bullish_signals += 1
        elif ema20_slope < 0:
            bearish_signals += 1

        if ema50_slope > 0:
            bullish_signals += 1
        elif ema50_slope < 0:
            bearish_signals += 1

        if bullish_signals == 4:
            trend = "Strong Bullish"
        elif bullish_signals >= 3:
            trend = "Bullish"
        elif bearish_signals == 4:
            trend = "Strong Bearish"
        elif bearish_signals >= 3:
            trend = "Bearish"
        else:
            trend = "Neutral"

    if pd.isna(rsi14):
        momentum = "Insufficient Data"
    elif rsi14 >= 70:
        momentum = "Overbought"
    elif rsi14 <= 30:
        momentum = "Oversold"
    elif rsi14 >= 55:
        momentum = "Positive"
    elif rsi14 <= 45:
        momentum = "Negative"
    else:
        momentum = "Neutral"

    return {
        "trend": trend,
        "momentum": momentum,
        "technical_score": round(score, 1),
        "close": close,
        "ema20": None if pd.isna(ema20) else float(ema20),
        "ema50": None if pd.isna(ema50) else float(ema50),
        "ema200": None if pd.isna(ema200) else float(ema200),
        "rsi14": None if pd.isna(rsi14) else float(rsi14),
        "atr14": None if pd.isna(atr14) else float(atr14),
    }


def fetch_yfinance_ohlc(
    ticker: str,
    period: str,
    interval: str,
) -> pd.DataFrame:
    df = yf.Ticker(ticker).history(
        period=period,
        interval=interval,
    )

    if df.empty:
        return pd.DataFrame()

    df = df.reset_index()

    time_col = "Datetime" if "Datetime" in df.columns else "Date"

    df = df.rename(
        columns={
            time_col: "time",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )

    return df[
        ["time", "open", "high", "low", "close", "volume"]
    ].dropna()


def calculate_technical_indicators(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add EMA, RSI, ATR, trend, and technical-score fields to OHLC data.
    """
    if df.empty:
        return df.copy()

    result = (
        df.copy()
        .sort_values("time")
        .reset_index(drop=True)
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    for column in numeric_columns:
        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

    result = result.dropna(
        subset=["high", "low", "close"]
    )

    result["ema20"] = result["close"].ewm(
        span=20,
        adjust=False,
        min_periods=20,
    ).mean()

    result["ema50"] = result["close"].ewm(
        span=50,
        adjust=False,
        min_periods=50,
    ).mean()

    result["ema200"] = result["close"].ewm(
        span=200,
        adjust=False,
        min_periods=200,
    ).mean()

    delta = result["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    average_gain = gain.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14,
    ).mean()

    average_loss = loss.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14,
    ).mean()

    relative_strength = (
        average_gain
        / average_loss.replace(0, float("nan"))
    )

    result["rsi14"] = 100 - (
        100 / (1 + relative_strength)
    )

    previous_close = result["close"].shift(1)

    true_range = pd.concat(
        [
            result["high"] - result["low"],
            (result["high"] - previous_close).abs(),
            (result["low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    result["atr14"] = true_range.ewm(
        alpha=1 / 14,
        adjust=False,
        min_periods=14,
    ).mean()

    return result


def get_candle_settings(
    range_label: str,
) -> dict:
    settings = {
        "Past 24 Hours": {
            "left_label": "15m Trend",
            "left_period": "1d",
            "left_interval": "15m",
            "right_label": "5m Tactical",
            "right_period": "1d",
            "right_interval": "5m",
        },
        "Past 3 Days": {
            "left_label": "1H Trend",
            "left_period": "3d",
            "left_interval": "1h",
            "right_label": "15m Tactical",
            "right_period": "3d",
            "right_interval": "15m",
        },
        "Past 7 Days": {
            "left_label": "4H Trend",
            "left_period": "7d",
            "left_interval": "4h",
            "right_label": "1H Tactical",
            "right_period": "7d",
            "right_interval": "1h",
        },
        "Past 30 Days": {
            "left_label": "1D Trend",
            "left_period": "1mo",
            "left_interval": "1d",
            "right_label": "4H Tactical",
            "right_period": "30d",
            "right_interval": "4h",
        },
        "Past Year": {
            "left_label": "1W Trend",
            "left_period": "1y",
            "left_interval": "1wk",
            "right_label": "1D Tactical",
            "right_period": "1y",
            "right_interval": "1d",
        },
    }

    return settings.get(
        range_label,
        settings["Past 7 Days"],
    )
