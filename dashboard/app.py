from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh


st.set_page_config(
    page_title="BCH Rental Engine Dashboard",
    layout="wide",
)

STATE_DIR = Path.home() / "bch_rental_engine/state"
DB_PATH = STATE_DIR / "bch_rental_history.sqlite"

def safe_num(value, default=0.0):
    if pd.isna(value):
        return default
    return value


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

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Market",
        "Strike Analysis",
        "History",
        "Settings",
    ],
    key="main_navigation",
)

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
action = latest.get("opportunity_action", "N/A")

if page == "Dashboard":
    st.subheader("Current Decision")

    decision_col1, decision_col2 = st.columns([2, 1])

    with decision_col1:
        st.markdown(f"""
# {recommendation}

**Current Recommendation**

Probability is high, but the engine still does not like the economics.

**Action:** `{action}`
""")

    with decision_col2:
        st.metric("Opportunity", f"{opportunity_score:.0f}/100")
        st.metric("Market Regime", market_regime)
        st.metric("P(1+ Block)", f"{prob_1plus * 100:.2f}%")

    st.subheader("Why?")

    reasons = []

    if prob_1plus >= 0.70:
        reasons.append("✓ Probability is high at the current budget range.")
    elif prob_1plus >= 0.50:
        reasons.append("✓ Probability is meaningful, but not exceptional.")
    else:
        reasons.append("✗ Probability is still relatively low.")

    if fvr >= 1.0:
        reasons.append("✓ Hashpower is priced at or below fair value.")
    elif fvr >= 0.90:
        reasons.append("⚠ Hashpower is getting closer to fair value, but still not clearly attractive.")
    else:
        reasons.append("✗ Hashpower remains overpriced versus expected BCH value.")

    if risk_roi >= 0:
        reasons.append("✓ Risk-adjusted ROI is positive.")
    else:
        reasons.append("✗ Risk-adjusted ROI is still negative.")

    for reason in reasons:
        st.write(reason)

    st.subheader("Current Strike")

    strike_col1, strike_col2, strike_col3, strike_col4 = st.columns(4)

    strike_col1.metric("Source", str(latest.get("best_source", "N/A")).upper())
    strike_col2.metric("Hashrate", f"{latest.get('best_hashrate_ph', 0):,.0f} PH/s")
    strike_col3.metric("Duration", f"{latest.get('best_duration_hours', 0):.2f}h")
    strike_col4.metric("Cost", f"${latest.get('best_cost_usd', 0):,.2f}")

    strike_col5, strike_col6, strike_col7 = st.columns(3)

    strike_col5.metric("FVR", f"{fvr:.3f}")
    strike_col6.metric("Risk ROI", f"{risk_roi:.2f}%")
    strike_col7.metric("Expected Profit", f"${latest.get('best_expected_profit_usd', 0):,.2f}")

    st.subheader("Opportunity Score Over Time")
    fig = px.line(df, x="timestamp", y="opportunity_score")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Fair Value Ratio Over Time")
    fig = px.line(df, x="timestamp", y="best_fair_value_ratio")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("P(1+ Block) Over Time")
    fig = px.line(df, x="timestamp", y="best_prob_1plus")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Market":
    st.subheader("Market Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("BTC Price", f"${latest.get('btc_usd', 0):,.0f}")
    col2.metric("BCH Price", f"${latest.get('bch_usd', 0):,.2f}")
    col3.metric("Difficulty", f"{latest.get('bch_difficulty', 0):,.0f}")
    col4.metric("Network EH/s", f"{latest.get('bch_network_hashrate_eh', 0):.4f}")

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

elif page == "Strike Analysis":
    st.subheader("Strike Analysis")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Best Source", latest.get("best_source", "N/A"))
    col2.metric("Hashrate", f"{latest.get('best_hashrate_ph', 0):,.0f} PH/s")
    col3.metric("Duration", f"{latest.get('best_duration_hours', 0):.2f}h")
    col4.metric("Cost", f"${latest.get('best_cost_usd', 0):,.2f}")

    st.subheader("P(1+ Block) Over Time")
    fig = px.line(df, x="timestamp", y="best_prob_1plus")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Risk-adjusted ROI Over Time")
    fig = px.line(df, x="timestamp", y="best_risk_adjusted_roi_pct")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Best Duration Over Time")
    fig = px.line(df, x="timestamp", y="best_duration_hours")
    st.plotly_chart(fig, use_container_width=True)

elif page == "History":
    st.subheader("Historical Performance")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Runs", len(df))
    col2.metric("Avg FVR", f"{df['best_fair_value_ratio'].mean():.3f}")
    col3.metric("Best FVR", f"{df['best_fair_value_ratio'].max():.3f}")
    col4.metric("Best Opportunity", f"{df['opportunity_score'].dropna().max():.1f}")

    st.subheader("Opportunity Score Over Time")
    opp_df = df.dropna(subset=["opportunity_score"])

    if not opp_df.empty:
        fig = px.line(opp_df, x="timestamp", y="opportunity_score")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No opportunity score history available yet.")

    st.subheader("Recent History")
    st.dataframe(df.tail(100), use_container_width=True)

elif page == "Settings":
    st.subheader("Current Engine Settings")

    col1, col2, col3 = st.columns(3)

    col1.metric("Budget Min", f"${latest.get('budget_min_usd', 0):,.0f}")
    col2.metric("Budget Max", f"${latest.get('budget_max_usd', 0):,.0f}")
    col3.metric("Budget Step", f"${latest.get('budget_step_usd', 0):,.0f}")

    st.subheader("Latest Config Snapshot")

    st.write(
        {
            "Budget Min": latest.get("budget_min_usd"),
            "Budget Max": latest.get("budget_max_usd"),
            "Budget Step": latest.get("budget_step_usd"),
            "Best Source": latest.get("best_source"),
            "Best Hashrate PH": latest.get("best_hashrate_ph"),
            "Best Duration Hours": latest.get("best_duration_hours"),
            "Best Cost USD": latest.get("best_cost_usd"),
        }
    )