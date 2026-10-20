import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
import research_queue as q
import native_storage458 as worker


class Boundaries(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=q.ROOT/'.build')
        self.addCleanup(self.tmp.cleanup)
        worker.OUT = Path(self.tmp.name)

    def test_capture_failure_does_not_compact(self):
        with patch.object(worker.storage, 'local_compact') as compact:
            with self.assertRaises(ValueError):
                worker.compact_after(Mock(side_effect=ValueError('capture failed')))
            compact.assert_not_called()

    def test_retention_failure_does_not_repeat_capture(self):
        step = Mock()
        with patch.object(worker.storage, 'local_compact', side_effect=ValueError('busy')):
            with self.assertRaisesRegex(ValueError, 'busy'): worker.compact_after(step)
        step.assert_called_once()

    def test_success_runs_retention_after_capture(self):
        calls = []
        with patch.object(worker.storage, 'local_compact', side_effect=lambda _:calls.append('retention')):
            worker.compact_after(lambda:calls.append('capture'))
        self.assertEqual(calls, ['capture', 'retention'])

    def test_serial_capture_specs_preserve_supported_adapter(self):
        from test_recovery_capture_gate437 import GateTests
        import recovery_capture_gate437 as gate
        fixture = GateTests()
        fixture.setUp()
        try:
            children, _ = gate.prepare(fixture.spec, fixture.queue, fixture.plan, fixture.output)
            worker.serial_children(children)
            self.assertEqual(len(children), 6)
            for index, child in enumerate(children):
                self.assertEqual(child['adapter']['steps'], ['template_bridge395.capture'])
                self.assertEqual(child['retention'], 'verified-png-hardlinks-v1')
                q.validate(child)
                if index:
                    dep = child['dependencies'][-1]
                    self.assertEqual(dep['specSHA256'], q.text_digest(children[index-1]))
                    self.assertEqual(dep['outputs'], ['retention/compaction.json'])
        finally:
            fixture.temp.cleanup()

if __name__ == '__main__': unittest.main()
