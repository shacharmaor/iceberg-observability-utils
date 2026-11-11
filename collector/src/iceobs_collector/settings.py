"""Collector settings, parsed from an env mapping (not os.environ, so tests can pass their own)."""

from collections.abc import Mapping
from dataclasses import dataclass

DEFAULT_CATALOG_NAME = "default"
DEFAULT_POLL_INTERVAL_SECONDS = 30
DEFAULT_HTTP_PORT = 8080


class SettingsError(ValueError):
    """Raised at startup when the configuration is missing or invalid."""


def _positive_int(env: Mapping[str, str], name: str, default: int) -> int:
    raw = env.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        raise SettingsError(f"{name} must be a positive integer, got {raw!r}") from None
    if value <= 0:
        raise SettingsError(f"{name} must be a positive integer, got {raw!r}")
    return value


@dataclass(frozen=True)
class Settings:
    catalog_uri: str
    catalog_name: str = DEFAULT_CATALOG_NAME
    poll_interval_seconds: int = DEFAULT_POLL_INTERVAL_SECONDS
    http_port: int = DEFAULT_HTTP_PORT

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "Settings":
        catalog_uri = env.get("ICEOBS_CATALOG_URI")
        if not catalog_uri:
            raise SettingsError("ICEOBS_CATALOG_URI is required (JDBC Catalog database URI)")
        return cls(
            catalog_uri=catalog_uri,
            catalog_name=env.get("ICEOBS_CATALOG_NAME", DEFAULT_CATALOG_NAME),
            poll_interval_seconds=_positive_int(
                env, "ICEOBS_POLL_INTERVAL_SECONDS", DEFAULT_POLL_INTERVAL_SECONDS
            ),
            http_port=_positive_int(env, "ICEOBS_HTTP_PORT", DEFAULT_HTTP_PORT),
        )
