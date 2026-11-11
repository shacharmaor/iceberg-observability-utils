"""The Collector: reads the Catalog, computes Signals, exports them on /metrics."""

import threading
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Gauge, generate_latest
from pyiceberg.catalog.sql import SqlCatalog

from iceobs_collector.poller import diff_pointers, poll_pointers
from iceobs_collector.settings import Settings
from iceobs_collector.signals import REGISTRY, read_metadata


class Collector:
    def __init__(self, settings: Settings, catalog: SqlCatalog | None = None) -> None:
        self._settings = settings
        self.catalog = catalog or SqlCatalog(settings.catalog_name, uri=settings.catalog_uri)
        self._last_seen: dict[tuple[str, str], str] = {}
        self._registry = CollectorRegistry()
        self._signals = [s for s in REGISTRY.values() if s.name not in settings.disabled_signals]
        self._gauges = {
            signal.name: Gauge(
                signal.metric_name,
                signal.description,
                ["namespace", "table"],
                registry=self._registry,
            )
            for signal in self._signals
        }

    def run_cycle(self) -> None:
        pointers = poll_pointers(self._settings.catalog_uri, self._settings.catalog_name)
        diff = diff_pointers(self._last_seen, pointers)
        for namespace, table in diff.removed:
            for gauge in self._gauges.values():
                gauge.remove(namespace, table)
            del self._last_seen[(namespace, table)]
        locations = {(p.namespace, p.table): p.metadata_location for p in pointers}
        with ThreadPoolExecutor(max_workers=self._settings.load_concurrency) as pool:
            list(pool.map(self._reload, sorted(diff.to_reload)))
        for key in diff.to_reload:
            self._last_seen[key] = locations[key]

    def _reload(self, key: tuple[str, str]) -> None:
        table = self.catalog.load_table(key)
        metadata = read_metadata(table, self._signals)
        for signal in self._signals:
            self._gauges[signal.name].labels(*key).set(signal.compute(metadata))

    def metrics_text(self) -> str:
        return generate_latest(self._registry).decode()

    def serve(self, port: int | None = None) -> ThreadingHTTPServer:
        """Start /metrics and /healthz in a background thread; the caller owns shutdown."""
        collector = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                if self.path == "/healthz":
                    self._respond(200, b"ok", "text/plain")
                elif self.path == "/metrics":
                    self._respond(200, collector.metrics_text().encode(), CONTENT_TYPE_LATEST)
                else:
                    self._respond(404, b"not found", "text/plain")

            def _respond(self, status: int, body: bytes, content_type: str) -> None:
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:
                pass

        server = ThreadingHTTPServer(
            ("0.0.0.0", self._settings.http_port if port is None else port), Handler
        )
        threading.Thread(target=server.serve_forever, daemon=True).start()
        return server
