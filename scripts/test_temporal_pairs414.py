"""T47 temporal pair evaluation: unit checks and isolated-queue qualification on retained PROGRAM384-D1 pairs."""
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
import research_queue as q
import experiment_batch402 as batches
import hcf_templates395 as templates
from temporal_pairs414 import parameters, check_pair, manifest, oriented, case, summarize, prior_values

D1 = 'reports/work/TEMPORAL414/pairs-d1.json'
BASELINE = 'reports/work/FOCUS-329/run/last.pt'
SEED42 = 'reports/work/research-queue/jobs/trust-replay-01-v1/attempts/1/out/last.pt'
D1_PREDICTIONS = 'reports/work/research-queue/jobs/program384-d1-evaluate42-v2/attempts/1/out/predictions.json'
FIXED = dict(stable=0.15, changed=0.85)


def pin(name='a'):
    return dict(path='reports/' + name + '.png', sha256=hashlib.sha256(name.encode()).hexdigest())


def pair(kind='movement', before='x', after='y', **extra):
    row = dict(id='p-' + kind, group='g', role='development', kind=kind, changed=int(kind == 'movement'),
               condition=kind, sourceDomain='authored', images=[pin('a'), pin('b')],
               endpoints=dict(before=before, after=after),
               action=dict(source='authored-render', evidence=pin('r')))
    row.update(extra)
    return row


class UnitTests(unittest.TestCase):
    def test_parameters(self):
        self.assertEqual(parameters(dict(direction='reverse', thresholds=FIXED)), 'reverse')
        for value, error in [(dict(direction='sideways', thresholds=FIXED), 'temporal_direction'),
                             (dict(direction='forward', thresholds=dict(stable=0.2, changed=0.85)), 'temporal_thresholds_fixed'),
                             (dict(direction='forward'), 'temporal_parameters')]:
            with self.assertRaisesRegex(ValueError, error): parameters(value)

    def test_pair_refusals(self):
        check_pair(pair()); check_pair(pair('no-op', 'x', 'x'))
        for row, error in [(pair(endpoints=dict(before='x')), 'pair_endpoint_identity_missing'),
                           (pair(endpoints=dict(before='x', after='')), 'pair_endpoint_identity_missing'),
                           (pair(endpoints=dict(before=None, after='y')), 'pair_endpoint_identity_missing'),
                           (pair('no-op', 'x', 'y'), 'pair_label_endpoint_conflict'),
                           (pair('movement', 'x', 'x'), 'pair_label_endpoint_conflict'),
                           (pair('content-only', 'x', 'x', images=[pin('a'), pin('a')]), 'pair_content_unchanged'),
                           (pair(action=dict(source='guess', evidence=pin('r'))), 'pair_action_receipt'),
                           (pair(role='final-audit'), 'pair_role')]:
            with self.assertRaisesRegex(ValueError, error): check_pair(row)
        bare = pair(); bare.pop('action')
        with self.assertRaisesRegex(ValueError, 'pair_fields'): check_pair(bare)

    def test_reverse_swaps_images_and_endpoints(self):
        row = pair()
        back = oriented(row, 'reverse')
        self.assertEqual(back['images'], row['images'][::-1])
        self.assertEqual(back['endpoints'], dict(before='y', after='x'))
        self.assertEqual(back['changed'], 1); self.assertIs(oriented(row, 'forward'), row)

    def test_outcomes_gains_losses(self):
        moved, still = pair(), pair('no-op', 'x', 'x', id='p-still')
        lost = case(moved, .5, .9)          # abstention after a prior success
        gained = case(still, .1, .9)        # prior false change, now correct
        false = case(still, .95, None)
        self.assertEqual((lost['outcome'], lost['lost'], lost['gain']), ('abstention', True, False))
        self.assertEqual((gained['outcome'], gained['gain']), ('correct', True))
        self.assertEqual((false['outcome'], false['gain'], false['lost']), ('false-change', False, False))
        report = summarize([lost, gained], 'forward', dict(kind='pinned-predictions'))
        self.assertEqual((report['gains'], report['lostPriorSuccesses']), (['p-still'], ['p-movement']))
        self.assertEqual(report['slices']['kind:no-op']['gained'], 1)
        self.assertEqual(report['legacyCounts']['authored/movement/g']['abstentions'], 1)
        self.assertFalse(report['modelAccepted']); self.assertFalse(report['decisions']['zeroLostPriorSuccesses'])
        self.assertIsNone(summarize([false], 'forward', None)['decisions']['gainWithoutLoss'])
        with self.assertRaisesRegex(ValueError, 'prior_membership'):
            prior_values(dict(rows=[dict(id='other', probability=.5)]), [moved])

    def test_retained_manifest_counts(self):
        rows = manifest(q.load(q.ROOT / D1))
        self.assertEqual(len(rows), 1408)
        self.assertEqual(sum(r['role'] == 'train' for r in rows), 1392)
        self.assertEqual(sum(r['action']['source'] == 'native-receipt' for r in rows), 16)

    def test_compiler_rejects_bad_parameters(self):
        doc = description('t47-bad', D1, BASELINE)
        doc['parameters']['thresholds'] = dict(stable=0.2, changed=0.8)
        with self.assertRaisesRegex(ValueError, 'temporal_thresholds_fixed'):
            batches.compile_batch(dict(version='experiment-batch-v1', jobs=[doc]))
        doc = description('t47-bad', D1, BASELINE); doc['inputs'].pop('pairs')
        with self.assertRaisesRegex(ValueError, 'template_inputs'):
            batches.compile_batch(dict(version='experiment-batch-v1', jobs=[doc]))


