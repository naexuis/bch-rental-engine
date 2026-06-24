from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="BCH Rental Engine Dashboard",
    layout="wide",
)

STATE_DIR = Path.home() / "bch_rental_engine/state"
DB_PATH = STATE_DIR / "bch_rental_history.sqlite"


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


df = load_history()

st.title("BCH Solo Rental Strike Engine")

if df.empty:
    st.warning("No history data found yet.")
    st.stop()

latest = df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Recommendation", latest.get("best_recommendation", "N/A"))
col2.metric("Market Regime", latest.get("market_regime", "N/A"))
col3.metric("Opportunity Score", latest.get("opportunity_score", "N/A"))
col4.metric("P(1+ Block)", f"{latest.get('best_prob_1plus', 0) * 100:.2f}%")

st.subheader("Latest Snapshot")

st.write(
    {
        "Timestamp": latest["timestamp"],
        "BCH Price": latest["bch_usd"],
        "BTC Price": latest["btc_usd"],
        "Difficulty": latest["bch_difficulty"],
        "FVR": latest["best_fair_value_ratio"],
        "Risk ROI": latest["best_risk_adjusted_roi_pct"],
        "Budget Min": latest.get("budget_min_usd"),
        "Budget Max": latest.get("budget_max_usd"),
    }
)

st.subheader("Fair Value Ratio Over Time")
fig = px.line(df, x="timestamp", y="best_fair_value_ratio")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Opportunity Score Over Time")
if "opportunity_score" in df.columns:
    fig = px.line(df, x="timestamp", y="opportunity_score")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("BCH Price Over Time")
fig = px.line(df, x="timestamp", y="bch_usd")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Difficulty Over Time")
fig = px.line(df, x="timestamp", y="bch_difficulty")
st.plotly_chart(fig, use_container_width=True)

st.subheader("P(1+ Block) Over Time")
fig = px.line(df, x="timestamp", y="best_prob_1plus")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Recent History")
st.dataframe(df.tail(100), use_container_width=True)
