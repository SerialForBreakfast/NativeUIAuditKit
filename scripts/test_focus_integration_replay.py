import unittest
from pathlib import Path
from focus_integration_replay import extract_block, run, ROOT


class ReplaySafetyTests(unittest.TestCase):
    def test_nested_extraction_preserves_exact_bytes(self):
        source = 'before\nfunc crop() { if true { return 1 } }\nafter'
        self.assertEqual(extract_block(source, 'func crop()'), 'func crop() { if true { return 1 } }')

    def test_missing_ambiguous_and_partial_source_rejected(self):
        for source in ('nothing', 'func crop() {} func crop() {}', 'func crop() {'):
            with self.assertRaises(ValueError): extract_block(source, 'func crop()')

    def test_existing_output_rejected_before_peer_access(self):
        with self.assertRaisesRegex(ValueError, 'output_collision'):
            run(Path('/nonexistent-peer'), ROOT / 'reports')

    def test_outside_output_rejected_before_any_write(self):
        with self.assertRaisesRegex(ValueError, 'outside_project'):
            run(Path('/nonexistent-peer'), ROOT.parent / 'not-authorized-output')


if __name__ == '__main__': unittest.main()
