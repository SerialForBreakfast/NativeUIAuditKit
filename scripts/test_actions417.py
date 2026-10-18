"""ACTIONS417: approval during execution, post-run authorization, and training report schemas."""
import json
import os
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

import research_queue as q
import research_approval as approval
import research_trust as trust
import test_research_queue as _queue_tests


class Base(unittest.TestCase):
    setUp = _queue_tests.QueueTests.setUp
    tearDown = _queue_tests.QueueTests.tearDown
    spec = _queue_tests.QueueTests.spec
    spec_v2 = _queue_tests.QueueTests.spec_v2
    write_spec = _queue_tests.QueueTests.write_spec
    submit = _queue_tests.QueueTests.submit
    run_queue = _queue_tests.QueueTests.run_queue
    attempt = _queue_tests.QueueTests.attempt

    def job(self, ident, step='produce', **changes):
        return self.spec_v2(id=ident, adapter=dict(type='python-callable', steps=['rq_fixture.' + step],
                                                   outputAttributes=['rq_fixture.OUT']), **changes)

    def approve(self, ident):
        return approval.approve(self.queue, ident, 'test', 'isolated test fixture approval', self.modules)


class ApprovalTests(Base):
    def test_concurrent_approvals_keep_both_records(self):
        for ident in ('job-a', 'job-b'):
            self.submit(self.job(ident), approve=False)
        errors = []
        def run(ident):
            try:
                self.approve(ident)
            except ValueError as error:
                errors.append(error)
        threads = [threading.Thread(target=run, args=(i,)) for i in ('job-a', 'job-b')]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(errors, [])
        self.assertEqual(set(approval.load(self.queue)['jobs']), {'job-a', 'job-b'})

    def test_approval_does_not_wait_for_the_runner(self):
        self.submit(self.job('job-a'), approve=False)
        with q.host_lock(self.lock), q.host_lock(self.queue / 'batch-dispatch.lock'):
            start = time.monotonic()
            self.approve('job-a')
            self.assertLess(time.monotonic() - start, 5)

    def test_register_batch_takes_no_dispatch_lock(self):
        import experiment_batch402 as batches
        used = []
        real = q.host_lock
        def record(path, *args, **kwargs):
            used.append(Path(path).name)
            return real(path, *args, **kwargs)
        doc = dict(id='job-a')
        with mock.patch.object(batches, 'compile_batch', return_value=[doc]), \
             mock.patch.object(batches.templates, 'register', return_value=dict(id='job-a')), \
             mock.patch.object(batches.approval, 'approve') as approve, \
             mock.patch.object(q, 'host_lock', side_effect=record):
            result = batches.register_batch(dict(version='experiment-batch-v1', jobs=[doc]), self.queue,
                                            approved=['job-a'], approver='test')
        self.assertTrue(result['jobs'][0]['approved'])
        approve.assert_called_once()
        self.assertNotIn('batch-dispatch.lock', used)
        self.assertNotIn('research-queue.lock', used)

    def test_concurrent_registration_of_the_same_id_is_safe(self):
        spec = self.job('job-a')
        outcomes = []
        def run():
            try:
                outcomes.append(q.submit(self.write_spec(spec, name=f'spec-{threading.get_ident()}.json'),
                                         self.queue, self.modules))
            except ValueError as error:
                outcomes.append(str(error))
        threads = [threading.Thread(target=run) for _ in range(4)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(q.load(self.queue / 'jobs/job-a/spec.json'), spec)
        self.assertEqual(sum(o == 'submitted' for o in outcomes), 1)
        self.assertTrue(all(o in ('submitted', 'already_submitted', 'output_collision') for o in outcomes), outcomes)

    def test_interrupted_approval_leaves_a_valid_file(self):
        for ident in ('job-a', 'job-b'):
            self.submit(self.job(ident), approve=False)
        self.approve('job-a')
        with mock.patch.object(os, 'replace', side_effect=OSError('interrupted')):
            with self.assertRaises(OSError):
                self.approve('job-b')
        self.assertEqual(set(approval.load(self.queue)['jobs']), {'job-a'})

    def test_revocation_before_dispatch_prevents_the_start(self):
        self.submit(self.job('job-a'))
        approval.revoke(self.queue, 'job-a', 'test', 'withdrawn before dispatch')
        self.run_queue()
        self.assertFalse((self.queue / 'jobs/job-a/attempts/1').exists())

    def test_new_approval_starts_at_the_next_boundary(self):
        self.submit(self.job('job-a'))
        self.submit(self.job('job-b'), approve=False)
        self.run_queue()
        self.assertEqual(q.state(self.queue / 'jobs/job-a')[0], 'complete')
        self.assertFalse((self.queue / 'jobs/job-b/attempts/1').exists())
        self.approve('job-b')
        self.run_queue()
        self.assertEqual(q.state(self.queue / 'jobs/job-b')[0], 'complete')


class PostRunTests(Base):
    def run_with(self, action, ident='job-a'):
        """Run the queue and act once the attempt's step is in progress, not before dispatch."""
        progress = self.attempt(job=ident) / 'progress.json'
        def act():
            deadline = time.monotonic() + 10
            while not progress.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            action()
        thread = threading.Thread(target=act)
        thread.start()
        self.run_queue()
        thread.join()
        return q.load(self.attempt(job=ident) / 'result.json')

    def test_revoking_the_current_approval_fails_acceptance(self):
        self.submit(self.job('job-a', step='brief'))
        result = self.run_with(lambda: approval.revoke(self.queue, 'job-a', 'test', 'revoked during the run'))
        self.assertEqual((result['status'], result['reason']), ('failed', 'approval_revoked_during_run'))

    def test_an_unrelated_approval_change_does_not_fail_the_attempt(self):
        self.submit(self.job('job-a', step='brief'))
        self.submit(self.job('job-b'), approve=False)
        result = self.run_with(lambda: self.approve('job-b'))
        self.assertEqual(result['status'], 'complete')

    def test_a_changed_pinned_file_is_named(self):
        self.submit(self.job('job-a', step='brief'))
        fixture = self.modules / 'rq_fixture.py'
        result = self.run_with(lambda: fixture.write_text(fixture.read_text() + '\n# changed during the run\n'))
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['reason'], 'code_changed_during_run:' + q.relative(fixture))

    def test_missing_or_malformed_closure_fails_clearly(self):
        spec = self.job('job-a')
        self.submit(spec)
        self.run_queue()
        attempt = self.attempt()
        self.assertIsNone(approval.post_run_authorization(self.queue, spec, attempt))
        closure = attempt / 'closure.json'
        saved = closure.read_text()
        closure.write_text(json.dumps(dict(modules='not-a-list')))
        self.assertEqual(approval.post_run_authorization(self.queue, spec, attempt), 'closure_record_invalid')
        closure.unlink()
        self.assertEqual(approval.post_run_authorization(self.queue, spec, attempt), 'closure_record_missing')
        closure.write_text(saved)


