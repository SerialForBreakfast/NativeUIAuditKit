import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import workflow_review as w


class WorkflowReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=w.ROOT / '.build', prefix='review-test-')
        self.path = Path(self.temp.name) / 'status.yaml'
        self.now = dt.datetime(2026, 10, 4, tzinfo=dt.timezone.utc)

    def tearDown(self):
        self.temp.cleanup()

    def test_expired_requests_and_unknown_fields_preserved(self):
        data = {'schema_version': 1, 'packets': {'old': {
            'updated_at': '2020-01-01T00:00:00Z', 'valid_until': '2020-01-02T00:00:00Z',
            'state': 'blocked', 'newField': {'pending_requests': [{'id': 'still-open'}]},
            'blockers': ['missing evidence']}}, 'pending_requests': [{'id': 'top'}]}
        self.path.write_text(json.dumps(data))
        before = self.path.read_bytes()
        result = w.status_view(self.path, self.now)
        self.assertEqual(result['packets']['old']['freshness'], 'expired')
        self.assertIn('newField', result['packets']['old']['otherFields'])
        self.assertEqual(len(result['actionable']), 3)
        self.assertEqual(self.path.read_bytes(), before)
        data['packets']['peer'] = {'state': 'working', 'pending_requests': [{'id': 'new'}]}
        self.path.write_text(json.dumps(data))
        later = w.status_view(self.path, self.now)
        self.assertEqual(len(later['actionable']), 4)
        self.assertNotEqual(result['sourceSHA256'], later['sourceSHA256'])

    def test_invalid_status_rejected(self):
        for text in ['schema_version: 1\nschema_version: 1', '{"schema_version":99}',
                     '{"schema_version":1,"packets":{"bad":null}}']:
            self.path.write_text(text)
            with self.assertRaises((ValueError, RuntimeError)):
                w.status_view(self.path, self.now)

    def test_missing_and_changed_source(self):
        with self.assertRaises(FileNotFoundError):
            w.status_view(self.path, self.now)
        self.path.write_text('{"schema_version":1}')
        def mutate(path):
            path.write_text('{"schema_version":1,"new":true}')
            return {'schema_version': 1}
        with patch.object(w, 'document', side_effect=mutate):
            with self.assertRaisesRegex(ValueError, 'changed'):
                w.status_view(self.path, self.now)

    def test_freshness_never_invents_availability(self):
        self.assertEqual(w.freshness({}, self.now), 'unknown')
        self.assertEqual(w.freshness({'updated_at': 'bad', 'valid_until': 'bad'}, self.now), 'unknown')
        self.assertEqual(w.freshness({'updated_at': '2026-10-04T00:00:00Z',
                                    'valid_until': '2026-10-04T01:00:00Z'}, self.now), 'current')

    def test_nul_inventory_handles_rename_spaces_and_newlines(self):
        rows = w.parse_porcelain(b' M file with space\0R  new\0old\0?? line\nbreak\0')
        self.assertEqual(rows[1]['originalPath'], 'old')
        self.assertEqual(rows[2]['path'], 'line\nbreak')
        with self.assertRaises(ValueError):
            w.parse_porcelain(b'R  new\0')

    def test_exact_intended_subset_and_no_git_mutation(self):
        calls = []
        def git(*args):
            calls.append(args)
            return b'abc123\n' if args[0] == 'rev-parse' else b' M tracked\0?? scripts/new.py\0'
        with patch.object(w, 'git_output', side_effect=git):
            result = w.git_view(['scripts/new.py'], 'message', ['reported test'], 'consumer build')
            self.assertEqual(result['unassignedPaths'], ['tracked'])
            self.assertFalse(result['published'])
            for intended in [['ignored.bin'], ['../escape'], ['tracked', 'tracked']]:
                with self.assertRaises(ValueError):
                    w.git_view(intended, 'x', [], 'x')
        self.assertTrue(all(c[0] in {'status', 'rev-parse'} for c in calls))


if __name__ == '__main__':
    unittest.main()
