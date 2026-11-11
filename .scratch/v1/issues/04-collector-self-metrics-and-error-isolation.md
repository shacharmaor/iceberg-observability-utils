# 04: Collector self-metrics and per-Table error isolation

**What to build:** A Table that fails to load or compute is flagged without stopping collection for the others. The Collector exports its own status: last successful poll timestamp, poll duration, Tables pending reload, and a per-Table error indicator.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] A broken fixture Table sets its error indicator while the other Tables' Signals still export
- [ ] A broken Table that recovers clears its error indicator
- [ ] Last poll timestamp, poll duration and pending reload count are exported and advance with the controllable clock
