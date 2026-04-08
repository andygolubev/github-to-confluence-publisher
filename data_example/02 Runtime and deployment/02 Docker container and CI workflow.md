# Docker container and CI workflow

The repository ships one container image and one GitHub Actions workflow. Together they define the automated publish path that the sample docs are intended to exercise.

![CI and container flow from checkout to publish](/data_images/ci-runtime-flow.svg)

## Container behavior

| Artifact | Purpose |
|---|---|
| `Dockerfile` | Builds a `python:3.14-slim` image, installs `ca-certificates`, installs Python dependencies, and copies the `publisher/` package |
| `publisher/docker_entrypoint.py` | Runs `update-ca-certificates`, then `exec()`s `publisher/main.py` |
| Mounted `/app/data` | Default Markdown root inside the container |
| Mounted `/app/data_images` | Default image root inside the container |

## Workflow stages

1. Check out the repository.
2. Build the publisher image tagged with the current commit SHA.
3. Run the unit test suite inside the container.
4. Run `publisher/test_atlassian_connection.py` when secrets are available.
5. Publish `data_example/` and `data_example_images/` into the configured Confluence space.

## Secrets and branch guards

The workflow skips live Confluence steps on fork pull requests because GitHub does not expose repository secrets there. Unit tests still run because they do not need credentials.

## TLS and custom certificates

The container trusts the system CA store by default. For private Confluence instances or corporate proxies, mount `.crt` files into `/usr/local/share/ca-certificates/custom/` or set `REQUESTS_CA_BUNDLE` or `SSL_CERT_FILE`.

## Local equivalent

```bash
docker run --rm \
  -e CONFLUENCE_URL=... \
  -e CONFLUENCE_SPACE=... \
  -e CONFLUENCE_PARENT_PAGE_ID=... \
  -e CONFLUENCE_LOGIN=... \
  -e CONFLUENCE_API_TOKEN=... \
  -v ./data_example:/app/data:ro \
  -v ./data_example_images:/app/data_images:ro \
  confluence-publisher
```
