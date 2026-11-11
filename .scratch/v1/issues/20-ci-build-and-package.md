# 20: CI builds images and packages the chart

**What to build:** The GitLab CI pipeline builds and pushes images to the internal registry and packages the Helm chart as a `.tgz` artifact, through `make build` and `make package`.

**Blocked by:** 02, 18

**Status:** ready-for-agent

- [ ] Pipelines on the main branch push tagged images to the internal registry
- [ ] The packaged chart is available as a pipeline artifact
