def classify_engine_status(
    consecutive_failures: int,
) -> str:
    if consecutive_failures == 0:
        return "HEALTHY"

    return "DEGRADED"


def build_success_health(
    timestamp: str,
    previous_health: dict | None = None,
) -> dict:
    health = {
        "status": "HEALTHY",
        "heartbeat": timestamp,
        "last_successful_execution": timestamp,
        "consecutive_failures": 0,
    }

    if previous_health is not None:
        last_failure_timestamp = previous_health.get(
            "last_failure_timestamp"
        )

        if last_failure_timestamp is not None:
            health["last_failure_timestamp"] = (
                last_failure_timestamp
            )

    return health


def build_failure_health(
    timestamp: str,
    previous_health: dict,
) -> dict:
    consecutive_failures = (
        previous_health.get("consecutive_failures", 0) + 1
    )

    return {
        "status": classify_engine_status(consecutive_failures),
        "heartbeat": timestamp,
        "last_successful_execution": previous_health.get(
            "last_successful_execution"
        ),
        "last_failure_timestamp": timestamp,
        "consecutive_failures": consecutive_failures,
    }


def load_previous_engine_health(
    state_path,
) -> dict:
    import json

    if not state_path.exists():
        return {}

    try:
        state = json.loads(
            state_path.read_text()
        )
    except json.JSONDecodeError:
        return {}

    health = state.get(
        "engine_health",
        {},
    )

    if not isinstance(health, dict):
        return {}

    return health


def classify_heartbeat_status(
    heartbeat: str,
    current_time: str,
    stale_after_minutes: int,
) -> str:
    from datetime import datetime

    try:
        heartbeat_dt = datetime.fromisoformat(
            heartbeat
        )
        current_dt = datetime.fromisoformat(
            current_time
        )
    except (TypeError, ValueError):
        return "UNKNOWN"

    age_minutes = (
        current_dt - heartbeat_dt
    ).total_seconds() / 60

    if age_minutes > stale_after_minutes:
        return "STALE"

    return "HEALTHY"


def evaluate_engine_health_status(
    health: dict,
    current_time: str,
    stale_after_minutes: int,
) -> str:
    if health.get("status") == "DEGRADED":
        return "DEGRADED"

    return classify_heartbeat_status(
        heartbeat=health.get("heartbeat"),
        current_time=current_time,
        stale_after_minutes=stale_after_minutes,
    )
