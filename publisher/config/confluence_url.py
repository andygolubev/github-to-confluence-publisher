"""Normalize Confluence REST API base URLs."""

from __future__ import annotations

from urllib.parse import urlparse


def normalize_confluence_rest_api_url(url: str) -> str:
    """
    Return a base URL suitable for joining paths like ``content/`` and ``search``.

    Cloud sites often use ``https://<site>.atlassian.net/wiki/rest/api/``.
    A frequent mistake is setting the wiki space root (``.../wiki``) or site root,
    which returns HTML and surfaces as "Page Not Found" in the response body.
    """
    raw = (url or "").strip()
    if not raw:
        return raw

    parsed = urlparse(raw)
    if not parsed.scheme or not parsed.netloc:
        return raw if raw.endswith("/") else raw + "/"

    path = (parsed.path or "").rstrip("/")
    lower_path = path.lower()
    netloc_lower = parsed.netloc.lower()

    if "/rest/api" in lower_path:
        base = raw.split("#", 1)[0].rstrip("/")
        return base + "/"

    # Atlassian Cloud: REST API is always under /wiki/rest/api/ (not /wiki/spaces/...).
    if "atlassian.net" in netloc_lower:
        return f"{parsed.scheme}://{parsed.netloc}/wiki/rest/api/"

    # Confluence Server / Data Center: often .../confluence/rest/api/
    if lower_path.endswith("/confluence"):
        return f"{parsed.scheme}://{parsed.netloc}{path}/rest/api/"

    base = raw.split("#", 1)[0].rstrip("/")
    return base + "/"
