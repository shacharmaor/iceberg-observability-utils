# 02: GitLab CI runs lint and tests

**What to build:** A GitLab CI pipeline, inside the network, that calls the `make` targets for lint and test against the internal PyPI mirror, so every push is checked the same way as a local run.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] The pipeline installs dependencies through uv from the internal PyPI mirror (index URL from a CI variable)
- [ ] Lint and test jobs call `make lint` and `make test` and fail the pipeline on failure
- [ ] The pipeline needs no service containers
