## Problem Statement

I run an Iceberg lakehouse with about 500 Tables, a JDBC Catalog on PostgreSQL, and S3-compatible object storage, inside an air-gapped OpenShift environment. Tables degrade quietly. Small Files pile up, snapshots and manifests accumulate, Delete Files build up, and storage grows with bytes that only expired history or failed writes are holding. Nothing breaks, so nobody notices until queries slow down or storage runs out.

I have no single place that tells me which Tables are degrading, how badly, and where the bytes are going. Our existing monitoring system and anything new I build must agree on the numbers. Two views that disagree are worse than one.

## Solution

A read-only observability service made of three workloads:

- **Collector:** watches the Catalog. When a Table's Metadata Pointer moves, it recomputes that Table's Table Health and Storage Footprint Signals and exports them as raw Prometheus metrics. An optional slow Orphan Scan measures Orphan Bytes. It never judges health and never changes anything.
- **UI Backend:** queries the same Prometheus that our external monitoring reads, so both always see the same stored values. It derives Findings by comparing Signals with configurable thresholds.
- **Web UI:** a small React application that ranks Tables by their Findings and lets me drill into Namespaces and individual Tables.

All three are built inside the network from internal mirrors, ship as images in the internal registry, and deploy to OpenShift with a Helm chart. All configuration comes from environment variables.

Vocabulary follows `CONTEXT.md`. Decisions are recorded in ADR-0001 to ADR-0005.

## User Stories

### Scope and configuration

1. As a platform engineer, I want the Collector to watch every Namespace in the Catalog by default, so that new Namespaces are covered without config changes.
2. As a platform engineer, I want a Namespace allow list and deny list, so that I can narrow the Observed Scope to what matters or exclude scratch Namespaces.
3. As a platform engineer, I want to switch each Signal on or off individually, so that expensive Signals don't cost anything when I don't need them.
4. As a platform engineer, I want to switch the Orphan Scan on or off and set its schedule and safety window, so that the heaviest work only runs when and how often I choose.
5. As a platform engineer, I want every setting to come from environment variables set through Kubernetes, so that this service is configured like our other applications.
6. As a platform engineer, I want per-Namespace and per-Table threshold overrides passed as a JSON string in an environment variable, so that I can tune Findings for unusual Tables using a format we already use elsewhere.
7. As a platform engineer, I want invalid configuration (malformed JSON, unknown Signal names, invalid durations) to stop the workload at startup with a clear error, so that I never run with settings I didn't intend.
8. As a platform engineer, I want the poll interval to be configurable, so that I can trade freshness against load on the Catalog database.

### Change detection

9. As a platform engineer, I want the Collector to detect changed Tables by reading every Table's Metadata Pointer from the Catalog database in a single query, so that 500 Tables don't mean 500 loads per cycle.
10. As a platform engineer, I want only Tables whose Metadata Pointer moved to be reloaded, so that the load stays proportional to commit activity.
11. As a platform engineer, I want Tables committing every few minutes to show updated Signals within about one poll interval plus one scrape, so that the numbers are current for hot Tables.
12. As a platform engineer, I want newly registered Tables to be picked up automatically, so that coverage keeps up with the lakehouse.
13. As a platform engineer, I want dropped or renamed Tables to stop being exported, so that stale series don't linger and mislead.
14. As a platform engineer, I want a Table that fails to load or compute to be reported as erroring without stopping collection for the other Tables, so that one broken Table can't blind me to the rest.

### Table Health Signals

