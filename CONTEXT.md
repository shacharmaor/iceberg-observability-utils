# Iceberg Observability

A read-only service that watches an Iceberg lakehouse (JDBC catalog, S3-compatible storage) and reports on the health and storage footprint of its tables.

## Language

### Lakehouse structure

**Catalog**:
The single JDBC catalog that registers every Namespace and Table being observed.
_Avoid_: Database, metastore

**Namespace**:
A named grouping of Tables inside the Catalog.
_Avoid_: Database, schema

**Table**:
An Iceberg table registered in the Catalog, identified by `namespace.name`.

**Metadata Pointer**:
The location of a Table's current metadata file, as recorded in the Catalog. A Table has changed exactly when its Metadata Pointer has moved.
_Avoid_: Version, revision

**Observed Scope**:
The set of Namespaces the service watches: every Namespace in the Catalog, narrowed by an allow list and a deny list.

### Concerns

**Table Health**:
How far a Table's physical layout (files, snapshots, manifests, delete files) has drifted from a state that is cheap to read and plan.

**Storage Footprint**:
The bytes a Table occupies in object storage, broken down by why those bytes are still there.

### Measurement

**Signal**:
One named, measurable property of a Table, such as small-file ratio or Retained Bytes. Each Signal can be switched on or off.
_Avoid_: Metric (reserve for the exported Prometheus series), KPI, stat

**Small File**:
A data file smaller than its Table's own target file size.

**Delete File**:
A file that marks rows of data files as deleted without rewriting them: position deletes, equality deletes, or deletion vectors.

**Live Bytes**:
Bytes of data and delete files referenced by a Table's current snapshot.

**Retained Bytes**:
Bytes of data and delete files referenced only by older, unexpired snapshots.

**Metadata Bytes**:
Bytes of a Table's metadata files, manifest lists and manifests.

**Orphan Bytes**:
Bytes under a Table's location that no snapshot references and that are older than the safety window.

**Finding**:
A judgement, made only by the UI, that a Signal has crossed its configured threshold for a Table. Findings are never exported.
_Avoid_: Alert, issue, violation

### Components

**Collector**:
The workload that reads the Catalog and object storage, computes Signals, and exports them as Prometheus metrics. It makes no judgements.

**UI Backend**:
The workload that queries Signals from Prometheus, derives Findings, and serves them to the Web UI.
_Avoid_: API server, collector API

**Web UI**:
The browser application that presents Signals and Findings. It talks only to the UI Backend.
_Avoid_: Dashboard (reserve for Grafana), frontend

**UI**:
The UI Backend and the Web UI together.

### Collection

**Collection Loop**:
The continuous process that detects moved Metadata Pointers and recomputes the enabled Signals for those Tables.

**Orphan Scan**:
The separate, slow, optionally enabled process that lists object storage to compute Orphan Bytes.
