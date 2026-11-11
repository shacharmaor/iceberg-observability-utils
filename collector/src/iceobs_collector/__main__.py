"""Entry point: `python -m iceobs_collector` configures from the process environment."""

import os
import sys
import time

from iceobs_collector.collector import Collector
from iceobs_collector.settings import Settings, SettingsError


def main() -> None:
    try:
        settings = Settings.from_env(os.environ)
    except SettingsError as error:
        sys.exit(f"configuration error: {error}")
    collector = Collector(settings)
    collector.serve()
    while True:
        collector.run_cycle()
        time.sleep(settings.poll_interval_seconds)


if __name__ == "__main__":
    main()
