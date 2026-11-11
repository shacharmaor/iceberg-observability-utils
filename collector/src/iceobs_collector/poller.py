"""Pointer poller: one query returns the Metadata Pointer of every Table (ADR-0003)."""

from collections.abc import Iterable
from typing import NamedTuple

from sqlalchemy import create_engine, text


class TablePointer(NamedTuple):
    namespace: str
    table: str
    metadata_location: str


_POINTER_QUERY = text(
    "SELECT table_namespace, table_name, metadata_location FROM iceberg_tables "
    "WHERE catalog_name = :catalog_name AND metadata_location IS NOT NULL"
)


def poll_pointers(catalog_uri: str, catalog_name: str) -> list[TablePointer]:
    engine = create_engine(catalog_uri)
    try:
        with engine.connect() as connection:
            rows = connection.execute(_POINTER_QUERY, {"catalog_name": catalog_name}).all()
    finally:
        engine.dispose()
    return [TablePointer(row[0], row[1], row[2]) for row in rows]


class PointerDiff(NamedTuple):
    added: set[tuple[str, str]]
    changed: set[tuple[str, str]]
    removed: set[tuple[str, str]]

    @property
    def to_reload(self) -> set[tuple[str, str]]:
        return self.added | self.changed


def diff_pointers(
    last_seen: dict[tuple[str, str], str], current: Iterable[TablePointer]
) -> PointerDiff:
    """Compare the last-seen Metadata Pointers with the current ones."""
    now = {(p.namespace, p.table): p.metadata_location for p in current}
    return PointerDiff(
        added=now.keys() - last_seen.keys(),
        changed={key for key in now.keys() & last_seen.keys() if now[key] != last_seen[key]},
        removed=last_seen.keys() - now.keys(),
    )