15. As a platform engineer, I want each Table's data file count, so that I can see file sprawl.
16. As a platform engineer, I want each Table's average and median data file size, so that I can tell whether files are close to their target size.
17. As a platform engineer, I want each Table's Small File ratio, measured against that Table's own target file size, so that the judgement fits each Table's configuration rather than one global number.
18. As a platform engineer, I want each Table's snapshot count, so that I can spot Tables whose snapshots are never expired.
19. As a platform engineer, I want the timestamp of each Table's oldest retained snapshot, so that I can see how much history the Table keeps.
20. As a platform engineer, I want each Table's manifest count and average entries per manifest, so that I can spot fragmented manifests that slow down query planning.
21. As a platform engineer, I want each Table's Delete File counts split by kind (position deletes, equality deletes, deletion vectors) and its delete-to-data file ratio, so that I can see merge-on-read debt building up.
22. As a platform engineer, I want each Table's metadata file size and metadata log length, so that I can spot metadata bloat.
23. As a platform engineer, I want each Table's partition skew (largest partition bytes divided by median partition bytes), so that I can spot uneven layouts.

### Storage Footprint Signals

24. As a platform engineer, I want each Table's Live Bytes, so that I know what the current state actually costs.
25. As a platform engineer, I want each Table's Retained Bytes, so that I can see what unexpired history costs on top of the current state.
26. As a platform engineer, I want each Table's Metadata Bytes, so that I can see what the metadata layer itself costs.
27. As a platform engineer, I want each Table's Orphan Bytes from the Orphan Scan, so that I can find storage that no snapshot references.
28. As a platform engineer, I want the Orphan Scan to ignore objects younger than the safety window, so that files from commits still in progress are never counted as orphans.
29. As a platform engineer, I want the Orphan Scan to run separately from the Collection Loop, so that a slow storage listing never delays Table Health Signals.
30. As a platform engineer, I want Storage Footprint totals per Namespace, so that I can see which areas of the lakehouse are growing.

### Export and agreement with external monitoring

31. As a platform engineer, I want every Signal exported as a Prometheus metric labelled by Namespace and Table, so that Grafana and our external monitoring can use them directly.
32. As a platform engineer, I want the Collector to export only raw Signals and never Findings, so that alerting stays in our separate monitoring system.
33. As a platform engineer, I want the UI Backend to read Signals from the same Prometheus that our external monitoring reads, so that the UI and our alerts never disagree.
34. As a platform engineer, I want the Collector to export its own status (last successful poll, Tables pending reload, Tables in error, last Orphan Scan time), so that both the UI and our monitoring can tell when the observer itself is unhealthy.
35. As a platform engineer, I want the Collector to report ready only after its first full load is finished, so that Prometheus never stores partial numbers after a restart.

### Findings (UI Backend)

36. As a platform engineer, I want each Signal compared against warn and critical thresholds to produce Findings, so that I don't have to interpret raw numbers myself.
37. As a platform engineer, I want sensible default thresholds out of the box, so that the UI is useful from the first deploy.
38. As a platform engineer, I want Table overrides to take precedence over Namespace overrides, and Namespace overrides over global defaults, so that the most specific setting wins.
39. As a platform engineer, I want each Finding to show the Signal, its current value, the threshold it crossed, and its severity, so that I can understand it at a glance.
40. As a platform engineer, I want disabled Signals to produce no Findings and no empty widgets, so that switching a Signal off is clean.

### Web UI

41. As a platform engineer, I want an Overview that ranks every Table in the Observed Scope by the severity and number of its Findings, so that I know where to look first.
42. As a platform engineer, I want to filter the Overview by Namespace and severity, so that I can focus on my own area.
43. As a platform engineer, I want a Namespace view with Live, Retained, Metadata and Orphan Bytes totals and its worst Tables, so that I can reason about one area at a time.
44. As a platform engineer, I want a Table view showing every enabled Signal next to its thresholds, plus a short history chart for each Signal, so that I can see whether a Table is getting better or worse.
45. As a platform engineer, I want a link from the Table view to the matching Grafana view, so that I can go deeper with the tools we already use.
46. As a platform engineer, I want a Collector status panel (last poll, pending reloads, erroring Tables, last Orphan Scan), so that I can trust what the UI shows.
47. As a platform engineer, I want the UI to say clearly when Prometheus can't be reached, so that I never mistake missing data for healthy Tables.
48. As a platform engineer, I want the Web UI to load no remote assets, so that it works fully inside the air gap.

