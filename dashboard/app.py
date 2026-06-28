from pathlib import Path
import sqlite3
import json
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
CONFIG_DIR = Path.home() / "bch_rental_engine/config"
CONFIG_OVERRIDE_PATH = CONFIG_DIR / "dashboard_config_override.json"

def safe_num(value, default=0.0):
    if pd.isna(value):
        return default
    return value

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


df = load_history()

st.title("BCH Solo Rental Strike Engine")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Market",
        "Strike Analysis",
        "Pool Routing",
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
action = str(latest.get("opportunity_action", "WAIT")).upper()

if page == "Dashboard":
    st.subheader("Current Decision")
    render_decision_status(action)

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

    st.subheader("Current Blockers")

    blockers = []

    if fvr < 0.90:
        blockers.append("Rental pricing is still too expensive versus estimated fair value.")

    if risk_roi < 0:
        blockers.append("Risk-adjusted ROI is still negative.")

    if prob_1plus < 0.70:
        blockers.append("Probability is not high enough at the current budget range.")

    if not blockers:
        st.success("No major blockers detected.")
    else:
        for blocker in blockers:
            st.error(blocker)

    st.subheader("Conditions Needed")

    cond1, cond2, cond3 = st.columns(3)

    cond1.metric(
        "FVR Target",
        ">= 0.90",
        f"Current: {fvr:.3f}",
    )

    cond2.metric(
        "Risk ROI Target",
        ">= 0%",
        f"Current: {risk_roi:.2f}%",
    )

    cond3.metric(
        "Probability Target",
        ">= 70%",
        f"Current: {prob_1plus * 100:.2f}%",
    )

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

elif page == "Pool Routing":
    st.subheader("Pool Routing")
    render_decision_status(action)

    state_path = Path.home() / "bch_rental_engine/state/bch_solo_rental_strike_engine.json"

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
    st.subheader("Editable Engine Settings")

    override = load_config_override()

    current_budget_min = int(override.get("budget_min_usd", latest.get("budget_min_usd", 100)))
    current_budget_max = int(override.get("budget_max_usd", latest.get("budget_max_usd", 1000)))
    current_budget_step = int(override.get("budget_step_usd", latest.get("budget_step_usd", 10)))

    with st.form("settings_form"):
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

        submitted = st.form_submit_button("Save Settings")

    if submitted:
        if budget_min >= budget_max:
            st.error("Budget Min must be less than Budget Max.")
        else:
            save_config_override(
                {
                    "budget_min_usd": int(budget_min),
                    "budget_max_usd": int(budget_max),
                    "budget_step_usd": int(budget_step),
                }
            )
            st.success("Settings saved. The engine will use these values after the next engine config update.")

    st.subheader("Current Override File")
    st.json(load_config_override())