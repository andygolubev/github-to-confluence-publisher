# Markdown images and attachments

The publisher handles **local** image references on single-line Markdown image syntax. Remote URLs (`http` / `https`) are left unchanged so you can still embed external images if Confluence allows them.

## Pipeline

![Markdown local image to attachment](/data_images/markdown-image-pipeline.svg)

## Authoring convention

Use a path whose **last segment** is the filename on disk under `github_folder_with_image_files`:

```markdown
![Architecture overview](/data_images/architecture-overview.svg)
```

The parser extracts `architecture-overview.svg`, looks for `github_folder_with_image_files/architecture-overview.svg`, uploads it, and replaces the line with Confluence storage format referencing that attachment name.

## Supported formats

Confluence accepts common web image types. This example set uses **SVG** diagrams (lightweight, version-control friendly) plus the existing sample **JPEG** below for raster smoke tests.

## Raster example (legacy sample asset)

The repository still ships a small bitmap used in older examples:

![Sample raster image](/data_images/01_pikachu.jpg)

## Troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| Broken image on page | Filename mismatch or file missing under images root |
| Image line appears as plain text | Image syntax split across lines (parser is line-based) |
| External image missing | CSP or Confluence restrictions on hotlinking |

For line-based processing details, see `publisher/pagesPublisher.py` (`re.findall` on each line).
