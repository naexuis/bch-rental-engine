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
    render_decision_status,
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
from dashboard.components.pool_routing_helpers import (
    pool_rank_label,
    render_pool_card,
)
from dashboard.pages.pool_routing import (
    render_pool_routing_page,
)
from dashboard.history_data import (
    load_history_dataframe,
)
from dashboard.pages.history import (
    render_history_page,
)
from dashboard.settings_service import (
    load_config_override,
    request_engine_run,
    resolve_setting_value,
    save_config_override,
)
from dashboard.pages.settings import (
    render_settings_page,
)
from dashboard.pages.storage import (
    render_storage_page,
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
        "Storage",
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
    render_pool_routing_page(
        state=state,
    )

elif page == "History":
    render_history_page(
        db_path=DB_PATH,
    )

elif page == "Storage":
    render_storage_page(
        db_path=DB_PATH,
        config_override_path=CONFIG_OVERRIDE_PATH,
    )

elif page == "Settings":
    render_settings_page(
        state=state,
        latest=latest,
        config_dir=CONFIG_DIR,
        config_override_path=CONFIG_OVERRIDE_PATH,
    )