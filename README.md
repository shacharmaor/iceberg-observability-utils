# iceberg-observability-utils

Read-only observability for an Iceberg lakehouse (JDBC catalog, S3-compatible storage). See
`CONTEXT.md` for vocabulary, `docs/adr/` for decisions and `.scratch/v1/spec.md` for the v1 spec.

## Proof of concept (tickets 01, 03, 07, 21, 23)

| Component | Path | Status |
|---|---|---|
| Collector | `collector/` | Polls Metadata Pointers, reloads only moved Tables, exports `iceobs_data_files` on `/metrics`, `/healthz`; Signal registry with `ICEOBS_DISABLED_SIGNALS` |
| UI Backend | `ui-backend/` | `/api/overview`: Tables from Prometheus ranked by Finding severity (data file count only) |
| Web UI | `web-ui/` | Overview table (React + Mantine + Vite); `nginx/default.conf.template` for the future image |

```sh
make lint test          # both Python projects, offline
cd web-ui && npm install && npm run build
```

Run by hand: `python -m iceobs_collector` (needs `ICEOBS_CATALOG_URI`) and
`python -m iceobs_ui_backend` (needs `ICEOBS_PROMETHEUS_URL`); `npm run dev` proxies `/api` to
`localhost:8000`.

Test fixtures are restored to `/tmp/iceobs-fixture` per test, because Iceberg metadata holds
absolute paths. Rebuild them with `collector/tools/build_fixture_warehouse.py`.
