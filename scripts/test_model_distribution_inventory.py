"""Check deterministic inventories without changing model files."""
import tempfile
import unittest
from pathlib import Path
import model_distribution_inventory as m


class InventoryTests(unittest.TestCase):
    def setUp(self):
        root = m.ROOT / '.build/debug-output'
        root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)

    def test_deterministic_and_changed_bytes(self):
        (self.path / 'b').write_bytes(b'bb')
        (self.path / 'a').write_bytes(b'a')
        first = m.inventory(self.path)
        self.assertEqual(first, m.inventory(self.path))
        self.assertEqual(first['bytes'], 3)
        self.assertEqual([f['path'] for f in first['files']], ['a', 'b'])
        (self.path / 'a').write_bytes(b'c')
        self.assertNotEqual(first['inventorySHA256'], m.inventory(self.path)['inventorySHA256'])

    def test_missing_empty_and_link(self):
        self.assertFalse(m.inventory(self.path / 'missing')['available'])
        with self.assertRaisesRegex(ValueError, 'Empty'):
            m.inventory(self.path)
        (self.path / 'link').symlink_to(self.path / 'missing')
        with self.assertRaisesRegex(ValueError, 'link'):
            m.inventory(self.path)


if __name__ == '__main__':
    unittest.main()
