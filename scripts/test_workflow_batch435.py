"""Test description authoring and read-only graph inspection."""
from unittest import main

import research_queue as q
import workflow_batch435 as workflow
import test_model_decision434 as fixtures


class WorkflowTests(fixtures.DecisionTests):
    def request(self):
        return dict(version='model-decision-request-v1', id='authored-experiment',
                    question=self.plan['question'], controlledComparison=self.plan['controlledComparison'],
                    training='training', baseline=[p['baseline'] for p in self.pairs],
                    candidate=[p['candidate'] for p in reversed(self.pairs)])

    def test_pairing_uses_inputs_not_order_and_executes(self):
        plan = workflow.author(self.request(), self.queue)
        actual = {(p['baseline'], p['candidate']) for p in plan['pairs']}
        self.assertEqual(actual, {(p['baseline'], p['candidate']) for p in self.pairs})
        manifest = self.compile(plan)
        self.execute(manifest)
        report = workflow.inspect(manifest, self.queue)
        self.assertEqual(report['counts'], {'finished': 4})
        self.assertFalse(report['modelAccepted'])
        self.assertFalse(report['executionChanged'])
        self.assertIn('Standard proposal selection: 1 gains, 0 losses', workflow.summary(report))

    def test_author_rejects_missing_and_duplicate_membership(self):
        request = self.request()
        request['candidate'].pop()
        with self.assertRaisesRegex(ValueError, 'workflow_unmatched_suite'):
            workflow.author(request, self.queue)
        request = self.request()
        request['candidate'] *= 2
        with self.assertRaisesRegex(ValueError, 'workflow_score_ids'):
            workflow.author(request, self.queue)

    def test_prepare_register_restart_without_duplicate_execution(self):
        output = self.root/'prepared'
        first = workflow.prepare(self.request(), output, self.queue, register=True, approve=True)
        manifest = q.load(q.ROOT/first['manifest'])
        self.execute(manifest)
        second = workflow.prepare(self.request(), output, self.queue, register=True, approve=True)
        self.assertEqual(first, second)
        for row in manifest['jobs']:
            self.assertEqual(len(q.attempts_of(self.queue/'jobs'/row['job'])), 1)
        self.assertFalse(second['executionStarted'])
        changed = self.request()
        changed['question'] = 'Does a conflicting request overwrite a prior description?'
        with self.assertRaisesRegex(ValueError, 'decision_immutable_conflict'):
            workflow.prepare(changed, output, self.queue, register=True, approve=True)

    def test_author_rejects_traversal_and_wrong_model(self):
        request = self.request()
        request['baseline'][0] = '../outside'
        with self.assertRaisesRegex(ValueError, 'workflow_job_id'):
            workflow.author(request, self.queue)
        path = self.queue/'jobs/native-candidate/spec.json'
        spec = q.load(path)
        spec['template']['inputs']['model']['job'] = 'other'
        q.save(path, spec, replace=True)
        with self.assertRaisesRegex(ValueError, 'workflow_candidate_model'):
            workflow.author(self.request(), self.queue)

    def test_status_distinguishes_eligible_and_waiting_without_writes(self):
        manifest = self.compile()
        import model_decision_batch434 as compiler
        compiler.register(manifest, self.queue, approve=True)
        before = {str(p): q.digest(p) for p in self.queue.rglob('*') if p.is_file()}
        report = workflow.inspect(manifest, self.queue)
        self.assertEqual(report['counts']['eligible-pending-runner-checks'], 1)
        self.assertEqual(report['counts']['waiting'], 3)
        self.assertEqual(report['eta'], 'ETA unavailable')
        after = {str(p): q.digest(p) for p in self.queue.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_status_reports_missing_approval_and_changed_evidence(self):
        manifest = self.compile()
        import model_decision_batch434 as compiler
        compiler.register(manifest, self.queue)
        report = workflow.inspect(manifest, self.queue)
        leaf = next(r for r in report['rows'] if r['job'] == 'experiment-a-compare-01')
        self.assertIn('approval', ' '.join(leaf['blockers']))
        path = self.queue/'jobs/native-candidate/attempts/1/out/selection.json'
        q.save(path, {}, replace=True)
        report = workflow.inspect(manifest, self.queue)
        leaf = next(r for r in report['rows'] if r['job'] == 'experiment-a-compare-01')
        self.assertIn('dependency_output_changed', ' '.join(leaf['blockers']))
        self.assertEqual(leaf['dispatch'], 'blocked')

    def test_status_preserves_failed_attempt_and_shows_impact(self):
        path = self.queue/'jobs/native-candidate/spec.json'
        spec = q.load(path)
        spec['limits'] = dict(maxAttempts=1)
        q.save(path, spec, replace=True)
        self.reinventory('native-candidate', 'failed')
        manifest = self.compile()
        import model_decision_batch434 as compiler
        compiler.register(manifest, self.queue)
        report = workflow.inspect(manifest, self.queue)
        failed = next(r for r in report['rows'] if r['job'] == 'native-candidate')
        self.assertEqual(failed['execution'], 'exhausted')
        self.assertTrue(failed['blockers'])
        self.assertEqual(failed['affectedGeneratedJobs'], 4)
        self.assertEqual(len(q.attempts_of(self.queue/'jobs/native-candidate')), 1)


if __name__ == '__main__':
    main()
