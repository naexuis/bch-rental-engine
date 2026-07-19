from pathlib import Path
import sqlite3
import json
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import plotly.graph_objects as go


st.set_page_config(
    page_title="BCH Rental Engine Dashboard",
    layout="wide",
)

BASE_DIR = Path(os.getenv("BCH_BASE_DIR", Path.home() / "bch_rental_engine"))
STATE_DIR = Path(os.getenv("BCH_STATE_DIR", BASE_DIR / "state"))
CONFIG_DIR = Path(os.getenv("BCH_CONFIG_DIR", BASE_DIR / "config"))

DB_PATH = STATE_DIR / "bch_rental_history.sqlite"
STATE_PATH = STATE_DIR / "bch_solo_rental_strike_engine.json"
CONFIG_OVERRIDE_PATH = CONFIG_DIR / "dashboard_config_override.json"

def safe_num(value, default=0.0):
    if pd.isna(value):
        return default
    return value

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

    # Trend scoring
    if pd.notna(ema20) and close is not None:
        score += 10 if close > ema20 else -10

    if pd.notna(ema20) and pd.notna(ema50):
        score += 15 if ema20 > ema50 else -15

    if pd.notna(ema50) and pd.notna(ema200):
        score += 10 if ema50 > ema200 else -10

    # Momentum scoring
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

def fmt_large_number(value):
    value = safe_num(value)

    if abs(value) >= 1_000_000_000_000:
        return f"{value/1_000_000_000_000:.2f} T"

    if abs(value) >= 1_000_000_000:
        return f"{value/1_000_000_000:.2f} B"

    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:.2f} M"

    if abs(value) >= 1_000:
        return f"{value/1_000:.2f} K"

    return f"{value:,.0f}"

def fmt_hashrate_from_ph(value_ph):
    value_ph = safe_num(value_ph)

    if value_ph >= 1:
        return f"{value_ph:,.2f} PH/s"

    value_th = value_ph * 1_000
    if value_th >= 1:
        return f"{value_th:,.2f} TH/s"

    value_gh = value_th * 1_000
    if value_gh >= 1:
        return f"{value_gh:,.2f} GH/s"

    value_mh = value_gh * 1_000
    return f"{value_mh:,.2f} MH/s"

def render_decision_status(action: str):
    action = str(action or "WAIT").upper()

    if action in ["RENT", "STRONG_RENT"]:
        st.success("🟢 RENT")
    elif action in ["WATCH", "WEAK_WATCH", "MONITOR"]:
        st.warning("🟡 WATCH")
    else:
        st.error("🔴 WAIT")

def progress_pct(value: float, max_value: float = 100.0) -> int:
    value = safe_num(value)
    max_value = safe_num(max_value, 100.0)

    if max_value <= 0:
        return 0

    pct = int(round((value / max_value) * 100))
    return max(0, min(100, pct))

def pool_rank_label(index: int) -> str:
    labels = ["🥇 Recommended", "🥈 Strong Alternative", "🥉 Backup Option"]
    if index < len(labels):
        return labels[index]
    return "Additional Pool"


def render_pool_card(pool: dict, index: int):
    score = safe_num(pool.get("routing_score", 0))
    dominance = safe_num(pool.get("pool_dominance_pct", 0))
    existing_pool = pool.get("existing_pool_hashrate_ph", 0)
    fee_pct = safe_num(pool.get("fee_pct", 0))

    st.markdown(f"### {pool.get('pool_name', 'Unknown Pool')}")
    st.caption(pool_rank_label(index))

    st.metric("Routing Score", f"{score:.1f}/100")
    st.metric("Dominance", f"{dominance:.2f}%")
    st.metric("Existing Pool", fmt_hashrate_from_ph(existing_pool))
    st.metric("Fee", f"{fee_pct:.2f}%")

def load_config_override() -> dict:
    if not CONFIG_OVERRIDE_PATH.exists():
        return {}

    try:
        import json
        with CONFIG_OVERRIDE_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config_override(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    tmp = CONFIG_OVERRIDE_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        import json
        json.dump(config, f, indent=2, sort_keys=True)

    tmp.replace(CONFIG_OVERRIDE_PATH)

@st.cache_data(ttl=60)
def load_history() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            """
            SELECT *
            FROM run_history
            ORDER BY timestamp ASC
            """,
            conn,
        )

    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

@st.cache_data(ttl=60)
def load_latest_state() -> dict:
    state_path = STATE_PATH

    if not state_path.exists():
        return {}

    try:
        with state_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

df = load_history()
state = load_latest_state()

st.title("BCH Solo Rental Strike Engine")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Market",
        "Market Trends",
        "Strike Analysis",
        "Pool Routing",
        "History",
        "Settings",
    ],
    key="main_navigation",
)

