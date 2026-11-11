# 27: Namespace view

**What to build:** An API and a page for one Namespace: Live, Retained, Metadata and Orphan Bytes totals, plus its worst Tables by Findings. Orphan Bytes shows as not measured when the Orphan Scan is off.

**Blocked by:** 23, 24

**Status:** ready-for-agent

- [ ] Totals match the sum of the Namespace's Tables in the fake Prometheus
- [ ] With no orphan series, Orphan Bytes shows as not measured rather than 0
