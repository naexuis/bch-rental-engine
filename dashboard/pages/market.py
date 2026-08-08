from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.market_utils import (
    calculate_technical_indicators,
    fetch_yfinance_ohlc,
    get_candle_settings,
    summarize_technical_indicators,
)
from dashboard.ui_utils import (
    fmt_large_number,
)


def render_market_page(
    *,
    df: pd.DataFrame,
    latest: dict,
    has_history: bool,
) -> None:
    st.subheader("Market Overview")

    col1, col2, col3, col4 = st.columns(4)

    if has_history:
        col1.metric("BTC Price", f"${latest.get('btc_usd', 0):,.0f}")
        col2.metric("BCH Price", f"${latest.get('bch_usd', 0):,.2f}")
        col3.metric(
            "Difficulty",
            fmt_large_number(latest.get("bch_difficulty", 0)),
        )
        col4.metric(
            "Network EH/s",
            f"{latest.get('bch_network_hashrate_eh', 0):.4f}",
        )
    else:
        col1.metric("BTC Price", "Waiting")
        col2.metric("BCH Price", "Waiting")
        col3.metric("Difficulty", "Waiting")
        col4.metric("Network EH/s", "Waiting")

    st.divider()
    st.subheader("BCH Price Candlesticks")

    candle_ticker = st.selectbox(
        "Trading Pair",
        ["BCH-USD", "BCH-BTC"],
        index=0,
    )

    candle_range = st.selectbox(
        "Time Range",
        [
            "Past 24 Hours",
            "Past 3 Days",
            "Past 7 Days",
            "Past 30 Days",
            "Past Year",
        ],
        index=2,
    )

    candle_settings = get_candle_settings(candle_range)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"### {candle_settings['left_label']}")
        try:
            df_4h = fetch_yfinance_ohlc(
                candle_ticker,
                candle_settings["left_period"],
                candle_settings["left_interval"],
            )

            df_4h = calculate_technical_indicators(df_4h)
            left_summary = summarize_technical_indicators(df_4h)

            if df_4h.empty:
                st.warning("No left candle data returned.")
            else:
                fig = go.Figure(
                    data=[
                        go.Candlestick(
                            x=df_4h["time"],
                            open=df_4h["open"],
                            high=df_4h["high"],
                            low=df_4h["low"],
                            close=df_4h["close"],
                            increasing_line_color="#2ECC71",
                            decreasing_line_color="#E74C3C",
                            name="4H",
                        )
                    ]
                )
                fig.add_trace(
                    go.Scatter(
                        x=df_4h["time"],
                        y=df_4h["ema20"],
                        mode="lines",
                        name="EMA 20",
                        line=dict(width=1.5),
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=df_4h["time"],
                        y=df_4h["ema50"],
                        mode="lines",
                        name="EMA 50",
                        line=dict(width=1.5),
                    )
                )

                if df_4h["ema200"].notna().any():
                    fig.add_trace(
                        go.Scatter(
                            x=df_4h["time"],
                            y=df_4h["ema200"],
                            mode="lines",
                            name="EMA 200",
                            line=dict(width=1.2, dash="dot"),
                        )
                    )
                fig.update_layout(
                    height=450,
                    xaxis_rangeslider_visible=False,
                    title=f"{candle_ticker} {candle_settings['left_label']} Candlestick",
                )
                st.plotly_chart(fig, use_container_width=True)

                left_metric_1, left_metric_2, left_metric_3, left_metric_4, left_metric_5 = st.columns(5)

                left_metric_1.metric(
                    "Trend",
                    left_summary["trend"],
                )

                left_metric_2.metric(
                    "Momentum",
                    left_summary["momentum"],
                )

                left_metric_3.metric(
                    "RSI 14",
                    (
                        f"{left_summary['rsi14']:.1f}"
                        if left_summary["rsi14"] is not None
                        else "N/A"
                    ),
                )

                left_atr = left_summary["atr14"]

                if left_atr is None:
                    left_atr_display = "N/A"
                elif candle_ticker == "BCH-USD":
                    left_atr_display = f"${left_atr:,.2f}"
                else:
                    left_atr_display = f"{left_atr:.8f} BTC"

                left_metric_4.metric(
                    "ATR 14",
                    left_atr_display,
                )

                left_metric_5.metric(
                    "Technical Score",
                    (
                        f"{left_summary['technical_score']:.0f}/100"
                        if left_summary["technical_score"] is not None
                        else "N/A"
                    ),
                )

        except Exception as e:
            st.warning(f"Unable to load left candles: {e}")

    with c2:
        st.markdown(f"### {candle_settings['right_label']}")
        try:
            df_15m = fetch_yfinance_ohlc(
                candle_ticker,
                candle_settings["right_period"],
                candle_settings["right_interval"],
            )

            df_15m = calculate_technical_indicators(df_15m)
            right_summary = summarize_technical_indicators(df_15m)

            if df_15m.empty:
                st.warning("No right candle data returned.")
            else:
                fig = go.Figure(
                    data=[
                        go.Candlestick(
                            x=df_15m["time"],
                            open=df_15m["open"],
                            high=df_15m["high"],
                            low=df_15m["low"],
                            close=df_15m["close"],
                            increasing_line_color="#2ECC71",
                            decreasing_line_color="#E74C3C",
                            name="15m",
                        )
                    ]
                )
                fig.add_trace(
                    go.Scatter(
                        x=df_15m["time"],
                        y=df_15m["ema20"],
                        mode="lines",
                        name="EMA 20",
                        line=dict(width=1.5),
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=df_15m["time"],
                        y=df_15m["ema50"],
                        mode="lines",
                        name="EMA 50",
                        line=dict(width=1.5),
                    )
                )

                if df_15m["ema200"].notna().any():
                    fig.add_trace(
                        go.Scatter(
                            x=df_15m["time"],
                            y=df_15m["ema200"],
                            mode="lines",
                            name="EMA 200",
                            line=dict(width=1.2, dash="dot"),
                        )
                    )
                fig.update_layout(
                    height=450,
                    xaxis_rangeslider_visible=False,
                    title=f"{candle_ticker} {candle_settings['right_label']} Candlestick",
                )
                st.plotly_chart(fig, use_container_width=True)

                right_metric_1, right_metric_2, right_metric_3, right_metric_4, right_metric_5 = st.columns(5)

                right_metric_1.metric(
                    "Trend",
                    right_summary["trend"],
                )

                right_metric_2.metric(
                    "Momentum",
                    right_summary["momentum"],
                )

                right_metric_3.metric(
                    "RSI 14",
                    (
                        f"{right_summary['rsi14']:.1f}"
                        if right_summary["rsi14"] is not None
                        else "N/A"
                    ),
                )

                right_atr = right_summary["atr14"]

                if right_atr is None:
                    right_atr_display = "N/A"
                elif candle_ticker == "BCH-USD":
                    right_atr_display = f"${right_atr:,.2f}"
                else:
                    right_atr_display = f"{right_atr:.8f} BTC"

                right_metric_4.metric(
                    "ATR 14",
                    right_atr_display,
                )

                right_metric_5.metric(
                    "Technical Score",
                    (
                        f"{right_summary['technical_score']:.0f}/100"
                        if right_summary["technical_score"] is not None
                        else "N/A"
                    ),
                )

        except Exception as e:
            st.warning(f"Unable to load right candles: {e}")

    if has_history:
        st.subheader("Fair Value Ratio Over Time")
        fig = px.line(df, x="timestamp", y="best_fair_value_ratio")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("BCH Price Over Time")
        fig = px.line(df, x="timestamp", y="bch_usd")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("BTC Price Over Time")
        fig = px.line(df, x="timestamp", y="btc_usd")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Difficulty Over Time")
        fig = px.line(df, x="timestamp", y="bch_difficulty")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(
            "Historical engine charts will appear after the first successful engine run."
        )
