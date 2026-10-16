"""T48 representation comparison: unit checks and isolated-queue qualification on the retained tall-control pair."""
import copy
from pathlib import Path
import tempfile
import unittest
import research_queue as q
import experiment_batch402 as batches
import hcf_templates395 as templates
import backlog_pipeline
from representation_t48 import parameters, tool_box, crop_geometry, compare, summarize, EXPANSION

BUNDLE = 'Research/Experiments/backlog405-native-inputs.json'
MODEL = 'reports/work/research-queue/jobs/hcf375c-70-crop-train/attempts/1/out/final.pt'
TOOL = '.build/standard392-swift/arm64-apple-macosx/debug/FocusRingTool'
TALL = 'hcf402-tall-controls-hcf-item-3-0'


def row(score=.9, outcome='correct'):
    arm = dict(scores=[score], boxes=[[100, 200, 40, 80]], outcome=outcome)
    return dict(id='frame', group='group', profile='hcf', noFocus=False,
                arms={k: copy.deepcopy(arm) for k in ('known-box', 'raw-proposal', 'mapped-proposal')})


def desc(ident, change, bundle, source='known-box'):
    return dict(version='hcf-template-description-v1', id=ident, owner='test-NUIAK', template='T48',
                question='Does one representation change move the tall-control score?',
                decision='Reject a change that loses a previous success.',
                inputs=dict(bundle=dict(file=q.relative(bundle)), model=dict(file=MODEL), tool=dict(file=TOOL)),
                parameters=dict(source=source, representation=change), dependencies=[])


class UnitTests(unittest.TestCase):
    def test_parameters(self):
        self.assertEqual(parameters(dict(source='known-box', representation=dict(kind='aspect-fit')))[0], 'known-box')
        parameters(dict(source='mapped-proposal', representation=dict(kind='context', expansion=.24)))
        for value, error in [(dict(source='other', representation=dict(kind='none')), 'representation_source'),
                             (dict(source='known-box', representation=dict(kind='scale')), 'representation_kind'),
                             (dict(source='known-box', representation=dict(kind='context')), 'representation_fields'),
                             (dict(source='known-box', representation=dict(kind='aspect-fit', expansion=.2)), 'representation_fields'),
                             (dict(source='known-box', representation=dict(kind='context', expansion=float('nan'))), 'representation_value'),
                             (dict(source='known-box', representation=dict(kind='context', expansion=.9)), 'representation_value'),
                             (dict(source='known-box', representation=dict(kind='context', expansion=.16)), 'representation_no_change'),
                             (dict(source='known-box', intervention=dict(kind='none')), 'representation_parameters')]:
            with self.assertRaisesRegex(ValueError, error): parameters(value)

    def test_context_box_gives_requested_crop(self):
        box = [100, 200, 40, 80]
        self.assertEqual(tool_box(box, dict(kind='aspect-fit')), box)
        x, y, w, h = tool_box(box, dict(kind='context', expansion=.24))
        self.assertAlmostEqual(x + w / 2, 120); self.assertAlmostEqual(y + h / 2, 240)
        # The tool expands the scaled box by 0.16. The result equals a 0.24 expansion of the source box.
        self.assertAlmostEqual(w * (1 + 2 * EXPANSION), 40 * 1.48)
        g = crop_geometry(box, (3840, 2160), dict(kind='context', expansion=.24))
        self.assertEqual([round(v, 6) for v in g['rect']], [90.4, 180.8, 59.2, 118.4])
        self.assertFalse(g['clamped']); self.assertEqual(g['padding'], 0)

    def test_aspect_padding_from_geometry_and_clamping(self):
        g = crop_geometry([100, 200, 40, 80], (3840, 2160), dict(kind='aspect-fit'))
        self.assertAlmostEqual(g['padding'], .5)
        edge = crop_geometry([0, 0, 40, 80], (3840, 2160), dict(kind='none'))
        self.assertTrue(edge['clamped']); self.assertEqual(edge['rect'][:2], [0, 0])

    def test_loss_gain_selection_uses_source_box(self):
        truth = [100, 200, 40, 80]
        geometry = [crop_geometry(truth, (3840, 2160), dict(kind='context', expansion=.3))]
        change = dict(kind='context', expansion=.3)
        lost = compare(row(), truth, 'known-box', change, [.9], [.4], ['h'], geometry)
        self.assertTrue(lost['loss']); self.assertEqual(lost['outcome'], 'miss'); self.assertEqual(lost['orientation'], 'tall')
        # A large context change must not move the box used for matching: the selection stays correct.
        kept = compare(row(), truth, 'known-box', change, [.9], [.95], ['h'], geometry)
        self.assertEqual(kept['outcome'], 'correct'); self.assertFalse(kept['loss'])
        gained = compare(row(.4, 'miss'), truth, 'raw-proposal', change, [.4], [.95], ['h'], geometry)
        self.assertTrue(gained['gain'])
        report = summarize([lost, gained], 'known-box', change)
        self.assertEqual(report['lostPriorSuccesses'], ['frame']); self.assertEqual(report['gains'], ['frame'])
        self.assertEqual(report['decisions']['transitions'], {'correct->miss': 1, 'miss->correct': 1})
        self.assertIn('hcf-tall', report['slices']); self.assertFalse(report['modelAccepted'])
        with self.assertRaisesRegex(ValueError, 'cached_score_mismatch'):
            summarize([compare(row(), truth, 'known-box', change, [.5], [.5], ['h'], geometry)], 'known-box', change)
        with self.assertRaisesRegex(ValueError, 'score_count'):
            compare(row(), truth, 'known-box', change, [.9], [], [], [])

    def test_compiler_and_plan_reject_bad_parameters(self):
        doc = desc('t48-bad', dict(kind='rotate'), q.ROOT / BUNDLE)
        with self.assertRaisesRegex(ValueError, 'representation_kind'):
            templates.build(doc)
        doc = desc('t48-bad', dict(kind='none'), q.ROOT / BUNDLE); doc['inputs'].pop('tool')
        with self.assertRaisesRegex(ValueError, 'template_inputs'):
            templates.build(doc)
        plan = dict(template='T48', owner='research-host-NUIAK', jobPrefix='t48-test', rule='any-loss', control='control',
                    question='T48 test plan: does an aspect-fit crop lose previous correct selections?',
                    decision='Reject the change if it loses a success.',
                    outcomes=dict(supported='x' * 12, contradicted='x' * 12, inconclusive='x' * 12),
                    shared=dict(parameters=dict(source='known-box')),
                    arms=[dict(id='control', job='b405-002-known-none'),
                          dict(id='bad', parameters=dict(representation=dict(kind='context', expansion=2)))])
        with self.assertRaisesRegex(ValueError, 'representation_value'):
            backlog_pipeline.validate_plan(dict(id='B405-999', plan=plan))


