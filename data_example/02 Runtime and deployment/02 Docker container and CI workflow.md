# Docker container and CI workflow

The repository ships one container image and one GitHub Actions workflow. Together they define the automated publish path that the sample docs are intended to exercise.

![CI and container flow from checkout to publish](/data_images/ci-runtime-flow.svg)

## Container behavior

| Artifact | Purpose |
|---|---|
| `Dockerfile` | Builds a `python:3.14-slim` image, installs Python dependencies, creates a non-root `publisher` user, and copies the `publisher/` package |
| Mounted `/app/data` | Default Markdown root inside the container |
| Mounted `/app/data_images` | Default image root inside the container |

## Container security

The image follows Docker security best practices:

- **Non-root user** — runs as `publisher` (UID 10001), never as root
- **Read-only filesystem** — the container needs no writable layers; use `--read-only --tmpfs /tmp`
- **Dropped capabilities** — CI runs with `--cap-drop=ALL --security-opt=no-new-privileges`
- **No secrets in the image** — credentials are passed via environment variables at runtime
- **Minimal base** — `python:3.14-slim` with only `ca-certificates` added

## Workflow stages

1. Check out the repository.
2. Build the publisher image tagged with the current commit SHA.
3. Run the unit test suite inside the container.
4. Run `publisher/test_atlassian_connection.py` when secrets are available.
5. Publish `data_example/` and `data_example_images/` into the configured Confluence space.

## Secrets and branch guards

The workflow skips live Confluence steps on fork pull requests because GitHub does not expose repository secrets there. Unit tests still run because they do not need credentials.

## TLS and custom certificates

The container trusts the system CA store by default. For private Confluence instances or corporate proxies, mount a PEM file and set the `REQUESTS_CA_BUNDLE` or `SSL_CERT_FILE` environment variable:

```bash
-v ./my-ca.crt:/certs/my-ca.crt:ro -e REQUESTS_CA_BUNDLE=/certs/my-ca.crt
```

## Local equivalent

```bash
docker run --rm \
  --read-only --tmpfs /tmp \
  --security-opt=no-new-privileges --cap-drop=ALL \
  -e CONFLUENCE_URL=... \
  -e CONFLUENCE_SPACE=... \
  -e CONFLUENCE_PARENT_PAGE_ID=... \
  -e CONFLUENCE_LOGIN=... \
  -e CONFLUENCE_API_TOKEN=... \
  -v ./data_example:/app/data:ro \
  -v ./data_example_images:/app/data_images:ro \
  confluence-publisher
```
