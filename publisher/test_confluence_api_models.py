"""Unit tests for Confluence API Pydantic response models."""

import unittest

from confluence_api_models import (
    AttachmentResponse,
    CreatedPageResponse,
    ParentPageResponse,
    SearchResponse,
    validate_response_payload,
    ConfluenceApiValidationError,
)


class ValidateResponsePayloadTests(unittest.TestCase):
    def test_parent_page_response(self):
        data = {"space": {"key": "DOC"}}
        m = validate_response_payload(data, ParentPageResponse, "ctx")
        self.assertEqual(m.space.key, "DOC")

    def test_parent_page_missing_space_ok(self):
        m = validate_response_payload({}, ParentPageResponse, "ctx")
        self.assertIsNone(m.space)

    def test_created_page_id_coerced_to_str(self):
        m = validate_response_payload({"id": 12345}, CreatedPageResponse, "ctx")
        self.assertEqual(m.id, "12345")

    def test_search_response(self):
        data = {
            "results": [
                {"content": {"id": "1", "title": "A"}},
                {"content": {"id": 2, "title": "B"}},
            ]
        }
        m = validate_response_payload(data, SearchResponse, "ctx")
        self.assertEqual([r.content.id for r in m.results], ["1", "2"])

    def test_search_missing_content_id_raises(self):
        with self.assertRaises(ConfluenceApiValidationError):
            validate_response_payload(
                {"results": [{"content": {"title": "x"}}]},
                SearchResponse,
                "ctx",
            )

    def test_attachment_response(self):
        data = {"results": [{"id": "att-1"}]}
        m = validate_response_payload(data, AttachmentResponse, "ctx")
        self.assertEqual(m.results[0].id, "att-1")

    def test_attachment_empty_results_raises(self):
        with self.assertRaises(ConfluenceApiValidationError):
            validate_response_payload({"results": []}, AttachmentResponse, "ctx")


if __name__ == "__main__":
    unittest.main()
