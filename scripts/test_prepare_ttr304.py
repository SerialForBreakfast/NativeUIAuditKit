"""Check review handoff boundaries without model execution."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import prepare_ttr304 as p


class HandoffTests(unittest.TestCase):
    def setUp(self):
        base = p.ROOT / '.build/debug-output'
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_missing_reference_stops_before_copy(self):
        with patch.object(p, 'OUT', self.root), self.assertRaisesRegex(ValueError, 'reference_required'):
            p.prepare()
        self.assertFalse((self.root / 'delivery').exists())

    def test_existing_delivery_is_not_overwritten(self):
        reference = self.root / 'reference-r2'
        reference.mkdir()
        (reference / 'review-receipt.json').write_text('{}')
        (self.root / 'delivery').mkdir()
        with patch.object(p, 'OUT', self.root), self.assertRaisesRegex(ValueError, 'output_exists'):
            p.prepare()

    def test_seal_requires_final_archive_execution(self):
        with patch.object(p, 'OUT', self.root), self.assertRaisesRegex(ValueError, 'final_archive_test_required'):
            p.seal()
        self.assertFalse((self.root / 'transfer.json').exists())


if __name__ == '__main__':
    unittest.main()
