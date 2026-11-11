"""Entry point: `python -m iceobs_ui_backend` configures from the process environment."""

import os
import sys

import uvicorn

from iceobs_ui_backend.app import create_app
from iceobs_ui_backend.prometheus import HttpPrometheusClient
from iceobs_ui_backend.settings import Settings, SettingsError


def main() -> None:
    try:
        settings = Settings.from_env(os.environ)
    except SettingsError as error:
        sys.exit(f"configuration error: {error}")
    client = HttpPrometheusClient(settings.prometheus_url, settings.prometheus_token)
    uvicorn.run(
        create_app(settings, client),
        host="0.0.0.0",
        port=int(os.environ.get("ICEOBS_HTTP_PORT", 8000)),
    )


if __name__ == "__main__":
    main()
