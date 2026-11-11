"""Signals: pure functions from a loaded Table to values."""

from pyiceberg.table import Table


def data_file_count(table: Table) -> int:
    if table.current_snapshot() is None:
        return 0
    return table.inspect.data_files().num_rows
