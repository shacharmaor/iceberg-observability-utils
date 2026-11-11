# 31: Explicit "Prometheus unavailable" handling

**What to build:** When Prometheus can't be reached, the UI Backend returns an explicit error and reports not-ready, and the Web UI shows a clear banner instead of empty data that could look like healthy Tables.

**Blocked by:** 23

**Status:** ready-for-agent

- [ ] With the fake Prometheus failing, every API returns the explicit unavailable error rather than empty results
- [ ] Readiness reports Prometheus as unreachable
- [ ] The page shows the banner
