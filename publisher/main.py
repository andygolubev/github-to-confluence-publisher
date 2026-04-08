import argparse
import logging
import os
import sys

from config.get_config import get_config
from pages_controller import ConfluenceClient
from pages_publisher import publish_folder

logging.basicConfig(level=logging.INFO)


def _resolve_credentials(login, api_token):
    login = (login or os.environ.get("CONFLUENCE_LOGIN") or "").strip() or None
    api_token = (
        api_token or os.environ.get("CONFLUENCE_API_TOKEN") or ""
    ).strip() or None
    return login, api_token


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--login",
        default=None,
        help="Confluence user email (or set CONFLUENCE_LOGIN)",
    )
    parser.add_argument(
        "--api-token",
        default=None,
        help="Atlassian API token (or set CONFLUENCE_API_TOKEN)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be published without making any API calls",
    )
    args = parser.parse_args()

    login, api_token = _resolve_credentials(args.login, args.api_token)
    if not login or not api_token:
        logging.error(
            "Missing credentials: pass --login and --api-token, or set "
            "CONFLUENCE_LOGIN and CONFLUENCE_API_TOKEN."
        )
        sys.exit(1)

    config = get_config()
    logging.debug(config)

    if args.dry_run:
        logging.info("Dry-run mode: no changes will be made to Confluence.")
        logging.info("Would publish markdown from: %s", config["github_folder_with_md_files"])
        logging.info(
            "Target: space=%s parent_page_id=%s",
            config["confluence_space"],
            config["confluence_parent_page_id"],
        )
        return

    client = ConfluenceClient(login=login, password=api_token, config=config)
    client.verify_parent_page_exists()

    # Snapshot existing published pages before we touch anything.
    existing_pages = set(client.search_pages())

    # Upsert all pages from the local folder (create new, update existing).
    published_pages = publish_folder(
        folder=str(config["github_folder_with_md_files"]),
        client=client,
        images_root=str(config["github_folder_with_image_files"]),
    )

    # Delete pages that were published before but are no longer in the repo.
    stale_pages = existing_pages - published_pages
    if stale_pages:
        logging.info("Deleting %d stale page(s) no longer present in the repository", len(stale_pages))
        client.delete_pages(list(stale_pages))


if __name__ == "__main__":
    main()
