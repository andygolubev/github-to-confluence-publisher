# Docker and environment

Production-style runs use the **Dockerfile** in this repository: a slim Python 3.14 image with CA certificates updated at container start so TLS to Atlassian works behind typical enterprise proxies when custom roots are mounted.

## What the container expects

![Docker inputs: secrets, volumes, behavior](/data_images/docker-runtime.svg)

### Credentials (never in Git)

| Variable | Purpose |
|----------|---------|
| `CONFLUENCE_URL` | REST API base (overrides YAML) |
| `CONFLUENCE_SPACE` | Space key |
| `CONFLUENCE_PARENT_PAGE_ID` | Root page for generated tree |
| `CONFLUENCE_LOGIN` | Atlassian account email |
| `CONFLUENCE_API_TOKEN` | API token (used as password) |

CLI flags `--login` / `--password` are alternatives when running outside Docker.

### Optional overrides

| Variable | Effect |
|----------|--------|
| `PUBLISHER_MARKDOWN_ROOT` | Replaces `github_folder_with_md_files` from config |
| `PUBLISHER_IMAGES_ROOT` | Replaces `github_folder_with_image_files` from config |
| `BANNER_REPO_URL`, `BANNER_PROJECT_NAME` | Banner link back to Git |

### TLS and custom CAs

- Default: **verify** TLS using the system trust store (`verify=False` is not used).  
- Corporate CAs: mount PEM files under `/usr/local/share/ca-certificates/custom/`; the entrypoint runs `update-ca-certificates`.  
- Alternatively set `REQUESTS_CA_BUNDLE` or `SSL_CERT_FILE` for a bundle path.

## Local vs CI

- **Local:** `docker run` with env vars and volumes for Markdown + images, or run `python publisher/main.py` from a venv with the same variables set.  
- **CI:** `.github/workflows/publisher.yml` builds the image and runs the container when secrets exist (guarded so fork PRs without secrets do not fail the job).
