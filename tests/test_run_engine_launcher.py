from pathlib import Path


def test_run_engine_launches_engine_as_python_module():
    script = Path("run_engine.sh").read_text()

    assert "python -m scripts.bch_solo_rental_strike_engine" in script
    assert "python /app/scripts/bch_solo_rental_strike_engine.py" not in script
