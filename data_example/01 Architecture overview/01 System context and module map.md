# System context and module map

The publisher is a short-lived Python CLI that turns a repository folder tree into Confluence pages beneath one existing parent page. It does not run a background service and it does not store local state between runs.

![Publisher modules, repo inputs, and Confluence target](/data_images/publisher-system-map.svg)

## Runtime boundary

| Layer | Responsibility |
|---|---|
| Git working tree | Holds Markdown files and image files that act as the source of truth |
| Publisher process | Loads config, talks to Confluence, rewrites images, upserts pages, and prunes stale ids |
| Confluence REST API | Stores pages, attachments, and content properties |
| GitHub Actions and Docker | Provide the execution environment for automated runs |

## Code map

| File | What it owns |
|---|---|
| `publisher/main.py` | CLI args, credential resolution, dry-run short circuit, top-level orchestration |
| `publisher/config/getconfig.py` | Load `config.yaml`, normalize URL, apply env overrides, validate keys |
| `publisher/pagesPublisher.py` | Recursive filesystem walk, Markdown conversion, local image extraction, attachment upload |
| `publisher/pagesController.py` | REST calls for verify, search, create, update, delete, property writes, and attachments |
| `publisher/docker_entrypoint.py` | Refresh the container CA bundle before starting the CLI |
| `.github/workflows/publisher.yml` | Build, test, smoke test, and publish the example content |

## Stack

| Concern | Implementation |
|---|---|
| Runtime | Python 3.14 |
| HTTP | `requests` with default TLS verification |
| Markdown | `markdown` with `tables` and `fenced_code` extensions |
| Config | YAML plus selected environment overrides |
| Response validation | Pydantic models in `confluence_api_models.py` |
| Packaging | `python:3.14-slim` Docker image |

## Sample tree as an integration fixture

The workflow in this repository publishes `data_example/` as the Markdown root and `data_example_images/` as the image root. This documentation set therefore doubles as a realistic integration fixture for hierarchy, attachment, and sync behavior.
