"""T43 detector inference: parameter checks, frame lookup, and actual-queue runs on 3 reviewed tvOS frames."""
import json
import tempfile
import unittest
from pathlib import Path

import research_queue as q
import experiment_batch402 as batches
from detector_inference412 import parameters, frame_path, ARCHIVE

SCORECARD = 'reports/work/REAL-MODEL-SCORECARD-36/scorecard-final/scorecard.json'
LABELS = 'reports/work/REAL-MODEL-SCORECARD-36/production/inputs.json'
BINARY = '.build/arm64-apple-macosx/debug/nativeui-audit'
WEIGHTS = 'NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.pt'


class UnitTests(unittest.TestCase):
    def test_parameters(self):
        self.assertEqual(parameters(dict(engine='production', confidence=.1, imageSize=None, slice='class'))[0], 'production')
        self.assertEqual(parameters(dict(engine='pytorch', confidence=.5, imageSize=1280, slice='screen'))[2], 1280)
        for value, error in [(dict(engine='production', confidence=.1, imageSize=640, slice='class'), 'inference_image_size'),
                             (dict(engine='pytorch', confidence=.5, imageSize=None, slice='class'), 'inference_image_size'),
                             (dict(engine='pytorch', confidence=.5, imageSize=1000, slice='class'), 'inference_image_size'),
                             (dict(engine='onnx', confidence=.5, imageSize=None, slice='class'), 'inference_engine'),
                             (dict(engine='production', confidence=0, imageSize=None, slice='class'), 'inference_confidence'),
                             (dict(engine='production', confidence=.5, imageSize=None, slice='group'), 'inference_slice'),
                             (dict(engine='production', confidence=.5, imageSize=None), 'inference_parameters')]:
            with self.assertRaisesRegex(ValueError, error):
                parameters(value)

    def test_frame_lookup_uses_archive_and_checks_hash(self):
        frames = q.load(q.ROOT / LABELS)['frames']
        archived = next(f for f in frames if not (q.ROOT / f['image']['path']).is_file())
        self.assertEqual(frame_path(archived['image']), ARCHIVE / archived['image']['path'])
        with self.assertRaisesRegex(ValueError, 'frame_missing_or_changed'):
            frame_path(dict(archived['image'], sha256='0' * 64))


class QueueTests(unittest.TestCase):
    """The production control reproduces the stored scorecard. Changed inputs fail before output."""

    def test_actual_queue(self):
        labels, card = q.load(q.ROOT / LABELS), q.load(q.ROOT / SCORECARD)
        frames = q.load(q.ROOT / LABELS)['frames']
        # 2 project frames and 1 archived frame.
        pick = [i for i, f in enumerate(frames) if (q.ROOT / f['image']['path']).is_file()][:2]
        pick += [next(i for i, f in enumerate(frames) if not (q.ROOT / f['image']['path']).is_file())]
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='inference412-') as folder:
            root = Path(folder); queue = root / 'queue'
            q.save(root / 'labels.json', dict(labels, frames=[frames[i] for i in pick]))
            subset = dict(path=q.relative(root / 'labels.json'), sha256=q.digest(root / 'labels.json'))
            q.save(root / 'baseline.json', dict(card, inputs=subset, rawPredictions=[card['rawPredictions'][i] for i in pick],
                                                frames=[card['frames'][i] for i in pick]))
            changed = root / 'weights.pt'
            changed.write_bytes(b'not the pinned weights')

            def desc(ident, model, **change):
                value = dict(engine='production', confidence=.5, imageSize=None, slice='class'); value.update(change)
                return dict(version='hcf-template-description-v1', id=ident, owner='test-NUIAK', template='T43',
                            question='Does the production detector reproduce the stored scorecard at confidence 0.50?',
                            decision='Accept the template only if the control arm has 0 gains and 0 losses.',
                            inputs=dict(labels=dict(file=q.relative(root / 'labels.json')),
                                        baseline=dict(file=q.relative(root / 'baseline.json')), model=dict(file=model)),
                            parameters=value, dependencies=[])
            docs = [desc('inference-control', BINARY), desc('inference-pytorch', WEIGHTS, engine='pytorch', imageSize=640),
                    desc('inference-changed', q.relative(changed), engine='pytorch', imageSize=640)]
            batches.register_batch(dict(version='experiment-batch-v1', jobs=docs), queue, [d['id'] for d in docs], approver='test')
            changed.write_bytes(b'changed after registration')
            for ident in ('inference-control', 'inference-pytorch'):
                outcome = q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=[ident])
                log = queue / 'jobs' / ident / 'attempts/1/stderr.log'
                self.assertEqual(outcome, [(ident, 'complete')], log.read_text()[-2000:] if log.is_file() else '')
            control = q.load(queue / 'jobs/inference-control/attempts/1/out/benchmark_summary.json')
            self.assertEqual((control['gains'], control['lostPriorSuccesses']), ([], []))
            self.assertEqual(control['totals']['baseline'], control['totals']['candidate'])
            self.assertEqual(control['totals']['unmatchedPredictions']['baseline'],
                             control['totals']['unmatchedPredictions']['candidate'])
            self.assertFalse(control['modelAccepted'])
            torch_run = q.load(queue / 'jobs/inference-pytorch/attempts/1/out/benchmark_summary.json')
            self.assertEqual(torch_run['engine'], 'pytorch')
            self.assertEqual(torch_run['labels'], control['labels'])
            self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=['inference-changed']),
                             [('inference-changed', 'failed')])
            attempt = queue / 'jobs/inference-changed/attempts/1'
            self.assertFalse((attempt / 'out/benchmark_summary.json').exists())
            # The pin check fails before the worker starts, so the reason is in the result, not in a log.
            evidence = json.dumps(q.load(attempt / 'result.json'))
            if (attempt / 'stderr.log').is_file():
                evidence += (attempt / 'stderr.log').read_text()
            self.assertIn('input_changed', evidence)


if __name__ == '__main__':
    unittest.main()
