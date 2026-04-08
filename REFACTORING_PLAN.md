# Refactoring Plan

## Overview

Code review of the `github-to-confluence-publisher` project — a Python tool that publishes
Markdown files from a GitHub repository to Confluence pages via the REST API, running inside
a Docker container triggered by GitHub Actions.

---

## 1. Bugs

### 1.1 Typo in config key: `counfluence_parent_page_id`

| | |
|---|---|
| **Severity** | Low (functional, but confusing) |
| **Files** | `publisher/config/config.yaml:4`, `publisher/config/getconfig.py:51,83`, `publisher/pagesController.py:73,124,184` |

The key `counfluence_parent_page_id` is a typo — should be `confluence_parent_page_id`.
It works because the typo is consistent everywhere, but it's confusing for anyone reading
the code or config.

**Fix:** Rename to `confluence_parent_page_id` across all files. Keep backward compatibility
by checking both keys in `getConfig()` during a transition period if needed.

### 1.2 `deletePages` returns empty list

| | |
|---|---|
| **Severity** | Low |
| **File** | `publisher/pagesController.py:223-242` |

`deletePages()` initializes `deletedPages = []` but never appends to it. The return value
is always `[]`. The caller in `main.py:57` ignores the return value anyway.

**Fix:** Either append successfully deleted page IDs to the list and use the return value,
or change the function to return `None`.

---

## 2. Code Quality Issues

### 2.1 Credentials passed through every function call

| | |
|---|---|
| **Severity** | Medium |
| **Files** | `publisher/main.py`, `publisher/pagesController.py`, `publisher/pagesPublisher.py` |

`login` and `password` are threaded through every function as positional arguments. This
creates noisy signatures and makes it easy to accidentally swap parameters.

**Fix:** Create a `ConfluenceClient` class that holds the base URL, auth, and common request
logic. Functions become methods, and credentials are set once at construction.

### 2.2 Module-level `CONFIG = getConfig()` called at import time

| | |
|---|---|
| **Severity** | Medium |
| **Files** | `publisher/pagesController.py:17`, `publisher/pagesPublisher.py:10` |

`getConfig()` is called at module import time. This means:
- Config must be valid before any import, making testing harder.
- Tests must patch `CONFIG` on the module object rather than injecting config naturally.
- Import order matters — importing `pagesController` triggers file I/O and env-var reads.

**Fix:** Pass config as a parameter (ideally via the client class from 2.1), or use a
lazy-loading pattern.

### 2.3 `createPage` builds JSON from a hardcoded string template

| | |
|---|---|
| **Severity** | Low |
| **File** | `publisher/pagesController.py:97-156` |

The function parses a JSON string literal into a dict, then overwrites every field. The
initial template values (`"DEFAULT PAGE TITLE"`, `111`, etc.) serve no purpose.

**Fix:** Build the dict directly:
```python
payload = {
    "type": "page",
    "title": title,
    "ancestors": [{"id": parent_id or CONFIG["confluence_parent_page_id"]}],
    "space": {"key": CONFIG["confluence_space"]},
    "body": {"storage": {"value": banner_html + content, "representation": "storage"}},
}
```

### 2.4 Image extraction in `pagesPublisher.py` is fragile

| | |
|---|---|
| **Severity** | Medium |
| **File** | `publisher/pagesPublisher.py:41-50` |

The image regex `r"\A!\[.*]\((?!http)(.*)\)"` has issues:
- `.*` in `alt` text is greedy — `![a](b) ![c](d)` on one line matches incorrectly.
- `result = str(result).split('\'')[1]` relies on Python's `repr()` format to extract
  from a list, which is brittle and breaks if the path contains a single quote.
- Only handles `http` prefix exclusion, not `https` (the `(?!http)` lookahead catches
  `https` too by accident, but the intent is unclear).

**Fix:** Use `re.findall()` result directly (it returns a list of strings from the capture
group), and iterate properly:
```python
for match in re.finditer(r"!\[.*?]\((?!https?://)(.*?)\)", line):
    filename = os.path.basename(match.group(1))
```

### 2.5 String concatenation instead of f-strings / logging format

| | |
|---|---|
| **Severity** | Low |
| **Files** | `publisher/pagesController.py`, `publisher/pagesPublisher.py` |

Many logging calls use `"text " + variable` concatenation. This eagerly evaluates the
string even when the log level is disabled, and is less readable than f-strings or
`%s`-style formatting.

**Fix:** Use `logging.info("Found file: %s", entry.path)` or f-strings consistently.

### 2.6 `bool()` used unnecessarily as a truthiness check

| | |
|---|---|
| **Severity** | Low |
| **File** | `publisher/pagesPublisher.py:43,62` |

`if bool(result):` and `if bool(filesToUpload):` — `bool()` is redundant. Python's `if`
already evaluates truthiness.

**Fix:** `if result:` and `if filesToUpload:`.

### 2.7 Hardcoded macro ID in `pagesPublisher.py`

| | |
|---|---|
| **Severity** | Low |
| **File** | `publisher/pagesPublisher.py:19` |

