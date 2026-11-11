# 01: Collector tracer bullet: data file count on `/metrics`

**What to build:** The Collector starts from an env mapping, reads every Table's Metadata Pointer from the JDBC Catalog database, loads the Tables through PyIceberg, and exports one Signal, the data file count, per Table on `/metrics`. Liveness works. This sets up the Seam A test harness (env mapping + SQLite fixture catalog over a committed local warehouse + controllable clock + parsed exposition text) and the Python tooling (uv, pytest, ruff, `make lint test`).

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Settings are parsed from a plain env mapping into an immutable settings object; missing required values fail at startup with a clear error
- [ ] The Pointer poller returns `(namespace, table, metadata_location)` for every Table from the catalog's `iceberg_tables` table in one query
- [ ] A committed fixture warehouse with at least two Tables loads through PyIceberg's SQL catalog on SQLite
- [ ] Running one cycle exports the data file count for each fixture Table, labelled `namespace` and `table`
- [ ] A liveness endpoint answers while the process runs
- [ ] `make lint` and `make test` pass offline, with no services
