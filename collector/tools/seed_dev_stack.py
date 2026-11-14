"""Seed sample Tables into the dev stack's catalog through PyIceberg.

Configured with the Collector's own env vars (ICEOBS_CATALOG_URI, ICEOBS_S3_*) plus
ICEOBS_WAREHOUSE (default s3://warehouse/). Idempotent: Tables that already exist are skipped.
"""

import os
import sys

import pyarrow as pa
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.exceptions import NamespaceAlreadyExistsError, TableAlreadyExistsError

from iceobs_collector.settings import Settings

SCHEMA = pa.schema([("id", pa.int64()), ("payload", pa.string())])

# (namespace, table, number of single-row appends -> that many small data files)
SAMPLE_TABLES = [
    ("sales", "orders", 3),
    ("sales", "returns", 12),
    ("ops", "events", 30),
    ("ops", "heartbeats", 1),
]


def seed(catalog: SqlCatalog) -> None:
    for namespace, name, appends in SAMPLE_TABLES:
        try:
            catalog.create_namespace(namespace)
        except NamespaceAlreadyExistsError:
            pass
        try:
            table = catalog.create_table(f"{namespace}.{name}", SCHEMA)
        except TableAlreadyExistsError:
            print(f"{namespace}.{name}: exists, skipped")
            continue
        for i in range(appends):
            table.append(pa.table({"id": [i], "payload": ["x"]}, schema=SCHEMA))
        print(f"{namespace}.{name}: created with {appends} data files")


def main() -> None:
    settings = Settings.from_env(os.environ)
    catalog = SqlCatalog(
        settings.catalog_name,
        uri=settings.catalog_uri,
        warehouse=os.environ.get("ICEOBS_WAREHOUSE", "s3://warehouse/"),
        **settings.catalog_properties(),
    )
    seed(catalog)
    print("seed complete", file=sys.stderr)


if __name__ == "__main__":
    main()
