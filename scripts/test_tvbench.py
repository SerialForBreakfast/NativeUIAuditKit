"""Tests for RESET604 T1.4 TVBench scorer and D3 12-role taxonomy."""
import json
import tempfile
import unittest
from pathlib import Path

import research_queue as q
import roles559 as r559
import tvbench


class TVBenchTests(unittest.TestCase):
    def test_twelve_roles_drop_text(self):
        self.assertEqual(len(r559.ROLES), 12)
        self.assertNotIn('text', r559.ROLES)
        self.assertIsNone(r559.role('label'))
        self.assertEqual(r559.role('secondaryButton'), 'button')
        self.assertEqual(r559.role('collectionItem'), 'cell')

    def test_reproduces_realapp554_pilot(self):
        rep = tvbench.score_pilot()
        self.assertEqual(rep['overall']['controlsFound']['numerator'], 23)
        self.assertEqual(rep['overall']['controlsFound']['denominator'], 207)
        if rep['officialAP50'] is not None:
            self.assertAlmostEqual(rep['officialAP50'], 0.206414, places=4)
        else:
            self.assertAlmostEqual(rep['customAP50'], 0.205361, places=4)
        self.assertEqual(rep['focusSummary']['extendedFocusAll']['all']['focusedFrames'], 15)
        self.assertEqual(rep['focusSummary']['extendedFocusAll']['all']['outcomes']['correct'], 0)

    def test_rejects_prediction_derived_labels(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='tvbench-pred-') as tmp:
            root = Path(tmp)
            img = root / 'frame.png'
            img.write_bytes(b'fake')
            label_path = root / 'labels.json'
            q.save(label_path, dict(
                imageSHA256='abc',
                review=dict(blinded=True, reviewer='joe', status='accepted'),
                complete=True,
                objects=[dict(
                    id='o1',
                    **{'class': 'button'},
                    box=[10, 10, 50, 30],
                    visibility='visible',
                    provenance='candidate-model-output',
                )],
                focus=dict(state='no_focus', box=None),
            ))
            manifest = dict(
                version='tvbench-v1',
                classes=['button'],
                baseline=dict(confidence=0.5),
                apps=[dict(id='AppA', sealed=False)],
                cases=[dict(
                    id='case-1', app='AppA', flow='f1', status='captured', width=100, height=100,
                    image=dict(path=str(img.relative_to(q.ROOT)), sha256='abc'),
                    labels=dict(path=str(label_path.relative_to(q.ROOT)), sha256=q.digest(label_path)),
                )],
            )
            preds = {'case-1': dict(id='case-1', imageSHA256='abc', status='ok', detections=[], focusBox=None, latencyScope='unavailable', latencyUnavailableReason='test')}
            with self.assertRaisesRegex(ValueError, 'candidate_prediction_as_reference'):
                tvbench.score_manifest(manifest, preds)

    def test_sealed_apps_emit_aggregate_only(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='tvbench-sealed-') as tmp:
            root = Path(tmp)
            img = root / 'secret-frame-xyz.png'
            img.write_bytes(b'fake')
            label_path = root / 'labels.json'
            q.save(label_path, dict(
                imageSHA256='abc',
                review=dict(blinded=True, reviewer='joe', status='accepted'),
                complete=True,
                objects=[dict(
                    id='o1',
                    **{'class': 'button'},
                    box=[10, 10, 50, 30],
                    visibility='visible',
                    provenance='sdk-draft:b1',
                )],
                focus=dict(state='focused', box=[10, 10, 50, 30]),
            ))
            manifest = dict(
                version='tvbench-v1',
                classes=['button'],
                baseline=dict(confidence=0.5),
                apps=[dict(id='SealedApp', sealed=True)],
                cases=[dict(
                    id='secret-case-001', app='SealedApp', flow='secret-flow', status='captured', width=100, height=100,
                    image=dict(path=str(img.relative_to(q.ROOT)), sha256='abc'),
                    labels=dict(path=str(label_path.relative_to(q.ROOT)), sha256=q.digest(label_path)),
                )],
            )
            preds = {'secret-case-001': dict(
                id='secret-case-001', imageSHA256='abc', status='ok',
                detections=[dict(cls='button', box=[10, 10, 50, 30], score=0.9)],
                focusBox=[10, 10, 50, 30], latencyScope='unavailable', latencyUnavailableReason='test',
            )}
            rep = tvbench.score_manifest(manifest, preds)
            self.assertTrue(rep['sealed'])
            self.assertNotIn('rows', rep)
            serialized = json.dumps(rep)
            self.assertNotIn('secret-case-001', serialized)
            self.assertNotIn('secret-frame-xyz', serialized)
            self.assertEqual(rep['overall']['controlsFound']['numerator'], 1)
            self.assertEqual(rep['focusSummary']['all']['correctFocused'], 1)

    def test_rejects_pytorch_checkpoint(self):
        with self.assertRaisesRegex(ValueError, 'tvbench_shipping_mlpackage_required'):
            tvbench.predict_coreml('weights/best.pt', [])

    def test_score_focus_with_focusring_filters_focusable_and_dispositions(self):
        cases = [
            dict(id='c1', width=200, height=100, status='captured', image=dict(path='f1.png', sha256='h1')),
            dict(id='c2', width=200, height=100, status='captured', image=dict(path='f2.png', sha256='h2')),
        ]
        dets = {
            'c1': [
                dict(cls='label', box=[0, 0, 50, 20], score=0.99),  # unsupportedRole in raw 41-class taxonomy
                dict(cls='primaryButton', box=[10, 10, 40, 20], score=0.9),
                dict(cls='collectionItem', box=[100, 10, 40, 20], score=0.8),
                dict(cls='secondaryButton', box=[400, 400, 20, 20], score=0.7),  # cropRejected (outside 200x100)
            ],
            'c2': [dict(cls='primaryButton', box=[10, 10, 40, 20], score=0.9)],
        }
        calls = []

        def fake_invoke(items, model_path):
            calls.append([i['id'] for i in items])
            return {
                'version': 1,
                'results': [
                    {'id': 'c1|1', 'probability': 0.50, 'modelInputRGBSHA256': 'rgb1'},
                    {'id': 'c1|2', 'probability': 0.91, 'modelInputRGBSHA256': 'rgb2'},
                    {'id': 'c2|0', 'probability': 0.80, 'modelInputRGBSHA256': 'rgb3'},
                ],
            }

        execs = tvbench.score_focus_with_focusring(
            cases, dets, 'FocusRingDetector.mlmodelc', conf=0.25, threshold=0.85,
            class_names=['label', 'primaryButton', 'collectionItem', 'secondaryButton'],
            invoke_fn=fake_invoke,
        )
        self.assertEqual(calls, [['c1|1', 'c1|2', 'c2|0']])
        self.assertEqual(execs['c1']['focusBox'], [100, 10, 40, 20])
        self.assertEqual(execs['c1']['unsupportedRoleCount'], 1)
        self.assertEqual(execs['c1']['cropRejectedCount'], 1)
        self.assertEqual(execs['c1']['scoredCount'], 2)
        self.assertIsNone(execs['c2']['focusBox'])
        self.assertTrue(execs['c2']['candidates'][0]['isAmbiguous'])

    def test_zero_ap50_and_label_hash_mismatch_and_wrong_class(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='tvbench-metrics-') as tmp:
            root = Path(tmp)
            img = root / 'f.png'
            img.write_bytes(b'imgbytes')
            img_sha = q.digest(img)
            label_path = root / 'labels.json'
            q.save(label_path, dict(
                imageSHA256=img_sha,
                review=dict(blinded=True, reviewer='joe', status='accepted'),
                complete=True,
                objects=[dict(id='o1', **{'class': 'button'}, box=[10, 10, 50, 30], visibility='visible', provenance='sdk')],
                focus=dict(state='no_focus', box=None),
            ))
            manifest = dict(
                version='tvbench-v2',
                classes=['button', 'cell'],
                baseline=dict(confidence=0.25),
                apps=[dict(id='AppA', sealed=False)],
                cases=[dict(
                    id='case-1', app='AppA', flow='f1', status='captured', width=200, height=100,
                    image=dict(path=str(img.relative_to(q.ROOT)), sha256=img_sha),
                    labels=dict(path=str(label_path.relative_to(q.ROOT)), sha256=q.digest(label_path)),
                )],
            )
            preds = {'case-1': dict(
                id='case-1', imageSHA256=img_sha, status='ok',
                detections=[dict(cls='cell', box=[10, 10, 50, 30], score=0.9)],  # wrong-class detection -> 0.0 AP
                focusBox=None, latencyScope='unavailable', latencyUnavailableReason='test',
            )}
            rep = tvbench.score_manifest(manifest, preds)
            self.assertEqual(rep['overall']['controlsFound']['numerator'], 0)
            self.assertEqual(rep['rows'][0]['wrongClass'], 1)
            # Separate officialAP50 / customAP50 preserves 0.0 cleanly (never hidden by falsy `or`)
            if rep['officialCOCO']['status'] == 'available':
                self.assertEqual(rep['officialAP50'], 0.0)
                self.assertIsNone(rep['customAP50'])
            else:
                self.assertIsNone(rep['officialAP50'])
                self.assertEqual(rep['customAP50'], 0.0)

            bad_manifest = dict(manifest, cases=[dict(manifest['cases'][0], labels=dict(path=str(label_path.relative_to(q.ROOT)), sha256='0'*64))])
            with self.assertRaisesRegex(ValueError, 'tvbench_labels_sha_mismatch'):
                tvbench.score_manifest(bad_manifest, preds)

    def test_greedy_same_class_nms_at_030(self):
        kept = tvbench.greedy_same_class_nms([
            dict(cls='button', box=[0, 0, 100, 100], score=0.9),
            dict(cls='button', box=[30, 0, 100, 100], score=0.8),  # IoU = 7000/13000 = 0.538 >= 0.30 -> suppressed
            dict(cls='cell', box=[0, 0, 100, 100], score=0.7),    # different class -> kept
        ], iou_threshold=0.30)
        self.assertEqual(len(kept), 2)
        self.assertEqual([d['cls'] for d in kept], ['button', 'cell'])


if __name__ == '__main__':
    unittest.main()
