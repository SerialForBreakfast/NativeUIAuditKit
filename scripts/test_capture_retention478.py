"""Exercise cleanup ordering without device input or capture."""
from contextlib import ExitStack, nullcontext
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import hcf_capture362 as worker
import research_queue as q


class CaptureRetentionTests(unittest.TestCase):
    def exercise(self, failure=None, enabled=True):
        with tempfile.TemporaryDirectory(dir=q.ROOT/'.build') as directory, ExitStack() as stack:
            root = Path(directory)
            helper = root/'helper'
            helper.write_bytes(b'fixture helper')
            events = []
            client = Mock()
            sessions = iter(('first', 'second'))
            def remote(action, session=None):
                events.append((action, session))
                return dict(operationID=next(sessions) if action == 'connect' else session,
                            state='ready' if action == 'connect' else 'closed')
            client.remote.side_effect = remote
            def terminal(receipt, desired):
                if failure == 'disconnect' and desired == 'closed':
                    raise ValueError('test_disconnect')
                return receipt
            client.terminal.side_effect = terminal
            def call(name, *args):
                if name in ('readiness', 'postflight'):
                    return dict(can_run=True, ownership=[dict(state='clear')])
                desired = args[args.index('--desired')+1]
                events.append(('profile', desired))
                return dict(hcf=dict(status='completed', desiredVerified=True, requested=desired,
                    observed=desired, original='standard', mode='ensure',
                    policy='hcf-setting-en-us-23L470-v2'))
            client.call.side_effect = call
            def compact(output):
                events.append(('compact', None))
                if failure == 'compact':
                    raise ValueError('test_compact')
                q.save(output/'compaction.json', dict(pathsRemoved=0))
            fixture = Mock()
            fixture.snapshot.return_value = dict(scene=dict(recipe={}, focused_element_id='a'))
            replacements = [
                (worker, 'CLI', helper), (worker, 'Client', Mock(return_value=client)),
                (worker, 'lock', lambda: nullcontext()), (worker, 'validate_plan', lambda p: None),
                (worker.d, 'Fixture', Mock(return_value=fixture)),
                (worker.d, 'bind_target', Mock(return_value={})), (worker.d, 'run', Mock()),
                (worker.n, 'identity', Mock(return_value=(1, 2, 3))),
                (worker.n, 'settle', Mock()), (worker.dataset351, 'clean', lambda x: x),
                (worker.q, 'live_output_bytes', lambda p: 0)]
            for target, name, value in replacements:
                stack.enter_context(patch.object(target, name, value))
            stack.enter_context(patch('ttr_evidence_compaction458.compact_with_producer_lock', compact))
            plan = dict(version='software-test', helperSHA256=q.digest(helper), binding={'endpoint':'test'},
                profiles=['standard', 'hcf'], originalProfile='standard', cases=[], expectedFrames=0,
                group='test', role='development')
            # The mocked binding matches the explicit test endpoint.
            worker.d.bind_target.return_value = plan['binding']
            if enabled:
                plan['restorationRetention'] = 'verified-png-hardlinks-v1'
            output = root/'capture'
            error = None
            try:
                worker.capture(output, plan)
            except ValueError as exc:
                error = str(exc)
            return events, q.load(output/'capture.json'), error

    def test_closed_retention_precedes_restoration(self):
        events, receipt, error = self.exercise()
        self.assertIsNone(error)
        self.assertTrue(receipt['cleanup'])
        start = events.index(('compact', None))
        self.assertEqual(events[start-1], ('disconnect', 'first'))
        self.assertEqual(events[start+1:start+3], [('connect', None), ('profile', 'standard')])
        self.assertEqual(events[-1], ('disconnect', 'second'))

    def test_retention_failure_preserves_failed_cleanup(self):
        events, receipt, error = self.exercise('compact')
        self.assertIn('test_compact', error)
        self.assertFalse(receipt['cleanup'])
        self.assertEqual(sum(e[0] == 'connect' for e in events), 1)

    def test_uncertain_disconnect_never_compacts(self):
        events, receipt, error = self.exercise('disconnect')
        self.assertIn('test_disconnect', error)
        self.assertFalse(receipt['cleanup'])
        self.assertNotIn(('compact', None), events)

    def test_existing_plan_keeps_existing_behavior(self):
        events, receipt, error = self.exercise(enabled=False)
        self.assertIsNone(error)
        self.assertTrue(receipt['cleanup'])
        self.assertNotIn(('compact', None), events)
        self.assertEqual(sum(e[0] == 'connect' for e in events), 1)


if __name__ == '__main__':
    unittest.main()
