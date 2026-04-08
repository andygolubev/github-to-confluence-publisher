# Tested behaviors and current limitations

The test suite gives good coverage of the small core, but the implementation is intentionally simple and some tradeoffs are visible at the documentation layer.

## Behaviors covered by tests

| Area | Examples covered |
|---|---|
| URL handling | Atlassian Cloud space URLs and server-style `/confluence` URLs normalize correctly |
| Config validation | Allowed space key characters, numeric parent ids, and typo-key migration |
| Search and tagging | Property writes, `409` tolerance, and property-based filtering |
| Publish walk | Folder pages, recursion, non-Markdown skips, and returned processed ids |
| Image extraction | Local vs remote images, multiple images on one line, and basename extraction |
| Update semantics | Existing pages increment version numbers on update |

## Current limits to understand

| Limit | Operational effect |
|---|---|
| Upsert search ignores content property | Manual pages can be overwritten when title and parent match a generated page |
| `os.scandir()` order is not sorted | Child page order can vary unless filenames use numeric prefixes |
| Page titles keep `.md` | Confluence page names mirror raw filenames, not cleaned titles |
| Image attachment lookup uses basename only | Duplicate filenames across directories can attach the wrong file |
| Dry run is shallow | It checks credentials and config target, but it does not walk content or ping Confluence |
| Markdown support is narrow | Only tables and fenced code are explicitly enabled |

## Recommended operating pattern

- Publish into a dedicated parent page.
- Use unique image filenames across the image root.
- Keep numeric prefixes on folders and files.
- Treat the repository, not Confluence, as the editing surface for generated pages.
