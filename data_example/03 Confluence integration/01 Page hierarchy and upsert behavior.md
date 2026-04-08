# Page hierarchy and upsert behavior

Folder names and Markdown filenames define the page tree. The publisher never invents friendly titles; it uses the raw directory name or filename that it sees on disk.

![Repository tree mapped to Confluence pages](/data_images/confluence-hierarchy-map.svg)

## Mapping rules

| On disk | In Confluence |
|---|---|
| Directory | Child page whose body is the Children macro |
| `.md` file | Page titled exactly like the filename, including `.md` |
| Any other file | Ignored for publishing |
| Symlink | Logged, but not published as a page |

## Upsert behavior

`ConfluenceClient.upsert_page()` first searches for an existing direct child page with the same title under the target parent. It then:

- updates the page when a matching title already exists under that parent
- creates a new page when no direct child match exists

That means generated pages can keep stable ids across runs as long as both title and parent stay the same.

## Navigation pages

Directory pages are created with this storage body:

```xml
<ac:structured-macro ac:name="children" ac:schema-version="2"/>
```

Those pages are lightweight navigation shells. The useful narrative content lives in the Markdown file pages beneath them.

## Safe naming practice

Because upserts are title-based, dedicate a parent page to generated content and keep numeric prefixes in filenames when ordering matters. A manual sibling page with the same title as a generated page is a collision risk.
