"""The one real Prometheus client, against a mocked HTTP transport (no network)."""

import httpx

from iceobs_ui_backend.prometheus import HttpPrometheusClient, Sample


def test_instant_query_parses_the_prometheus_response_and_sends_the_bearer_token():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["query"] = request.url.params["query"]
        seen["auth"] = request.headers.get("authorization")
        return httpx.Response(
            200,
            json={
                "status": "success",
                "data": {
                    "resultType": "vector",
                    "result": [
                        {"metric": {"namespace": "a", "table": "t"}, "value": [1700000000, "42"]}
                    ],
                },
            },
        )

    client = HttpPrometheusClient(
        "http://prom:9090", token="s3cret", transport=httpx.MockTransport(handler)
    )

    assert client.instant_query("iceobs_data_files") == [
        Sample(labels={"namespace": "a", "table": "t"}, value=42.0)
    ]
    assert seen == {
        "path": "/api/v1/query",
        "query": "iceobs_data_files",
        "auth": "Bearer s3cret",
    }