class TrainingReportSchemaTests(unittest.TestCase):
    """Report fields that the trust check requires, produced by the real adapter code without training."""
    EVIDENCE = dict(history='history.json', trainingReport='fit.json')

    def setUp(self):
        import tempfile
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT / '.build')
        self.out = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_t06_report_passes_and_records_exposure(self):
        import hcf_factor_train376 as t06
        crop = self.out / 'crop.png'; crop.write_bytes(b'png')
        init = self.out / 'init.pt'; init.write_bytes(b'init')
        rows = [dict(role=r, group=r, path=str(crop), sha256=q.digest(crop)) for r in ('train', 'development')]
        q.save(self.out / 'config.json', dict(profile='balanced', deduplicate=True, seed=371, repeat=5,
                                              initialization=dict(path=q.relative(init), sha256=q.digest(init))))
        def fake(rows, initial, out, **kwargs):
            self.assertEqual(kwargs['repeat'], 5)
            (out / 'history.json').write_text(json.dumps([dict(epoch=i, trainLoss=0.1) for i in range(1, 31)]))
            (out / 'final.pt').write_bytes(b'weights')
            return dict(epochs=30, exposure=dict(uniqueTrainImages=1, repeat=5, samplesPresented=150, optimizerUpdates=30))
        t06.OUT = self.out
        with mock.patch.object(t06.study, 'dependency', return_value=(dict(rows=rows),)), \
             mock.patch('train_focus_ring_detector.train_native_hcf', side_effect=fake):
            t06.train()
        self.assertIsNone(trust.check_training_report(self.out, self.EVIDENCE, 30))
        self.assertEqual(q.load(self.out / 'fit.json')['exposure']['repeat'], 5)
        q.save(self.out / 'fit.json', dict(modelAccepted=False), replace=True)
        self.assertEqual(trust.check_training_report(self.out, self.EVIDENCE, 30), 'training_history_epoch_mismatch')

    def test_t06_rejects_an_invalid_repeat(self):
        import hcf_factor_train376 as t06
        for value in (0, 17, 2.0):
            with self.assertRaisesRegex(ValueError, 'repeat_invalid'):
                t06.validate_config(dict(profile='balanced', deduplicate=True, seed=371, repeat=value))

    def test_t49_finish_writes_the_required_fields(self):
        import transition_training415 as t49
        t49.OUT = self.out
        (self.out / 'last.pt').write_bytes(b'weights')
        q.save(self.out / 'fit.json', dict(configuration=dict(seed=43, epochs=t49.EPOCHS),
                                           history=[dict(loss=0.2) for _ in range(t49.EPOCHS)]))
        t49.finish('control', 43)
        self.assertIsNone(trust.check_training_report(self.out, self.EVIDENCE, t49.EPOCHS))


if __name__ == '__main__':
    unittest.main()
