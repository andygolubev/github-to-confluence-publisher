"""Container entrypoint: refresh CA bundle, then run the publisher main module."""

from __future__ import annotations

import logging
import os
import subprocess
import sys


def main() -> None:
    # Pick up CAs under custom/ if mounted.
    result = subprocess.run(["update-ca-certificates"], check=False)
    if result.returncode != 0:
        logging.warning(
            "update-ca-certificates exited with code %d — CA bundle may be stale",
            result.returncode,
        )
    os.execv(
        sys.executable,
        [sys.executable, os.path.join(os.path.dirname(__file__), "main.py"), *sys.argv[1:]],
    )


if __name__ == "__main__":
    main()
