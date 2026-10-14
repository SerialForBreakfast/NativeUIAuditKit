"""Authenticity checks reject fabricated, decorative, and unchanged-weight jobs (RCA-20261013-01)."""
import json
from pathlib import Path
import shutil
import sys
import textwrap
import unittest
from unittest import mock
import uuid

import research_approval as approval
import research_queue as q
import research_trust as t

FIXTURE = textwrap.dedent('''
    import json
    from pathlib import Path
    ROOT = Path(__file__).resolve().parents[{depth}]
    OUT = None
    def fabricated_eval():
        # Hardcoded metrics; no pinned file is read.
        (OUT / "predictions.json").write_text(json.dumps([dict(id=i, prediction=1) for i in range(3)]))
    def real_eval():
        model = json.loads((ROOT / "{model}").read_text())
        rows = json.loads((ROOT / "{data}").read_text())
        (OUT / "predictions.json").write_text(json.dumps([dict(id=r, prediction=model["bias"]) for r in rows]))
    def decorative_eval():
        # Reads the model but never the pinned data.
        model = json.loads((ROOT / "{model}").read_text())
        (OUT / "predictions.json").write_text(json.dumps([dict(id=i, prediction=model["bias"]) for i in range(3)]))
    def unchanged_train():
        (ROOT / "{data}").read_bytes()
        (OUT / "weights.bin").write_bytes((ROOT / "{model}").read_bytes())
    def produce_model():
        (OUT / "weights.bin").write_bytes(b"trained")
        (OUT / "model.json").write_text(json.dumps(dict(path=str(OUT / "weights.bin"))))
    def eval_from_dependency(read_weights):
        deps = json.loads((OUT / "dependencies.json").read_text())
        model = json.loads((ROOT / deps[0]["outputs"][0]["path"]).read_text())
        if read_weights:
            open(model["path"], "rb").read()
        (OUT / "predictions.json").write_text(json.dumps([dict(id=i, prediction=1) for i in range(3)]))
    def eval_reads_weights():
        eval_from_dependency(True)
    def eval_skips_weights():
        eval_from_dependency(False)
    def real_train():
        data = (ROOT / "{data}").read_bytes()
        (OUT / "weights.bin").write_bytes((ROOT / "{model}").read_bytes() + data)
        (OUT / "history.json").write_text(json.dumps([dict(epoch=1, trainLoss=0.5)]))
        (OUT / "fit.json").write_text(json.dumps(dict(epochs=1)))
''')


