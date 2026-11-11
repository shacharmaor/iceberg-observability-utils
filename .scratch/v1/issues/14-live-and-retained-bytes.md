# 14: Live Bytes and Retained Bytes

**What to build:** Exports each Table's Live Bytes (data and delete files of the current snapshot) and Retained Bytes (files reachable from any retained snapshot, minus Live files), built on a shared "reachable files" computation that later tickets reuse.

**Blocked by:** 07

**Status:** ready-for-agent

- [ ] A fixture Table whose older snapshots reference replaced files exports Retained Bytes > 0 and the expected Live Bytes
- [ ] A Table with a single snapshot exports Retained Bytes = 0
