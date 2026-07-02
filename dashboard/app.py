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

@st.cache_data(ttl=60)
def load_latest_state() -> dict:
    state_path = Path.home() / "bch_rental_engine/state/bch_solo_rental_strike_engine.json"

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
    st.subheader("Current Decision")
    render_decision_status(action)

    st.markdown(f"### {recommendation}")

    if interpretation:
        st.write(interpretation)
    elif engine_answer:
        st.write(engine_answer)

    st.divider()

    st.subheader("Best Strike")

    strike_col1, strike_col2, strike_col3, strike_col4 = st.columns(4)

    strike_col1.metric(
        "Budget",
        f"${safe_num(best_strike.get('budget_usd', latest.get('best_cost_usd', 0))):,.0f}",
    )

    strike_col2.metric(
        "Hashrate",
        fmt_hashrate_from_ph(
            safe_num(best_strike.get("hashrate_ph", latest.get("best_hashrate_ph", 0)))
        ),
    )

    strike_col3.metric(
        "Duration",
        f"{safe_num(best_strike.get('duration_hours', latest.get('best_duration_hours', 0))):.2f}h",
    )

    strike_col4.metric(
        "P(1+ Block)",
        f"{safe_num(best_strike.get('prob_1plus', latest.get('best_prob_1plus', 0))) * 100:.2f}%",
    )

    strike_col5, strike_col6, strike_col7, strike_col8 = st.columns(4)

    strike_col5.metric(
        "FVR",
        f"{safe_num(best_strike.get('fair_value_ratio', fvr)):.3f}",
    )

    strike_col6.metric(
        "Risk ROI",
        f"{safe_num(best_strike.get('risk_adjusted_roi_pct', risk_roi)):.2f}%",
    )

    strike_col7.metric(
        "Expected Profit",
        f"${safe_num(best_strike.get('expected_profit_usd', latest.get('best_expected_profit_usd', 0))):,.2f}",
    )

    strike_col8.metric(
        "Market Regime",
        market_regime,
    )

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

    if prob_1plus < 0.70:
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
    cond3.metric("Probability Target", ">= 70%", f"Current: {prob_1plus * 100:.2f}%")

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