# 24: Findings for every Signal with default thresholds

**What to build:** The UI Backend derives warn and critical Findings for every Signal, using the spec's default thresholds and configurable global thresholds. It handles higher-is-worse and lower-is-worse Signals, computes ages from timestamps, and produces no Findings for Signals absent from Prometheus.

**Blocked by:** 08, 09, 10, 11, 12, 13, 14, 15, 21

**Status:** ready-for-agent

- [ ] Table-driven Seam C cases cover every Signal at, below and above its warn and critical thresholds
- [ ] Ratio Findings (Retained ÷ Live, Orphan ÷ Live) are derived correctly
- [ ] A Signal absent from Prometheus produces no Finding
