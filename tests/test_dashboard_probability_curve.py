import math

from dashboard.app import build_success_probability_curve


def test_success_probability_curve_matches_poisson_model():
    expected_blocks = 1.0
    duration_hours = 2.0

    curve = build_success_probability_curve(
        expected_blocks=expected_blocks,
        duration_hours=duration_hours,
        max_multiplier=1.0,
        points=3,
    )

    assert len(curve) == 3

    final_probability = curve.iloc[-1]["probability_pct"]
    expected_probability = (1 - math.exp(-1.0)) * 100

    assert abs(final_probability - expected_probability) < 1e-9


def test_success_probability_curve_returns_empty_for_invalid_inputs():
    curve = build_success_probability_curve(
        expected_blocks=0,
        duration_hours=2.0,
    )

    assert curve.empty