# Read-only by design

The service only observes. It never commits to a Table, never expires snapshots, never compacts, and never deletes objects from storage, including the Orphan Scan, which reports Orphan Bytes but removes nothing. We chose this so the service cannot damage a Table, needs only read credentials for the Catalog and storage, and stays small. Maintenance actions belong in a separate tool that may act on what this service reports.
