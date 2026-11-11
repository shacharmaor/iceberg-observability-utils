"""A narrow Prometheus client interface, with one real HTTP implementation."""

from dataclasses import dataclass
from typing import Protocol

import httpx


@dataclass(frozen=True)
class Sample:
    labels: dict[str, str]
    value: float


class PrometheusClient(Protocol):
    def instant_query(self, query: str) -> list[Sample]: ...


class HttpPrometheusClient:
    def __init__(
        self,
        url: str,
        token: str | None = None,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        self._http = httpx.Client(
            base_url=url, headers=headers, timeout=timeout, transport=transport
        )

    def instant_query(self, query: str) -> list[Sample]:
        response = self._http.get("/api/v1/query", params={"query": query})
        response.raise_for_status()
        result = response.json()["data"]["result"]
        return [Sample(labels=item["metric"], value=float(item["value"][1])) for item in result]
