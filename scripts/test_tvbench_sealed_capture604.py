"""Tests for blinded tvOS sealed capture safety checks (`tvbench_sealed_capture604.py`)."""
import unittest

import tvbench_sealed_capture604 as sc


class TVBenchSealedCaptureTests(unittest.TestCase):
    def test_forbidden_keywords_block_unsafe_rows(self):
        self.assertFalse(sc.text_is_safe('General\nReset and Update'))
        self.assertFalse(sc.text_is_safe('Sign Out of Apple Account'))
        self.assertFalse(sc.text_is_safe('Erase All Settings'))
        self.assertTrue(sc.text_is_safe('General\nAbout\nLanguage & Region'))

    def test_matching_safe_submenu_enforces_whitelist_and_blacklist(self):
        self.assertEqual(sc.matching_safe_submenu('Settings\nGeneral\nVideo and Audio'), 'General')
        self.assertIsNone(sc.matching_safe_submenu('General\nReset'))
        self.assertIsNone(sc.matching_safe_submenu('Software Update'))

    def test_is_pineboard_home_detects_escape(self):
        self.assertTrue(sc.is_pineboard_home('Photos\nApp Store\nSettings'))
        self.assertFalse(sc.is_pineboard_home('TVCatalog\nFeatured\nDocumentaries'))


if __name__ == '__main__':
    unittest.main()
