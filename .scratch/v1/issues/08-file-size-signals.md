# 08: File size Signals: average and median size, Small File ratio

**What to build:** Exports each Table's average and median data file size, and its Small File ratio measured against the Table's own `write.target-file-size-bytes`, falling back to Iceberg's default target when the property isn't set.

**Blocked by:** 07

**Status:** ready-for-agent

- [ ] A small-files fixture Table exports the expected average, median and ratio
- [ ] Seam B cases: a Table with zero files, a Table without the target property, a Table with a custom target
- [ ] Each Signal can be switched off independently
