"""UI Backend settings, parsed from an env mapping."""

from collections.abc import Mapping
from dataclasses import dataclass

# PoC guesses for the data file count; the spec's threshold table has no entry for it.
DEFAULT_DATA_FILES_WARN = 1_000
DEFAULT_DATA_FILES_CRITICAL = 10_000


class SettingsError(ValueError):
    """Raised at startup when the configuration is missing or invalid."""


def _number(env: Mapping[str, str], name: str, default: float) -> float:
    raw = env.get(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        raise SettingsError(f"{name} must be a number, got {raw!r}") from None


@dataclass(frozen=True)
class Settings:
    prometheus_url: str
    prometheus_token: str | None = None
    data_files_warn: float = DEFAULT_DATA_FILES_WARN
    data_files_critical: float = DEFAULT_DATA_FILES_CRITICAL

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "Settings":
        url = env.get("ICEOBS_PROMETHEUS_URL")
        if not url:
            raise SettingsError("ICEOBS_PROMETHEUS_URL is required")
        warn = _number(env, "ICEOBS_DATA_FILES_WARN", DEFAULT_DATA_FILES_WARN)
        critical = _number(env, "ICEOBS_DATA_FILES_CRITICAL", DEFAULT_DATA_FILES_CRITICAL)
        if warn >= critical:
            raise SettingsError(
                "ICEOBS_DATA_FILES_WARN must be lower than ICEOBS_DATA_FILES_CRITICAL, "
                f"got {warn} and {critical}"
            )
        return cls(
            prometheus_url=url,
            prometheus_token=env.get("ICEOBS_PROMETHEUS_TOKEN") or None,
            data_files_warn=warn,
            data_files_critical=critical,
        )
