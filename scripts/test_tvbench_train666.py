"""Synthetic tests for TRAIN666 denominators, clustering, and decision support."""
import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import tvbench


class Train666Tests(unittest.TestCase):
    def labels(self, complete=True, focus='unknown'):
        return dict(complete=complete, objects=[
            dict(id='a', **{'class': 'button'}, box=[0, 0, 10, 10], visibility='visible'),
            dict(id='b', **{'class': None}, box=[20, 0, 10, 10], visibility='visible')],
            focus=dict(state=focus, box=[0, 0, 10, 10] if focus == 'focused' else None))

    def detections(self):
        return [dict(**{'class': 'cell'}, box=[0, 0, 10, 10], score=.9),
                dict(**{'class': 'button'}, box=[20, 0, 10, 10], score=.8),
                dict(**{'class': 'button'}, box=[50, 0, 10, 10], score=.7)]

    def test_geometry_before_role_and_unknown_roles(self):
        counts = tvbench._train666_counts(self.labels(), self.detections(), {})
        self.assertEqual(counts['localizationRecall'], [2, 2])
        self.assertEqual(counts['localizationPrecision'], [2, 3])
        self.assertEqual(counts['roleAccuracy'], [0, 1])
        self.assertEqual(counts['roleConfusion'], {'button': {'cell': 1}})

    def test_partial_precision_and_failure_denominators(self):
        counts = tvbench._train666_counts(self.labels(False, 'focused'), self.detections(),
                                         dict(status='failed', focusBox=[0, 0, 10, 10]))
        self.assertEqual(counts['localizationRecall'], [0, 2])
        self.assertEqual(counts['localizationPrecision'], [0, 0])
        self.assertEqual(counts['roleAccuracy'], [0, 0])
        self.assertEqual(counts['focusTop1'], [0, 1])

    def test_rejected_control_flags_and_auxiliary_focus_are_excluded(self):
        labels = self.labels()
        labels['objects'][0]['sourceFlag'] = 'not-control'
        labels['objects'][1]['sourceFlag'] = 'wrong-box'
        detections = self.detections() + [dict(**{'class': 'focused'}, box=[0, 0, 10, 10], score=1)]
        counts = tvbench._train666_counts(labels, detections, {})
        self.assertEqual(counts['localizationRecall'], [0, 0])
        self.assertEqual(counts['localizationPrecision'], [0, 3])
        self.assertEqual(counts['roleAccuracy'], [0, 0])
        labels = self.labels()
        counts = tvbench._train666_counts(labels,
            [dict(**{'class': 'focused'}, box=[0, 0, 10, 10], score=1)], {})
        self.assertEqual(counts['localizationRecall'], [0, 2])
        self.assertEqual(counts['localizationPrecision'], [0, 0])

    def test_unknown_visibility_excludes_precision(self):
        labels = self.labels()
        labels['objects'][1]['visibility'] = 'unknown'
        counts = tvbench._train666_counts(labels, self.detections(), {})
        self.assertEqual(counts['localizationRecall'], [1, 1])
        self.assertEqual(counts['localizationPrecision'], [0, 0])

    def test_focus_states(self):
        for state in ('no_focus', 'known_no_focus'):
            counts = tvbench._train666_counts(self.labels(focus=state), [], dict(focusBox=[0, 0, 10, 10]))
            self.assertEqual(counts['falseSelectionRate'], [1, 1])
            self.assertEqual(counts['focusTop1'], [0, 0])
        counts = tvbench._train666_counts(self.labels(), [], {})
        self.assertEqual(counts['falseSelectionRate'], [0, 0])

    def row(self, app, layout, correct):
        counts = tvbench._train666_counts(self.labels(), self.detections() if correct else [], {})
        return dict(app=app, flow='flow', layoutId=layout, train666Counts=counts)

    def test_equal_app_mean_and_deterministic_intervals(self):
        rows = [self.row('a', '1', True)] * 10 + [self.row('b', '1', False)]
        result = tvbench.train666_summary(rows, ['a', 'b', 'empty'], samples=100)
        self.assertEqual(result['equalAppMean']['localizationRecall']['value'], .5)
        self.assertEqual(result['equalAppMean']['localizationRecall']['apps'], 2)
        self.assertEqual(result['equalAppMean']['localizationRecall']['interval95'], [.5, .5])
        self.assertIsNone(result['perApplication']['empty']['localizationRecall']['value'])
        self.assertEqual(result, tvbench.train666_summary(rows, ['a', 'b', 'empty'], samples=100))
        self.assertEqual(result['independentLayoutCount'], 2)
        self.assertEqual(result['verdict'], 'refused')

    def test_detector_only_focus_is_unavailable(self):
        counts = tvbench._train666_counts(self.labels(focus='focused'), [], {})
        self.assertEqual(counts['focusTop1'], [0, 0])
        self.assertEqual(counts['focusUnavailable'], 1)
        counts = tvbench._train666_counts(self.labels(focus='focused'), [],
                    dict(focusBox=[0, 0, 10, 10], focusStatus='unavailable'))
        self.assertEqual(counts['focusTop1'], [0, 0])

    def test_default_contract_prediction_projection_and_overrides(self):
        classes = sorted(tvbench.CONTRACT_CLASSES666)
        mapping = tvbench.prediction_class_map666({}, classes)
        for name in ('primaryButton', 'secondaryButton'):
            self.assertEqual(mapping[name], 'button')
        for name in ('collectionItem', 'listRow'):
            self.assertEqual(mapping[name], 'cell')
        for name in ('webContent', 'picker'):
            self.assertIsNone(mapping[name])
        self.assertEqual(tvbench.prediction_class_map666(
            dict(predictionClassMap={'primaryButton': None}), classes)['primaryButton'], None)
        self.assertEqual(tvbench.prediction_class_map666({}, ['button']), {})

    def test_cover618_null_focus_execution_is_unavailable(self):
        for state in ('focused', 'known_no_focus'):
            counts = tvbench._train666_counts(self.labels(focus=state), [],
                dict(status='ok', focusBox=None, focusExecution=None))
            self.assertEqual(counts['focusTop1'], [0, 0])
            self.assertEqual(counts['falseSelectionRate'], [0, 0])
            self.assertEqual(counts['focusUnavailable'], 1)
        counts = tvbench._train666_counts(self.labels(focus='known_no_focus'), [],
            dict(status='ok', focusBox=None, focusExecution=dict(policy='selector')))
        self.assertEqual(counts['falseSelectionRate'], [0, 1])

    def test_manifest_integration_contract_roles_and_sealed_output(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'labels.json'
            labels = self.labels(focus='known_no_focus')
            labels.update(imageSHA256='abc', review=dict(blinded=True, reviewer='test', status='accepted'))
            for obj in labels['objects']:
                obj['provenance'] = 'human-reviewed'
            path.write_text(json.dumps(labels))
            manifest = dict(classes=['button', 'cell'], apps=[dict(id='a', sealed=True)],
                predictionClassMap={'primaryButton': 'button'}, cases=[dict(id='secret-case', app='a',
                    flow='f', independentLayoutId='secret-layout', status='captured', width=100, height=100,
                    image=dict(path=str(Path(temp) / 'absent.png'), sha256='abc'),
                    labels=dict(path=str(path), sha256=tvbench.q.digest(path)))])
            predictions = {'secret-case': dict(imageSHA256='abc', detections=[
                dict(cls='primaryButton', box=[0, 0, 10, 10], score=.9)])}
            with patch.object(tvbench.r543, 'official_ap', return_value=dict(status='unavailable')):
                report = tvbench.score_manifest(manifest, predictions)
            metrics = report['train666']['perApplication']['a']
            self.assertEqual(metrics['localizationRecall']['value'], .5)
            self.assertEqual(metrics['roleAccuracy']['value'], 1)
            self.assertIsNone(metrics['focusTop1']['value'])
            self.assertIsNone(metrics['falseSelectionRate']['value'])
            self.assertEqual(metrics['focusUnavailableScreens'], 1)
            self.assertEqual(report['train666']['independentLayoutCount'], 1)
            self.assertNotIn('rows', report)
            self.assertNotIn('secret-layout', json.dumps(report))
            self.assertNotIn('secret-case', json.dumps(report))

    def test_guard_requires_30_explicit_layouts(self):
        rows = [self.row('a', str(i), True) for i in range(30)]
        self.assertTrue(tvbench.train666_summary(rows, ['a'], samples=10)['decisionEligible'])
        rows[-1]['layoutId'] = None
        summary = tvbench.train666_summary(rows, ['a'], samples=10)
        self.assertFalse(summary['decisionEligible'])
        self.assertEqual(summary['missingLayoutIdCount'], 1)
        self.assertFalse(summary['modelAccepted'])


if __name__ == '__main__':
    unittest.main()
