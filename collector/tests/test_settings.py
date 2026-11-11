import dataclasses

import pytest

from iceobs_collector.settings import Settings, SettingsError


def test_parses_required_and_default_values():
    settings = Settings.from_env({"ICEOBS_CATALOG_URI": "postgresql://u:p@db/iceberg"})

    assert settings.catalog_uri == "postgresql://u:p@db/iceberg"
    assert settings.poll_interval_seconds == 30
    assert settings.http_port == 8080
    assert settings.catalog_name == "default"


def test_parses_optional_overrides():
    settings = Settings.from_env(
        {
            "ICEOBS_CATALOG_URI": "sqlite:///c.db",
            "ICEOBS_POLL_INTERVAL_SECONDS": "5",
            "ICEOBS_HTTP_PORT": "9000",
            "ICEOBS_CATALOG_NAME": "lake",
        }
    )
    assert settings.catalog_name == "lake"

    assert settings.poll_interval_seconds == 5
    assert settings.http_port == 9000


def test_settings_are_immutable():
    settings = Settings.from_env({"ICEOBS_CATALOG_URI": "sqlite:///c.db"})

    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.catalog_uri = "other"  # type: ignore[misc]


def test_missing_required_value_fails_with_clear_error():
    with pytest.raises(SettingsError, match="ICEOBS_CATALOG_URI"):
        Settings.from_env({})


@pytest.mark.parametrize("name", ["ICEOBS_POLL_INTERVAL_SECONDS", "ICEOBS_HTTP_PORT"])
@pytest.mark.parametrize("bad", ["abc", "0", "-3"])
def test_invalid_numbers_fail_naming_the_variable(name, bad):
    with pytest.raises(SettingsError, match=name):
        Settings.from_env({"ICEOBS_CATALOG_URI": "sqlite:///c.db", name: bad})