### Delivery and operations

49. As a platform engineer, I want three images (Collector, UI Backend, Web UI) built inside the network from our PyPI mirror, npm mirror and registry, so that development and builds happen where the system runs.
50. As a platform engineer, I want images that run under OpenShift's default restricted policy (arbitrary non-root UID, group-0-writable directories, ports above 1024), so that no special security exceptions are needed.
51. As a platform engineer, I want a Helm chart that deploys all three workloads, a Route for the Web UI, Secrets for credentials, and scrape configuration for our own Prometheus, so that one command deploys the system.
52. As a platform engineer, I want the Collector to need only read-only credentials for the Catalog database and object storage, so that it is impossible for it to damage a Table.
53. As a platform engineer, I want liveness and readiness probes on every workload, so that OpenShift restarts anything that hangs.
54. As a developer, I want a local dev stack (PostgreSQL as a JDBC Catalog, MinIO as S3, Prometheus) with a seed script, so that I can run the whole system by hand.
55. As a developer, I want the automated test suite to run offline with no services, so that it is fast, deterministic, and runs unchanged in GitLab CI.
56. As a developer, I want `make` targets for lint, test, build and package, with a GitLab CI pipeline calling them, so that local and CI runs behave the same.

## Implementation Decisions

### Architecture

- Three workloads: **Collector**, **UI Backend**, **Web UI**. Each is its own image and Deployment with one replica. Availability means OpenShift restarting a failed pod. A restart costs one full reload of every Table, which is acceptable.
- **Read-only everywhere (ADR-0001).** No commits, snapshot expiry, compaction or object deletion, including by the Orphan Scan.
- **Air-gapped at runtime and build time (ADR-0002).** The only runtime dependencies are the Catalog's PostgreSQL, the object store and Prometheus. There is no telemetry and no external calls.
- **Prometheus is the single source of truth (ADR-0004).** The UI Backend never calls the Collector. It queries the same Prometheus that our external monitoring reads.
- **No database of our own.** The Collector keeps current state in memory and rebuilds it on start. History lives in Prometheus.

### Collector modules

- **Settings:** parses an environment mapping (not the process environment directly, so it can be tested) into a validated, immutable settings object. Invalid settings fail at startup.
- **Pointer poller (ADR-0003):** one query against the JDBC Catalog's `iceberg_tables` table returns `(namespace, table, metadata_location)` for every Table, filtered to the Observed Scope. It compares the result with the last-seen pointers and returns three sets: added, changed and removed Tables. Default interval: 30 s.
- **Table loader:** loads changed Tables through PyIceberg's SQL catalog and collects only the metadata the enabled Signals need. Several Tables load concurrently, up to a configurable limit.
- **Signals:** a registry of named Signals. Each Signal is a pure function from loaded Table metadata to one or more values. It declares the metadata it needs, so disabled Signals cause no reads. v1 Signals:
  - Table Health: data file count; average and median data file size; Small File ratio (against `write.target-file-size-bytes`, falling back to Iceberg's default target when the property isn't set); snapshot count; oldest snapshot timestamp; manifest count; average entries per manifest; Delete File count per kind (position, equality, deletion vector); delete-to-data file ratio; metadata file size; metadata log length; partition skew.
  - Storage Footprint: Live Bytes (data and delete files of the current snapshot); Retained Bytes (files reachable from any retained snapshot minus Live files); Metadata Bytes (metadata files, manifest lists, manifests); Orphan Bytes (Orphan Scan only).
  - Time-based Signals export **timestamps, not ages**, so values only change when a Table changes. The UI computes ages.
