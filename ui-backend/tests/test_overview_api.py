from conftest import sample

DATA_FILES = "iceobs_data_files"


def overview(client):
    response = client.get("/api/overview")
    assert response.status_code == 200
    return {(t["namespace"], t["table"]): t for t in response.json()["tables"]}


def test_lists_every_table_found_in_prometheus_with_its_finding_severity(make_client):
    client = make_client(
        {
            DATA_FILES: [
                sample("sales", "orders", 5),
                sample("sales", "returns", 150),
                sample("ops", "events", 2000),
            ]
        },
        ICEOBS_DATA_FILES_WARN="100",
        ICEOBS_DATA_FILES_CRITICAL="1000",
    )

    tables = overview(client)

    assert set(tables) == {("sales", "orders"), ("sales", "returns"), ("ops", "events")}
    assert tables[("sales", "orders")]["findings"] == []
    (warn,) = tables[("sales", "returns")]["findings"]
    assert warn == {
        "signal": "data_file_count",
        "value": 150,
        "severity": "warn",
        "threshold": 100,
    }
    (critical,) = tables[("ops", "events")]["findings"]
    assert (critical["severity"], critical["threshold"]) == ("critical", 1000)


def test_a_value_exactly_at_a_threshold_is_not_a_finding(make_client):
    client = make_client(
        {DATA_FILES: [sample("a", "t", 100)]},
        ICEOBS_DATA_FILES_WARN="100",
        ICEOBS_DATA_FILES_CRITICAL="1000",
    )

    assert overview(client)[("a", "t")]["findings"] == []


def test_tables_with_the_worst_findings_rank_first(make_client):
    client = make_client(
        {DATA_FILES: [sample("a", "ok", 1), sample("a", "warn", 150), sample("a", "bad", 5000)]},
        ICEOBS_DATA_FILES_WARN="100",
        ICEOBS_DATA_FILES_CRITICAL="1000",
    )

    names = [t["table"] for t in client.get("/api/overview").json()["tables"]]

    assert names == ["bad", "warn", "ok"]


def test_liveness_answers(make_client):
    assert make_client({}).get("/healthz").status_code == 200
