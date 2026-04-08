# Publisher architecture (sample docs)

This tree is **example content** for the GitHub to Confluence publisher. It mirrors how real teams document an internal tool: overview first, then runtime, then integration details.

| Section | What you will find |
|--------|---------------------|
| **01 Architecture overview** | System context and the ordered steps of one publish run |
| **02 Runtime and deployment** | Docker inputs, env vars, and automation |
| **03 Confluence integration** | How folders map to pages, how cleanup works, how images attach |

The diagrams below live in `data_example_images/` and are referenced from Markdown as `/data_images/<filename>` — the same pattern the publisher expects when rewriting lines to Confluence `ac:image` attachments.

## At a glance

![System context: Git repo, publisher, Confluence](/data_images/architecture-overview.svg)

**Source of truth:** Git. **Target:** Pages under a configured Confluence parent. **Model:** Full refresh each run (delete previously tagged pages, then recreate from disk).

## Where to read next

Under this parent in Confluence, open the numbered sections (they mirror subfolders in Git):

1. **01 Architecture overview** — system context + ordered publish steps (with diagrams)  
2. **02 Runtime and deployment** — Docker, secrets, volumes, config  
3. **03 Confluence integration** — folder mapping, content properties, images  

For the canonical technical write-up in this repository, see `openspec/architecture.md`.
