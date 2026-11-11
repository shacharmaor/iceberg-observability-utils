# 16: Orphan Scan

**What to build:** A separate loop, off by default, runs on its own schedule. It lists each in-scope Table's location, subtracts every reachable file, ignores objects younger than the safety window (default 72 h), and exports Orphan Bytes plus its own start, finish and duration self-metrics. It never deletes anything (ADR-0001). It goes through a filesystem abstraction so it works on S3-compatible storage and on local files.

**Blocked by:** 04, 15

**Status:** ready-for-agent

- [ ] Stray files added to a fixture Table's data directory, with a safety window of 0, produce the expected Orphan Bytes
- [ ] With the default window, freshly added stray files are not counted
- [ ] With the scan disabled, no orphan series are exported
- [ ] A slow scan doesn't delay the Collection Loop
