# 29: Table view history charts and Grafana link

**What to build:** The Table view shows a short history chart per Signal from Prometheus range queries, and a link to Grafana built from a configurable URL template.

**Blocked by:** 28

**Status:** ready-for-agent

- [ ] The history API returns a range series per Signal from the fake Prometheus
- [ ] The Grafana link is built from the template using the Namespace and Table
- [ ] With no template configured, no link is shown
