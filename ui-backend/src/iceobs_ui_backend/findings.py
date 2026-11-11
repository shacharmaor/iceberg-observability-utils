"""Findings: a Signal value compared with its thresholds."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    signal: str
    value: float
    severity: str  # "warn" | "critical"
    threshold: float


def evaluate_higher_is_worse(
    signal: str, value: float, warn: float, critical: float
) -> Finding | None:
    """A value strictly above a threshold crosses it; critical wins over warn."""
    if value > critical:
        return Finding(signal, value, "critical", critical)
    if value > warn:
        return Finding(signal, value, "warn", warn)
    return None
