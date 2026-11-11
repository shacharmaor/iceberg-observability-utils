# Runs and builds air-gapped

The service is developed, built and deployed inside a network with no internet access. At runtime it makes no outbound calls beyond the Catalog's PostgreSQL, the S3-compatible object store, and Prometheus. All three images are built inside the network against the internal PyPI mirror, npm mirror and container registry, so development happens where the system runs. The Web UI bundles all of its assets: no CDNs, web fonts or remote scripts. Anything that assumes internet access, such as telemetry, update checks or runtime downloads, is out.
