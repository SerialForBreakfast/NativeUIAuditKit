"""MEASURE553 software tests. Synthetic replay exports only. No app, model execution, capture, or accuracy claim."""
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from PIL import Image
import research_queue as q
from experiment_templates import pin
from observer_identity398 import compiled_digest
import real_app_benchmark543 as b
import real_app_runtime553 as m

REVISION = 'c' * 40


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=q.ROOT/'.build'); self.root = Path(self.tmp.name)
        self.image = self.root/'frame.png'; Image.new('RGB', (100, 80), (12, 34, 56)).save(self.image)
        self.detector = self.model('detector', b'detector-test'); self.focus = self.model('focus', b'focus-test')
        self.pre = self.descriptor('preprocessing', 'yolo-letterbox-v1')
        self.tax = self.descriptor('taxonomy', 'sha256-canonical-model-manifest-v1:' + 'd' * 64)

    def tearDown(self):
        self.tmp.cleanup()

    def model(self, name, data):
        tree = self.root/(name + '.mlmodelc'); tree.mkdir(); (tree/'weights.bin').write_bytes(data)
        ref = self.root/(name + '-reference.json')
        q.save(ref, dict(version='compiled-model-reference-v1', root=q.relative(tree), compiledSHA256=compiled_digest(tree)))
        return pin(ref)

    def descriptor(self, kind, identity):
        path = self.root/(kind + '.json'); q.save(path, dict(version=m.DESCRIPTOR, kind=kind, identity=identity), replace=True); return pin(path)

    def replay(self, name, selected=True, detector=None, role='button', box=(10, 10, 30, 20)):
        root = self.root/name; root.mkdir()
        source = root/'source.png'; source.write_bytes(self.image.read_bytes()); digest = q.digest(source)
        q.save(root/'input-manifest.json', dict(source_sha256=digest))
        element = dict(id='E1', role=role, pixels=list(box), confidence=.9, focused=selected, ambiguous=False)
        det = detector or q.load(Path(q.ROOT/self.detector['path']))['compiledSHA256']
        provider = dict(elements=[element], detector_artifact_digest='compiled-tree-sha256-v1:' + det, partial=not selected,
                        focus_model='compiled-tree-sha256-v1:' + q.load(Path(q.ROOT/self.focus['path']))['compiledSHA256'],
                        focus_execution=dict(model_digest=q.load(Path(q.ROOT/self.focus['path']))['compiledSHA256'],
                                             model_digest_algorithm='compiled-tree-sha256-v1', model_scoring_complete=True),
                        rejected_geometry={} if selected else {'X': [0, 90, 10, 10]})
        selection = dict(id='E1', status='selected') if selected else dict(id=None, status='partial_provider_result')
        result = dict(action_authorized=False, predictionSelection=selection, ttr_observed=dict(source_revision=REVISION),
                      unavailable_provenance=['crop_identity'],
                      receipt=dict(action_authorized=False, image_sha256=digest, width=100, height=80, provider=provider),
                      runtime_provenance=dict(source_revision=REVISION, source_revision_scope='build_supplied_base_revision_not_clean_tree_attestation',
                                              preprocessing_identity='yolo-letterbox-v1', taxonomy_identity='sha256-canonical-model-manifest-v1:' + 'd' * 64,
                                              focus_digest_algorithm='compiled-tree-sha256-v1'))
        q.save(root/'result.json', result)
        q.save(root/'completion.json', dict(completed=True, source_sha256=digest, input_manifest_sha256=q.digest(root/'input-manifest.json'),
                                            result_sha256=q.digest(root/'result.json'), request_to_result_durable_ms=50.0))
        return q.relative(root)

    def receipt(self, replays, name='runtime.json'):
        request = self.root/(name + '-request.json')
        q.save(request, dict(replays=replays, detector=self.detector, focus=self.focus, preprocessing=self.pre, taxonomy=self.tax))
        m.runtime_receipt(request, self.root/name)
        return pin(self.root/name)

    def manifest(self, runtime, focus_state='focused'):
        marker = self.root/'marker.json'; q.save(marker, {'softwareFixture': True}, replace=True); ref = pin(marker)
        case = dict(id='case-one', app='test-app', flow='flow-one', group='group-one', status='captured', width=100, height=80,
                    image=pin(self.image), pixelSHA256=hashlib.sha256(Image.open(self.image).convert('RGB').tobytes()).hexdigest(), sdkEvidence=ref)
        focus = dict(state='focused', box=[10, 10, 30, 20]) if focus_state == 'focused' else dict(state=focus_state, box=None)
        labels = dict(imageSHA256=case['image']['sha256'], complete=True, focus=focus,
                      objects=[dict(id='control', **{'class': 'button'}, box=[10, 10, 30, 20], visibility='visible', provenance='software fixture')],
                      review=dict(blinded=True, reviewer='test-only', status='accepted'))
        lp = self.root/'labels.json'; q.save(lp, labels, replace=True); case['labels'] = pin(lp)
        baseline = dict(inputMode='screenshots-only', coordinates='xywh-top-left-pixels', orientation='upright', confidence=.5, matchingIoU=.5,
                        ttrRevision=REVISION, detector=self.detector, focus=self.focus, preprocessing=self.pre, taxonomy=self.tax, runtimeReceipt=runtime)
        app = dict(id='test-app', ancestry='independent-source', kind='independent-app', trainingExposure='excluded', sourceRevision='b' * 40)
        ap = self.root/'app.json'
        q.save(ap, dict(version='real-app-qualification-v1', **app, independent=True, controlledContent=True, sdkObservationsVerified=True), replace=True)
        app['qualification'] = pin(ap)
        doc = dict(version=b.VERSION, platform='tvOS', profile='standard', phase='pilot', trainingEligible=False, classes=['button', 'label'],
                   baseline=baseline, apps=[app], exclusions=dict(groups=[], flows=[], images=[], pixels=[]), cases=[case])
        mp = self.root/'manifest.json'; q.save(mp, doc, replace=True)
        fp = self.root/'freeze.json'; b.freeze(mp, fp)
        return pin(fp), q.text_digest(baseline)

    def score(self, replay, focus_state='focused', **extra):
        runtime = self.receipt([replay])
        frozen, digest = self.manifest(runtime, focus_state)
        request = self.root/'predictions-request.json'
        q.save(request, dict(freeze=frozen, configuration=digest, replays={'case-one': replay}, **extra))
        doc = m.predictions(request, self.root/'predictions.json')
        return doc, b.score(frozen, doc)

    def test_receipt_binds_observed_identities(self):
        ref = self.receipt([self.replay('r1')])
        receipt = q.load(q.ROOT/ref['path'])
        self.assertTrue(receipt['observedLoaded'])
        self.assertEqual(receipt['ttrRevision'], REVISION)
        self.assertEqual(receipt['preprocessingSHA256'], self.pre['sha256'])
        self.assertEqual(receipt['unavailableProvenance'], ['crop_identity'])

    def test_receipt_rejects_other_detector(self):
        with self.assertRaisesRegex(ValueError, 'observed_detector'):
            self.receipt([self.replay('r1', detector='e' * 64)])

    def test_receipt_rejects_other_preprocessing(self):
        self.pre = self.descriptor('preprocessing', 'scale-fill-v1')
        with self.assertRaisesRegex(ValueError, 'observed_preprocessing'):
            self.receipt([self.replay('r1')])

    def test_selected_replay_scores_correct(self):
        doc, report = self.score(self.replay('r1'))
        self.assertEqual(doc['partialResults'], 0)
        self.assertEqual(report['overall']['correctFocus']['value'], 1)
        self.assertEqual(report['overall']['perClass']['button']['recall']['value'], 1)
        self.assertEqual(report['overall']['timingByScope']['request-to-result-durable']['median'], 50)
        self.assertFalse(report['modelAccepted'])

    def test_partial_result_stays_abstention(self):
        doc, report = self.score(self.replay('r1', selected=False))
        self.assertEqual(doc['partialResults'], 1)
        self.assertIsNone(doc['cases'][0]['focusBox'])
        self.assertEqual(report['overall']['focusCounts'], {'abstention': 1})

    def test_unmapped_role_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unmapped_runtime_class:primaryButton'):
            self.score(self.replay('r1', role='primaryButton'))

    def test_class_map(self):
        replay = self.replay('r2', role='primaryButton')
        doc, report = self.score(replay, classMap={'primaryButton': 'button'})
        self.assertEqual(doc['cases'][0]['detections'][0]['class'], 'button')

    def test_replay_outside_receipt_rejected(self):
        runtime = self.receipt([self.replay('r1')])
        frozen, digest = self.manifest(runtime)
        request = self.root/'predictions-request.json'
        q.save(request, dict(freeze=frozen, configuration=digest, replays={'case-one': self.replay('r2')}))
        with self.assertRaisesRegex(ValueError, 'replay_not_in_runtime_receipt'):
            m.predictions(request, self.root/'predictions.json')

    def test_failed_case_stays_counted(self):
        runtime = self.receipt([self.replay('r1')])
        frozen, digest = self.manifest(runtime)
        request = self.root/'predictions-request.json'
        q.save(request, dict(freeze=frozen, configuration=digest, failed={'case-one': 'replay timed out'}))
        report = b.score(frozen, m.predictions(request, self.root/'predictions.json'))
        self.assertEqual(report['overall']['executionFailures'], 1)
        self.assertEqual(report['overall']['correctFocus']['value'], 0)

    def test_missing_case_rejected(self):
        runtime = self.receipt([self.replay('r1')])
        frozen, digest = self.manifest(runtime)
        request = self.root/'predictions-request.json'
        q.save(request, dict(freeze=frozen, configuration=digest, replays={}))
        with self.assertRaisesRegex(ValueError, 'case_coverage'):
            m.predictions(request, self.root/'predictions.json')


