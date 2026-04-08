# Confluence publisher — python:3.14-slim, TLS via system CA store.
#
# Configuration is only via environment variables (no config.yaml in the image).
# Required: CONFLUENCE_URL, CONFLUENCE_SPACE, CONFLUENCE_PARENT_PAGE_ID
# Credentials: CONFLUENCE_LOGIN, CONFLUENCE_API_TOKEN
# Optional: BANNER_REPO_URL, BANNER_PROJECT_NAME, PUBLISHER_MARKDOWN_ROOT,
#   PUBLISHER_IMAGES_ROOT, PUBLISHER_PROPERTY_KEY
# Mount content: -v ./data:/app/data:ro -v ./data_images:/app/data_images:ro
# Custom CA: REQUESTS_CA_BUNDLE / SSL_CERT_FILE or mount under
#   /usr/local/share/ca-certificates/custom/ and run update-ca-certificates (see docs).

FROM python:3.14-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY publisher/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY publisher /app/publisher

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "/app/publisher/docker_entrypoint.py"]
