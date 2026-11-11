# 21: UI Backend tracer bullet: Overview with one Finding

**What to build:** The UI Backend (FastAPI) reads settings from an env mapping, queries Prometheus through a narrow client interface, and serves an Overview API listing every Table with Findings for one Signal (data file count) against a global threshold. This sets up the Seam C harness: the app runs in-process with a fake Prometheus client (ADR-0004, ADR-0005).

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] The Overview API returns every Table found in Prometheus, with its Finding severity for the one Signal
- [ ] Tests use a fake Prometheus client and need no services
- [ ] Prometheus URL and optional bearer token come from settings
