"""Check source audit and release preservation."""
import unittest
from unittest.mock import patch
import prepare_release305 as p


class SourceTests(unittest.TestCase):
    def test_record_hash(self):
        self.assertTrue(p.record_matches(b'', 'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU'))
        self.assertFalse(p.record_matches(b'changed', 'sha256=47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU'))
        self.assertFalse(p.record_matches(b'', ''))

    def test_collision_stops_before_source_read(self):
        with patch.object(p, 'OUT', p.ROOT), patch.object(p, 'source_members') as read:
            with self.assertRaisesRegex(ValueError, 'output_exists'):
                p.prepare()
            read.assert_not_called()

    def test_real_source_inventory(self):
        members, audits = p.source_members()
        self.assertEqual(len(members), 746)
        self.assertEqual(audits[0]['differences'], [])
        self.assertEqual({d['path'] for d in audits[1]['differences']},
                         {'ultralytics/data/base.py', 'ultralytics/utils/patches.py'})
        self.assertNotIn(b'/Users/', members['configuration/args.yaml'])
        self.assertFalse(any('__pycache__' in n or n.endswith('.pyc') for n in members))
        self.assertEqual(p.release.digest(members['historical/scripts/export_yolo_coreml.py']),
                         '8dcf2bbbeb67c7b0fff97021f5a9799922e9910a28f8419ea0d9cb9d1970f6ef')


if __name__ == '__main__':
    unittest.main()
