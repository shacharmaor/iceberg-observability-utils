# 17: Collector image

**What to build:** A Debian-slim Collector image built from the internal PyPI mirror that runs under OpenShift's restricted policy: arbitrary non-root UID, group-0-writable directories, port above 1024.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] `make build` produces the image using the mirror's index URL passed as a build argument
- [ ] The container starts and serves `/metrics` when run with a random UID and group 0
- [ ] There are no network calls at build time beyond the internal mirror and registry (ADR-0002)
