"""Seam A: change detection across cycles, observed through /metrics."""

import pyarrow as pa
import pytest
from pyiceberg.catalog.sql import SqlCatalog

from conftest import parse_exposition
from iceobs_collector.collector import Collector
from iceobs_collector.settings import Settings, SettingsError

SCHEMA = pa.schema([("id", pa.int64()), ("payload", pa.string())])


class RecordingCatalog(SqlCatalog):
    """The Collector's catalog, remembering which Tables it was asked to load."""

    loads: list[tuple[str, ...]]

    def load_table(self, identifier):
        self.loads.append(tuple(identifier))
        return super().load_table(identifier)


@pytest.fixture
def catalog(env, fixture_warehouse) -> SqlCatalog:
    """A writer, standing in for the engines that commit to the lakehouse."""
    return SqlCatalog(
        "default",
        uri=env["ICEOBS_CATALOG_URI"],
        warehouse=f"file://{fixture_warehouse}/warehouse",
    )


@pytest.fixture
def collector(env) -> Collector:
    recording = RecordingCatalog("default", uri=env["ICEOBS_CATALOG_URI"])
    recording.loads = []
    return Collector(Settings.from_env(env), catalog=recording)


def data_files(collector: Collector) -> dict[tuple[str, str], float]:
    samples = parse_exposition(collector.metrics_text())
    return {
        (dict(labels)["namespace"], dict(labels)["table"]): value
        for (name, labels), value in samples.items()
        if name == "iceobs_data_files"
    }


def append_one_file(catalog: SqlCatalog, identifier: str) -> None:
    catalog.load_table(identifier).append(pa.table({"id": [99], "payload": ["x"]}, schema=SCHEMA))


def test_a_commit_changes_only_that_tables_signals_and_reloads_only_that_table(collector, catalog):
    collector.run_cycle()
    collector.catalog.loads.clear()

    append_one_file(catalog, "sales.orders")
    collector.run_cycle()

    assert data_files(collector) == {("sales", "orders"): 4, ("ops", "events"): 2}
    assert collector.catalog.loads == [("sales", "orders")]


def test_an_unchanged_catalog_reloads_nothing(collector):
    collector.run_cycle()
    collector.catalog.loads.clear()

    collector.run_cycle()

    assert collector.catalog.loads == []


def test_a_table_registered_between_cycles_appears_on_the_next_cycle(collector, catalog):
    collector.run_cycle()

    catalog.create_namespace("new_ns")
    catalog.create_table("new_ns.fresh", SCHEMA).append(
        pa.table({"id": [1], "payload": ["x"]}, schema=SCHEMA)
    )
    collector.run_cycle()

    assert data_files(collector)[("new_ns", "fresh")] == 1


def test_a_dropped_table_has_no_series_on_the_next_cycle(collector, catalog):
    collector.run_cycle()

    catalog.drop_table("ops.events")
    collector.run_cycle()

    assert data_files(collector) == {("sales", "orders"): 3}


def test_load_concurrency_is_configurable_and_validated(env):
    assert Settings.from_env({**env, "ICEOBS_LOAD_CONCURRENCY": "8"}).load_concurrency == 8
    with pytest.raises(SettingsError, match="ICEOBS_LOAD_CONCURRENCY"):
        Settings.from_env({**env, "ICEOBS_LOAD_CONCURRENCY": "0"})
