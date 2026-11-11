# 07: Signal registry and per-Signal toggles

**What to build:** Signals become named entries in a registry. Each declares the metadata it needs, and any Signal can be switched off through settings. A disabled Signal is not exported and causes no metadata reads. An unknown Signal name in settings fails at startup.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] The data file count is moved into the registry as the first Signal
- [ ] Disabling a Signal removes its series from `/metrics`
- [ ] Metadata needed only by disabled Signals is not read
- [ ] An unknown Signal name fails startup with a clear error
