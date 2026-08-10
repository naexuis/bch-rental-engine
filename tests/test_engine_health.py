from scripts.health.engine_health import (
    build_success_health,
    classify_engine_status,
)


def test_engine_status_is_healthy_when_there_are_no_consecutive_failures():
    status = classify_engine_status(
        consecutive_failures=0,
    )

    assert status == "HEALTHY"


def test_engine_status_is_degraded_when_there_are_consecutive_failures():
    status = classify_engine_status(
        consecutive_failures=1,
    )

    assert status == "DEGRADED"


def test_build_success_health_records_heartbeat_and_last_success():
    from scripts.health.engine_health import build_success_health

    timestamp = "2026-08-09T23:30:00+00:00"

    health = build_success_health(
        timestamp=timestamp,
    )

    assert health == {
        "status": "HEALTHY",
        "heartbeat": timestamp,
        "last_successful_execution": timestamp,
        "consecutive_failures": 0,
    }


def test_build_failure_health_preserves_last_success_and_increments_failures():
    from scripts.health.engine_health import build_failure_health

    previous_health = {
        "status": "HEALTHY",
        "heartbeat": "2026-08-09T23:30:00+00:00",
        "last_successful_execution": "2026-08-09T23:30:00+00:00",
        "consecutive_failures": 0,
    }

    failure_timestamp = "2026-08-09T23:35:00+00:00"

    health = build_failure_health(
        timestamp=failure_timestamp,
        previous_health=previous_health,
    )

    assert health == {
        "status": "DEGRADED",
        "heartbeat": failure_timestamp,
        "last_successful_execution": "2026-08-09T23:30:00+00:00",
        "last_failure_timestamp": failure_timestamp,
        "consecutive_failures": 1,
    }


def test_build_failure_health_increments_existing_failure_count():
    from scripts.health.engine_health import build_failure_health

    previous_health = {
        "status": "DEGRADED",
        "heartbeat": "2026-08-09T23:35:00+00:00",
        "last_successful_execution": "2026-08-09T23:30:00+00:00",
        "last_failure_timestamp": "2026-08-09T23:35:00+00:00",
        "consecutive_failures": 1,
    }

    failure_timestamp = "2026-08-09T23:40:00+00:00"

    health = build_failure_health(
        timestamp=failure_timestamp,
        previous_health=previous_health,
    )

    assert health["status"] == "DEGRADED"
    assert health["heartbeat"] == failure_timestamp
    assert health["last_successful_execution"] == "2026-08-09T23:30:00+00:00"
    assert health["last_failure_timestamp"] == failure_timestamp
    assert health["consecutive_failures"] == 2


def test_build_success_health_resets_failures_and_preserves_last_failure():
    previous_health = {
        "status": "DEGRADED",
        "heartbeat": "2026-08-09T23:40:00+00:00",
        "last_successful_execution": "2026-08-09T23:30:00+00:00",
        "last_failure_timestamp": "2026-08-09T23:40:00+00:00",
        "consecutive_failures": 2,
    }

    success_timestamp = "2026-08-09T23:45:00+00:00"

    health = build_success_health(
        timestamp=success_timestamp,
        previous_health=previous_health,
    )

    assert health == {
        "status": "HEALTHY",
        "heartbeat": success_timestamp,
        "last_successful_execution": success_timestamp,
        "last_failure_timestamp": "2026-08-09T23:40:00+00:00",
        "consecutive_failures": 0,
    }


def test_load_previous_engine_health_returns_health_from_existing_state(
    tmp_path,
):
    import json

    from scripts.health.engine_health import (
        load_previous_engine_health,
    )

    state_path = tmp_path / "state.json"

    expected_health = {
        "status": "DEGRADED",
        "heartbeat": "2026-08-09T23:40:00+00:00",
        "last_successful_execution": "2026-08-09T23:30:00+00:00",
        "last_failure_timestamp": "2026-08-09T23:40:00+00:00",
        "consecutive_failures": 2,
    }

    state_path.write_text(
        json.dumps(
            {
                "engine_health": expected_health,
            }
        )
    )

    health = load_previous_engine_health(
        state_path,
    )

    assert health == expected_health


def test_load_previous_engine_health_returns_empty_when_state_file_is_missing(
    tmp_path,
):
    from scripts.health.engine_health import (
        load_previous_engine_health,
    )

    state_path = tmp_path / "missing_state.json"

    health = load_previous_engine_health(
        state_path,
    )

    assert health == {}


def test_load_previous_engine_health_returns_empty_when_health_key_is_missing(
    tmp_path,
):
    import json

    from scripts.health.engine_health import (
        load_previous_engine_health,
    )

    state_path = tmp_path / "state.json"

    state_path.write_text(
        json.dumps(
            {
                "timestamp": "2026-08-09T23:50:00+00:00",
                "recommendation": "WATCH",
            }
        )
    )

    health = load_previous_engine_health(
        state_path,
    )

    assert health == {}


