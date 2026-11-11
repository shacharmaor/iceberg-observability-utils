from iceobs_collector.poller import TablePointer, poll_pointers


def test_returns_every_tables_pointer_in_one_query(env):
    pointers = poll_pointers(env["ICEOBS_CATALOG_URI"], "default")

    assert {(p.namespace, p.table) for p in pointers} == {("sales", "orders"), ("ops", "events")}
    for pointer in pointers:
        assert isinstance(pointer, TablePointer)
        assert pointer.metadata_location.endswith(".metadata.json")
        assert f"/{pointer.namespace}/{pointer.table}/metadata/" in pointer.metadata_location


def test_ignores_tables_registered_under_another_catalog_name(env):
    assert poll_pointers(env["ICEOBS_CATALOG_URI"], "someone-else") == []
