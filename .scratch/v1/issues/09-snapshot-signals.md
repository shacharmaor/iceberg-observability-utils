# 09: Snapshot Signals: count and oldest retained snapshot timestamp

**What to build:** Exports each Table's snapshot count and the timestamp (not the age) of its oldest retained snapshot.

**Blocked by:** 07

**Status:** ready-for-agent

- [ ] A many-snapshots fixture Table exports the expected count and oldest timestamp
- [ ] Values only change when the Table changes, not with wall-clock time
- [ ] Seam B case: a Table with no snapshots