def test_run_engine_waiting_state_persists_successful_engine_health(
    tmp_path,
    monkeypatch,
):
    import json

    from scripts import bch_solo_rental_strike_engine as engine

    state_path = tmp_path / "state.json"
    log_path = tmp_path / "engine.jsonl"

    monkeypatch.setattr(
        engine,
        "STATE_PATH",
        state_path,
    )
    monkeypatch.setattr(
        engine,
        "LOG_PATH",
        log_path,
    )
    monkeypatch.setattr(
        engine,
        "now_utc",
        lambda: "2026-08-09T23:55:00+00:00",
    )

    market = engine.MarketData(
        timestamp="2026-08-09T23:55:00+00:00",
        btc_usd=120000.0,
        bch_usd=600.0,
        bch_btc=0.005,
        bch_difficulty=1.0,
        bch_network_hashrate_eh=1.0,
        bch_block_reward=3.125,
    )

    monkeypatch.setattr(
        engine,
        "fetch_market_data",
        lambda: market,
    )

    monkeypatch.setattr(
        engine,
        "load_all_sources",
        lambda: (_ for _ in ()).throw(
            RuntimeError("No hashpower sources found")
        ),
    )

    monkeypatch.setattr(
        engine,
        "get_storage_health_record",
        lambda: {
            "database_exists": True,
            "row_count": 1,
            "database_size_bytes": 4096,
            "integrity_ok": True,
        },
    )

    result = engine.run_engine()

    state = json.loads(
        state_path.read_text()
    )

    assert result["status"] == "waiting_for_pricing"
    assert state["engine_health"] == {
        "status": "HEALTHY",
        "heartbeat": "2026-08-09T23:55:00+00:00",
        "last_successful_execution": "2026-08-09T23:55:00+00:00",
        "consecutive_failures": 0,
    }


def test_run_engine_success_persists_successful_engine_health(
    tmp_path,
    monkeypatch,
):
    import json

    from scripts import bch_solo_rental_strike_engine as engine

    state_path = tmp_path / "state.json"
    log_path = tmp_path / "engine.jsonl"

    monkeypatch.setattr(
        engine,
        "STATE_PATH",
        state_path,
    )
    monkeypatch.setattr(
        engine,
        "LOG_PATH",
        log_path,
    )
    monkeypatch.setattr(
        engine,
        "now_utc",
        lambda: "2026-08-10T00:00:00+00:00",
    )

    market = engine.MarketData(
        timestamp="2026-08-10T00:00:00+00:00",
        btc_usd=120000.0,
        bch_usd=600.0,
        bch_btc=0.005,
        bch_difficulty=1.0,
        bch_network_hashrate_eh=4.0,
        bch_block_reward=3.125,
    )

    source = engine.HashSource(
        source="braiins",
        name="Test Hashpower",
        hashrate_ph=500.0,
        price_btc_per_ph_day=0.00001,
        min_hours=1.0,
        max_hours=12.0,
        executable=True,
    )

    best = engine.StrikeScenario(
        source="braiins",
        name="Test Hashpower",
        budget_usd=1000.0,
        budget_btc=0.008,
        hashrate_ph=500.0,
        hashrate_eh=0.5,
        duration_hours=2.0,
        cost_btc=0.008,
        cost_usd=1000.0,
        expected_blocks=1.0,
        prob_0_blocks=0.30,
        prob_1plus=0.70,
        prob_2plus=0.25,
        expected_bch_gross=3.125,
        expected_bch_net=3.078125,
        expected_revenue_usd=1846.875,
        expected_profit_usd=846.875,
        roi_pct=84.6875,
        risk_adjusted_profit_usd=100.0,
        risk_adjusted_roi_pct=10.0,
        profit_if_0_blocks=-1000.0,
        profit_if_1_block=846.875,
        profit_if_2_blocks=2693.75,
        break_even_price_btc_per_ph_day=0.000011,
        current_price_btc_per_ph_day=0.00001,
        fair_value_ratio=1.10,
        premium_discount_pct=-9.09,
        strike_score=90.0,
        strike_grade="A",
        alert_tier="RENT",
        recommendation="RENT",
        strike_type="SHORT",
    )

    monkeypatch.setattr(
        engine,
        "fetch_market_data",
        lambda: market,
    )
    monkeypatch.setattr(
        engine,
        "load_all_sources",
        lambda: [source],
    )
    monkeypatch.setattr(
        engine,
        "build_and_score_scenarios",
        lambda market, sources: [best],
    )
    monkeypatch.setattr(
        engine,
        "select_winners",
        lambda scenarios: {
            "best_strike": best,
        },
    )
    monkeypatch.setattr(
        engine,
        "build_budget_frontier",
        lambda scenarios: [],
    )
    monkeypatch.setattr(
        engine,
        "summarize_budget_frontier",
        lambda frontier: {},
    )
    monkeypatch.setattr(
        engine,
        "build_optimization_surface",
        lambda scenarios: {},
    )
    monkeypatch.setattr(
        engine,
        "calculate_probability_table",
        lambda market, price: [],
    )
    monkeypatch.setattr(
        engine,
        "get_history_trends",
        lambda: {},
    )
    monkeypatch.setattr(
        engine,
        "classify_market_regime",
        lambda fair_value_ratio: "FAIR",
    )
    monkeypatch.setattr(
        engine,
        "build_pool_rankings_for_strike",
        lambda best, market: {
            "recommended_pool": None,
        },
    )
    monkeypatch.setattr(
        engine,
        "calculate_opportunity_score",
        lambda **kwargs: {
            "score": 75,
            "action": "READY",
        },
    )
    monkeypatch.setattr(
        engine,
        "get_latest_opportunity_action",
        lambda: None,
    )
    monkeypatch.setattr(
        engine,
        "get_latest_opportunity_score",
        lambda: None,
    )
    monkeypatch.setattr(
        engine,
        "get_history_rows",
        lambda limit=25: [],
    )
    monkeypatch.setattr(
        engine,
        "analyze_metric",
        lambda history, metric: {},
    )
    monkeypatch.setattr(
        engine,
        "write_history_row",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        engine,
        "build_interpretation_text",
        lambda **kwargs: "Test interpretation",
    )
    monkeypatch.setattr(
        engine,
        "get_storage_health_record",
        lambda: {
            "database_exists": True,
            "row_count": 1,
            "database_size_bytes": 4096,
            "integrity_ok": True,
        },
    )
    monkeypatch.setattr(
        engine,
        "should_alert",
        lambda best, force_test_alert: False,
    )

    engine.run_engine()

    state = json.loads(
        state_path.read_text()
    )

    assert state["engine_health"] == {
        "status": "HEALTHY",
        "heartbeat": "2026-08-10T00:00:00+00:00",
        "last_successful_execution": "2026-08-10T00:00:00+00:00",
        "consecutive_failures": 0,
    }


