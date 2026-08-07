from pathlib import Path


def test_run_engine_launches_engine_as_python_module():
    script = Path("run_engine.sh").read_text()

    assert "python -m scripts.bch_solo_rental_strike_engine" in script
    assert "python /app/scripts/bch_solo_rental_strike_engine.py" not in script


def test_run_engine_supports_immediate_run_trigger():
    script = Path("run_engine.sh").read_text()

    assert 'RUN_NOW_TRIGGER="${CONFIG_DIR}/run_now.trigger"' in script
    assert 'POLL_SECONDS=5' in script
    assert 'if [ -f "${RUN_NOW_TRIGGER}" ]; then' in script
    assert 'rm -f "${RUN_NOW_TRIGGER}"' in script