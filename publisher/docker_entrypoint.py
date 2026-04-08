"""Container entrypoint: refresh CA bundle, then run the publisher main module."""

from __future__ import annotations

import os
import subprocess
import sys


def main() -> None:
    # Match previous shell entrypoint: pick up CAs under custom/ if mounted.
    subprocess.run(["update-ca-certificates"], check=False)
    os.execv(
        sys.executable,
        [sys.executable, os.path.join(os.path.dirname(__file__), "main.py"), *sys.argv[1:]],
    )


if __name__ == "__main__":
    main()