The "Display Children" macro uses a hardcoded `ac:macro-id`:
```
ac:macro-id="80b8c33e-cc87-4987-8f88-dd36ee991b15"
```
Confluence should generate this. Hardcoding it could cause conflicts if multiple pages
use the same macro ID.

**Fix:** Remove the `ac:macro-id` attribute; let Confluence assign it.

---

## 3. Security Issues

### 3.1 No request timeout on `_set_page_property`

| | |
|---|---|
| **Severity** | Medium |
| **File** | `publisher/pagesController.py:58-63` |

The `requests.post()` call in `_set_page_property` has no `timeout` parameter. If the
Confluence server hangs, the publisher blocks indefinitely. Other API calls correctly
set `timeout=120`.

**Fix:** Add `timeout=120` to the `requests.post()` call.

### 3.2 CQL injection via config values

| | |
|---|---|
| **Severity** | Low-Medium |
| **File** | `publisher/pagesController.py:182-211` |

The `space`, `parent_id`, and `legacy_pattern` values are interpolated directly into
CQL query strings. While these come from config/env vars (not user input), a
misconfigured or malicious environment variable could inject arbitrary CQL.

Example: setting `CONFLUENCE_SPACE` to `" OR type = attachment AND space = "SECRET`
would alter the query semantics.

**Fix:** Validate config values against expected patterns (e.g., space key is
alphanumeric, parent ID is numeric) at config load time. The `prop_key` already uses
`json.dumps()` for quoting, but `space` and `legacy_pattern` do not.

### 3.3 `subprocess.run(["update-ca-certificates"], check=False)` ignores failures

| | |
|---|---|
| **Severity** | Low |
| **File** | `publisher/docker_entrypoint.py:12` |

If `update-ca-certificates` fails, the publisher proceeds with a potentially stale
CA bundle. This could silently allow connections with outdated trust or fail to add
custom CAs.

**Fix:** Log a warning if the return code is non-zero.

---

## 4. Architecture Improvements

### 4.1 No update strategy — delete-then-recreate loses page history

| | |
|---|---|
| **Severity** | Medium |
| **Description** | Every run deletes all published pages and recreates them from scratch. This loses Confluence page version history, breaks watchers/notifications, and invalidates bookmarked URLs (page IDs change). |

**Fix:** Compare existing page content with new content. Use `PUT /content/{id}` to
update pages that already exist. Only create new pages and delete removed ones.

### 4.2 No dry-run mode

| | |
|---|---|
| **Severity** | Low |
| **Description** | There's no way to preview what pages will be created/deleted without actually doing it. |

**Fix:** Add a `--dry-run` flag that logs intended actions without making API calls.

### 4.3 `main.py` uses top-level script execution with side effects

| | |
|---|---|
| **Severity** | Low |
| **File** | `publisher/main.py` |

Argument parsing and execution happen at module level (not inside `if __name__ == "__main__"`
or a `main()` function). This makes the module impossible to import without triggering
the full publish workflow.

**Fix:** Wrap everything in a `main()` function guarded by `if __name__ == "__main__":`.

---

## 5. Testing Gaps

### 5.1 No tests for `pagesPublisher.py`

| | |
|---|---|
| **Severity** | Medium |
| **File** | `publisher/pagesPublisher.py` |

The recursive folder publishing logic, markdown conversion, and image extraction have
zero test coverage. These are the most complex parts of the codebase.

**Fix:** Add unit tests for:
- Markdown-to-Confluence conversion
- Image reference extraction and replacement
- Recursive folder traversal (mock `os.scandir`)

### 5.2 No tests for `getconfig.py` edge cases

| | |
|---|---|
| **Severity** | Low |
| **File** | `publisher/config/getconfig.py` |

No tests for: missing config file + missing env vars, env var overrides, type coercion
of `CONFLUENCE_PARENT_PAGE_ID` to `int`.

**Fix:** Add parametrized tests for config resolution.

---

## 6. Suggested Refactoring Order

For a Sonnet-model implementation, tackle these in order of impact and safety:

| Step | Items | Risk |
|------|-------|------|
| 1 | Fix bug 1.1 (typo), 1.2 (empty return), 3.1 (missing timeout) | Minimal — simple fixes |
| 2 | Fix 2.3 (JSON template), 2.6 (bool), 2.7 (macro ID), 2.5 (logging) | Low — cosmetic cleanup |
| 3 | Fix 2.4 (image regex) | Medium — needs test coverage first (5.1) |
| 4 | Add tests (5.1, 5.2) | None — additive |
| 5 | Fix 2.1 + 2.2 (extract ConfluenceClient class, remove module-level CONFIG) | Medium — structural refactor |
| 6 | Fix 4.3 (main.py entry point) | Low |
| 7 | Implement 4.1 (update instead of delete-recreate) | High — behavioral change, needs careful testing |
| 8 | Add 4.2 (dry-run mode) | Low — additive |
| 9 | Address 3.2 (CQL injection validation) | Low |
