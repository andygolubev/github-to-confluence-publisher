"""
Smoke test: Confluence REST API reachable with configured credentials.

Run from repo root:
  python3 publisher/test_atlassian_connection.py

Requires CONFLUENCE_LOGIN and CONFLUENCE_API_TOKEN (or CONFLUENCE_PASSWORD).
Connection targets come from CONFLUENCE_URL, CONFLUENCE_SPACE, and
CONFLUENCE_PARENT_PAGE_ID (or from publisher/config/config.yaml when present locally).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure publisher/ is on path when invoked as a file path
_PUBLISHER_ROOT = Path(__file__).resolve().parent
if str(_PUBLISHER_ROOT) not in sys.path:
    sys.path.insert(0, str(_PUBLISHER_ROOT))

import requests
from requests.auth import HTTPBasicAuth

from config.getconfig import getConfig


def main() -> int:
    login = (os.environ.get("CONFLUENCE_LOGIN") or "").strip()
    token = (
        os.environ.get("CONFLUENCE_API_TOKEN")
        or os.environ.get("CONFLUENCE_PASSWORD")
        or ""
    ).strip()
    if not login or not token:
        missing = []
        if not login:
            missing.append("CONFLUENCE_LOGIN (secret: confluence_login)")
        if not token:
            missing.append(
                "CONFLUENCE_API_TOKEN or CONFLUENCE_PASSWORD "
                "(secrets: confluence_api_token and/or confluence_password)"
            )
        print(
            "error: missing credentials — " + "; ".join(missing),
            file=sys.stderr,
        )
        print(
            "note: pull_request workflows from forks do not receive repository secrets; "
            "use a same-repo branch or push to main to run Confluence steps.",
            file=sys.stderr,
        )
        return 1

    cfg = getConfig()
    base = cfg["confluence_url"].rstrip("/") + "/"
    space_key = str(cfg["confluence_space"]).strip()
    auth = HTTPBasicAuth(login, token)

    r = requests.get(
        base + f"space/{space_key}",
        auth=auth,
        timeout=30,
    )
    if not r.ok:
        print(f"error: GET space/{space_key} -> {r.status_code}", file=sys.stderr)
        print(r.text[:500], file=sys.stderr)
        return 1

    r2 = requests.get(
        base + "search",
        params={
            "cql": f'type=page and space="{space_key}"',
            "limit": 1,
        },
        auth=auth,
        timeout=30,
    )
    if not r2.ok:
        print(f"error: GET search -> {r2.status_code}", file=sys.stderr)
        print(r2.text[:500], file=sys.stderr)
        return 1

    print("ok: Confluence API reachable")
    print(f"    site: {base}")
    print(f"    space: {space_key} ({r.json().get('name', '')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
