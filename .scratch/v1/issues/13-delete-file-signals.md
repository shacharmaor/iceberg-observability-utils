# 13: Delete File Signals

**What to build:** Exports each Table's Delete File counts per kind (position deletes, equality deletes, deletion vectors) and its delete-to-data file ratio, using pre-built merge-on-read fixture Tables.

**Blocked by:** 07

**Status:** ready-for-agent

- [ ] A pre-built merge-on-read fixture Table with position and equality deletes exports the expected counts and ratio
- [ ] Seam B case: deletion vectors are counted separately from position deletes