def report(config, outcomes, latency=50.0, detected=True):
    """Synthetic report rows: outcomes maps (app, flow, index) to a focus outcome."""
    rows = []
    for (app, flow, i), outcome in outcomes.items():
        ident = f'{app}-{flow}-{i}'
        rows.append(dict(id=ident, app=app, flow=flow, status='ok', focusState='focused', focusOutcome=outcome,
                         objects=[dict(id='c')], detected=['c'] if detected else [], measuredLatencyMs=latency,
                         latencyScope='request-to-result-durable'))
    return dict(freeze={'path': 'freeze.json', 'sha256': '0' * 64}, baselineSHA256=config, rows=rows)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=q.ROOT/'.build'); self.root = Path(self.tmp.name)
        self.keys = [(app, f'f{f}', i) for app in ('a1', 'a2', 'a3') for f in range(4) for i in range(2)]

    def tearDown(self):
        self.tmp.cleanup()

    def run_gate(self, left, right, retention=0, ratio=1.1):
        refs = {}
        for name, doc in (('base', left), ('cand', right)):
            q.save(self.root/(name + '.json'), doc, replace=True); refs[name] = pin(self.root/(name + '.json'))
        request = dict(baselineReport=refs['base'], candidateReport=refs['cand'], latencyRatio=ratio)
        if retention is not None:
            q.save(self.root/'retention.json', dict(lostPriorSuccesses=retention), replace=True); request['retentionReport'] = pin(self.root/'retention.json')
        q.save(self.root/'request.json', request, replace=True)
        out = self.root/'gate.json'
        if out.exists():
            out.unlink()
        return m.gate(self.root/'request.json', out)

    def improved(self):
        base = {k: 'correct' if k[2] == 0 else 'abstention' for k in self.keys}
        cand = {k: 'correct' for k in self.keys}
        return report('b' * 64, base), report('c' * 64, cand)

    def test_clear_improvement_passes(self):
        result = self.run_gate(*self.improved())
        self.assertTrue(result['gatePassed'], result['failedChecks'])
        self.assertEqual(result['improvedMetrics'], ['focus'])
        self.assertFalse(result['modelAccepted'])

    def test_lost_success_fails_even_with_gains(self):
        left, right = self.improved()
        right['rows'][0]['focusOutcome'] = 'abstention'
        left['rows'][0]['focusOutcome'] = 'correct'
        result = self.run_gate(left, right)
        self.assertIn('noLostFocus', result['failedChecks'])
        self.assertFalse(result['gatePassed'])

    def test_new_wrong_fails(self):
        left, right = self.improved()
        right['rows'][1]['focusOutcome'] = 'wrong-selection'
        self.assertIn('noNewWrong', self.run_gate(left, right)['failedChecks'])

    def test_retention_loss_and_missing_fail(self):
        self.assertIn('retentionPreserved', self.run_gate(*self.improved(), retention=3)['failedChecks'])
        self.assertIn('retention report missing', self.run_gate(*self.improved(), retention=None)['failedChecks'])

    def test_noise_does_not_pass(self):
        base = {k: 'correct' if (k[1], k[2]) != ('f0', 1) else 'abstention' for k in self.keys}
        cand = dict(base); cand[('a1', 'f0', 1)] = 'correct'
        result = self.run_gate(report('b' * 64, base), report('c' * 64, cand))
        self.assertIn('improvementBeyondInterval', result['failedChecks'])

    def test_latency_limit(self):
        left, right = self.improved()
        for row in right['rows']:
            row['measuredLatencyMs'] = 80.0
        self.assertIn('latencyWithinLimit', self.run_gate(left, right)['failedChecks'])

    def test_same_configuration_rejected(self):
        left, _ = self.improved()
        with self.assertRaisesRegex(ValueError, 'gate_membership'):
            self.run_gate(left, copy.deepcopy(left))

    def test_bootstrap_is_deterministic(self):
        left, right = self.improved()
        self.assertEqual(m.paired_bootstrap(left, right), m.paired_bootstrap(left, right))


if __name__ == '__main__':
    unittest.main()
