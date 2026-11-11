# 05: Readiness only after the first full load

**What to build:** The Collector reports not-ready until every Table in scope has loaded once, so Prometheus never scrapes partial numbers after a restart.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] Readiness is false before the first full load completes and true afterwards
- [ ] Tables that error count as loaded for readiness, so one broken Table can't keep the Collector unready
