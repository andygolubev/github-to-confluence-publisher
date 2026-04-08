"""Unit tests for pages_publisher module."""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import MagicMock

from pages_publisher import DISPLAY_CHILDREN_MACRO, _extract_images, publish_folder


class TestExtractImages(unittest.TestCase):
    def test_no_images_unchanged(self):
        line = "Just some text with no images\n"
        modified, images = _extract_images(line)
        self.assertEqual(modified, line)
        self.assertEqual(images, [])

    def test_local_image_replaced(self):
        line = "![alt text](/data_images/photo.jpg)\n"
        modified, images = _extract_images(line)
        self.assertIn("<ac:image>", modified)
        self.assertIn('ri:filename="photo.jpg"', modified)
        self.assertEqual(images, ["photo.jpg"])

    def test_http_image_ignored(self):
        line = "![remote](http://example.com/img.png)\n"
        modified, images = _extract_images(line)
        self.assertEqual(modified, line)
        self.assertEqual(images, [])

    def test_https_image_ignored(self):
        line = "![remote](https://example.com/img.png)\n"
        modified, images = _extract_images(line)
        self.assertEqual(modified, line)
        self.assertEqual(images, [])

    def test_multiple_images_on_one_line(self):
        line = "![a](/images/a.jpg) and ![b](/images/b.png)"
        modified, images = _extract_images(line)
        self.assertEqual(images, ["a.jpg", "b.png"])
        self.assertIn('ri:filename="a.jpg"', modified)
        self.assertIn('ri:filename="b.png"', modified)

    def test_nested_path_extracts_basename(self):
        line = "![x](/some/deep/path/image.gif)"
        _, images = _extract_images(line)
        self.assertEqual(images, ["image.gif"])

    def test_image_with_single_quote_in_path(self):
        line = "![alt](/data_images/o'clock.jpg)"
        _, images = _extract_images(line)
        self.assertEqual(images, ["o'clock.jpg"])


class TestPublishFolder(unittest.TestCase):
    def _make_client(self, page_id="page-123"):
        client = MagicMock()
        client.upsert_page.return_value = page_id
        return client

    def test_publishes_md_file(self):
        client = self._make_client()
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test.md"), 'w') as f:
                f.write("# Hello\nSome content")

            publish_folder(tmpdir, client, images_root="/tmp/images")

        client.upsert_page.assert_called_once()
        call_kwargs = client.upsert_page.call_args.kwargs
        self.assertEqual(call_kwargs["title"], "test.md")
        self.assertIn("Hello", call_kwargs["content"])

    def test_returns_set_of_processed_page_ids(self):
        client = self._make_client(page_id="page-abc")
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "a.md"), 'w') as f:
                f.write("content a")
            with open(os.path.join(tmpdir, "b.md"), 'w') as f:
                f.write("content b")

            result = publish_folder(tmpdir, client, images_root="/tmp")

        self.assertIsInstance(result, set)
        self.assertEqual(result, {"page-abc"})  # both return same mock value

    def test_skips_non_md_files(self):
        client = self._make_client()
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "readme.txt"), 'w') as f:
                f.write("text file")

            result = publish_folder(tmpdir, client, images_root="/tmp")

        client.upsert_page.assert_not_called()
        self.assertEqual(result, set())

    def test_creates_folder_page_with_children_macro(self):
        client = self._make_client(page_id="folder-id")
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "docs")
            os.makedirs(subdir)
            with open(os.path.join(subdir, "page.md"), 'w') as f:
                f.write("content")

            publish_folder(tmpdir, client, images_root="/tmp")

        calls = client.upsert_page.call_args_list
        folder_call = next(c for c in calls if c.kwargs["title"] == "docs")
        self.assertIn("children", folder_call.kwargs["content"])

    def test_subdirectory_pages_use_folder_as_parent(self):
        client = self._make_client(page_id="folder-id")
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "section")
            os.makedirs(subdir)
            with open(os.path.join(subdir, "article.md"), 'w') as f:
                f.write("body")

            publish_folder(tmpdir, client, images_root="/tmp")

        calls = client.upsert_page.call_args_list
        article_call = next(c for c in calls if c.kwargs["title"] == "article.md")
        self.assertEqual(article_call.kwargs["parent_page_id"], "folder-id")

    def test_folder_page_id_included_in_returned_set(self):
        call_count = [0]

        def side_effect(**kwargs):
            call_count[0] += 1
            return f"id-{call_count[0]}"

        client = MagicMock()
        client.upsert_page.side_effect = side_effect

        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "section")
            os.makedirs(subdir)
            with open(os.path.join(subdir, "page.md"), 'w') as f:
                f.write("body")

            result = publish_folder(tmpdir, client, images_root="/tmp")

        self.assertEqual(result, {"id-1", "id-2"})

    def test_attaches_local_images(self):
        client = self._make_client(page_id="img-page-id")
        with tempfile.TemporaryDirectory() as tmpdir:
            images_root = os.path.join(tmpdir, "images")
            os.makedirs(images_root)
            with open(os.path.join(images_root, "photo.jpg"), 'wb') as f:
                f.write(b'\xff\xd8\xff')

            with open(os.path.join(tmpdir, "post.md"), 'w') as f:
                f.write("![photo](photo.jpg)")

            publish_folder(tmpdir, client, images_root=images_root)

        client.attach_file.assert_called_once()
        self.assertEqual(client.attach_file.call_args.args[0], "img-page-id")

    def test_logs_error_for_missing_image(self):
        client = self._make_client()
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "post.md"), 'w') as f:
                f.write("![missing](/images/ghost.jpg)")

            publish_folder(tmpdir, client, images_root="/nonexistent")

        client.attach_file.assert_not_called()


if __name__ == "__main__":
    unittest.main()
