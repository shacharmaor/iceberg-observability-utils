import pytest

from conftest import parse_exposition
from iceobs_collector.collector import Collector
from iceobs_collector.settings import Settings, SettingsError
from iceobs_collector.signals import REGISTRY, read_metadata


def test_data_file_count_is_the_first_registered_signal():
    assert "data_file_count" in REGISTRY


def test_disabling_a_signal_removes_its_series(env):
    collector = Collector(Settings.from_env({**env, "ICEOBS_DISABLED_SIGNALS": "data_file_count"}))

    collector.run_cycle()

    names = {name for name, _ in parse_exposition(collector.metrics_text())}
    assert "iceobs_data_files" not in names


def test_unknown_signal_name_fails_startup_with_clear_error(env):
    with pytest.raises(SettingsError, match="no_such_signal"):
        Settings.from_env({**env, "ICEOBS_DISABLED_SIGNALS": "no_such_signal"})


def test_metadata_needed_only_by_disabled_signals_is_not_read():
    class ExplodingTable:
        def current_snapshot(self):
            raise AssertionError("metadata was read although no enabled Signal needs it")

        @property
        def inspect(self):
            raise AssertionError("metadata was read although no enabled Signal needs it")

    assert read_metadata(ExplodingTable(), signals=[]) == {}
