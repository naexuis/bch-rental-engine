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
