"""Restart software tests (EXTENSION408). Synthetic progress files are not model evidence."""
import sys
import unittest
import research_queue as q
import research_execution_policy as policy
import research_extensions as x
from research_continuations import select
from research_dashboard_server import Controller, progress_remaining
from test_research_queue import QueueTests

REASON = 'The parent ran out of time at a third of its epochs.'


class ExtensionTests(unittest.TestCase):
    setUp = QueueTests.setUp
    tearDown = QueueTests.tearDown
    spec = QueueTests.spec
    spec_v2 = QueueTests.spec_v2
    write_spec = QueueTests.write_spec
    submit = QueueTests.submit

    def exhaust(self, ident='parent', reason='timeout', spec=None, progress=(10, 30), approver=True):
        spec = spec or self.spec(id=ident, limits=dict(timeoutSeconds=20, maxOutputBytes=100000, maxAttempts=1))
        self.submit(spec, approve=approver)
        attempt = self.queue/'jobs'/ident/'attempts/1'
        (attempt/'out').mkdir(parents=True)
        q.save(attempt/'attempt.json', dict(startedAt=1000.0))
        if progress:
            q.save(attempt/'progress.json', dict(completed=progress[0], total=progress[1], updatedAt=1200.0, step='fit'))
        q.save(attempt/'result.json', dict(status='failed', reason=reason, wallSeconds=250.0,
                                           specSHA256=q.text_digest(spec), outputs=[]))
        return spec

    def test_estimate_and_suggestion(self):
        self.exhaust()
        row = x.describe('parent', self.queue)
        self.assertEqual(row['estimate']['secondsPerUnit'], 20)
        self.assertEqual(row['estimate']['restartSeconds'], 600)
        self.assertEqual(row['estimate']['remainingAfterProgressSeconds'], 400)
        self.assertEqual(row['suggested'], dict(timeoutSeconds=780, maxOutputBytes=100000))
        self.assertIsNone(row['blocker'])
        self.assertIsNone(row['warning'])
        self.assertEqual(row['successorId'], 'parent-r2')

    def test_no_progress_doubles_timeout(self):
        self.exhaust(progress=(0, 30))
        row = x.describe('parent', self.queue)
        self.assertFalse(row['estimate']['available'])
        self.assertEqual(row['suggested']['timeoutSeconds'], 40)

    def test_save_overrides_policy_and_runs_once(self):
        parent = self.exhaust()
        before = q.digest(self.queue/'jobs/parent/attempts/1/result.json')
        with self.assertRaisesRegex(ValueError, 'requires_maintainer'):
            x.save(q.QUEUE, 'parent', 1000, 100000, REASON, 'test', self.modules)
        outcome = x.save(self.queue, 'parent', 1000, 200000, REASON, 'test', self.modules)
        self.assertEqual(outcome['job'], 'parent-r2')
        self.assertTrue(outcome['approved'])
        spec = q.load(self.queue/'jobs/parent-r2/spec.json')
        self.assertEqual(spec['limits'], dict(timeoutSeconds=1000, maxOutputBytes=200000, maxAttempts=1))
        self.assertEqual({k: v for k, v in spec.items() if k not in ('id', 'limits')},
                         {k: v for k, v in parent.items() if k not in ('id', 'limits')})
        digest = q.text_digest(spec)
        self.assertEqual(policy.seconds(digest, 'diagnostic', 800, self.queue), 1000)
        self.assertEqual(policy.seconds(digest, 'diagnostic', 800), 800)
        self.assertEqual(q.run(self.queue, self.modules, 1, sys.executable, self.lock, job_ids=['parent-r2']),
                         [('parent-r2', 'complete')])
        self.assertEqual(q.run(self.queue, self.modules, 1, sys.executable, self.lock, job_ids=['parent-r2']), [])
        self.assertEqual(q.state(self.queue/'jobs/parent')[0], 'exhausted')
        self.assertEqual(q.digest(self.queue/'jobs/parent/attempts/1/result.json'), before)
        with self.assertRaisesRegex(ValueError, 'successor_exists'):
            x.save(self.queue, 'parent', 1000, 200000, REASON, 'test', self.modules)

    def test_runner_refuses_limit_without_override(self):
        self.submit(self.spec(id='long', limits=dict(timeoutSeconds=1000, maxOutputBytes=100000, maxAttempts=1)))
        with self.assertRaisesRegex(ValueError, 'execution_time_limit'):
            q.run(self.queue, self.modules, 1, sys.executable, self.lock, job_ids=['long'])

    def test_restart_runs_after_ordinary_work_in_save_order(self):
        self.exhaust('first'); self.exhaust('second')
        x.save(self.queue, 'second', 20, 100000, REASON, 'test', self.modules)
        x.save(self.queue, 'first', 20, 100000, REASON, 'test', self.modules)
        self.submit(self.spec(id='zz-new'))
        ready = ['first-r2', 'second-r2', 'zz-new']
        self.assertEqual(select(ready, self.queue), ['zz-new'])
        self.assertEqual(select(ready[:2], self.queue), ['second-r2'])

    def test_refusals(self):
        self.submit(self.spec(id='fresh'))
        with self.assertRaisesRegex(ValueError, 'not_exhausted:pending'):
            x.save(self.queue, 'fresh', 20, 100000, REASON, 'test', self.modules)
        self.exhaust()
        for seconds, size, reason, error in [(10, 100000, REASON, 'timeout_range'), (20, 10, REASON, 'output_range'),
                                             (90000, 100000, REASON, 'timeout_range'), (20, 100000, 'short', 'reason'),
                                             (20.5, 100000, REASON, 'limit_type')]:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                x.save(self.queue, 'parent', seconds, size, reason, 'test', self.modules)
        self.assertFalse((self.queue/'jobs/parent-r2').exists())

    def test_repair_warning_and_same_limits(self):
        self.exhaust(reason='process_failed')
        row = x.describe('parent', self.queue)
        self.assertIn('does not fix', row['warning'])
        self.assertTrue(x.save(self.queue, 'parent', 20, 100000, 'The adapter defect is repaired in the module.',
                               'test', self.modules)['approved'])
        self.assertFalse((self.queue/policy.OVERRIDES).exists())

    def test_chained_successor_id(self):
        self.exhaust()
        x.save(self.queue, 'parent', 20, 100000, REASON, 'test', self.modules)
        self.assertEqual(x.successor_id('parent-r2', self.queue), 'parent-r3')
        self.assertEqual(len(x.successor_id('a' * 64, self.queue)), 64)

    def test_override_approver(self):
        q.save(self.queue/policy.OVERRIDES, dict(version=policy.OVERRIDE_VERSION, events=[],
               specs={'0' * 64: dict(timeoutSeconds=5000, maxOutputBytes=5, by='agent:x')}))
        with self.assertRaisesRegex(ValueError, 'execution_limits_approver'):
            policy.seconds('0' * 64, 'diagnostic', 800, self.queue)
        self.assertEqual(policy.seconds('0' * 64, 'capture', 800, self.queue), 800)
        self.assertEqual(policy.output_bytes('1' * 64, 'training', 100, self.queue), 2 << 30)

    def test_dashboard_inspect_and_save(self):
        self.exhaust(spec=self.spec_v2(id='parent', limits=dict(timeoutSeconds=20, maxOutputBytes=100000, maxAttempts=1)))
        control = Controller(self.queue, self.modules, self.lock)
        rows = {row['job']: row for row in control.snapshot()['jobs']}
        self.assertEqual(rows['parent']['extension']['suggested']['timeoutSeconds'], 780)
        with self.assertRaisesRegex(ValueError, 'extension_fields'):
            control.extend(dict(job='parent'))
        result = control.extend(dict(job='parent', timeoutSeconds=900, maxOutputBytes=100000, reason=REASON))
        self.assertTrue(result['approved'], result)
        self.assertEqual(q.load(self.queue/policy.OVERRIDES)['specs'][result['specSHA256']]['by'], 'maintainer')
        rows = {row['job']: row for row in control.snapshot()['jobs']}
        self.assertEqual(rows['parent-r2']['extendedFrom']['parent'], 'parent')
        self.assertEqual(rows['parent-r2']['displayState'], 'ready')
        self.assertIsNotNone(rows['parent']['extension']['blocker'])

    def test_progress_remaining(self):
        progress = dict(completed=10, total=30, updatedAt=1200.0)
        self.assertEqual(progress_remaining(progress, 1000.0, now=1200.0), 400)
        self.assertEqual(progress_remaining(progress, 1000.0, now=1300.0), 300)
        self.assertIsNone(progress_remaining(dict(completed=0, total=30, updatedAt=1200.0), 1000.0))
        self.assertIsNone(progress_remaining(None, 1000.0))


if __name__ == '__main__':
    unittest.main()
