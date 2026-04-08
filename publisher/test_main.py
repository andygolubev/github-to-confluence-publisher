"""Unit tests for the top-level publish orchestration in main.py."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import main as publisher_main


class TestMainStaleDeletion(unittest.TestCase):
    def _base_config(self) -> dict:
        return {
            "confluence_space": "DOC",
            "confluence_parent_page_id": 123,
            "github_folder_with_md_files": "./data_example",
            "github_folder_with_image_files": "./data_example_images",
        }

    def test_deletes_pages_missing_from_repo_after_publish(self) -> None:
        client = MagicMock()
        client.search_pages.return_value = ["page-1", "page-2", "page-3"]

        with patch("main._resolve_credentials", return_value=("user@example.com", "token")):
            with patch("main.get_config", return_value=self._base_config()):
                with patch("main.ConfluenceClient", return_value=client):
                    with patch("main.publish_folder", return_value={"page-1", "page-3", "page-4"}):
                        with patch("sys.argv", ["publisher/main.py"]):
                            publisher_main.main()

        client.verify_parent_page_exists.assert_called_once_with()
        client.delete_pages.assert_called_once_with(["page-2"])

    def test_does_not_delete_when_everything_was_republished(self) -> None:
        client = MagicMock()
        client.search_pages.return_value = ["page-1", "page-2"]

        with patch("main._resolve_credentials", return_value=("user@example.com", "token")):
            with patch("main.get_config", return_value=self._base_config()):
                with patch("main.ConfluenceClient", return_value=client):
                    with patch("main.publish_folder", return_value={"page-1", "page-2"}):
                        with patch("sys.argv", ["publisher/main.py"]):
                            publisher_main.main()

        client.delete_pages.assert_not_called()


if __name__ == "__main__":
    unittest.main()
