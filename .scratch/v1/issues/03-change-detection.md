# 03: Change detection reloads only Tables whose Metadata Pointer moved

**What to build:** On each poll the Collector compares Metadata Pointers with the last-seen ones. It reloads only changed Tables, loads newly registered Tables, and drops removed Tables' series (ADR-0003). The poll interval comes from settings (default 30 s). Loads run concurrently up to a configurable limit.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] A commit to one fixture Table between two cycles changes only that Table's Signals; other Tables are not reloaded
- [ ] A Table registered between cycles appears on the next cycle
- [ ] A Table dropped between cycles has no series on the next cycle
- [ ] Poll interval and load concurrency are configurable
