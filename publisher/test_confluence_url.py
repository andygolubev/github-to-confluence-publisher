"""Unit tests for Confluence REST API URL normalization."""

import unittest

from config.confluence_url import normalize_confluence_rest_api_url


class NormalizeConfluenceUrlTests(unittest.TestCase):
    def test_atlassian_cloud_wiki_root(self):
        self.assertEqual(
            normalize_confluence_rest_api_url("https://acme.atlassian.net/wiki"),
            "https://acme.atlassian.net/wiki/rest/api/",
        )

    def test_atlassian_cloud_space_url(self):
        self.assertEqual(
            normalize_confluence_rest_api_url(
                "https://acme.atlassian.net/wiki/spaces/DOC/pages/123/Foo"
            ),
            "https://acme.atlassian.net/wiki/rest/api/",
        )

    def test_atlassian_cloud_already_api_base(self):
        self.assertEqual(
            normalize_confluence_rest_api_url(
                "https://acme.atlassian.net/wiki/rest/api"
            ),
            "https://acme.atlassian.net/wiki/rest/api/",
        )

    def test_server_confluence_context(self):
        self.assertEqual(
            normalize_confluence_rest_api_url("https://intranet.example.com/confluence"),
            "https://intranet.example.com/confluence/rest/api/",
        )


if __name__ == "__main__":
    unittest.main()
