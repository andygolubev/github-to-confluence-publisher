# Markdown conversion and attachments

Markdown files are converted to Confluence storage HTML, and local image syntax is rewritten into attachment references before the page is created.

![Markdown image rewrite and attachment upload](/data_images/attachment-rewrite-flow.svg)

## Markdown features enabled

`pages_publisher.py` enables:

- tables
- fenced code blocks

Everything else uses the default `markdown` package behavior.

## Local image rule

Any image reference that is not `http://` or `https://` is treated as a local attachment candidate. The regex extracts only the basename, so all of these resolve to `diagram.svg` under the configured image root:

```markdown
![Architecture](/data_images/publish-lifecycle-current.svg)
![Architecture](publish-lifecycle-current.svg)
![Architecture](../nested/path/publish-lifecycle-current.svg)
```

## Remote image rule

Remote images are left unchanged in the HTML body. They are not downloaded or attached.

## Attachment upload sequence

1. Replace local Markdown image syntax with Confluence storage XML for `ri:attachment`.
2. Convert the Markdown body to HTML.
3. Create or update the page.
4. Open each referenced file from `github_folder_with_image_files`.
5. Upload the file as a page attachment.

## Practical limits

- The parser works line by line, so split image syntax can be missed.
- Duplicate filenames in different folders collide because only the basename is used.
- Missing image files are logged as errors, but the page body is still published.
