"""HTTP API consumed only by the Web UI."""

from dataclasses import asdict

from fastapi import FastAPI

from iceobs_ui_backend.findings import Finding, evaluate_higher_is_worse
from iceobs_ui_backend.prometheus import PrometheusClient
from iceobs_ui_backend.settings import Settings

SEVERITY_RANK = {"critical": 2, "warn": 1}


def _rank(findings: list[Finding]) -> tuple[int, int]:
    """Worst severity first, then number of Findings."""
    worst = max((SEVERITY_RANK[f.severity] for f in findings), default=0)
    return (worst, len(findings))


def create_app(settings: Settings, prometheus: PrometheusClient) -> FastAPI:
    app = FastAPI(title="Iceberg Observability UI Backend")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/overview")
    def overview() -> dict[str, list[dict]]:
        tables = []
        for sample in prometheus.instant_query("iceobs_data_files"):
            finding = evaluate_higher_is_worse(
                "data_file_count",
                sample.value,
                settings.data_files_warn,
                settings.data_files_critical,
            )
            tables.append(
                {
                    "namespace": sample.labels["namespace"],
                    "table": sample.labels["table"],
                    "findings": [finding] if finding else [],
                }
            )
        tables.sort(
            key=lambda t: (_rank(t["findings"]), t["namespace"], t["table"]),
            reverse=True,
        )
        return {"tables": [{**t, "findings": [asdict(f) for f in t["findings"]]} for t in tables]}

    return app
