"""Quarantine moves evidence with a receipt. It never deletes or overwrites."""
import json
import shutil
import unittest
import uuid

import queue_quarantine as qq
import research_queue as q


class QuarantineTests(unittest.TestCase):
    def setUp(self):
        self.base = q.ROOT / '.build' / f'test-quarantine-{uuid.uuid4().hex}'
        self.addCleanup(shutil.rmtree, self.base, True)
        self.root = self.base
        self.job = self.base / 'reports/work/research-queue/jobs/fake-job'
        self.job.mkdir(parents=True)
        (self.job / 'spec.json').write_text('{"id": "fake-job"}')
        self.q_root = self.base / 'reports/work/research-queue'

    def run_quarantine(self, paths, incident='FABRICATED-TEST', reason='fabricated metrics'):
        return qq.quarantine(incident, reason, paths, root=self.root, queue=self.q_root)

    def test_move_with_receipt(self):
        digest = q.digest(self.job / 'spec.json')
        receipt = self.run_quarantine(['reports/work/research-queue/jobs/fake-job'])
        self.assertFalse(self.job.exists())
        moved = self.q_root / 'quarantine/FABRICATED-TEST/reports/work/research-queue/jobs/fake-job/spec.json'
        self.assertEqual(q.digest(moved), digest)
        doc = json.loads(receipt.read_text())
        self.assertEqual(doc['items'][0]['files'][0]['sha256'], digest)
        self.assertEqual(doc['reason'], 'fabricated metrics')

    def test_refusals(self):
        cases = [(['reports/work/research-queue/jobs/missing'], 'path_missing'),
                 (['scripts/research_queue.py'], 'path_not_allowed'),
                 (['../outside'], 'unsafe_path')]
        for paths, reason in cases:
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                self.run_quarantine(paths)
        with self.assertRaisesRegex(ValueError, 'reason_missing'):
            self.run_quarantine(['reports/work/research-queue/jobs/fake-job'], reason=' ')
        self.assertTrue(self.job.exists())

    def test_never_overwrites(self):
        self.run_quarantine(['reports/work/research-queue/jobs/fake-job'])
        self.job.mkdir(parents=True)
        (self.job / 'spec.json').write_text('{"id": "second"}')
        with self.assertRaisesRegex(ValueError, 'quarantine_target_exists'):
            self.run_quarantine(['reports/work/research-queue/jobs/fake-job'])
        self.assertTrue((self.job / 'spec.json').exists())


if __name__ == '__main__':
    unittest.main()
