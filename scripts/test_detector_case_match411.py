"""T42 detector-case-match: unit checks and isolated-queue qualification on the Run 009/013 withheld predictions."""
import json
from pathlib import Path
import tempfile
import unittest
import research_queue as q
import experiment_batch402 as batches
from detector_case_match411 import parameters, match, evaluate, summarize, load_bundle, extra_kind, fit, suppress

IOS = 'Research/Experiments/detector-case-ios-r013.json'
TVOS = 'Research/Experiments/detector-case-tvos-sc36.json'
EVALUATION = 'reports/work/IOS-R013-EVAL/evaluation.json'
SCORECARD = 'reports/work/REAL-MODEL-SCORECARD-36/scorecard-final/scorecard.json'
META = dict(platform='iOS', role='development', format='prediction-artifact-v1', confidence=.25, labelReview='unknown',
            singleModel=False, baselineModel={}, candidateModel={})


def settings(**change):
    value = dict(slice='class', classes=None, groups={}, matching='class-aware')
    value.update(change)
    return parameters(value)


class UnitTests(unittest.TestCase):
    def test_parameters(self):
        self.assertEqual(settings()[0], 'class')
        for change, error in [(dict(slice='family'), 'case_slice'), (dict(matching='loose'), 'case_matching'),
                              (dict(classes=[]), 'case_classes'), (dict(classes=['a', 'a']), 'case_classes'),
                              (dict(groups=['a']), 'case_groups'),
                              (dict(groups={'a': 'b'}, matching='class-agnostic'), 'case_groups_unused')]:
            with self.assertRaisesRegex(ValueError, error): settings(**change)
        with self.assertRaisesRegex(ValueError, 'case_parameters'): parameters(dict(slice='class'))

    def test_match_statuses(self):
        labels = [('toggle', (0, 0, 10, 10)), ('label', (20, 0, 30, 10)), ('listRow', (40, 0, 50, 10)), ('link', (60, 0, 70, 10))]
        predictions = [('toggle', .9, (0, 0, 10, 10)), ('listRow', .8, (20, 0, 30, 10)),
                       ('listRow', .7, (40, 0, 44, 10)), ('toggle', .6, (0, 0, 10, 9))]
        unmatched, outcomes = match(labels, predictions, agnostic=False)
        self.assertEqual([o['status'] for o in outcomes], ['detected', 'wrong-class', 'mislocalized', 'missed'])
        self.assertEqual(outcomes[1]['predictedClass'], 'listRow')
        # The duplicate toggle and the 2 unused listRow boxes stay unmatched.
        self.assertEqual(sorted(unmatched), [1, 2, 3])
        _, agnostic = match(labels, predictions, agnostic=True)
        self.assertEqual([o['status'] for o in agnostic], ['detected', 'detected', 'mislocalized', 'missed'])

    def test_unmatched_kinds(self):
        found = [('bar', .9, [0, 0, 100, 20]), ('bar', .8, [1, 0, 101, 20]), ('bar', .7, [0, 40, 100, 60]),
                 ('bar', .6, [300, 300, 310, 310])]
        labels = [[0, 0, 100, 20], [0, 50, 100, 70]]
        self.assertEqual([extra_kind(found, i, [0], labels) for i in (1, 2, 3)], ['duplicate', 'near-label', 'no-label'])
        # A higher-scoring unmatched box of the same class is not a duplicate of a lower-scoring match.
        self.assertEqual(extra_kind(found, 0, [1], labels), 'near-label')

    def test_fit_and_suppression(self):
        label = (40, 40, 60, 60)
        self.assertEqual(fit(label, (0, 0, 100, 100)), 'larger')
        self.assertEqual(fit(label, (45, 45, 50, 50)), 'smaller')
        self.assertEqual(fit(label, (50, 50, 70, 70)), 'offset')
        self.assertIsNone(fit(label, (80, 80, 90, 90)))
        # A wide group box has IoU below 0.1 but still covers the label. Fit records it as larger.
        _, [outcome] = match([('pageControl', label)], [('pageControl', .5, (0, 0, 200, 100))], agnostic=False)
        self.assertEqual((outcome['status'], outcome['fit']), ('missed', 'larger'))
        boxes = [('a', .9, (0, 0, 10, 10)), ('b', .8, (0, 0, 10, 9)), ('a', .7, (20, 0, 30, 10))]
        self.assertEqual(suppress(boxes), [boxes[0], boxes[2]])

    def test_state_edge_and_suppressed_arm(self):
        image = ('img', 100, 100, 'home', [('listRow', (0, 0, 10, 10), 'r1', 'focused'),
                                           ('label', (40, 40, 50, 50), 'r2', 'unfocused')])
        found = [('listRow', .9, (0, 0, 10, 10)), ('label', .8, (40, 40, 50, 49)), ('listRow', .85, (40, 40, 50, 50))]
        predictions = dict(baseline={'img': found}, candidate={'img': found})
        rows, unmatched = evaluate([image], predictions, settings(slice='state'), .25)
        self.assertEqual({r['slice'] for r in rows}, {'focused', 'unfocused'})
        rows, unmatched = evaluate([image], predictions, settings(slice='edge'), .25)
        self.assertEqual([r['slice'] for r in rows], ['edge', 'interior'])
        # Suppression changes only the candidate arm: the label box under a higher-scored listRow box goes away.
        suppressed = settings(matching='class-aware-suppressed')
        rows, unmatched = evaluate([image], predictions, suppressed, .25)
        report = summarize(rows, unmatched, suppressed, META)
        self.assertEqual(report['lostPriorSuccesses'], ['img#r2'])

    def test_gain_loss_and_groups(self):
        image = ('img', 100, 100, None, [('primaryButton', (0, 0, 10, 10)), ('label', (20, 0, 30, 10))])
        predictions = dict(baseline={'img': [('secondaryButton', .9, (0, 0, 10, 10)), ('label', .9, (20, 0, 30, 10))]},
                           candidate={'img': [('primaryButton', .9, (0, 0, 10, 10)), ('label', .1, (20, 0, 30, 10))]})
        rows, unmatched = evaluate([image], predictions, settings(), .25)
        report = summarize(rows, unmatched, settings(), META)
        self.assertEqual(report['gains'], ['img#0']); self.assertEqual(report['lostPriorSuccesses'], ['img#1'])
        self.assertEqual(report['slices']['label']['outcomes']['lost'], 1)
        self.assertEqual(report['slices']['secondaryButton']['unmatchedPredictions'], dict(baseline=1, candidate=0))
        self.assertFalse(report['modelAccepted'])
        coarse = settings(groups={'primaryButton': 'button', 'secondaryButton': 'button'}, classes=['button'])
        rows, unmatched = evaluate([image], predictions, coarse, .25)
        report = summarize(rows, unmatched, coarse, META)
        self.assertEqual(list(report['slices']), ['button']); self.assertEqual(report['slices']['button']['outcomes']['kept'], 1)
        # A class without labels still reports its unmatched predictions.
        only = settings(classes=['secondaryButton'])
        rows, unmatched = evaluate([image], predictions, only, .25)
        report = summarize(rows, unmatched, only, META)
        self.assertEqual(report['labels'], 0)
        self.assertEqual(report['slices']['secondaryButton']['unmatchedPredictions']['baseline'], 1)
        with self.assertRaisesRegex(ValueError, 'empty_comparison'):
            summarize([], [], settings(), META)

    def test_reproduces_recorded_counts(self):
        """The class-aware matching repeats the Run 013 report counts. The class-agnostic tvOS matching repeats the scorecard."""
        evaluation = q.load(q.ROOT / EVALUATION)
        images, predictions, meta = load_bundle(q.load(q.ROOT / IOS))
        rows, unmatched = evaluate(images, predictions, settings(), meta['confidence'])
        report = summarize(rows, unmatched, settings(), meta)
        for arm, recorded in (('baseline', evaluation['baseline']), ('candidate', evaluation['populations']['withheld'])):
            expected = {r['class']: r['tp'] for r in recorded['perClass'] if r['support']}
            self.assertEqual({k: v[arm]['detected'] for k, v in report['slices'].items() if v['labels']}, expected)
        self.assertEqual(report['labelReview'], 'unknown')
        card = q.load(q.ROOT / SCORECARD)
        images, predictions, meta = load_bundle(q.load(q.ROOT / TVOS))
        agnostic = settings(matching='class-agnostic')
        rows, unmatched = evaluate(images, predictions, agnostic, meta['confidence'])
        report = summarize(rows, unmatched, agnostic, meta)
        self.assertTrue(report['singleModel']); self.assertEqual(report['lostPriorSuccesses'], [])
        self.assertEqual({k: v['candidate']['detected'] for k, v in report['slices'].items() if v['labels']},
                         {k: v['localized50'] for k, v in card['summary']['roles'].items()})