@st.cache_data(ttl=300)
def fetch_yfinance_ohlc(ticker: str, period: str, interval: str) -> pd.DataFrame:
    df = yf.Ticker(ticker).history(period=period, interval=interval)

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

    return df[["time", "open", "high", "low", "close", "volume"]].dropna()

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add EMA, RSI, ATR, trend, and technical-score fields to OHLC data.

    Expected input columns:
        time, open, high, low, close, volume
    """
    if df.empty:
        return df.copy()

    result = df.copy().sort_values("time").reset_index(drop=True)

    numeric_columns = ["open", "high", "low", "close", "volume"]
    for column in numeric_columns:
        result[column] = pd.to_numeric(result[column], errors="coerce")

    result = result.dropna(subset=["high", "low", "close"])

    # Exponential moving averages
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

    # RSI 14 using Wilder-style exponential smoothing
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

    relative_strength = average_gain / average_loss.replace(0, float("nan"))
    result["rsi14"] = 100 - (100 / (1 + relative_strength))

    # ATR 14
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

def get_candle_settings(range_label: str) -> dict:
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

    return settings.get(range_label, settings["Past 7 Days"])



st.sidebar.divider()

auto_refresh = st.sidebar.checkbox("Auto refresh", value=True)

refresh_seconds = st.sidebar.number_input(
    "Refresh every seconds",
    min_value=10,
    max_value=3600,
    value=60,
    step=10,
)

if auto_refresh:
    st_autorefresh(
        interval=refresh_seconds * 1000,
        key="dashboard_autorefresh",
    )

if st.sidebar.button("Refresh now"):
    st.cache_data.clear()
    st.rerun()

if df.empty:
    st.warning("No history data found yet.")
    st.stop()

latest = df.iloc[-1]

best_strike = state.get("winners", {}).get("best_strike", {})
recommended_pool = state.get("recommended_pool", {})
interpretation = state.get("interpretation", "")
engine_answer = state.get("answer", "")

last_updated = latest["timestamp"]
history_rows = len(df)

status_col1, status_col2 = st.columns(2)
status_col1.caption(f"Last Updated: {last_updated}")
status_col2.caption(f"History Rows: {history_rows}")

fvr = safe_num(latest.get("best_fair_value_ratio", 0))
risk_roi = safe_num(latest.get("best_risk_adjusted_roi_pct", 0))
prob_1plus = safe_num(latest.get("best_prob_1plus", 0))
opportunity_score = safe_num(latest.get("opportunity_score", 0))

market_regime = latest.get("market_regime", "N/A")
recommendation = latest.get("best_recommendation", "N/A")
action = str(latest.get("opportunity_action", "WAIT")).upper()

if page == "Dashboard":

    winners = state.get("winners", {})
    best = winners.get("best_strike", {}) or {}
    opportunity = state.get("opportunity", {}) or {}

    recommendation = str(best.get("recommendation", state.get("recommendation", "N/A"))).upper()
    market_regime = str(state.get("market_regime", "N/A")).upper()
    action = str(opportunity.get("action", "N/A")).upper()

    opportunity_score = safe_num(opportunity.get("score", 0))
    prob_1plus = safe_num(best.get("prob_1plus", 0)) * 100
    risk_roi = safe_num(best.get("risk_adjusted_roi_pct", 0))
    fvr = safe_num(best.get("fair_value_ratio", 0))
    premium = safe_num(best.get("premium_discount_pct", 0))
    strike_score = safe_num(best.get("strike_score", 0))

    # Human-readable recommendation title
    recommendation_title = {
        "STRONG_RENT": "Excellent Rental Opportunity",
        "RENT": "Rental Opportunity",
        "WATCH": "Near Strike Opportunity",
        "MONITOR": "Continue Monitoring",
    }.get(recommendation, "Do Not Rent")

    # Operator-facing action derived from the engine recommendation
    operator_action = {
        "STRONG_RENT": "RENT NOW",
        "RENT": "RENT",
        "WATCH": "WATCH",
        "MONITOR": "MONITOR",
        "NEAR STRIKE": "WATCH",
        "DO_NOT_RENT": "DO NOT RENT",
    }.get(recommendation, "DO NOT RENT")

    # Human-readable market condition
    recommendation_title = {
        "STRONG_RENT": "Excellent Rental Opportunity",
        "RENT": "Rental Opportunity",
        "WATCH": "Near Strike Opportunity",
        "MONITOR": "Continue Monitoring",
        "NEAR STRIKE": "Near Strike Opportunity",
        "DO_NOT_RENT": "Unfavorable Rental Conditions",
    }.get(recommendation, "Unfavorable Rental Conditions")

    # Human-readable operator guidance
    recommendation_message = {
        "STRONG_RENT": (
            "Multiple indicators align. Conditions favor executing a rental."
        ),
        "RENT": (
            "Current conditions support renting hashpower."
        ),
        "WATCH": (
            "Market conditions are approaching the strike threshold. "
            "Continue monitoring."
        ),
        "MONITOR": (
            "Conditions are improving but do not justify a rental yet."
        ),
        "NEAR STRIKE": (
            "Conditions are close to the strike threshold. "
            "Continue monitoring before renting."
        ),
        "DO_NOT_RENT": (
            "Current market conditions do not support renting hashpower."
        ),
    }.get(
        recommendation,
        "Current market conditions do not support renting hashpower.",
    )

    st.subheader("Decision Center")

    banner_text = f"""
    ### {operator_action}

    **Market State:** {recommendation_title}

    {recommendation_message}
    """

    if operator_action in ["RENT", "RENT NOW"]:
        st.success(banner_text)
    elif operator_action in ["WATCH", "MONITOR"]:
        st.warning(banner_text)
    else:
        st.error(banner_text)

    d1, d2, d3 = st.columns(3)

    d1.metric("Strike Score", f"{strike_score:.1f}/100")
    d2.metric("Opportunity Score", f"{opportunity_score:.1f}/100")
    d3.metric("Market Regime", market_regime)

    st.divider()
    st.subheader("Decision Drivers")

    d5, d6, d7, d8 = st.columns(4)

    d5.metric("P(1+ Block)", f"{prob_1plus:.2f}%")
    d6.metric("Risk ROI", f"{risk_roi:.2f}%")
    d7.metric("FVR", f"{fvr:.3f}")
    d8.metric("Rental Premium", f"{premium:+.2f}%")

    reasons = []

    if fvr >= 0.90:
        reasons.append("✅ FVR is above the 0.90 watch threshold.")
    else:
        reasons.append("❌ FVR is below the 0.90 watch threshold.")

    if prob_1plus >= 70:
        reasons.append("✅ P(1+ Block) is above the 70% target.")
    else:
        reasons.append(f"❌ P(1+ Block) is below target at {prob_1plus:.2f}%.")

    if risk_roi >= 0:
        reasons.append("✅ Risk-adjusted ROI is positive.")
    else:
        reasons.append(f"❌ Risk-adjusted ROI is still negative at {risk_roi:.2f}%.")

    if premium <= 0:
        reasons.append("✅ Rental pricing is at or below break-even fair value.")
    else:
        reasons.append(f"❌ Rental pricing is still {premium:.2f}% above break-even.")

    for reason in reasons:
        st.write(reason)

    st.divider()

    st.subheader("Budget Frontier")

    frontier = state.get("budget_frontier", [])

    if frontier:
        rows = []

        for item in frontier:
            best = item.get("best_score", {}) or item.get("best_probability", {})

            rows.append(
                {
                    "budget_usd": safe_num(item.get("budget_usd", best.get("cost_usd", 0))),
                    "cost_usd": safe_num(best.get("cost_usd", 0)),
                    "hashrate": fmt_hashrate_from_ph(best.get("hashrate_ph", 0)),
                    "duration_hours": safe_num(best.get("duration_hours", 0)),
                    "prob_1plus_pct": safe_num(best.get("prob_1plus", 0)) * 100,
                    "prob_2plus_pct": safe_num(best.get("prob_2plus", 0)) * 100,
                    "fvr": safe_num(best.get("fair_value_ratio", 0)),
                    "risk_roi_pct": safe_num(best.get("risk_adjusted_roi_pct", 0)),
                    "recommendation": best.get("recommendation", "N/A"),
                    "source": str(best.get("source", "N/A")).upper(),
                }
            )

        frontier_df = pd.DataFrame(rows)

        display_frontier_df = frontier_df.copy()
        display_frontier_df["budget_usd"] = display_frontier_df["budget_usd"].map(lambda x: f"${x:,.0f}")
        display_frontier_df["cost_usd"] = display_frontier_df["cost_usd"].map(lambda x: f"${x:,.0f}")
        display_frontier_df["duration_hours"] = display_frontier_df["duration_hours"].map(lambda x: f"{x:.2f}h")
        display_frontier_df["prob_1plus_pct"] = display_frontier_df["prob_1plus_pct"].map(lambda x: f"{x:.2f}%")
        display_frontier_df["prob_2plus_pct"] = display_frontier_df["prob_2plus_pct"].map(lambda x: f"{x:.2f}%")
        display_frontier_df["fvr"] = display_frontier_df["fvr"].map(lambda x: f"{x:.3f}")
        display_frontier_df["risk_roi_pct"] = display_frontier_df["risk_roi_pct"].map(lambda x: f"{x:.2f}%")

        display_frontier_df = display_frontier_df[
            [
                "budget_usd",
                "hashrate",
                "duration_hours",
                "prob_1plus_pct",
                "prob_2plus_pct",
                "fvr",
                "risk_roi_pct",
                "recommendation",
                "source",
            ]
        ]

        st.dataframe(display_frontier_df, use_container_width=True)

        chart_df = frontier_df.copy()
        chart_df["budget_usd"] = chart_df["budget_usd"].round(0)
        chart_df["prob_1plus_pct"] = chart_df["prob_1plus_pct"].round(2)

        fig = px.line(
            chart_df,
            x="budget_usd",
            y="prob_1plus_pct",
            markers=True,
            labels={
                "budget_usd": "Budget USD",
                "prob_1plus_pct": "P(1+ Block) %",
            },
        )

        fig.update_traces(
            hovertemplate="Budget: $%{x:,.0f}<br>P(1+): %{y:.2f}%<extra></extra>"
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No budget frontier data available yet.")

    st.divider()

    st.subheader("Recommended Pool")

    pool_col1, pool_col2, pool_col3, pool_col4 = st.columns(4)

    pool_col1.metric(
        "Pool",
        recommended_pool.get("pool_name", "N/A"),
    )

    pool_col2.metric(
        "Routing Score",
        f"{safe_num(recommended_pool.get('routing_score', 0)):.1f}/100",
    )

    pool_col3.metric(
        "Dominance",
        f"{safe_num(recommended_pool.get('pool_dominance_pct', 0)):.2f}%",
    )

    pool_col4.metric(
        "Existing Pool",
        fmt_hashrate_from_ph(recommended_pool.get("existing_pool_hashrate_ph", 0)),
    )

    st.divider()

    st.subheader("Main Blockers")

    blockers = []

    if fvr < 0.90:
        blockers.append("Hashpower is still priced above fair value.")

    if risk_roi < 0:
        blockers.append("Risk-adjusted ROI is still negative.")

    if prob_1plus < 70:
        blockers.append("Probability is below the preferred threshold.")

    if not blockers:
        st.success("No major blockers detected.")
    else:
        for blocker in blockers:
            st.error(blocker)

    st.subheader("Conditions Needed to Rent")

    cond1, cond2, cond3 = st.columns(3)

    cond1.metric("FVR Target", ">= 0.90", f"Current: {fvr:.3f}")
    cond2.metric("Risk ROI Target", ">= 0%", f"Current: {risk_roi:.2f}%")
    cond3.metric("Probability Target", ">= 70%", f"Current: {prob_1plus:.2f}%")

elif page == "Market":
    st.subheader("Market Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("BTC Price", f"${latest.get('btc_usd', 0):,.0f}")
    col2.metric("BCH Price", f"${latest.get('bch_usd', 0):,.2f}")
    col3.metric("Difficulty", fmt_large_number(latest.get("bch_difficulty", 0)))
    col4.metric("Network EH/s", f"{latest.get('bch_network_hashrate_eh', 0):.4f}")

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

elif page == "Market Trends":
    st.subheader("Market Trends")

    if df.empty:
        st.warning("No history data available yet.")
        st.stop()

    trend_df = df.copy()
    trend_df["timestamp"] = pd.to_datetime(trend_df["timestamp"], errors="coerce")
    trend_df = trend_df.dropna(subset=["timestamp"]).sort_values("timestamp")

    st.caption(f"Showing {len(trend_df)} historical engine runs.")

    latest = trend_df.iloc[-1]

    current_fvr = safe_num(latest.get("best_fair_value_ratio", 0))
    current_risk_roi = safe_num(latest.get("best_risk_adjusted_roi_pct", 0))
    current_prob = safe_num(latest.get("best_prob_1plus", 0)) * 100
    current_bch = safe_num(latest.get("bch_usd", 0))

    TARGET_FVR = 0.90
    TARGET_RISK_ROI = 0.0
    TARGET_PROB = 70.0

    fvr_gap = TARGET_FVR - current_fvr
    risk_gap = TARGET_RISK_ROI - current_risk_roi
    prob_gap = TARGET_PROB - current_prob

    fvr_delta = "✓ Fair value met" if current_fvr >= TARGET_FVR else f"+{fvr_gap:.3f} needed"

    risk_delta = "✓ Profitable" if current_risk_roi >= 0 else f"+{risk_gap:.1f}% needed"

    prob_delta = "✓ Target met" if current_prob >= TARGET_PROB else f"+{prob_gap:.1f}% needed"

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("FVR", f"{current_fvr:.3f}", delta=fvr_delta, delta_color="inverse")
    c2.metric("Risk ROI", f"{current_risk_roi:.1f}%", delta=risk_delta, delta_color="inverse")
    c3.metric("P(1+ Block)", f"{current_prob:.1f}%", delta=prob_delta, delta_color="inverse")
    c4.metric("BCH Price", f"${current_bch:,.2f}", )

    st.divider()

    # -------------------------------------------------
    # FVR Trend
    # -------------------------------------------------
    if "best_fair_value_ratio" in trend_df.columns:
        fig = px.line(
            trend_df,
            x="timestamp",
            y="best_fair_value_ratio",
            markers=True,
            title="Fair Value Ratio Over Time",
            labels={
                "timestamp": "Time",
                "best_fair_value_ratio": "FVR",
            },
        )
        fig.add_hline(y=0.90, line_dash="dash", annotation_text="Rent target: 0.90")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # Probability Trend
    # -------------------------------------------------
    if "best_prob_1plus" in trend_df.columns:
        prob_df = trend_df.copy()
        prob_df["best_prob_1plus_pct"] = prob_df["best_prob_1plus"] * 100

        fig = px.line(
            prob_df,
            x="timestamp",
            y="best_prob_1plus_pct",
            markers=True,
            title="P(1+ Block) Over Time",
            labels={
                "timestamp": "Time",
                "best_prob_1plus_pct": "P(1+ Block) %",
            },
        )
        fig.add_hline(y=70, line_dash="dash", annotation_text="Target: 70%")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # Risk ROI Trend
    # -------------------------------------------------
    if "best_risk_adjusted_roi_pct" in trend_df.columns:
        fig = px.line(
            trend_df,
            x="timestamp",
            y="best_risk_adjusted_roi_pct",
            markers=True,
            title="Risk-Adjusted ROI Over Time",
            labels={
                "timestamp": "Time",
                "best_risk_adjusted_roi_pct": "Risk ROI %",
            },
        )
        fig.add_hline(y=0, line_dash="dash", annotation_text="Break-even")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------
    # BCH Price
    # -------------------------------------------------
    if "bch_usd" in trend_df.columns:

        fig = px.line(
            trend_df,
            x="timestamp",
            y="bch_usd",
            markers=True,
            title="BCH Price",
            labels={
                "timestamp": "Time",
                "bch_usd": "USD"
            }
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


elif page == "Strike Analysis":
    st.subheader("Strike Analysis")

    winners = state.get("winners", {})
    best = winners.get("best_strike", {}) or {}

    if not best:
        st.warning("No strike analysis data available yet.")
        st.stop()

    strike_recommendation = str(best.get("recommendation", "N/A")).upper()
    strike_grade = str(best.get("strike_grade", "N/A")).upper()
    strike_score = safe_num(best.get("strike_score", 0))
    strike_fvr = safe_num(best.get("fair_value_ratio", 0))
    strike_risk_roi = safe_num(best.get("risk_adjusted_roi_pct", 0))
    strike_expected_profit = safe_num(best.get("expected_profit_usd", 0))
    strike_prob = safe_num(best.get("prob_1plus", 0)) * 100

    if strike_recommendation in ["RENT", "STRONG_RENT"]:
        st.success(f"🟢 Recommendation: {strike_recommendation}")
    elif strike_recommendation in ["WATCH", "MONITOR"]:
        st.warning(f"🟡 Recommendation: {strike_recommendation}")
    else:
        st.error(f"🔴 Recommendation: {strike_recommendation}")

    st.write(
        f"Current setup is **{strike_grade} grade** with a **{strike_score:.1f}/100** strike score. "
        f"FVR is **{strike_fvr:.3f}**, risk-adjusted ROI is **{strike_risk_roi:.2f}%**, "
        f"and expected profit is **${strike_expected_profit:,.2f}**."
    )

    st.divider()


    st.markdown("### Selected Strike")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Budget", f"${safe_num(best.get('budget_usd', 0)):,.0f}")
    c2.metric("Hashrate", fmt_hashrate_from_ph(best.get("hashrate_ph", 0)))
    c3.metric("Duration", f"{safe_num(best.get('duration_hours', 0)):.2f}h")
    c4.metric("Strike Grade", strike_grade)

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("P(1+ Block)", f"{safe_num(best.get('prob_1plus', 0)) * 100:.2f}%")
    c6.metric("P(2+ Blocks)", f"{safe_num(best.get('prob_2plus', 0)) * 100:.2f}%")
    c7.metric("FVR", f"{safe_num(best.get('fair_value_ratio', 0)):.3f}")
    c8.metric("Risk ROI", f"{safe_num(best.get('risk_adjusted_roi_pct', 0)):.2f}%")

    st.caption(f"Strike Score: {strike_score:.1f}/100")
    st.progress(progress_pct(strike_score, 100))

    pb1, pb2 = st.columns(2)

    with pb1:
        st.caption(f"P(1+ Block): {strike_prob:.2f}% / 70% target")
        st.progress(progress_pct(strike_prob, 70))

    with pb2:
        st.caption(f"FVR: {strike_fvr:.3f} / 0.900 target")
        st.progress(progress_pct(strike_fvr, 0.90))

    st.divider()

    st.subheader("Expected Outcomes")

    o1, o2, o3, o4 = st.columns(4)

    o1.metric("Expected Revenue", f"${safe_num(best.get('expected_revenue_usd', 0)):,.2f}")
    o2.metric("Expected Profit", f"${safe_num(best.get('expected_profit_usd', 0)):,.2f}")
    o3.metric("Risk-Adjusted Profit", f"${safe_num(best.get('risk_adjusted_profit_usd', 0)):,.2f}")
    o4.metric("Expected BCH Net", f"{safe_num(best.get('expected_bch_net', 0)):.4f} BCH")

    st.divider()

    st.subheader("Block Outcome Scenarios")

    p0 = safe_num(best.get("prob_0_blocks", 0))
    p1plus = safe_num(best.get("prob_1plus", 0))
    p2plus = safe_num(best.get("prob_2plus", 0))

    p1_exact = max(0, p1plus - p2plus)

    outcome_rows = [
        {
            "Outcome": "0 Blocks",
            "Probability": f"{p0 * 100:.2f}%",
            "Profit": f"${safe_num(best.get('profit_if_0_blocks', 0)):,.2f}",
        },
        {
            "Outcome": "1 Block",
            "Probability": f"{p1_exact * 100:.2f}%",
            "Profit": f"${safe_num(best.get('profit_if_1_block', 0)):,.2f}",
        },
        {
            "Outcome": "2+ Blocks",
            "Probability": f"{p2plus * 100:.2f}%",
            "Profit": f"${safe_num(best.get('profit_if_2_blocks', 0)):,.2f}",
        },
    ]

    st.dataframe(pd.DataFrame(outcome_rows), use_container_width=True)

    st.divider()

    st.subheader("Why this strike?")

    st.write(
        f"The engine selected this strike because it provides the strongest overall tradeoff "
        f"within the current budget and hashrate constraints. It uses **{fmt_hashrate_from_ph(best.get('hashrate_ph', 0))}** "
        f"for **{safe_num(best.get('duration_hours', 0)):.2f} hours**, producing a "
        f"**{safe_num(best.get('prob_1plus', 0)) * 100:.2f}%** chance of finding at least one block. "
        f"However, the economics are still unfavorable: FVR is **{safe_num(best.get('fair_value_ratio', 0)):.3f}** "
        f"and risk-adjusted ROI is **{safe_num(best.get('risk_adjusted_roi_pct', 0)):.2f}%**, "
        f"so the recommendation remains **{best.get('recommendation', 'N/A')}**."
    )

    st.divider()

    st.subheader("Alternative Winners")

    cards = [
        ("Highest Probability", "best_probability"),
        ("Best Fair Value", "best_fair_value"),
        ("Best Risk ROI", "best_risk_adjusted_roi"),
        ("Lowest Cost", "lowest_cost_per_probability"),
    ]

    cols = st.columns(2)

    for i, (title, key) in enumerate(cards):

        strike = winners.get(key)

        if not strike:
            continue

        with cols[i % 2]:

            st.markdown(f"#### {title}")

            st.metric(
                "Budget",
                f"${safe_num(strike.get('budget_usd',0)):,.0f}"
            )

            st.metric(
                "Probability",
                f"{safe_num(strike.get('prob_1plus',0)*100):.1f}%"
            )

            st.metric(
                "Duration",
                f"{safe_num(strike.get('duration_hours',0)):.2f} h"
            )

            st.metric(
                "Expected Profit",
                f"${safe_num(strike.get('expected_profit_usd',0)):,.2f}"
            )

            st.caption(
                f"FVR {safe_num(strike.get('fair_value_ratio',0)):.3f} • "
                f"Risk ROI {safe_num(strike.get('risk_adjusted_roi_pct',0)):.1f}%"
            )

    st.divider()

    st.subheader("Optimization Surface")

    surface = state.get("optimization_surface", [])

    if surface:
        surface_df = pd.DataFrame(surface)

        heatmap_metric = st.selectbox(
            "Heatmap Metric",
            [
                "strike_score",
                "prob_1plus",
                "risk_adjusted_roi_pct",
                "fair_value_ratio",
            ],
            format_func=lambda x: {
                "strike_score": "Strike Score",
                "prob_1plus": "P(1+ Block)",
                "risk_adjusted_roi_pct": "Risk ROI %",
                "fair_value_ratio": "FVR",
            }.get(x, x),
        )

        plot_df = surface_df.copy()

        if heatmap_metric == "prob_1plus":
            plot_df[heatmap_metric] = plot_df[heatmap_metric] * 100

        heat_df = plot_df.pivot_table(
            index="hashrate_ph",
            columns="budget_usd",
            values=heatmap_metric,
            aggfunc="max",
        )

        hover_df = plot_df.copy()

        hover_df["prob_1plus_pct"] = hover_df["prob_1plus"] * 100
        hover_df["prob_2plus_pct"] = hover_df["prob_2plus"] * 100

        fig = px.imshow(
            heat_df,
            aspect="auto",
            title="Budget × Hashrate Optimization Surface",
            labels={
                "x": "Budget USD",
                "y": "Hashrate PH/s",
                "color": heatmap_metric,
            },
        )

        fig.update_traces(
            hovertemplate=(
                "Budget: $%{x}<br>"
                "Hashrate: %{y} PH/s<br>"
                f"{heatmap_metric}: %{{z:.2f}}<br>"
                "<extra></extra>"
            )
        )

        selected = state.get("winners", {}).get("best_strike", {})

        selected_budget = selected.get("budget_usd")
        selected_hashrate = selected.get("hashrate_ph")

        if selected_budget is not None and selected_hashrate is not None:
            fig.add_scatter(
                x=[selected_budget],
                y=[selected_hashrate],
                mode="markers+text",
                marker=dict(
                    size=18,
                    symbol="star",
                    color="red",
                    line=dict(width=2, color="white"),
                ),
                text=["Selected"],
                textposition="top center",
                name="Selected Strike",
            )

        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "This heatmap shows how the engine scored each budget and hashrate combination."
        )
    else:
        st.info("No optimization surface data available yet.")


elif page == "Pool Routing":
    st.subheader("Pool Routing")
    render_decision_status(action)

    state_path = STATE_PATH

    if not state_path.exists():
        st.warning("Latest engine state file not found yet.")
        st.stop()

    with state_path.open("r", encoding="utf-8") as f:
        state = json.load(f)

    recommended_pool = state.get("recommended_pool")
    rankings = state.get("pool_routing", {}).get("rankings", [])

    if not recommended_pool:
        st.warning("No pool routing data available yet.")
        st.stop()

    pool_name = recommended_pool.get("pool_name", "N/A") if recommended_pool else "N/A"
    pool_score = safe_num(recommended_pool.get("routing_score", 0)) if recommended_pool else 0

    if pool_score >= 85:
        st.success(f"🟢 Recommended Route: {pool_name}")
    elif pool_score >= 70:
        st.warning(f"🟡 Acceptable Route: {pool_name}")
    else:
        st.error(f"🔴 Weak Route: {pool_name}")

    st.write(
        f"Route rented hashrate to **{pool_name}**. "
        f"It has the highest current routing score at **{pool_score:.1f}/100**."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Recommended Pool", recommended_pool.get("pool_name", "N/A"))
    col2.metric("Routing Score", f"{recommended_pool.get('routing_score', 0):.1f}/100")
    col3.metric("Dominance", f"{recommended_pool.get('pool_dominance_pct', 0):.2f}%")
    col4.metric(
    "Existing Pool",
    fmt_hashrate_from_ph(recommended_pool.get("existing_pool_hashrate_ph", 0)),
    )

    st.subheader("Why this pool?")

    dominance = safe_num(recommended_pool.get("pool_dominance_pct", 0))
    existing_pool = recommended_pool.get("existing_pool_hashrate_ph", 0)
    fee_pct = safe_num(recommended_pool.get("fee_pct", 0))
    network_share = safe_num(
        recommended_pool.get("post_rental_network_share_pct", 0)
    )

    st.write(
        f"**{recommended_pool.get('pool_name', 'This pool')}** is currently the best routing choice. "
        f"After adding your rental, you would control approximately **{dominance:.2f}%** of that pool's hashrate. "
        f"The pool currently has **{fmt_hashrate_from_ph(existing_pool)}** of existing hashrate, "
        f"charges a **{fee_pct:.2f}%** fee, "
        f"and your rental would represent approximately **{network_share:.2f}%** of the entire BCH network."
    )

    st.divider()

    st.subheader("Pool Rankings")

    if rankings:
        top_pools = rankings[:4]
        card_cols = st.columns(len(top_pools))

        for idx, pool in enumerate(top_pools):
            with card_cols[idx]:
                render_pool_card(pool, idx)

        st.divider()

        pool_df = pd.DataFrame(rankings)

        display_df = pool_df.copy()

        display_df["existing_pool"] = display_df["existing_pool_hashrate_ph"].apply(fmt_hashrate_from_ph)
        display_df["post_rental_pool"] = display_df["post_rental_pool_hashrate_ph"].apply(fmt_hashrate_from_ph)

        display_df["routing_score"] = display_df["routing_score"].round(1)
        display_df["pool_dominance_pct"] = display_df["pool_dominance_pct"].round(2)
        display_df["post_rental_network_share_pct"] = display_df["post_rental_network_share_pct"].round(2)
        display_df["fee_pct"] = display_df["fee_pct"].round(2)

        display_df = display_df[
            [
                "pool_name",
                "routing_score",
                "pool_dominance_pct",
                "existing_pool",
                "post_rental_pool",
                "post_rental_network_share_pct",
                "fee_pct",
                "status",
            ]
        ]

        st.dataframe(display_df, use_container_width=True)

        chart_df = pool_df.copy()
        chart_df["routing_score"] = chart_df["routing_score"].round(1)

        fig = px.bar(
            chart_df,
            x="pool_name",
            y="routing_score",
            text="routing_score",
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="inside")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No pool rankings available.")

elif page == "History":
    st.subheader("Historical Performance")

    import sqlite3

    history_path = DB_PATH

    if not history_path.exists():
        st.warning("History database not found yet.")
        st.stop()

    with sqlite3.connect(history_path) as conn:
        hist_df = pd.read_sql_query(
            "SELECT * FROM run_history ORDER BY timestamp ASC",
            conn,
        )

    if hist_df.empty:
        st.warning("No history records available yet.")
        st.stop()

    hist_df["timestamp"] = pd.to_datetime(hist_df["timestamp"], errors="coerce")
    hist_df = hist_df.dropna(subset=["timestamp"]).sort_values("timestamp")

    hist_df["best_prob_1plus_pct"] = hist_df["best_prob_1plus"] * 100

    latest_hist = hist_df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Runs", f"{len(hist_df):,}")
    col2.metric("Latest Recommendation", str(latest_hist.get("best_recommendation", "N/A")))
    col3.metric("Latest FVR", f"{safe_num(latest_hist.get('best_fair_value_ratio', 0)):.3f}")
    col4.metric("Latest Risk ROI", f"{safe_num(latest_hist.get('best_risk_adjusted_roi_pct', 0)):.2f}%")

    st.divider()

    st.subheader("Recommendation Timeline")

    timeline_df = hist_df[
        [
            "timestamp",
            "best_recommendation",
            "opportunity_action",
            "opportunity_score",
            "best_prob_1plus_pct",
            "best_risk_adjusted_roi_pct",
            "best_fair_value_ratio",
            "best_hashrate_ph",
            "best_cost_usd",
            "best_duration_hours",
        ]
    ].tail(100).copy()

    timeline_df["timestamp"] = timeline_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    timeline_df["best_prob_1plus_pct"] = timeline_df["best_prob_1plus_pct"].round(2)
    timeline_df["best_risk_adjusted_roi_pct"] = timeline_df["best_risk_adjusted_roi_pct"].round(2)
    timeline_df["best_fair_value_ratio"] = timeline_df["best_fair_value_ratio"].round(3)
    timeline_df["best_hashrate_ph"] = timeline_df["best_hashrate_ph"].round(0)
    timeline_df["best_cost_usd"] = timeline_df["best_cost_usd"].round(2)
    timeline_df["best_duration_hours"] = timeline_df["best_duration_hours"].round(2)

    st.dataframe(timeline_df, use_container_width=True)

    st.divider()

    st.subheader("Key Metric Trends")

    fig = px.line(
        hist_df,
        x="timestamp",
        y="opportunity_score",
        markers=True,
        title="Opportunity Score Over Time",
        labels={"timestamp": "Time", "opportunity_score": "Opportunity Score"},
    )
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        hist_df,
        x="timestamp",
        y="best_prob_1plus_pct",
        markers=True,
        title="P(1+ Block) Over Time",
        labels={"timestamp": "Time", "best_prob_1plus_pct": "P(1+ Block) %"},
    )
    fig.add_hline(y=70, line_dash="dash", annotation_text="Target: 70%")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        hist_df,
        x="timestamp",
        y="best_risk_adjusted_roi_pct",
        markers=True,
        title="Risk-Adjusted ROI Over Time",
        labels={"timestamp": "Time", "best_risk_adjusted_roi_pct": "Risk ROI %"},
    )
    fig.add_hline(y=0, line_dash="dash", annotation_text="Break-even")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        hist_df,
        x="timestamp",
        y="best_fair_value_ratio",
        markers=True,
        title="Fair Value Ratio Over Time",
        labels={"timestamp": "Time", "best_fair_value_ratio": "FVR"},
    )
    fig.add_hline(y=0.90, line_dash="dash", annotation_text="Watch target: 0.90")
    fig.add_hline(y=1.00, line_dash="dash", annotation_text="Fair value: 1.00")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Raw History")

    with st.expander("Show raw history table"):
        st.dataframe(hist_df.tail(500), use_container_width=True)

elif page == "Settings":
    st.subheader("Settings")

    override = load_config_override()

    current_budget_min = int(override.get("budget_min_usd", latest.get("budget_min_usd", 100)))
    current_budget_max = int(override.get("budget_max_usd", latest.get("budget_max_usd", 1000)))
    current_budget_step = int(override.get("budget_step_usd", latest.get("budget_step_usd", 10)))

    current_hashrate_min = int(override.get("hashrate_min_ph", latest.get("hashrate_min_ph", 300)))
    current_hashrate_max = int(override.get("hashrate_max_ph", latest.get("hashrate_max_ph", 300)))
    current_hashrate_step = int(override.get("hashrate_step_ph", latest.get("hashrate_step_ph", 50)))

    st.markdown("### Engine Budget Controls")
    st.write(
        "Use these settings to control the budget range the engine evaluates. "
        "Changes are saved to the dashboard override file and will apply on the next engine run."
    )

    s1, s2, s3 = st.columns(3)
    s1.metric("Current Min", f"${current_budget_min:,.0f}")
    s2.metric("Current Max", f"${current_budget_max:,.0f}")
    s3.metric("Current Step", f"${current_budget_step:,.0f}")

    h1, h2, h3 = st.columns(3)
    h1.metric("Hashrate Min", f"{current_hashrate_min:,.0f} PH/s")
    h2.metric("Hashrate Max", f"{current_hashrate_max:,.0f} PH/s")
    h3.metric("Hashrate Step", f"{current_hashrate_step:,.0f} PH/s")

    st.divider()

    with st.form("settings_form"):
        st.markdown("### Edit Budget Range")

        budget_min = st.number_input(
            "Budget Min USD",
            min_value=1,
            max_value=100000,
            value=current_budget_min,
            step=10,
        )

        budget_max = st.number_input(
            "Budget Max USD",
            min_value=1,
            max_value=100000,
            value=current_budget_max,
            step=10,
        )

        budget_step = st.number_input(
            "Budget Step USD",
            min_value=1,
            max_value=10000,
            value=current_budget_step,
            step=1,
        )

        st.markdown("### Edit Hashrate Range")

        hashrate_min = st.number_input(
            "Hashrate Min PH/s",
            min_value=1,
            max_value=100000,
            value=current_hashrate_min,
            step=10,
        )

        hashrate_max = st.number_input(
            "Hashrate Max PH/s",
            min_value=1,
            max_value=100000,
            value=current_hashrate_max,
            step=10,
        )

        hashrate_step = st.number_input(
            "Hashrate Step PH/s",
            min_value=1,
            max_value=10000,
            value=current_hashrate_step,
            step=10,
        )

        submitted = st.form_submit_button("Save Settings")

    if submitted:
        errors = []

        if budget_min >= budget_max:
            errors.append("Budget Min must be less than Budget Max.")

        if budget_step > (budget_max - budget_min):
            errors.append("Budget Step should be smaller than the total budget range.")

        if hashrate_min > hashrate_max:
            errors.append("Hashrate Min must be less than or equal to Hashrate Max.")

        if hashrate_step > (hashrate_max - hashrate_min) and hashrate_min != hashrate_max:
            errors.append("Hashrate Step should be smaller than the total hashrate range.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            save_config_override(
                {
                    "budget_min_usd": int(budget_min),
                    "budget_max_usd": int(budget_max),
                    "budget_step_usd": int(budget_step),
                    "hashrate_min_ph": int(hashrate_min),
                    "hashrate_max_ph": int(hashrate_max),
                    "hashrate_step_ph": int(hashrate_step),
                }
            )

            st.success(
                "Settings saved. The engine will use these values after the next scheduled engine run."
            )

    st.divider()

    st.markdown("### Current Override File")
    st.caption("This is the exact JSON file currently being used by the engine override system.")
    st.json(load_config_override())