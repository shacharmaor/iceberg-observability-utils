# 25: Finding threshold overrides from JSON

**What to build:** `ICEOBS_FINDING_OVERRIDES` holds a JSON string with Namespace-level and Table-level threshold overrides. Precedence is Table, then Namespace, then global. Invalid JSON or unknown Signal names stop the UI Backend at startup with a clear error.

**Blocked by:** 24

**Status:** ready-for-agent

- [ ] Table-driven cases show that each level of precedence wins as specified
- [ ] Malformed JSON and unknown Signal names fail startup
