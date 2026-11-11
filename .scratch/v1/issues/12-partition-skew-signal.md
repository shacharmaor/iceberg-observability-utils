# 12: Partition skew Signal

**What to build:** Exports each Table's partition skew: bytes in its largest partition divided by the median partition's bytes.

**Blocked by:** 07

**Status:** ready-for-agent

- [ ] A skewed-partitions fixture Table exports the expected ratio
- [ ] Seam B cases: an unpartitioned Table and a single-partition Table give a well-defined value
