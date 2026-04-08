# Configuration sources and precedence

The publisher has two runtime modes:

- Local development: read `publisher/config/config.yaml`, then apply overrides.
- Container and CI: run from the Docker image, which does not bundle `config.yaml`, so the effective config comes from environment variables plus built-in defaults.

![Runtime inputs, overrides, and mounted roots](/data_images/runtime-inputs-precedence.svg)

## Effective precedence

| Input source | Applies to | Notes |
|---|---|---|
| `publisher/config/config.yaml` | Local runs | Optional; ignored in the container image because the file is not copied into the image |
| Environment variables | Local runs and CI | Override URL, space, parent id, banner fields, property key, Markdown root, and image root |
| CLI flags | Credentials only | `--login` and `--api-token` override the credential environment variables |

## Config fields with behavior attached

| Field | Effect in code |
|---|---|
| `confluence_url` | Normalized to a REST API base such as `/wiki/rest/api/` |
| `confluence_space` | Used in search CQL and page creation payloads |
| `confluence_parent_page_id` | Default ancestor for all generated pages |
| `publisher_property_key` | Property key written to each generated page |
| `github_folder_with_md_files` | Root scanned by `publish_folder()` |
| `github_folder_with_image_files` | Directory searched for attachment files by basename |
| `banner_repo_url`, `banner_project_name` | Render the HTML banner prepended to every page body |

## Environment variables used in automation

```text
CONFLUENCE_URL
CONFLUENCE_SPACE
CONFLUENCE_PARENT_PAGE_ID
CONFLUENCE_LOGIN
CONFLUENCE_API_TOKEN
PUBLISHER_PROPERTY_KEY
BANNER_REPO_URL
BANNER_PROJECT_NAME
PUBLISHER_MARKDOWN_ROOT
PUBLISHER_IMAGES_ROOT
```

## Compatibility detail

`get_config()` still accepts the old YAML key `counfluence_parent_page_id` and rewrites it to `confluence_parent_page_id`. That keeps older local config files working even though the typo should not be used in new examples.