class QueueTests(unittest.TestCase):
    """Positive, changed-input, and wrong-role paths through the actual queue."""

    def test_actual_queue(self):
        bundle = q.load(q.ROOT / IOS)
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='case-match411-') as folder:
            root = Path(folder); queue = root / 'queue'

            def desc(ident, path, **change):
                value = dict(slice='class', classes=None, groups={}, matching='class-aware'); value.update(change)
                return dict(version='hcf-template-description-v1', id=ident, owner='test-NUIAK', template='T42',
                            question='Which classes lose previous Run 009 detections in Run 013?',
                            decision='Name each class with lost prior successes.',
                            inputs=dict(bundle=dict(file=q.relative(path))), parameters=value, dependencies=[])
            # Negative: a changed prediction file keeps its old pin.
            changed = root / 'candidate.json'
            document = q.load(q.ROOT / bundle['candidate']['path'])
            document['results'][0]['detections'] = []
            changed.write_text(json.dumps(document))
            q.save(root / 'changed.json', dict(bundle, candidate=dict(path=q.relative(changed), sha256=bundle['candidate']['sha256'])))
            # Negative: a final-audit role is rejected before any output.
            q.save(root / 'role.json', dict(bundle, role='final-audit'))
            docs = [desc('case-positive', q.ROOT / IOS), desc('case-changed', root / 'changed.json'),
                    desc('case-role', root / 'role.json')]
            batches.register_batch(dict(version='experiment-batch-v1', jobs=docs), queue, [d['id'] for d in docs], approver='test')
            # The queue stops after a failed job. Run each job separately.
            self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=['case-positive']), [('case-positive', 'complete')])
            report = q.load(queue / 'jobs/case-positive/attempts/1/out/benchmark_summary.json')
            self.assertFalse(report['modelAccepted'])
            self.assertEqual(report['slices']['label']['candidate']['detected'] + report['slices']['label']['candidate']['missed'] +
                             report['slices']['label']['candidate']['wrong-class'] + report['slices']['label']['candidate']['mislocalized'],
                             report['slices']['label']['labels'])
            self.assertGreater(report['slices']['label']['outcomes']['lost'], 0)
            self.assertEqual(len(report['lostPriorSuccesses']), sum(v['outcomes']['lost'] for v in report['slices'].values()))
            for name in ('benchmark_summary.json', 'cases.json'):
                self.assertTrue((queue / 'jobs/case-positive/attempts/1/out' / name).is_file())
            for ident, reason in (('case-changed', 'input_changed'), ('case-role', 'bundle_role')):
                self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=[ident]), [(ident, 'failed')])
                attempt = queue / 'jobs' / ident / 'attempts/1'
                self.assertFalse((attempt / 'out/benchmark_summary.json').exists())
                self.assertIn(reason, (attempt / 'stderr.log').read_text())


if __name__ == '__main__':
    unittest.main()
