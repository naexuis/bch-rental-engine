from pathlib import Path


def test_pool_routing_page_uses_passed_state_without_reloading_state_file():
    source = Path(
        "dashboard/pages/pool_routing.py"
    ).read_text()

    # The modular page receives state from dashboard/app.py.
    # It must not depend on the old monolithic STATE_PATH globals.
    assert "STATE_PATH" not in source
    assert "json.load" not in source
    assert "state_path =" not in source


def test_pool_routing_page_derives_action_from_passed_state():
    source = Path(
        "dashboard/pages/pool_routing.py"
    ).read_text()

    assert 'state.get("opportunity")' in source
    assert 'opportunity.get("action"' in source

    # Protect against the exact RC regression.
    assert "render_decision_status(action)" in source