class QueueTests(unittest.TestCase):
    """Positive and negative paths through the actual queue on the retained tall-control pair."""

    def test_actual_queue(self):
        bundle = q.load(q.ROOT / BUNDLE)
        tall = [p for p in bundle['pairs'] if 'native404-selection-03/' in p['selection']['report']['path']]
        self.assertEqual(len(tall), 1)
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='representation-t48-') as folder:
            root = Path(folder); queue = root / 'queue'
            small = root / 'bundle.json'
            q.save(small, dict(bundle, pairs=tall))
            docs = [desc('t48-context', dict(kind='context', expansion=.24), small),
                    desc('t48-aspect', dict(kind='aspect-fit'), small)]
            batches.register_batch(dict(version='experiment-batch-v1', jobs=docs), queue, [d['id'] for d in docs], approver='test')
            self.assertEqual(sorted(q.run(queue, max_jobs=2, lock=root / 'lock', job_ids=[d['id'] for d in docs])),
                             [('t48-aspect', 'complete'), ('t48-context', 'complete')])
            context, aspect = [q.load(queue / 'jobs' / d['id'] / 'attempts/1/out/benchmark_summary.json') for d in docs]
            for report in (context, aspect):
                self.assertLessEqual(report['maxCachedScoreDeviation'], 1e-4); self.assertFalse(report['modelAccepted'])
                target = next(r for r in report['rows'] if r['id'] == TALL)['target']
                self.assertAlmostEqual(target['cachedScore'], .9654197096824646, places=6)
                self.assertEqual(target['orientation'], 'tall')
            self.assertEqual([r['id'] for r in context['rows']], [r['id'] for r in aspect['rows']])
            self.assertGreater(aspect['geometry']['meanPadding'], .2); self.assertEqual(context['geometry']['meanPadding'], 0)
            # Negative: an evaluation role is rejected before any score is written.
            bad = q.load(small); bad['role'] = 'final-audit'; q.save(root / 'bad.json', bad)
            batches.register_batch(dict(version='experiment-batch-v1', jobs=[desc('t48-role', dict(kind='aspect-fit'), root / 'bad.json')]),
                                   queue, ['t48-role'], approver='test')
            self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=['t48-role']), [('t48-role', 'failed')])
            attempt = queue / 'jobs/t48-role/attempts/1'
            self.assertFalse((attempt / 'out/benchmark_summary.json').exists())
            self.assertIn('bundle_scope', (attempt / 'stderr.log').read_text())


if __name__ == '__main__':
    unittest.main()
