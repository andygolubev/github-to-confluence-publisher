# Publish lifecycle and sync model

The current implementation preserves matching pages by updating them in place when possible, then removes only stale generated pages at the end of the run.

![Publish lifecycle with verify, snapshot, upsert, and prune](/data_images/publish-lifecycle-current.svg)

## Ordered flow

### 1. Resolve credentials

`main.py` accepts `--login` and `--api-token` or falls back to `CONFLUENCE_LOGIN` and `CONFLUENCE_API_TOKEN`. Empty values stop the run immediately.

### 2. Load and normalize configuration

`get_config()` reads `publisher/config/config.yaml` when present, migrates the historical `counfluence_parent_page_id` typo, normalizes `confluence_url`, and applies environment overrides.

### 3. Optional dry run

`--dry-run` logs the effective Markdown root and target page without calling Confluence. It still requires credentials to be present because validation happens before the dry-run branch.

### 4. Verify the parent page

`verify_parent_page_exists()` fetches the configured parent page through the REST API. A wrong numeric id or wrong API base fails before any writes happen.

### 5. Snapshot existing generated descendants

`search_pages()` collects descendant page ids beneath the configured ancestor, filters them by content property, and keeps that set as the before snapshot.

### 6. Walk the repository tree

`publish_folder()` traverses the Markdown root with `os.scandir()`:

- Directory -> upsert a Confluence page with the Children macro, then recurse beneath that page id.
- Markdown file -> rewrite local image syntax, convert Markdown to HTML, upsert the page, then upload referenced attachments.
- Anything else -> skip with logging.

### 7. Delete stale ids

After publishing, `stale_pages = existing_pages - published_pages`. Only page ids from the original snapshot that were not republished are deleted.

## Why this matters

This behavior is less destructive than the older full-refresh design. Existing generated pages keep their ids when title and parent match, which reduces churn in Confluence history and links. Renames or moved pages still produce new ids and cause the old ids to be pruned as stale.

## Ordering note

Because `publish_folder()` relies on `os.scandir()`, the child order is filesystem-dependent. Numeric prefixes in folder and file names are the safest way to keep a predictable reading order.
