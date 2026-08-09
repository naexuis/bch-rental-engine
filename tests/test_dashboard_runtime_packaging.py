from pathlib import Path


def test_dashboard_dockerfile_copies_scripts_package():
    dockerfile = Path("Dockerfile.dashboard").read_text()

    assert "COPY scripts /app/scripts" in dockerfile


def test_dashboard_dockerfile_sets_pythonpath_to_app():
    dockerfile = Path("Dockerfile.dashboard").read_text()

    assert "ENV PYTHONPATH=/app" in dockerfile


def test_streamlit_config_disables_automatic_sidebar_navigation():
    config_path = Path(".streamlit/config.toml")

    assert config_path.exists()

    config = config_path.read_text()

    assert "showSidebarNavigation = false" in config
