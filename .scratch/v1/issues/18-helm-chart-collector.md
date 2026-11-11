# 18: Helm chart deploys the Collector to OpenShift

**What to build:** A Helm chart with the Collector Deployment (one replica), a Service, Secrets for catalog and object store credentials, env vars rendered from `values.yaml`, liveness and readiness probes, resources, and scrape annotations or a `ServiceMonitor` for our own Prometheus. No `runAsUser`.

**Blocked by:** 17

**Status:** ready-for-agent

- [ ] `helm install` on OpenShift brings the Collector up under the default restricted policy
- [ ] Our Prometheus scrapes the Collector's `/metrics`
- [ ] Every Collector setting can be set through `values.yaml`
