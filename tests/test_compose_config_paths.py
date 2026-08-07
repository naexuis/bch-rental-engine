from pathlib import Path


def test_compose_uses_shared_config_directory():
    text = Path("docker-compose.yml").read_text()

    assert text.count("BCH_CONFIG_DIR: /config") == 2
    assert text.count("${APP_DATA_DIR}/config:/config") == 2


def test_compose_does_not_use_legacy_config_path():
    text = Path("docker-compose.yml").read_text()

    assert "/root/bch_rental_engine/config" not in text