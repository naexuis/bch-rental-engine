from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.settings_service import (
    load_config_override,
    request_engine_run,
    resolve_setting_value,
    save_config_override,
)


def render_settings_page(
    *,
    state: dict,
    latest: pd.Series,
    config_dir: Path,
    config_override_path: Path,
) -> None:
    st.subheader("Settings")

    override = load_config_override(
        config_override_path,
    )
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
                },
                config_dir=config_dir,
                config_override_path=config_override_path,
            )

            request_engine_run(
                config_dir,
            )

            st.success(
                "Settings saved. An immediate engine run has been requested."
            )

    st.divider()

    st.markdown("### Current Override File")
    st.caption("This is the exact JSON file currently being used by the engine override system.")
    st.json(
        load_config_override(
            config_override_path,
        )
    )
