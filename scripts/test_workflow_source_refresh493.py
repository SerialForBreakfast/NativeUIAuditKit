"""Test approval refresh without live jobs or TTR."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import research_queue as q
import research_approval as approval
from workflow_source_refresh493 import refresh


class RefreshTests(unittest.TestCase):
    def setUp(self):
        folder = q.ROOT / '.build/adr493-tests'
        folder.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=folder)
        self.root = Path(self.temp.name)
        self.queue = self.root / 'queue'
        self.job = self.queue / 'jobs/example'
        self.job.mkdir(parents=True)
        self.spec = {'id': 'example'}
        q.save(self.job / 'spec.json', self.spec)
        q.save(self.root / 'source.json', {'revision': 2})
        self.after = q.digest(self.root / 'source.json')
        self.changes = [dict(path='source.json', before='a'*64, after=self.after)]
        self.oldchecks = dict(code=[dict(path='source.json', sha256='a'*64)])
        record = dict(sha256=q.text_digest(self.spec), checks=self.oldchecks,
                      checksSHA256=q.text_digest(self.oldchecks), approver='agent:Maximum-mini-NUIAK')
        self.doc = dict(version=approval.VERSION, jobs={'example': record}, events=[])
        q.save(approval.path(self.queue), self.doc)
        self.rootpatch = patch.object(q, 'ROOT', self.root)
        self.rootpatch.start()
        self.checkpatch = patch.object(approval, 'checks', autospec=True, return_value=(self.spec,
            dict(code=[dict(path='source.json', sha256=self.after)])))
        self.checkpatch.start()

    def tearDown(self):
        self.checkpatch.stop()
        self.rootpatch.stop()
        self.temp.cleanup()

    def run_refresh(self):
        return refresh(self.queue, ['example'], self.changes, 'Qualify the reviewed admission change.')

    def test_refresh_preserves_spec_and_records_history(self):
        before = q.digest(self.job / 'spec.json')
        self.run_refresh()
        self.assertEqual(before, q.digest(self.job / 'spec.json'))
        doc = approval.load(self.queue)
        self.assertEqual(doc['events'][0]['previousChecksSHA256'], q.text_digest(self.oldchecks))
        self.assertTrue(approval.is_approved(self.queue, self.spec))

    def test_attempt_blocks_refresh(self):
        (self.job / 'attempts/001').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'refresh_attempt_exists'): self.run_refresh()

    def test_active_runner_blocks_refresh(self):
        with q.host_lock(self.root / '.build/research-queue.lock'):
            with self.assertRaisesRegex(ValueError, 'resource_busy'): self.run_refresh()

    def test_unreviewed_source_blocks_refresh(self):
        self.changes[0]['after'] = 'b'*64
        with self.assertRaisesRegex(ValueError, 'refresh_unreviewed_change'): self.run_refresh()

    def test_changed_spec_blocks_refresh(self):
        q.save(self.job / 'spec.json', {'id': 'different'}, replace=True)
        with self.assertRaisesRegex(ValueError, 'refresh_spec_changed'): self.run_refresh()

    def test_revocation_blocks_refresh(self):
        self.doc['events'].append(dict(action='revoke', job='example'))
        q.save(approval.path(self.queue), self.doc, replace=True)
        with self.assertRaisesRegex(ValueError, 'refresh_revoked'): self.run_refresh()

    def test_failed_recheck_preserves_original_approval(self):
        before = q.digest(approval.path(self.queue))
        with patch.object(approval, 'checks', side_effect=ValueError('input_changed')):
            with self.assertRaisesRegex(ValueError, 'input_changed'): self.run_refresh()
        self.assertEqual(before, q.digest(approval.path(self.queue)))


if __name__ == '__main__':
    unittest.main()
