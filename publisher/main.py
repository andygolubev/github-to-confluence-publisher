import argparse
import logging
import os
import sys

from config.getconfig import getConfig
from pagesController import deletePages, searchPages, verify_parent_page_exists
from pagesPublisher import publishFolder

logging.basicConfig(level=logging.INFO)


def _resolve_credentials(login, password):
    login = (login or os.environ.get("CONFLUENCE_LOGIN") or "").strip() or None
    password = (
        password
        or os.environ.get("CONFLUENCE_API_TOKEN")
        or os.environ.get("CONFLUENCE_PASSWORD")
        or ""
    ).strip() or None
    return login, password


# Parse arguments; credentials may come from CONFLUENCE_LOGIN / CONFLUENCE_API_TOKEN
parser = argparse.ArgumentParser()
parser.add_argument(
    "--login",
    default=None,
    help="Confluence user email (or set CONFLUENCE_LOGIN)",
)
parser.add_argument(
    "--password",
    default=None,
    help="Atlassian API token (or set CONFLUENCE_API_TOKEN / CONFLUENCE_PASSWORD)",
)
args = parser.parse_args()
inputArguments = vars(args)
login, password = _resolve_credentials(
    inputArguments.get("login"), inputArguments.get("password")
)
if not login or not password:
    logging.error(
        "Missing credentials: pass --login and --password, or set "
        "CONFLUENCE_LOGIN and CONFLUENCE_API_TOKEN."
    )
    sys.exit(1)
inputArguments["login"] = login
inputArguments["password"] = password


CONFIG = getConfig()

logging.debug(CONFIG)

verify_parent_page_exists(
    login=inputArguments["login"], password=inputArguments["password"]
)

pages = searchPages(login=inputArguments['login'], password=inputArguments['password'])
deletePages(pagesIDList=pages, login=inputArguments['login'], password=inputArguments['password'])

publishFolder(folder = str(CONFIG["github_folder_with_md_files"]), 
  login=inputArguments['login'], 
  password=inputArguments['password'])
