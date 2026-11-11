# 19: Dev stack with PostgreSQL, MinIO and Prometheus

**What to build:** A compose dev stack (PostgreSQL as a JDBC Catalog, MinIO as S3-compatible storage, Prometheus scraping the Collector) plus a seed script that creates sample Tables through PyIceberg, so the whole system can be run by hand inside the network.

**Blocked by:** 17

**Status:** ready-for-agent

- [ ] One command brings the stack up and seeds Tables
- [ ] Prometheus shows the Collector's Signals for the seeded Tables
- [ ] All images come from the internal registry