class TrustTests(unittest.TestCase):
    def setUp(self):
        self.base = q.ROOT / '.build' / f'test-research-trust-{uuid.uuid4().hex}'
        self.addCleanup(shutil.rmtree, self.base, True)
        self.modules, self.queue = self.base / 'modules', self.base / 'queue'
        for folder in (self.modules, self.queue):
            folder.mkdir(parents=True)
        self.model = self.base / 'model.json'
        self.model.write_text(json.dumps(dict(bias=1)))
        self.data = self.base / 'data.json'
        self.data.write_text(json.dumps([1, 2, 3]))
        depth = len(self.modules.relative_to(q.ROOT).parts)
        (self.modules / 'trust_fixture.py').write_text(FIXTURE.format(
            depth=depth, model=q.relative(self.model), data=q.relative(self.data)))
        self.log = self.base / 'ExperimentLog.md'
        self.log.write_text('TRUST-R1 registered before the run\n')

    def pin(self, path):
        return dict(path=q.relative(path), sha256=q.digest(path))

    def spec(self, step, kind='evaluation', **changes):
        spec = dict(version=t.SPEC_V2, id='job-a', task='TRUST', owner='Test-NUIAK', kind='screen',
                    hypothesis='The model predicts each pinned case.', decisionRule='Every case has 1 prediction.',
                    question='Does the pinned model produce 1 prediction for each pinned case?',
                    controlledComparison='Pinned cases against the produced prediction rows.',
                    nextActionByOutcome={'supported': 'Use the predictions in the comparison.',
                                         'contradicted': 'Diagnose the evaluator before any decision.'},
                    authority='diagnostic', jobKind=kind,
                    adapter=dict(type='python-callable', steps=['trust_fixture.' + step], outputAttributes=['trust_fixture.OUT']),
                    inputs=[self.pin(self.model), self.pin(self.data)],
                    evidence=dict(reads=[q.relative(self.model), q.relative(self.data)],
                                  model=q.relative(self.model), predictions='predictions.json', membershipCount=3),
                    limits=dict(timeoutSeconds=20, maxOutputBytes=100000, maxAttempts=1))
        spec.update(changes)
        return spec

    def training(self, step):
        return self.spec(step, kind='training', authority='training', inputs=[],
                         evidence=dict(reads=[q.relative(self.data), q.relative(self.model)], weights='weights.bin',
                                       history='history.json', trainingReport='fit.json'),
                         training=dict(experimentLogRunId='TRUST-R1', membership=[self.pin(self.data)],
                                       initialization=self.pin(self.model), epochs=1, storageBudgetBytes=200000,
                                       acceptanceEvidence='The weights change from the initialization.', resume='restart'))

    def submit_and_run(self, spec, approve=True):
        path = self.base / 'spec.json'
        path.write_text(json.dumps(spec))
        with mock.patch.object(q, 'EXPERIMENT_LOG', self.log):
            q.submit(path, self.queue, self.modules)
            if approve:
                approval.approve(self.queue, spec['id'], 'agent:trust-test', 'approve after authenticity checks', self.modules)
            report = q.run(self.queue, self.modules, 5, sys.executable, self.base / 'lock')
        result = self.queue / 'jobs' / spec['id'] / 'attempts/1/result.json'
        return report, q.load(result) if result.exists() else None

    def test_real_evaluation_completes(self):
        report, result = self.submit_and_run(self.spec('real_eval'))
        self.assertEqual(result['status'], 'complete', result.get('reason'))
        reads = q.load(self.queue / 'jobs/job-a/attempts/1/reads.json')['files']
        self.assertIn(str(self.data.resolve()), reads)

    def test_fabricated_evaluation_fails(self):
        _, result = self.submit_and_run(self.spec('fabricated_eval'))
        self.assertEqual((result['status'], result['reason']), ('failed', 'evidence_not_read:' + q.relative(self.model)))

    def test_decorative_pin_fails(self):
        _, result = self.submit_and_run(self.spec('decorative_eval'))
        self.assertEqual((result['status'], result['reason']), ('failed', 'evidence_not_read:' + q.relative(self.data)))

    def test_training_with_unchanged_weights_fails(self):
        _, result = self.submit_and_run(self.training('unchanged_train'))
        self.assertEqual((result['status'], result['reason']), ('failed', 'training_weights_unchanged'))

    def test_real_training_completes(self):
        _, result = self.submit_and_run(self.training('real_train'))
        self.assertEqual(result['status'], 'complete', result.get('reason'))

    def test_unapproved_job_never_runs(self):
        report, result = self.submit_and_run(self.spec('real_eval'), approve=False)
        self.assertEqual(report, [('job-a', 'not_approved')])
        self.assertIsNone(result)

    def test_registration_rules(self):
        cases = [
            (dict(question=' '), 'question_missing'),
            (dict(owner='ambiguous-worker'), 'owner_not_machine_project'),
            (dict(nextActionByOutcome={'supported': 'Use it now please.'}), 'next_action_by_outcome_missing'),
            (dict(jobKind='aggregation', evidence={}), 'aggregation_dependencies_missing'),
            (dict(evidence=dict(reads=['not/pinned.json'], predictions='p.json', membershipCount=1)), 'evidence_read_not_pinned'),
            (dict(jobKind='analytic'), 'analytic_declares_no_evidence'),
            (dict(evidence=dict(reads=[], predictions='p.json', membershipCount=1)), 'evaluation_reads_missing'),
        ]
        for change, reason in cases:
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                q.validate(self.spec('real_eval', **change), self.modules)

    def test_empty_membership_list_is_rejected(self):
        config = self.base / 'shard-config.json'
        config.write_text(json.dumps(dict(shard=3, sources=[])))
        spec = self.spec('real_eval', stage=[dict(**{'from': self.pin(config)}, to='config.json')])
        with self.assertRaisesRegex(ValueError, 'empty_membership_list:sources'):
            q.validate(spec, self.modules)
        config.write_text(json.dumps(dict(shard=3, sources=['a'])))
        q.validate(self.spec('real_eval', stage=[dict(**{'from': self.pin(config)}, to='config.json')]), self.modules)

    def test_approval_rules(self):
        spec = self.spec('real_eval')
        path = self.base / 'spec.json'
        path.write_text(json.dumps(spec))
        q.submit(path, self.queue, self.modules)
        for approver, reason, error in [('anyone', 'a sufficient reason', 'approver_format'),
                                        ('agent:x', 'short', 'approval_reason')]:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                approval.approve(self.queue, 'job-a', approver, reason, self.modules)
        with self.assertRaisesRegex(ValueError, 'test_approver_on_live_queue'):
            approval.approve(q.QUEUE, 'job-a', 'test', 'a sufficient reason', self.modules)
        record = approval.approve(self.queue, 'job-a', 'agent:x', 'approve after authenticity checks', self.modules)
        self.assertEqual(record['approver'], 'agent:x')
        approval.revoke(self.queue, 'job-a', 'maintainer', 'veto for the test')
        self.assertEqual(approval.approved_map(self.queue), {})
        events = [e['action'] for e in approval.load(self.queue)['events']]
        self.assertEqual(events, ['approve', 'revoke'])

    def test_legacy_v1_needs_test_approver(self):
        spec = self.spec('real_eval')
        legacy = {k: v for k, v in spec.items() if k not in
                  ('question', 'controlledComparison', 'nextActionByOutcome', 'jobKind', 'evidence')}
        legacy.update(version='research-spec-v1', owner='test')
        path = self.base / 'spec.json'
        path.write_text(json.dumps(legacy))
        q.submit(path, self.queue, self.modules)
        with self.assertRaisesRegex(ValueError, 'approval_requires_spec_v2'):
            approval.approve(self.queue, 'job-a', 'agent:x', 'approve after authenticity checks', self.modules)

    def dependent_evaluation(self, step):
        producer = self.spec('produce_model', kind='analytic', id='producer', inputs=[], evidence={})
        self.submit_and_run(producer)
        consumer = self.spec(step, id='consumer', inputs=[], evidence=dict(predictions='predictions.json', membershipCount=3),
                             dependencies=[dict(job='producer', specSHA256=q.text_digest(producer), outputs=['model.json'])])
        _, result = self.submit_and_run(consumer)
        return result

    def test_evaluation_must_read_dependency_weights(self):
        self.assertEqual(self.dependent_evaluation('eval_reads_weights')['status'], 'complete')

    def test_evaluation_without_weight_read_fails(self):
        result = self.dependent_evaluation('eval_skips_weights')
        self.assertEqual(result['status'], 'failed')
        self.assertTrue(result['reason'].startswith('evidence_not_read:'), result['reason'])
        self.assertTrue(result['reason'].endswith('weights.bin'), result['reason'])

    def test_drift_is_reported(self):
        self.submit_and_run(self.spec('real_eval'))
        job = self.queue / 'jobs/job-a'
        self.assertEqual(t.drift(job), [])
        fixture = self.modules / 'trust_fixture.py'
        fixture.write_text(fixture.read_text() + '\n# changed after the run\n')
        self.assertEqual(t.drift(job), [q.relative(fixture)])
        self.assertEqual(q.state(job)[0], 'complete')
        row=q.summarize(self.queue,write=False)['jobs'][0]
        self.assertEqual(row['trust'],'drifted')
        self.assertEqual(row['reproducibility'],'source-changed')
        self.assertFalse(approval.is_approved(self.queue, q.load(job / 'spec.json')))

    def test_missing_epoch_history_fails(self):
        fixture = self.modules / 'trust_fixture.py'
        fixture.write_text(fixture.read_text().replace('(OUT / "history.json").write_text', '(OUT / "other.json").write_text'))
        _, result = self.submit_and_run(self.training('real_train'))
        self.assertEqual(result['reason'], 'training_history_missing')

    def test_wrong_epoch_count_fails(self):
        fixture = self.modules / 'trust_fixture.py'
        fixture.write_text(fixture.read_text().replace('dict(epochs=1)', 'dict(epochs=2)'))
        _, result = self.submit_and_run(self.training('real_train'))
        self.assertEqual(result['reason'], 'training_history_epoch_mismatch')

    def test_duplicate_prediction_ids_fail(self):
        fixture = self.modules / 'trust_fixture.py'
        fixture.write_text(fixture.read_text().replace('dict(id=r, prediction=', 'dict(id=1, prediction='))
        _, result = self.submit_and_run(self.spec('real_eval'))
        self.assertEqual(result['reason'], 'evaluation_prediction_ids_duplicate')

    def test_approval_saves_reproducible_checks(self):
        self.submit_and_run(self.spec('real_eval'))
        record = approval.load(self.queue)['jobs']['job-a']
        self.assertEqual(q.text_digest(record['checks']), record['checksSHA256'])
        self.assertTrue(record['checks']['code'])

    def test_bulk_dashboard_approval_fails(self):
        from research_dashboard_server import Controller
        with self.assertRaisesRegex(ValueError, 'one_job_approval_required'):
            Controller(self.queue, self.modules).add([{}, {}])

if __name__ == '__main__':
    unittest.main()
