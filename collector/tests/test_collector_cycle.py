"""Seam A: run Collector cycles, then assert on the exported exposition text."""

import urllib.request

from conftest import parse_exposition
from iceobs_collector.collector import Collector
from iceobs_collector.settings import Settings

DATA_FILES = "iceobs_data_files"


def labels(namespace: str, table: str):
    return tuple(sorted({"namespace": namespace, "table": table}.items()))


def test_one_cycle_exports_data_file_count_per_table(env):
    collector = Collector(Settings.from_env(env))

    collector.run_cycle()

    samples = parse_exposition(collector.metrics_text())
    assert samples[(DATA_FILES, labels("sales", "orders"))] == 3
    assert samples[(DATA_FILES, labels("ops", "events"))] == 2


def test_liveness_endpoint_answers_while_running(env):
    collector = Collector(Settings.from_env(env))
    server = collector.serve(port=0)  # port 0: let the OS pick a free port
    try:
        port = server.server_address[1]
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz") as response:
            assert response.status == 200
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/metrics") as response:
            assert response.status == 200
            assert response.headers["Content-Type"].startswith("text/plain")
    finally:
        server.shutdown()
        server.server_close()
