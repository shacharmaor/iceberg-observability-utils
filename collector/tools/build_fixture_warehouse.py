"""Build the committed fixture warehouse used by the hermetic test suite.

Run manually (`uv run python tools/build_fixture_warehouse.py`) only when the fixtures need to
change; the result is committed. Iceberg metadata holds absolute paths, so the warehouse is built
at the canonical location the test harness restores it to.
"""

import shutil
import sys
from pathlib import Path

import pyarrow as pa
from pyiceberg.catalog.sql import SqlCatalog

CANONICAL_ROOT = Path("/tmp/iceobs-fixture")
COMMITTED = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "warehouse"

SCHEMA = pa.schema([("id", pa.int64()), ("payload", pa.string())])


def batch(start: int, rows: int) -> pa.Table:
    return pa.table(
        {"id": list(range(start, start + rows)), "payload": ["x"] * rows}, schema=SCHEMA
    )


def main() -> None:
    shutil.rmtree(CANONICAL_ROOT, ignore_errors=True)
    CANONICAL_ROOT.mkdir(parents=True)
    catalog = SqlCatalog(
        "default",
        uri=f"sqlite:///{CANONICAL_ROOT}/catalog.db",
        warehouse=f"file://{CANONICAL_ROOT}/warehouse",
    )
    catalog.create_namespace("sales")
    catalog.create_namespace("ops")
    orders = catalog.create_table("sales.orders", SCHEMA)
    for start in (0, 10, 20):  # three appends -> three data files
        orders.append(batch(start, 10))
    events = catalog.create_table("ops.events", SCHEMA)
    for start in (0, 5):  # two appends -> two data files
        events.append(batch(start, 5))
    catalog.engine.dispose()

    shutil.rmtree(COMMITTED, ignore_errors=True)
    shutil.copytree(CANONICAL_ROOT, COMMITTED)
    print(f"fixture warehouse written to {COMMITTED}", file=sys.stderr)


if __name__ == "__main__":
    main()
