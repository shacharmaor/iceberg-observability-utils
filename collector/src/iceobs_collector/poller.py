"""Pointer poller: one query returns the Metadata Pointer of every Table (ADR-0003)."""

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
