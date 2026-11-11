# 06: Observed Scope with Namespace allow and deny lists

**What to build:** By default the Collector watches every Namespace. Comma-separated allow and deny lists from settings narrow the Observed Scope. Out-of-scope Tables are never loaded and never exported.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] With no lists set, every fixture Namespace is exported
- [ ] An allow list exports only the listed Namespaces
- [ ] A deny list excludes the listed Namespaces, and deny wins over allow
- [ ] Out-of-scope Tables are never loaded
