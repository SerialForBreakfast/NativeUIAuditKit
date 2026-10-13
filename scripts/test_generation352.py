"""Test queue capture cleanup without simulator access."""
import signal
import shutil
import unittest
import uuid
from unittest.mock import patch
import generation352 as g
import research_queue as q


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.root = q.ROOT / '.build' / ('generation-test-' + uuid.uuid4().hex)
        self.out = self.root / 'job/attempts/1/out'
        self.out.mkdir(parents=True)
        self.plan = self.root / 'plan.json'
        q.save(self.plan, dict(role='development', trainingEligible=False,
            binding=dict(endpoint='http://127.0.0.1:8080', simulatorUDID='target')))
        q.save(self.root / 'job/spec.json', dict(id='test', capture=dict(
            target='target', endpoint='http://127.0.0.1:8080',
            plan=dict(path=q.relative(self.plan), sha256=q.digest(self.plan)))))
        self.marker = self.root / 'recovery.json'
        self.patches = [patch.object(g, 'OUT', self.out), patch.object(g, 'MARKER', self.marker),
            patch.object(g.compare351, 'validate_capture')]
        for p in self.patches: p.start()

    def tearDown(self):
        for p in reversed(self.patches): p.stop()
        shutil.rmtree(self.root)

    def receipt(self, cleanup):
        (self.out / 'capture').mkdir()
        q.save(self.out / 'capture/capture.json', dict(cleanup=cleanup))

    def test_success_removes_marker(self):
        with patch.object(g.capture, 'run', side_effect=lambda *a, **k: self.receipt(True)):
            g.run()
        self.assertFalse(self.marker.exists())

    def test_failed_cleanup_preserves_marker(self):
        def fail(*args, **kwargs):
            self.receipt(False)
            raise RuntimeError('cleanup failed')
        with patch.object(g.capture, 'run', side_effect=fail), self.assertRaises(RuntimeError):
            g.run()
        self.assertTrue(self.marker.exists())

    def test_existing_marker_prevents_mutation(self):
        q.save(self.marker, dict(previous='unknown'))
        with patch.object(g.capture, 'run') as run, self.assertRaises(FileExistsError):
            g.run()
        run.assert_not_called()

    def test_cancel_handler_allows_cleanup(self):
        def cancelled(*args, **kwargs):
            try:
                signal.getsignal(signal.SIGTERM)(signal.SIGTERM, None)
            finally:
                self.receipt(True)
        with patch.object(g.capture, 'run', side_effect=cancelled), self.assertRaisesRegex(RuntimeError, 'capture_cancelled'):
            g.run()
        self.assertFalse(self.marker.exists())
