"""Seam A harness: env mapping + SQLite fixture catalog + controllable clock + parsed exposition."""

import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
from prometheus_client.parser import text_string_to_metric_families

# Iceberg metadata holds absolute paths, so the committed warehouse is restored to the exact
# location it was built at (see tools/build_fixture_warehouse.py). Each test gets a fresh copy.
CANONICAL_ROOT = Path("/tmp/iceobs-fixture")
COMMITTED_WAREHOUSE = Path(__file__).parent / "fixtures" / "warehouse"


class FakeClock:
    """Controllable clock, injected wherever the Collector needs the time."""

    def __init__(self, now: float = 1_700_000_000.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def fixture_warehouse() -> Iterator[Path]:
    shutil.rmtree(CANONICAL_ROOT, ignore_errors=True)
    shutil.copytree(COMMITTED_WAREHOUSE, CANONICAL_ROOT)
    yield CANONICAL_ROOT
    shutil.rmtree(CANONICAL_ROOT, ignore_errors=True)


@pytest.fixture
def env(fixture_warehouse: Path) -> dict[str, str]:
    """A complete env mapping pointing the Collector at the SQLite fixture catalog."""
    return {"ICEOBS_CATALOG_URI": f"sqlite:///{fixture_warehouse}/catalog.db"}


def parse_exposition(text: str) -> dict[tuple[str, tuple[tuple[str, str], ...]], float]:
    """Parse Prometheus exposition text into {(sample name, sorted labels): value}."""
    samples = {}
    for family in text_string_to_metric_families(text):
        for sample in family.samples:
            samples[(sample.name, tuple(sorted(sample.labels.items())))] = sample.value
    return samples
