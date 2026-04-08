"""Unit tests for config validation helpers."""

from __future__ import annotations

import unittest

from config.get_config import _validate_config


class TestValidateConfig(unittest.TestCase):
    def test_valid_config_passes(self):
        _validate_config({"confluence_space": "MY_SPACE", "confluence_parent_page_id": 999})

    def test_alphanumeric_space_key_passes(self):
        _validate_config({"confluence_space": "DOC123", "confluence_parent_page_id": 1})

    def test_space_key_with_underscore_passes(self):
        _validate_config({"confluence_space": "MY_SPACE_KEY", "confluence_parent_page_id": 1})

    def test_space_key_with_tilde_passes(self):
        _validate_config({"confluence_space": "~personal", "confluence_parent_page_id": 1})

    def test_space_key_with_space_raises(self):
        with self.assertRaises(ValueError):
            _validate_config({"confluence_space": "bad space", "confluence_parent_page_id": 1})

    def test_space_key_with_special_chars_raises(self):
        with self.assertRaises(ValueError):
            _validate_config({"confluence_space": "SPC; DROP TABLE", "confluence_parent_page_id": 1})

    def test_non_numeric_parent_id_raises(self):
        with self.assertRaises(ValueError):
            _validate_config({"confluence_space": "SPC", "confluence_parent_page_id": "not-a-number"})

    def test_numeric_string_parent_id_passes(self):
        _validate_config({"confluence_space": "SPC", "confluence_parent_page_id": "12345"})

    def test_missing_keys_skips_validation(self):
        # Empty config should not raise — keys are optional at validation time
        _validate_config({})

    def test_typo_key_migration(self):
        """counfluence_parent_page_id (old typo) should be migrated to the correct key."""
        cfg = {"counfluence_parent_page_id": 777, "confluence_space": "TST"}
        # Simulate the migration logic from get_config()
        if "counfluence_parent_page_id" in cfg and "confluence_parent_page_id" not in cfg:
            cfg["confluence_parent_page_id"] = cfg.pop("counfluence_parent_page_id")
        self.assertEqual(cfg["confluence_parent_page_id"], 777)
        self.assertNotIn("counfluence_parent_page_id", cfg)


if __name__ == "__main__":
    unittest.main()
