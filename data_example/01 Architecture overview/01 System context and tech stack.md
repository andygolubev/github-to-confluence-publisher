# System context and tech stack

The publisher is a **Python CLI** that reads a Markdown directory tree, talks to **Confluence Cloud REST API** with **HTTP Basic** auth (Atlassian account email + API token), and recreates a matching page hierarchy under a **parent page** you configure.

## Responsibilities

| Component | Role |
|-----------|------|
| **Git / CI** | Holds Markdown + images; optional GitHub Actions job runs the container |
| **`publisher/main.py`** | Entry point: parse args, load config, orchestrate publish |
| **`pagesPublisher.py`** | Walk folders, convert Markdown, rewrite local image refs, create pages, attach files |
| **`pagesController.py`** | Low-level REST calls: create page, attach file, search, delete |
| **Confluence** | Stores HTML pages, attachments, and **content properties** used for discovery |

## End-to-end context

The diagram summarizes data flow: repository content in, REST calls out, no long-lived server — each run is a batch job.

![Git repository, publisher process, Confluence Cloud](/data_images/architecture-overview.svg)

## Stack (summary)

- **Runtime:** Python 3.14  
- **HTTP:** `requests` / `urllib3` with normal TLS verification  
- **Markdown:** `markdown` library with tables and fenced code extensions  
- **Config:** YAML file plus environment variable overrides  

Pinned versions are listed in `publisher/requirements.txt`.

## Design choice: full refresh

Every successful publish **deletes** pages previously created under the parent (identified via a Confluence content property), then **rebuilds** from the current tree. That keeps Confluence a pure mirror of Git at the cost of churn on page IDs and history for generated pages.
