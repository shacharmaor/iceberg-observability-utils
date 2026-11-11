"""Seam C harness: the FastAPI app in-process with a fake Prometheus client."""

import pytest
from fastapi.testclient import TestClient

from iceobs_ui_backend.app import create_app
from iceobs_ui_backend.prometheus import Sample
from iceobs_ui_backend.settings import Settings


class FakePrometheus:
    """Canned instant-query results, keyed by metric name."""

    def __init__(self, series: dict[str, list[Sample]] | None = None) -> None:
        self.series = series or {}

    def instant_query(self, query: str) -> list[Sample]:
        return self.series.get(query, [])


def sample(namespace: str, table: str, value: float) -> Sample:
    return Sample(labels={"namespace": namespace, "table": table}, value=value)


@pytest.fixture
def env() -> dict[str, str]:
    return {"ICEOBS_PROMETHEUS_URL": "http://prometheus:9090"}


@pytest.fixture
def make_client(env):
    def make(series: dict[str, list[Sample]], **overrides: str) -> TestClient:
        settings = Settings.from_env({**env, **overrides})
        return TestClient(create_app(settings, FakePrometheus(series)))

    return make
