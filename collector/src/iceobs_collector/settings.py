"""Collector settings, parsed from an env mapping (not os.environ, so tests can pass their own)."""

from collections.abc import Mapping
from dataclasses import dataclass

from iceobs_collector.signals import REGISTRY

DEFAULT_CATALOG_NAME = "default"
DEFAULT_POLL_INTERVAL_SECONDS = 30
DEFAULT_HTTP_PORT = 8080
DEFAULT_LOAD_CONCURRENCY = 4


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
    load_concurrency: int = DEFAULT_LOAD_CONCURRENCY
    disabled_signals: frozenset[str] = frozenset()
    s3_endpoint: str | None = None
    s3_region: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "Settings":
        catalog_uri = env.get("ICEOBS_CATALOG_URI")
        if not catalog_uri:
            raise SettingsError("ICEOBS_CATALOG_URI is required (JDBC Catalog database URI)")
        disabled = frozenset(
            name.strip()
            for name in env.get("ICEOBS_DISABLED_SIGNALS", "").split(",")
            if name.strip()
        )
        unknown = sorted(disabled - REGISTRY.keys())
        if unknown:
            raise SettingsError(
                f"ICEOBS_DISABLED_SIGNALS names unknown Signal(s) {unknown}; "
                f"known Signals: {sorted(REGISTRY)}"
            )
        return cls(
            catalog_uri=catalog_uri,
            catalog_name=env.get("ICEOBS_CATALOG_NAME", DEFAULT_CATALOG_NAME),
            poll_interval_seconds=_positive_int(
                env, "ICEOBS_POLL_INTERVAL_SECONDS", DEFAULT_POLL_INTERVAL_SECONDS
            ),
            http_port=_positive_int(env, "ICEOBS_HTTP_PORT", DEFAULT_HTTP_PORT),
            load_concurrency=_positive_int(
                env, "ICEOBS_LOAD_CONCURRENCY", DEFAULT_LOAD_CONCURRENCY
            ),
            disabled_signals=disabled,
            s3_endpoint=env.get("ICEOBS_S3_ENDPOINT") or None,
            s3_region=env.get("ICEOBS_S3_REGION") or None,
            s3_access_key_id=env.get("ICEOBS_S3_ACCESS_KEY_ID") or None,
            s3_secret_access_key=env.get("ICEOBS_S3_SECRET_ACCESS_KEY") or None,
        )

    def catalog_properties(self) -> dict[str, str]:
        """PyIceberg FileIO properties for S3-compatible storage (path-style addressing)."""
        configured = {
            "s3.endpoint": self.s3_endpoint,
            "s3.region": self.s3_region,
            "s3.access-key-id": self.s3_access_key_id,
            "s3.secret-access-key": self.s3_secret_access_key,
        }
        properties = {key: value for key, value in configured.items() if value}
        if properties:
            properties["s3.force-virtual-addressing"] = "false"
        return properties
