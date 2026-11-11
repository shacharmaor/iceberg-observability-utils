import pytest

from iceobs_ui_backend.settings import Settings, SettingsError


def test_prometheus_url_is_required():
    with pytest.raises(SettingsError, match="ICEOBS_PROMETHEUS_URL"):
        Settings.from_env({})


def test_url_token_and_thresholds_come_from_the_env_mapping():
    settings = Settings.from_env(
        {
            "ICEOBS_PROMETHEUS_URL": "http://prom:9090",
            "ICEOBS_PROMETHEUS_TOKEN": "s3cret",
            "ICEOBS_DATA_FILES_WARN": "10",
            "ICEOBS_DATA_FILES_CRITICAL": "20",
        }
    )

    assert settings.prometheus_url == "http://prom:9090"
    assert settings.prometheus_token == "s3cret"
    assert (settings.data_files_warn, settings.data_files_critical) == (10, 20)


def test_token_is_optional_and_thresholds_have_defaults():
    settings = Settings.from_env({"ICEOBS_PROMETHEUS_URL": "http://prom:9090"})

    assert settings.prometheus_token is None
    assert 0 < settings.data_files_warn < settings.data_files_critical


@pytest.mark.parametrize(
    "overrides",
    [
        {"ICEOBS_DATA_FILES_WARN": "lots"},
        {"ICEOBS_DATA_FILES_WARN": "50", "ICEOBS_DATA_FILES_CRITICAL": "10"},
    ],
)
def test_invalid_thresholds_fail_startup(overrides):
    with pytest.raises(SettingsError, match="ICEOBS_DATA_FILES"):
        Settings.from_env({"ICEOBS_PROMETHEUS_URL": "http://prom:9090", **overrides})
