# 30: Collector status panel

**What to build:** The UI shows the Collector's last poll, pending reloads, erroring Tables and last Orphan Scan, all read from the Collector's self-metrics in Prometheus, so I can tell whether to trust what I see.

**Blocked by:** 04, 23

**Status:** ready-for-agent

- [ ] The status API reflects the self-metrics in the fake Prometheus
- [ ] A stale last poll (older than a configurable threshold) is flagged
- [ ] Erroring Tables are listed