- **Exporter:** keeps one current value per (Signal, Namespace, Table) and serves `/metrics`. When a Table is removed, its series are removed too. All metrics share one project prefix and carry `namespace` and `table` labels. Units are bytes, counts, ratios (0–1) and Unix seconds. Exact metric names are not fixed and may change.
- **Self-metrics:** last successful poll timestamp, poll duration, Tables pending reload, Tables in error (a per-Table error indicator), last Orphan Scan start and finish, and Orphan Scan duration.
- **Orphan Scan:** a separate loop on its own schedule, off by default. For each Table in scope, it lists objects under the Table's location, removes every file reachable from any retained snapshot (data, delete and metadata files), and ignores objects younger than the safety window (default 72 h). The remaining bytes become Orphan Bytes. It reports and never deletes. It uses a filesystem abstraction so the same code runs on S3-compatible storage and on the local filesystem.
- **Health endpoints:** liveness on the process, and readiness that turns true only after the first full load finishes.

### Collector configuration (environment variables, `ICEOBS_` prefix)

Catalog database connection (URI and credentials from a Secret); object store endpoint, region and credentials (from a Secret, with path-style access for S3-compatible stores); Namespace allow list and deny list (comma-separated); poll interval; load concurrency; list of disabled Signals; Orphan Scan enabled, schedule interval and safety window.

### UI Backend modules

- **Settings:** the same env-mapping approach. It holds the Prometheus URL, an optional bearer token, global warn and critical thresholds per Signal, and `ICEOBS_FINDING_OVERRIDES`, a JSON string with Namespace-level and Table-level threshold overrides.
- **Prometheus client:** a narrow interface (instant query, range query) with one real HTTP implementation. Tests replace it with a fake.
- **Findings evaluator:** for each Table, takes Signal values and resolves thresholds by precedence (Table override, then Namespace override, then global default). It returns Findings with Signal, value, threshold, severity (warn or critical) and direction (higher-is-worse or lower-is-worse).
- **HTTP API (FastAPI)**, consumed only by the Web UI:
  - Overview: every Table with its Finding counts by severity, sortable and filterable by Namespace and severity.
  - Namespace: Storage Footprint totals and the worst Tables.
  - Table: current values of all enabled Signals, their thresholds, Findings, short history series, and a Grafana link built from a configurable URL template.
  - Collector status: derived from the Collector's self-metrics.
  - Health: liveness, and readiness that reports whether Prometheus is reachable. The API returns an explicit "Prometheus unavailable" error rather than empty results.
- **Default thresholds** (warn / critical):

| Signal | Warn | Critical |
|---|---|---|
| Small File ratio | > 30% | > 60% |
| Average data file size vs target | < 50% | < 20% |
| Snapshot count | > 200 | > 1000 |
| Oldest snapshot age | > 7 d | > 30 d |
| Delete-to-data file ratio | > 10% | > 50% |
| Average entries per manifest | < 20 | < 5 |
| Metadata log length | > 100 | > 500 |
| Retained ÷ Live Bytes | > 1.5× | > 3× |
| Orphan ÷ Live Bytes | > 10% | > 50% |
| Partition skew | > 10× | > 100× |

### Web UI

- React + TypeScript + Vite, with Recharts for charts and Mantine for components. All assets are bundled, with no remote fonts, scripts or CDNs.
- Served by unprivileged nginx on port 8080, which reverse-proxies `/api` to the UI Backend's Service. One Route, one origin, no CORS, and no Route for the UI Backend.
- Views: Overview, Namespace, Table, and the Collector status panel.
- No authentication in v1.

### Tooling and delivery

- Python: uv (through the internal PyPI mirror), pytest, ruff. The Collector and the UI Backend are separate Python projects.
- Frontend: built with the internal npm mirror.
- Base images: **Debian slim** (`python:*-slim` for the Python images, `node:*` as the frontend build stage, `nginxinc/nginx-unprivileged` to serve). Writable directories belong to group 0 and are group-writable, and no fixed UID is assumed.
- Helm chart for OpenShift: three Deployments, Services, a Route for the Web UI, Secrets for credentials, env vars rendered from `values.yaml` (including the overrides JSON), probes, resource requests and limits, and scrape annotations or a `ServiceMonitor` for our own Prometheus. No `runAsUser` anywhere.
- GitLab CI inside the network, calling the `make` targets for lint, test, image build and chart packaging.
- Dev stack (compose): PostgreSQL as a JDBC Catalog, MinIO, Prometheus, and a seed script that creates sample Tables through PyIceberg.

