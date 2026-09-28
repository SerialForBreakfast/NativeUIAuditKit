"""Generated local fixtures; no capture, inference or real human attestations."""
import copy
import unittest

import human_annotation_review as h
import human_regression_review as r
import human_review_finish as bulk
import test_human_annotation_review as fixtures


class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.ReviewTests(); self.f.setUp()

    def tearDown(self):
        self.f.tearDown()

    def queue(self, **kwargs):
        self.f.imported()
        path = self.f.root/'queue.json'
        h.write(path, r.prepare(self.f.batch/'batch.json', **kwargs), sealed=True)
        return path

    def reseal(self, path, document):
        document.pop('seal', None)
        document['seal'] = h.digest(document)
        self.f.dump(path, document)

    def test_deterministic_queue_and_complete_accounting(self):
        path = self.queue(limit=1)
        doc = r.validate_queue(path)
        self.assertEqual(doc['selectedFrames'], ['frame-0'])
        self.assertEqual(doc['counts'], {'selected':1, 'deferred':1})
        self.assertEqual(r.queue_scope(path, self.f.batch/'batch.json', 1), ['frame-0'])
        self.assertEqual(r.prepare(self.f.batch/'batch.json', limit=1), {k:v for k,v in doc.items() if k != 'seal'})
        with self.assertRaises(ValueError): r.queue_scope(path, self.f.batch/'batch.json', 2)

    def test_scope_does_not_confirm_hidden_frame(self):
        self.queue()
        hidden = sorted((self.f.batch/'editor').glob('*.json'))[1]
        before = h.sha(hidden)
        plan = bulk.preview(self.f.batch/'batch.json', ['frame-0'])
        receipt = bulk.apply_preview(plan, self.f.root/'finish', reviewer='fixture', attested=True)
        self.assertEqual(receipt['appliedFrames'], ['frame-0'])
        self.assertEqual(h.sha(hidden), before)
        self.assertNotIn('completeness', receipt)

    def test_completeness_and_coverage_are_explicit_revision_bound(self):
        path = self.queue()
        output = self.f.root/'finish'
        bulk.apply_preview(bulk.preview(self.f.batch/'batch.json'), output,
                           reviewer='generated-fixture', attested=True, complete_frames=True)
        revision = output/'revision/revision.json'
        report = r.coverage(path, revision, output/'completeness.json')
        self.assertEqual(report['families']['unknown']['complete'], 2)
        self.assertEqual(sum(c['count'] for c in report['controlSupport']), 2)
        self.assertEqual(report['families']['native-list']['status'], 'unrepresented')
        self.assertFalse(h.read(revision)['completeFrameCandidates'])
        self.assertFalse(report['trainingEligible'])
        snapshot = next((output/'revision/editor-snapshot').glob('*.json'))
        doc = h.read(snapshot); doc['shapes'][0]['points'][0][0] += 1
        self.f.dump(snapshot, doc)
        with self.assertRaises(ValueError): r.coverage(path, revision, output/'completeness.json')

    def test_software_cannot_attest(self):
        self.queue()
        with self.assertRaisesRegex(ValueError, 'completeness_requires_human'):
            bulk.apply_preview(bulk.preview(self.f.batch/'batch.json'), self.f.root/'finish',
                               reviewer='software', reviewer_kind='software-test', attested=True, complete_frames=True)
        self.assertFalse((self.f.root/'finish').exists())

    def duplicate_fixture(self, conflict=False):
        image0 = self.f.spec['frames'][0]['image']
        self.f.spec['frames'][1]['image'] = copy.deepcopy(image0)
        obs0 = h.read(self.f.source/'frame-0.json')['data']['observation']['_0']
        self.f.alter_obs(lambda o: o.update(imageBase64=obs0['imageBase64']), 1)
        if not conflict:
            self.f.spec['frames'][1]['proposals'] = copy.deepcopy(self.f.spec['frames'][0]['proposals'])
        self.f.save_spec()

    def test_exact_duplicates_keep_timeline_and_skip_annotation(self):
        self.duplicate_fixture()
        before = h.sha(self.f.source/'timeline.json')
        path = self.queue()
        doc = r.validate_queue(path)
        self.assertEqual(doc['counts'], {'selected':1, 'exact-duplicate':1})
        self.assertEqual(doc['frames'][1]['canonical'], 'frame-0')
        self.assertEqual(h.sha(self.f.source/'timeline.json'), before)
        self.assertEqual(len(h.read(self.f.batch/'batch.json')['frames']), 2)

    def test_duplicate_conflicting_labels_block_both(self):
        self.duplicate_fixture(conflict=True)
        doc = r.validate_queue(self.queue())
        self.assertEqual(doc['counts'], {'blocked':2})
        self.assertEqual(doc['selectedFrames'], [])

    def test_changed_membership_even_resealed_is_rejected(self):
        path = self.queue()
        doc = h.read(path); doc['selectedFrames'].reverse(); self.reseal(path, doc)
        with self.assertRaises(ValueError): r.validate_queue(path)

    def test_changed_pixels_and_missing_file_fail_closed(self):
        path = self.queue()
        image = h.checked(h.ROOT, h.read(self.f.batch/'batch.json')['frames'][0]['image'])
        image.write_bytes(b'corrupt')
        with self.assertRaises(ValueError): r.validate_queue(path)
        image.unlink()
        with self.assertRaises((ValueError, OSError)): r.validate_queue(path)

    def test_metadata_version_role_and_coverage(self):
        meta = self.f.root/'metadata.json'
        h.write(meta, dict(version=r.META, **h.FLAGS, screens={'screen':
                dict(app='Settings', layout='list', family='native-list', focusTreatment='white-row')}), sealed=True)
        path = self.queue(metadata_path=meta)
        self.assertEqual(r.coverage(path)['families']['native-list']['selected'], 2)
        self.f.annotate(); self.f.finish()
        self.assertEqual(r.coverage(path, self.f.root/'revision/revision.json')['controlSupport'][0]['focusTreatment'], 'white-row')
        doc = h.read(meta); doc['trainingEligible'] = True; self.reseal(meta, doc)
        with self.assertRaises(ValueError): r.validate_queue(path)

    def test_empty_supported_subsets_no_fabricated_support(self):
        report = r.coverage(self.queue())
        self.assertEqual(report['controlSupport'], [])
        self.assertTrue(all(f['complete'] == 0 for f in report['families'].values()))

    def test_family_rotation_and_near_pixels_are_not_duplicates(self):
        self.f.spec['frames'][1]['screen'] = 'list-screen'
        self.f.save_spec()
        meta = self.f.root/'metadata.json'
        h.write(meta, dict(version=r.META, **h.FLAGS, screens={
            'screen':dict(app='Home', layout='grid', family='artwork-grid'),
            'list-screen':dict(app='Settings', layout='rows', family='native-list')}), sealed=True)
        queue = r.validate_queue(self.queue(metadata_path=meta))
        self.assertEqual([f['family'] for f in queue['frames']], ['artwork-grid', 'native-list'])
        self.assertEqual(queue['counts'], {'selected':2})

    def test_unknown_family_and_unlisted_screen_rejected(self):
        self.f.imported()
        meta = self.f.root/'metadata.json'
        for screens in ({'missing':{}}, {'screen':{'family':'guessed'}}):
            self.reseal(meta, dict(version=r.META, **h.FLAGS, screens=screens))
            with self.assertRaises(ValueError): r.prepare(self.f.batch/'batch.json', meta)

    def test_completeness_wrong_revision_and_membership_rejected(self):
        self.queue()
        output = self.f.root/'finish'
        bulk.apply_preview(bulk.preview(self.f.batch/'batch.json'), output,
                           reviewer='fixture', attested=True, complete_frames=True)
        path = output/'completeness.json'
        doc = h.read(path); doc['frames'].append('not-a-frame'); self.reseal(path, doc)
        with self.assertRaises(ValueError): r.checked_completeness(path, output/'revision/revision.json')

    def test_invalid_scope_rejected_before_writes(self):
        self.queue()
        for ids in (['missing'], ['frame-0', 'frame-0']):
            with self.assertRaises(ValueError): bulk.preview(self.f.batch/'batch.json', ids)


if __name__ == '__main__':
    unittest.main()
