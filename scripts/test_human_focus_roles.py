"""Generated diagnostic role integration; no model or human artifact mutations."""
import unittest
import human_annotation_review as h
import human_regression_review as regression
import human_review_audit as audit
import human_review_finish as finish
import human_review_presets as presets
import test_human_annotation_review as fixtures


class RoleTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.ReviewTests(); self.f.setUp(); self.f.imported()
        self.taxonomy_hash = h.sha(h.CATEGORY)

    def tearDown(self):
        self.assertEqual(h.sha(h.CATEGORY), self.taxonomy_hash)
        self.f.tearDown()

    def test_finish_completeness_real_crops_and_audit(self):
        self.f.annotate(lambda doc: doc['shapes'][0].update(label='focus:tabItem'))
        result = finish.apply_preview(finish.preview(self.f.batch/'batch.json'), self.f.root/'finish',
            reviewer='generated-test-fixture', attested=True, complete_frames=True)
        revision = h.checked(h.ROOT, result['revision'])
        doc = regression.checked_revision(revision)
        self.assertEqual(doc['version'], h.FOCUS_REVISION)
        self.assertFalse(doc['trainingEligible'])
        self.assertEqual(doc['pairs'][0]['disposition'], 'reviewed')
        for frame in doc['frames']:
            control = frame['controls'][0]
            self.assertIsNone(control['class'])
            self.assertEqual(control['focusRole'], 'tabItem')
        self.assertEqual(regression.checked_completeness(self.f.root/'finish/completeness.json', revision),
                         {'frame-0','frame-1'})
        crops = h.crop_qa(self.f.batch/'batch.json', self.f.root/'crops', revision)
        self.assertEqual(crops['completed'], 2)
        report = audit.audit(revision, self.f.root/'crops/crop-qa.json')
        self.assertEqual(report['coverage']['focusRoles'], {'tabItem': 2})
        self.assertEqual(report['coverage']['classes'], {})
        queue = self.f.root/'queue.json'
        h.write(queue, regression.prepare(self.f.batch/'batch.json'), sealed=True)
        coverage = regression.coverage(queue, revision)
        self.assertEqual({s['category'] for s in coverage['controlSupport']}, {'focus:tabItem'})
        from human_focus_evaluation import admitted
        with self.assertRaisesRegex(ValueError, 'separate_admission'):
            admitted(revision, self.f.root/'crops/crop-qa.json')
        from focus_dataset_contract import validate_manifest
        with self.assertRaises(ValueError): validate_manifest(doc, self.f.root)

    def test_resealed_detector_mapping_is_rejected(self):
        self.f.annotate(lambda doc: doc['shapes'][0].update(label='focus:tabItem'))
        doc = self.f.finish()
        doc['frames'][0]['controls'][0]['class'] = 'tabBar'
        doc.pop('seal', None)
        path = self.f.root/'tampered.json'
        h.write(path, doc, sealed=True)
        with self.assertRaisesRegex(ValueError, 'invalid_focus_role_mapping'): h.read_revision(path)

    def test_role_mismatch_does_not_form_pair(self):
        self.f.annotate(lambda doc: doc['shapes'][0].update(label='focus:tabItem'))
        path = sorted((self.f.batch/'editor').glob('*.json'))[1]
        doc = h.read(path); doc['shapes'][0]['label'] = 'focus:otherFocusable'
        self.f.dump(path, doc)
        self.assertEqual(self.f.finish()['pairs'][0]['disposition'], 'blocked')

    def test_unsettled_remains_blocked_and_unknown_role_rejected(self):
        self.f.annotate(lambda doc: (doc['shapes'][0].update(label='focus:tabItem'),
                                     doc['flags'].update(settled=False)))
        self.assertEqual(self.f.finish()['frameCounts'], {'blocked':2})
        batch = h.validate_batch(self.f.batch/'batch.json')
        frame = batch['frames'][0]
        path = self.f.batch/'editor'/(frame['editorStem']+'.json')
        doc = h.read(path); doc['shapes'][0]['label'] = 'focus:madeUp'
        with self.assertRaises(ValueError): h.parse_editor_document(batch, frame, path, doc)

    def test_presets_and_legacy_versions(self):
        boxes = [dict(label='focus:tabItem', points=[[1,2],[20,30]])]
        path = presets.save('Tabs', (100,60), boxes, self.f.root/'presets')
        self.assertEqual(h.read(path)['version'], 'rectangle-preset-v2')
        self.assertEqual(presets.load(path, (100,60)), boxes)
        self.f.annotate()
        self.assertEqual(self.f.finish()['version'], h.REVISION)


if __name__ == '__main__':
    unittest.main()
