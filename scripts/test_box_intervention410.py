"""T41 scored box interventions: unit checks and isolated-queue qualification on retained frames."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import research_queue as q
import experiment_batch402 as batches
import hcf_templates395 as templates
from box_intervention410 import parameters, intervene, compare, summarize

BUNDLE = 'Research/Experiments/backlog405-native-inputs.json'
MODEL = 'reports/work/research-queue/jobs/hcf375c-70-crop-train/attempts/1/out/final.pt'
TOOL = '.build/standard392-swift/arm64-apple-macosx/debug/FocusRingTool'
TALL = 'hcf402-tall-controls-hcf-item-3-0'


def row(score=.9, outcome='correct'):
    arm = dict(scores=[score], boxes=[[10.4, 20.6, 30, 40]], outcome=outcome)
    return dict(id='frame', group='group', profile='hcf', noFocus=False,
                arms={k: copy.deepcopy(arm) for k in ('known-box', 'raw-proposal', 'mapped-proposal')})


class UnitTests(unittest.TestCase):
    def test_parameters(self):
        self.assertEqual(parameters(dict(source='known-box', intervention=dict(kind='none')))[0], 'known-box')
        for value, error in [(dict(source='other', intervention=dict(kind='none')), 'intervention_source'),
                             (dict(source='known-box', intervention=dict(kind='scale')), 'intervention_fields'),
                             (dict(source='known-box', intervention=dict(kind='translate', dx=1)), 'intervention_fields'),
                             (dict(source='known-box', intervention=dict(kind='margin', dw=float('nan'), dh=0)), 'intervention_value'),
                             (dict(source='known-box', intervention=dict(kind='translate', dx=100, dy=0)), 'intervention_value'),
                             (dict(source='known-box', intervention=dict(kind='translate', dx=0, dy=0)), 'intervention_no_change'),
                             (dict(source='known-box'), 'intervention_parameters')]:
            with self.assertRaisesRegex(ValueError, error): parameters(value)

    def test_one_factor(self):
        box = [10.4, 20.6, 30.2, 40]
        self.assertEqual(intervene(box, dict(kind='none')), box)
        self.assertEqual(intervene(box, dict(kind='round')), [10, 21, 31, 40])
        self.assertEqual(intervene(box, dict(kind='translate', dx=1, dy=-2))[2:], box[2:])
        x, y, w, h = intervene(box, dict(kind='margin', dw=-2, dh=4))
        self.assertAlmostEqual(x + w / 2, box[0] + box[2] / 2)
        self.assertEqual([round(w, 6), h], [28.2, 44])
        with self.assertRaisesRegex(ValueError, 'intervention_empty_box'):
            intervene([0, 0, 1, 1], dict(kind='margin', dw=-2, dh=0))

    def test_loss_gain_and_abstention(self):
        truth = [10.4, 20.6, 30, 40]
        lost = compare(row(), truth, 'known-box', dict(kind='round'), [.4], ['h'])
        self.assertTrue(lost['loss']); self.assertEqual(lost['outcome'], 'miss'); self.assertEqual(lost['aboveThreshold'], 0)
        self.assertAlmostEqual(lost['target']['score'] - lost['target']['cachedScore'], -.5)
        gained = compare(row(.4, 'miss'), truth, 'raw-proposal', dict(kind='round'), [.95], ['h'])
        self.assertTrue(gained['gain'])
        report = summarize([lost], 'known-box', dict(kind='round'))
        self.assertEqual(report['lostPriorSuccesses'], ['frame']); self.assertEqual(report['abstentions'], 1)
        self.assertFalse(report['modelAccepted'])
        with self.assertRaisesRegex(ValueError, 'cached_score_mismatch'):
            summarize([compare(row(), truth, 'known-box', dict(kind='none'), [.5], ['h'])], 'known-box', dict(kind='none'))
        with self.assertRaisesRegex(ValueError, 'score_count'):
            compare(row(), truth, 'known-box', dict(kind='none'), [], [])

    def test_compiler_rejects_bad_parameters(self):
        doc = q.load(q.ROOT / 'Research/Experiments/b405-002-interventions.json')['jobs'][0]
        doc['parameters'] = dict(source='known-box', intervention=dict(kind='rotate'))
        with self.assertRaisesRegex(ValueError, 'intervention_fields'):
            batches.compile_batch(dict(version='experiment-batch-v1', jobs=[doc]))
        doc['parameters'] = dict(source='known-box', intervention=dict(kind='none'))
        doc['inputs'].pop('tool')
        with self.assertRaisesRegex(ValueError, 'template_inputs'):
            batches.compile_batch(dict(version='experiment-batch-v1', jobs=[doc]))


class QueueTests(unittest.TestCase):
    """Positive and negative paths through the actual queue on the retained tall-control pair."""

    def test_actual_queue_and_second_description(self):
        bundle = q.load(q.ROOT / BUNDLE)
        tall = [p for p in bundle['pairs'] if 'native404-selection-03/' in p['selection']['report']['path']]
        self.assertEqual(len(tall), 1)
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='intervention410-') as folder:
            root = Path(folder); queue = root / 'queue'
            small = root / 'bundle.json'
            q.save(small, dict(bundle, pairs=tall))

            def desc(ident, change, path=small):
                return dict(version='hcf-template-description-v1', id=ident, owner='test-NUIAK', template='T41',
                            question='Does one box change move the tall-control score?',
                            decision='Reject a change that loses a previous success.',
                            inputs=dict(bundle=dict(file=q.relative(path)), model=dict(file=MODEL), tool=dict(file=TOOL)),
                            parameters=dict(source='known-box', intervention=change), dependencies=[])
            docs = [desc('intervention-control', dict(kind='none')),
                    desc('intervention-margin', dict(kind='margin', dw=-1.9365, dh=-1.1111))]
            batch = dict(version='experiment-batch-v1', jobs=docs)
            batches.register_batch(batch, queue, [d['id'] for d in docs], approver='test')
            self.assertEqual(q.run(queue, max_jobs=2, lock=root / 'lock', job_ids=[d['id'] for d in docs]),
                             [('intervention-control', 'complete'), ('intervention-margin', 'complete')])
            control, margin = [q.load(queue / 'jobs' / d['id'] / 'attempts/1/out/benchmark_summary.json') for d in docs]
            self.assertLessEqual(control['maxCachedScoreDeviation'], 1e-4)
            self.assertEqual(control['lostPriorSuccesses'], []); self.assertFalse(margin['modelAccepted'])
            self.assertEqual([r['id'] for r in control['rows']], [r['id'] for r in margin['rows']])
            target = next(r for r in margin['rows'] if r['id'] == TALL)['target']
            self.assertAlmostEqual(target['cachedScore'], .9654197096824646, places=6)
            # Negative: an evaluation role is rejected before any score is written.
            bad = q.load(small); bad['role'] = 'final-audit'; q.save(root / 'bad.json', bad)
            batches.register_batch(dict(version='experiment-batch-v1', jobs=[desc('intervention-role', dict(kind='none'), root / 'bad.json')]),
                                   queue, ['intervention-role'], approver='test')
            # Negative: a changed producer receipt breaks candidate correspondence.
            receipt = q.load(q.ROOT / tall[0]['selection']['result']['path'])
            copied = root / 'jobs/native404-selection-03/attempts/1'; (copied / 'out').mkdir(parents=True)
            q.save(copied / 'out/selection.json', q.load(q.ROOT / tall[0]['selection']['report']['path']))
            receipt['specSHA256'] = '0' * 64; q.save(copied / 'result.json', receipt)
            q.save(root / 'jobs/native404-selection-03/spec.json', q.load(q.ROOT / 'reports/work/research-queue/jobs/native404-selection-03/spec.json'))
            changed = copy.deepcopy(q.load(small))
            changed['pairs'][0]['selection'] = dict(
                report=dict(path=q.relative(copied / 'out/selection.json'), sha256=q.digest(copied / 'out/selection.json')),
                result=dict(path=q.relative(copied / 'result.json'), sha256=q.digest(copied / 'result.json')))
            q.save(root / 'changed.json', changed)
            batches.register_batch(dict(version='experiment-batch-v1', jobs=[desc('intervention-receipt', dict(kind='none'), root / 'changed.json')]),
                                   queue, ['intervention-receipt'], approver='test')
            # The queue stops after a failed job. Run each negative job separately.
            for ident in ('intervention-role', 'intervention-receipt'):
                self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=[ident]), [(ident, 'failed')])
            for ident, reason in (('intervention-role', 'bundle_scope'), ('intervention-receipt', 'producer_spec_changed')):
                attempt = queue / 'jobs' / ident / 'attempts/1'
                self.assertFalse((attempt / 'out/benchmark_summary.json').exists())
                self.assertIn(reason, (attempt / 'stderr.log').read_text())


if __name__ == '__main__':
    unittest.main()
