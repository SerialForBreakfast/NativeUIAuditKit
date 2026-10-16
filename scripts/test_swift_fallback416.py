"""B405-127: check T51, the Swift fallback comparison on cached native selections."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_queue as q
import hcf_templates395 as templates
import swift_fallback416 as fallback

BUNDLE = q.ROOT / 'Research/Experiments/backlog405-native-inputs.json'
TOOL = q.ROOT / '.build/b405-127-tool/FocusFallbackTool'
CACHED = q.QUEUE / 'jobs/backlog405-native-failure-analysis/attempts/1/out/benchmark_summary.json'


class UnitTests(unittest.TestCase):
    def test_parameters(self):
        fallback.parameters(dict(arm='known-box', elementType='primaryButton'))
        with self.assertRaisesRegex(ValueError, 'fallback_arm'):
            fallback.parameters(dict(arm='oracle', elementType='primaryButton'))
        with self.assertRaisesRegex(ValueError, 'fallback_element_type'):
            fallback.parameters(dict(arm='known-box', elementType='label'))
        with self.assertRaisesRegex(ValueError, 'fallback_parameters'):
            fallback.parameters(dict(arm='known-box'))

    def test_outcomes_follow_t37_names(self):
        body = [0, 0, 10, 10]
        self.assertEqual(fallback.outcome([[0, 0, 10, 10]], body, False), 'correct')
        self.assertEqual(fallback.outcome([[20, 20, 10, 10]], body, False), 'wrong')
        self.assertEqual(fallback.outcome([], body, False), 'miss')
        self.assertEqual(fallback.outcome([body, body], body, False), 'miss')
        self.assertEqual(fallback.outcome([body], None, True), 'false-selection')
        self.assertEqual(fallback.outcome([], None, True), 'correct-abstention')

    def test_observation_uses_bottom_left_vision_box(self):
        value = fallback.observation([100, 200, 50, 20], 1000, 500, 'primaryButton', 0)
        self.assertAlmostEqual(value['boundingBox']['y'], 1 - 220 / 500)
        self.assertEqual(value['boundingBoxPixels'], dict(x=100, y=200, width=50, height=20))


@unittest.skipUnless(BUNDLE.is_file() and TOOL.is_file() and CACHED.is_file(), 'native inputs or tool missing')
class QueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='fallback416-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def description(self, parameters):
        return dict(version='hcf-template-description-v1', id='fallback-test', owner='research-host-NUIAK', template='T51',
                    question='How does the Swift fallback select on the cached native boxes?',
                    decision='Test only; the job decides nothing about the models.',
                    inputs=dict(bundle=dict(path=q.relative(BUNDLE), sha256=q.digest(BUNDLE)),
                                tool=dict(path=q.relative(TOOL), sha256=q.digest(TOOL))),
                    dependencies=[], parameters=parameters)

    def test_build_rejects_bad_parameters(self):
        templates.build(self.description(dict(arm='known-box', elementType='collectionItem')))
        with self.assertRaisesRegex(ValueError, 'fallback_element_type'):
            templates.build(self.description(dict(arm='known-box', elementType='label')))

    def test_known_box_run_matches_cached_learned_outcomes(self):
        job = self.root / 'jobs/fallback-test'
        out = job / 'attempts/1/out'; out.mkdir(parents=True)
        q.save(job / 'spec.json', templates.build(self.description(dict(arm='known-box', elementType='primaryButton'))))
        with patch.object(fallback, 'OUT', out):
            fallback.run()
        report = q.load(out / 'benchmark_summary.json')
        cached = {r['id']: r['arms']['known-box']['outcome'] for r in q.load(CACHED)['rows']}
        self.assertEqual(report['frames'], len(cached))
        self.assertEqual({r['id']: r['learned'] for r in report['rows']}, cached)
        self.assertTrue(all(r['fallback'] in fallback.SUCCESS | {'miss', 'wrong', 'false-selection'} for r in report['rows']))
        self.assertEqual(len(list((out / 'replies').iterdir())), sum(r['proposals'] > 0 for r in report['rows']))

    def test_changed_tool_is_refused(self):
        doc = self.description(dict(arm='known-box', elementType='primaryButton'))
        doc['inputs']['tool']['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            templates.build(doc)


if __name__ == '__main__':
    unittest.main()
