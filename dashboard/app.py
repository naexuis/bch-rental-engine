from pathlib import Path
import sqlite3
import json
import os
import math
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import plotly.graph_objects as go

from dashboard.ui_utils import (
    build_success_probability_curve,
    fmt_hashrate_from_ph,
    fmt_large_number,
    progress_pct,
    safe_num,
)
from dashboard.components.mission_timeline import (
    render_mission_timeline,
)
from dashboard.components.pool_recommendation import (
    render_recommended_pool,
)
from dashboard.components.alternative_strike_plans import (
    render_alternative_strike_plans,
)
from dashboard.decision_utils import (
    canonical_decision_from_state,
)
from dashboard.pages.dashboard import (
    render_dashboard_page,
)
from dashboard.market_utils import (
    calculate_technical_indicators,
    fetch_yfinance_ohlc,
    get_candle_settings,
    summarize_technical_indicators,
)
from dashboard.pages.market import (
    render_market_page,
)
from dashboard.pages.market_trends import (
    render_market_trends_page,
)
from dashboard.pages.strike_analysis import (
    render_strike_analysis_page,
)


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

RUN_NOW_TRIGGER_PATH = CONFIG_DIR / "run_now.trigger"

def request_engine_run() -> None:
    """
    Request an immediate engine run through the shared config directory.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    RUN_NOW_TRIGGER_PATH.touch()

def resolve_setting_value(
    key: str,
    override: dict,
    state_config: dict,
    latest: pd.Series,
    default: int | float,
) -> int | float:
    """
    Resolve one dashboard setting using the configured priority order.

    Priority:
        1. Dashboard override file
        2. Latest JSON state config
        3. Latest history row
        4. Hardcoded default
    """
    if key in override:
        return override[key]

    if key in state_config:
        return state_config[key]

    latest_value = latest.get(key)

    if pd.notna(latest_value):
        return latest_value

    return default

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

if st.sidebar.button("Refresh dashboard"):
    st.cache_data.clear()
    st.rerun()

has_history = not df.empty

best_strike = state.get("winners", {}).get("best_strike") or {}
recommended_pool = state.get("recommended_pool") or {}
pool_rankings = (
    state.get("pool_routing", {}).get("rankings", [])
    or []
)
interpretation = state.get("interpretation", "")
engine_answer = state.get("answer", "")

if has_history:
    latest = df.iloc[-1]
else:
    opportunity = state.get("opportunity") or {}

    latest = pd.Series({
        "timestamp": state.get("timestamp", "Never"),
        "best_fair_value_ratio": best_strike.get("fair_value_ratio", 0),
        "best_risk_adjusted_roi_pct": best_strike.get(
            "risk_adjusted_roi_pct",
            0,
        ),
        "best_prob_1plus": best_strike.get("prob_1plus", 0),
        "opportunity_score": opportunity.get("score", 0),
        "market_regime": state.get("market_regime", "N/A"),
        "best_recommendation": state.get("recommendation", "N/A"),
        "opportunity_action": opportunity.get("action", "WAIT"),
    })

last_updated = latest.get("timestamp", "Never")
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
    render_dashboard_page(
        state=state,
        df=df,
        latest=latest,
        has_history=has_history,
        history_rows=history_rows,
        last_updated=last_updated,
    )

elif page == "Market":
    render_market_page(
        df=df,
        latest=latest,
        has_history=has_history,
    )

elif page == "Market Trends":
    render_market_trends_page(
        df=df,
        latest=latest,
    )

elif page == "Strike Analysis":
    render_strike_analysis_page(
        state=state,
    )

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
    state_config = state.get("config", {}) or {}

    current_budget_min = int(
        resolve_setting_value(
            key="budget_min_usd",
            override=override,
            state_config=state_config,
            latest=latest,
            default=100,
        )
    )

    current_budget_max = int(
        resolve_setting_value(
            key="budget_max_usd",
            override=override,
            state_config=state_config,
            latest=latest,
            default=1000,
        )
    )

    current_budget_step = int(
        resolve_setting_value(
            key="budget_step_usd",
            override=override,
            state_config=state_config,
            latest=latest,
            default=10,
        )
    )

    current_hashrate_min = int(
        resolve_setting_value(
            key="hashrate_min_ph",
            override=override,
            state_config=state_config,
            latest=latest,
            default=300,
        )
    )

    current_hashrate_max = int(
        resolve_setting_value(
            key="hashrate_max_ph",
            override=override,
            state_config=state_config,
            latest=latest,
            default=300,
        )
    )

    current_hashrate_step = int(
        resolve_setting_value(
            key="hashrate_step_ph",
            override=override,
            state_config=state_config,
            latest=latest,
            default=50,
        )
    )

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

            request_engine_run()

            st.success(
                "Settings saved. An immediate engine run has been requested."
            )

    st.divider()

    st.markdown("### Current Override File")
    st.caption("This is the exact JSON file currently being used by the engine override system.")
    st.json(load_config_override())