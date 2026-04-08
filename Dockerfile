# Confluence publisher — python:3.14-slim, non-root, read-only filesystem.
#
# Configuration is only via environment variables (no config.yaml in the image).
# Required: CONFLUENCE_URL, CONFLUENCE_SPACE, CONFLUENCE_PARENT_PAGE_ID
# Credentials: CONFLUENCE_LOGIN, CONFLUENCE_API_TOKEN
# Optional: BANNER_REPO_URL, BANNER_PROJECT_NAME, PUBLISHER_MARKDOWN_ROOT,
#   PUBLISHER_IMAGES_ROOT, PUBLISHER_PROPERTY_KEY
# Mount content: -v ./data:/app/data:ro -v ./data_images:/app/data_images:ro
# Custom CA: set REQUESTS_CA_BUNDLE or SSL_CERT_FILE to a mounted PEM file path
#   (e.g. -v ./my-ca.crt:/certs/my-ca.crt:ro -e REQUESTS_CA_BUNDLE=/certs/my-ca.crt)

FROM python:3.14-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10001 publisher \
    && useradd --uid 10001 --gid publisher --shell /bin/false --no-create-home publisher

WORKDIR /app

COPY publisher/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY --chown=publisher:publisher publisher /app/publisher

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER publisher

ENTRYPOINT ["python", "/app/publisher/main.py"]
