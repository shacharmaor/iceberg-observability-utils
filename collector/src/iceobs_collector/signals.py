"""Signals: a registry of named, pure functions from loaded Table metadata to a value.

Each Signal declares the metadata it needs, so a disabled Signal causes no reads.
"""

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from pyiceberg.table import Table

Metadata = Mapping[str, Any]


def _read_data_files(table: Table) -> Any:
    if table.current_snapshot() is None:
        return None
    return table.inspect.data_files()


# Each kind of metadata is read once per Table load, and only if an enabled Signal needs it.
READERS: dict[str, Callable[[Table], Any]] = {"data_files": _read_data_files}


@dataclass(frozen=True)
class Signal:
    name: str
    metric_name: str
    description: str
    needs: tuple[str, ...]
    compute: Callable[[Metadata], float]


def _data_file_count(metadata: Metadata) -> float:
    data_files = metadata["data_files"]
    return 0 if data_files is None else data_files.num_rows


REGISTRY: dict[str, Signal] = {
    signal.name: signal
    for signal in [
        Signal(
            name="data_file_count",
            metric_name="iceobs_data_files",
            description="Number of data files in the Table's current snapshot",
            needs=("data_files",),
            compute=_data_file_count,
        ),
    ]
}


def read_metadata(table: Table, signals: Iterable[Signal]) -> Metadata:
    needed = {need for signal in signals for need in signal.needs}
    return {need: READERS[need](table) for need in needed}