def test_main_persists_degraded_engine_health_on_failure(
    tmp_path,
    monkeypatch,
):
    import json

    import pytest

    from scripts import bch_solo_rental_strike_engine as engine

    state_path = tmp_path / "state.json"
    log_path = tmp_path / "engine.jsonl"
    history_path = tmp_path / "history.sqlite"

    state_path.write_text(
        json.dumps(
            {
                "engine_health": {
                    "status": "HEALTHY",
                    "heartbeat": "2026-08-10T00:00:00+00:00",
                    "last_successful_execution": "2026-08-10T00:00:00+00:00",
                    "consecutive_failures": 0,
                }
            }
        )
    )

    monkeypatch.setattr(
        engine,
        "STATE_PATH",
        state_path,
    )
    monkeypatch.setattr(
        engine,
        "LOG_PATH",
        log_path,
    )
    monkeypatch.setattr(
        engine,
        "HISTORY_DB_PATH",
        history_path,
    )
    monkeypatch.setattr(
        engine,
        "now_utc",
        lambda: "2026-08-10T00:05:00+00:00",
    )
    monkeypatch.setattr(
        engine,
        "validate_storage_startup",
        lambda path: (_ for _ in ()).throw(
            RuntimeError("Test startup failure")
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="Test startup failure",
    ):
        engine.main()

    state = json.loads(
        state_path.read_text()
    )

    assert state["error"] == "Test startup failure"

    assert state["engine_health"] == {
        "status": "DEGRADED",
        "heartbeat": "2026-08-10T00:05:00+00:00",
        "last_successful_execution": "2026-08-10T00:00:00+00:00",
        "last_failure_timestamp": "2026-08-10T00:05:00+00:00",
        "consecutive_failures": 1,
    }


def test_load_previous_engine_health_returns_empty_when_state_json_is_malformed(
    tmp_path,
):
    from scripts.health.engine_health import (
        load_previous_engine_health,
    )

    state_path = tmp_path / "state.json"

    state_path.write_text(
        "{not-valid-json"
    )

    health = load_previous_engine_health(
        state_path,
    )

    assert health == {}


def test_load_previous_engine_health_returns_empty_when_health_is_not_object(
    tmp_path,
):
    import json

    from scripts.health.engine_health import (
        load_previous_engine_health,
    )

    state_path = tmp_path / "state.json"

    state_path.write_text(
        json.dumps(
            {
                "engine_health": "invalid-health-state",
            }
        )
    )

    health = load_previous_engine_health(
        state_path,
    )

    assert health == {}