## Testing Decisions

- **What makes a good test:** it drives a component through its public seam and asserts on what is observable from outside: exported metrics, HTTP responses, Findings. It doesn't assert on internal calls or intermediate structures, so the code can be refactored freely.
- **Hermetic suite (ADR-0005):** no running services and no network. Collector tests use PyIceberg's SQL catalog on **SQLite** over a committed **local fixture warehouse**. UI Backend tests use a **fake Prometheus client**.
- **Seam A: one Collector cycle → exposition text** (primary). Build the Collector from an env mapping, the SQLite fixture catalog and a controllable clock. Run cycles, then parse the `/metrics` output. Covers:
  - scenario fixture Tables (Small Files, many snapshots, merge-on-read Delete Files, fragmented manifests, skewed partitions) → expected Signal values
  - Signal toggles and Observed Scope allow/deny → series present or absent
  - change detection: a commit to one fixture Table makes only that Table's Signals change on the next cycle; added Tables appear and removed Tables disappear
  - Orphan Scan: stray files added to a fixture Table's data directory with a safety window of 0 → expected Orphan Bytes; no orphan series when the scan is disabled
  - a broken fixture Table → error self-metric set, other Tables unaffected
  - readiness before and after the first full load
- **Seam B: Signal functions** (lower level, kept on purpose). Unit tests with small hand-built metadata, for edge cases that are awkward to express as fixture Tables: zero files, deletion vectors versus position deletes, a missing target-file-size property, a single partition.
- **Seam C: UI Backend HTTP API with a fake Prometheus.** Start the FastAPI app in-process with canned Signal values. Covers:
  - table-driven Finding rules (Signal value + thresholds + overrides → expected severity or no Finding), including override precedence
  - parsing of threshold env vars and `ICEOBS_FINDING_OVERRIDES` JSON, with invalid JSON rejected
  - Overview, Namespace, Table and Collector status responses
  - the "Prometheus unavailable" behaviour
- **Fixtures:** pre-built and committed, including merge-on-read Delete Files. They are not generated at test time.
- **Not tested automatically:** the Web UI, the Helm chart, a shared metric-name contract, and S3-specific listing behaviour (checked by hand against the dev stack).
- **Prior art:** none yet, since this is a new repository. These seams set the pattern.

## Out of Scope

- Any action that changes a Table or storage: compaction, snapshot expiry, orphan removal, manifest rewrites (ADR-0001).
- Exporting Findings or alerting. Alerting belongs to the separate monitoring system.
- Running more than one replica, leader election, or a persistent store of our own.
- Authentication on the UI (an OpenShift oauth-proxy may come later).
- Editing configuration at runtime through the UI.
- Commit-activity, data-freshness and schema/partition-evolution Signals.
- Query-engine metrics, and Catalogs other than the single JDBC Catalog.
- ArgoCD/GitOps packaging.
- Automated tests for the Web UI and the Helm chart, and a metric-name contract test.

## Further Notes

- Scale assumptions: about 500 Tables; most commit about every 10 minutes, some every few minutes. At a 30 s poll interval, that means about one Table reload per second on average.
- Change detection depends on the JDBC catalog's internal `iceberg_tables` layout (ADR-0003). A PyIceberg or Iceberg upgrade that changes it would break change detection, so pin and test the catalog library version.
- The default thresholds are starting guesses. Expect to tune them against real data after the first deploy.
- Retained Bytes and the Orphan Scan both traverse every retained snapshot's manifests, so they are the most expensive Signals. They can be switched off individually.
- Grafana dashboards are not part of this work. The UI only links to a configurable Grafana URL.
