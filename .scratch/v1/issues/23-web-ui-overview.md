# 23: Web UI Overview page, nginx image and Route

**What to build:** A React + TS + Vite + Mantine app with an Overview page ranking Tables by Findings. It's served by an unprivileged nginx image on port 8080 that proxies `/api` to the UI Backend's Service. The chart gains the Web UI Deployment and a Route. Built from the internal npm mirror, with no remote assets (ADR-0002).

**Blocked by:** 22

**Status:** ready-for-agent

- [ ] Opening the Route in a browser shows the Overview with real Tables
- [ ] `/api` calls go through nginx to the UI Backend
- [ ] The built bundle makes no requests to external hosts
