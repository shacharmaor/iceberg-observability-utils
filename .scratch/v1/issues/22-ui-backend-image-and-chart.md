# 22: UI Backend image and chart Deployment

**What to build:** A Debian-slim UI Backend image (OpenShift-compatible) and a Deployment and Service in the Helm chart, pointed at our own Prometheus. No Route for the UI Backend.

**Blocked by:** 18, 21

**Status:** ready-for-agent

- [ ] The UI Backend runs on OpenShift and its Overview API returns data from our Prometheus
- [ ] Settings come from `values.yaml`, with the bearer token from a Secret