def description(ident, pairs, model, direction='forward', prior=None):
    inputs = dict(pairs=dict(file=pairs), model=dict(file=model))
    if prior:
        inputs['prior'] = prior
    return dict(version='hcf-template-description-v1', id=ident, owner='test-NUIAK', template='T47',
                question='Does the pinned transition model keep retained pair decisions?',
                decision='Reject a model that loses a previous success.', inputs=inputs,
                parameters=dict(direction=direction, thresholds=FIXED), dependencies=[])


class QueueTests(unittest.TestCase):
    """Positive and negative paths through the actual queue on a retained D1 subset."""

    def test_actual_queue_and_second_description(self):
        doc = q.load(q.ROOT / D1)
        # 6 authored training pairs per kind plus all 16 native development pairs.
        chosen = []
        for kind in ('movement', 'content-only', 'no-op'):
            chosen += [r for r in doc['rows'] if r['kind'] == kind and r['role'] == 'train'][:6]
        chosen += [r for r in doc['rows'] if r['role'] == 'development']
        recorded = {r['id']: r for r in q.load(q.ROOT / D1_PREDICTIONS)['rows']}
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='temporal414-') as folder:
            root = Path(folder); queue = root / 'queue'
            small = root / 'pairs.json'; q.save(small, dict(doc, rows=chosen))
            rel = q.relative(small)
            docs = [description('t47-baseline', rel, BASELINE),
                    description('t47-control42', rel, SEED42, prior=dict(job='t47-baseline', output='predictions.json')),
                    description('t47-reverse', rel, BASELINE, 'reverse')]
            batches.register_batch(dict(version='experiment-batch-v1', jobs=docs), queue, [d['id'] for d in docs], approver='test')
            self.assertEqual(q.run(queue, max_jobs=3, lock=root / 'lock', job_ids=[d['id'] for d in docs]),
                             [('t47-baseline', 'complete'), ('t47-control42', 'complete'), ('t47-reverse', 'complete')])
            out = {d['id']: queue / 'jobs' / d['id'] / 'attempts/1/out' for d in docs}
            control = q.load(out['t47-control42'] / 'benchmark_summary.json')
            cases = q.load(out['t47-control42'] / 'cases.json')['rows']
            # The T47 control reproduces the recorded D1 seed-42 and baseline probabilities per case.
            for c in cases:
                self.assertAlmostEqual(c['probability'], recorded[c['id']]['probability'], places=5)
                self.assertAlmostEqual(c['priorProbability'], recorded[c['id']]['baselineProbability'], places=5)
            self.assertEqual(control['totals']['frames'], len(chosen)); self.assertFalse(control['modelAccepted'])
            self.assertEqual(control['prior']['kind'], 'pinned-predictions')
            reverse = q.load(out['t47-reverse'] / 'benchmark_summary.json')
            self.assertEqual(reverse['prior'], dict(kind='same-model-forward'))
            forward = {r['id']: r['probability'] for r in q.load(out['t47-baseline'] / 'predictions.json')['rows']}
            for c in q.load(out['t47-reverse'] / 'cases.json')['rows']:
                self.assertAlmostEqual(c['priorProbability'], forward[c['id']], places=6)
            # Negative: a pair without an endpoint identity is refused before any output.
            bad = copy.deepcopy(dict(doc, rows=chosen)); del bad['rows'][0]['endpoints']['after']
            q.save(root / 'bad.json', bad)
            # Negative: a reverse arm with an external prior is refused.
            negatives = [description('t47-endpoint', q.relative(root / 'bad.json'), BASELINE),
                         description('t47-prior', rel, BASELINE, 'reverse', prior=dict(job='t47-baseline', output='predictions.json'))]
            batches.register_batch(dict(version='experiment-batch-v1', jobs=negatives), queue, [d['id'] for d in negatives], approver='test')
            for ident, reason in (('t47-endpoint', 'pair_endpoint_identity_missing'), ('t47-prior', 'reverse_prior_internal')):
                self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=[ident]), [(ident, 'failed')])
                attempt = queue / 'jobs' / ident / 'attempts/1'
                self.assertFalse((attempt / 'out/benchmark_summary.json').exists())
                self.assertIn(reason, (attempt / 'stderr.log').read_text())



