# GitHub to Confluence publisher reference set

This `data_example/` tree is a project-shaped documentation set for the publisher itself. It is written against the current Python code, Docker packaging, and GitHub Actions workflow in this repository.

## Why this sample tree exists

- Every directory becomes a Confluence folder page with a Children macro.
- Every Markdown file becomes a page whose title is the full filename, including `.md`.
- Every local image reference becomes an attachment lookup by filename under `data_example_images/`.

That makes this folder a realistic smoke test for navigation, hierarchy, Markdown conversion, and attachment uploads.

![Publisher system map](/data_images/publisher-system-map.svg)

## Section map

| Section | Focus | Main code paths |
|---|---|---|
| `01 Architecture overview` | Modules, data flow, and sync lifecycle | `publisher/main.py`, `publisher/pages_publisher.py`, `publisher/pages_controller.py` |
| `02 Runtime and deployment` | Config precedence, Docker runtime, GitHub Actions | `publisher/config/get_config.py`, `Dockerfile`, `.github/workflows/publisher.yml` |
| `03 Confluence integration` | Hierarchy mapping, upserts, properties, attachments | `publisher/pages_controller.py`, `publisher/pages_publisher.py` |
| `04 Reliability and limits` | Validation, TLS, tests, and edge cases | `publisher/test_*.py`, `publisher/config/confluence_url.py` |

## Current operating model

The publisher is a batch job, not a service. A normal run does four high-level things:

1. Resolve credentials and load config.
2. Verify the configured parent page and snapshot existing generated descendants.
3. Walk the Markdown tree and upsert folder pages, Markdown pages, and attachments.
4. Delete stale generated pages that existed before the run but were not republished.

This is an upsert-plus-prune model, not a blind delete-and-recreate pass.

## Reading order

Open the numbered sections in order. Numeric prefixes are deliberate because `os.scandir()` does not guarantee lexical ordering.