SETTINGS = 'reports/work/TEMPORAL414/pairs-settings.json'
RULE = 'reports/work/SETTINGS-STABILITY-23/retained-final/result.json'
RULE_SOURCE = 'scripts/settings_focus_stability.py'


class RuleTests(unittest.TestCase):
    """The guarded Settings rule as a T47 scorer arm, against the model on the same reviewed pairs."""

    def test_parameters_and_decisions(self):
        from temporal_pairs414 import decided
        self.assertEqual(parameters(dict(direction='forward', thresholds=FIXED, scorer='settings-guarded-rule')), 'forward')
        for value, error in [(dict(direction='reverse', thresholds=FIXED, scorer='settings-guarded-rule'), 'rule_direction'),
                             (dict(direction='forward', thresholds=FIXED, scorer='oracle'), 'temporal_scorer')]:
            with self.assertRaisesRegex(ValueError, error): parameters(value)
        self.assertEqual(decided(dict(decision=None, reason='rule_abstained')), None)
        self.assertEqual(case(pair(), dict(decision=1, reason='rule_switch'), .5)['gain'], True)

    def test_rule_arm_through_queue(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='temporal414-rule-') as folder:
            root = Path(folder); queue = root / 'queue'

            def rule(ident, source=RULE_SOURCE):
                doc = description(ident, SETTINGS, source, prior=dict(job='rule-a-model', output='predictions.json'))
                doc['inputs']['rule'] = dict(file=RULE); doc['parameters']['scorer'] = 'settings-guarded-rule'
                return doc
            docs = [description('rule-a-model', SETTINGS, BASELINE), rule('rule-guarded')]
            batches.register_batch(dict(version='experiment-batch-v1', jobs=docs), queue, [d['id'] for d in docs], approver='test')
            self.assertEqual(q.run(queue, max_jobs=2, lock=root / 'lock', job_ids=[d['id'] for d in docs]),
                             [('rule-a-model', 'complete'), ('rule-guarded', 'complete')])
            report = q.load(queue / 'jobs/rule-guarded/attempts/1/out/benchmark_summary.json')
            cases = {c['id']: c for c in q.load(queue / 'jobs/rule-guarded/attempts/1/out/cases.json')['rows']}
            self.assertEqual(report['scorer'], 'settings-guarded-rule'); self.assertFalse(report['modelAccepted'])
            # Page changes are outside the rule context. The 5 same-screen actions keep the retained guarded summary.
            self.assertEqual(sum(c['reason'] == 'unsupported_context' for c in cases.values()), 2)
            self.assertEqual(report['ruleControls'], q.load(q.ROOT / RULE)['summaries']['guarded'])
            # Negative: the rule arm must pin the rule implementation as its scorer.
            batches.register_batch(dict(version='experiment-batch-v1', jobs=[rule('rule-pin', BASELINE)]), queue,
                                   ['rule-pin'], approver='test')
            self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=['rule-pin']), [('rule-pin', 'failed')])
            self.assertIn('rule_scorer_pin', (queue / 'jobs/rule-pin/attempts/1/stderr.log').read_text())


if __name__ == '__main__':
    unittest.main()
