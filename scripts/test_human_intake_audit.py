"""Generated offline tests; software attestations never admit actual data."""
import copy
import json
import subprocess
import sys
import unittest

import human_annotation_review as h
import human_intake_audit as a
import human_regression_review as r
import human_review_finish as finish
import test_human_annotation_review as fixtures


class IntakeAuditTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.ReviewTests(); self.f.setUp()
        self.f.imported()
        self.batch = self.f.batch/'batch.json'
        self.out = self.f.root/'audit'

    def tearDown(self):
        self.f.tearDown()

    def reseal(self, path, doc):
        doc.pop('seal', None); doc['seal'] = h.digest(doc)
        self.f.dump(path, doc)

    def test_reproducible_population_and_real_queue_dispatch(self):
        before = {p: h.sha(p) for p in self.f.root.rglob('*') if p.is_file()}
        report = a.prepare(self.batch, self.out, count=1, seed=24)
        self.assertEqual({k:v for k,v in report.items() if k != 'seal'}, a.plan(self.batch, count=1, seed=24))
        self.assertEqual(report['sampling']['inclusionProbability'], .5)
        self.assertEqual(report['counts']['eligible'], 2)
        queue = self.out/'combined-queue.json'
        self.assertEqual(r.queue_scope(queue, self.out/'review/batch.json', 1), report['selectedFrames'])
        self.assertEqual(before, {p: h.sha(p) for p in before})
        with self.assertRaises(ValueError): a.prepare(self.batch, self.out)

    def test_larger_population_slices_and_wrong_report_entrypoint(self):
        batch = h.read(self.batch)
        seed_frame = batch['frames'][0]
        batch['frames'] = []
        for i in range(17):
            frame = copy.deepcopy(seed_frame)
            frame['id'] = f'frame-{i:02d}'
            frame['editorStem'] = f'{i+1:03d}-frame-{i:02d}'
            batch['frames'].append(frame)
        # Generated same-pixel fixtures test queue mechanics, not independent data.
        batch['counts']['imported'] = 17
        index_path = h.checked(h.ROOT, batch['index'])
        index = h.read(index_path)
        index['frames'] = [copy.deepcopy(index['frames'][0]) for _ in range(17)]
        self.reseal(index_path, index)
        batch['index'] = h.ref(index_path)
        batch['rawEvidence'] = [h.ref(index_path) if r['path'] == batch['index']['path'] else r
                                for r in batch['rawEvidence']]
        self.reseal(self.batch, batch)
        report = a.prepare(self.batch, self.out, count=17, exception_limit=0)
        self.assertEqual([len(s) for s in report['batches']], [8, 8, 1])
        queue = self.out/'combined-queue.json'
        self.assertEqual(len(r.queue_scope(queue, self.out/'review/batch.json', 3)), 1)
        with self.assertRaisesRegex(ValueError, 'use_intake_audit_summary'):
            r.coverage(queue)

    def test_revision_prefill_reset_and_mutable_original_ignored(self):
        self.f.annotate(); self.f.finish()
        revision = self.f.root/'revision/revision.json'
        original = self.f.batch/'editor/001-frame-0.json'
        saved = h.read(original); saved['shapes'][0]['points'][0][0] = 22
        self.f.dump(original, saved)
        a.prepare(self.batch, self.out, revision)
        doc = h.read(self.out/'review/editor/001-frame-0.json')
        self.assertEqual(doc['shapes'][0]['points'][0][0], 10.25)
        self.assertTrue(doc['shapes'][0]['flags']['focused'])
        self.assertFalse(doc['shapes'][0]['flags']['confirmed'])
        self.assertFalse(any(doc['flags'].values()))
        self.assertEqual(h.read(original), saved)

    def test_unknown_focus_not_invented_and_exception_overlap_reviewed_once(self):
        batch = h.read(self.batch)
        batch['frames'][0]['proposals'][0]['state'] = 'unknown'
        self.reseal(self.batch, batch)
        report = a.prepare(self.batch, self.out, count=2)
        self.assertEqual(report['exceptions']['selected'], ['frame-0'])
        self.assertEqual(report['exceptions']['overlap'], ['frame-0'])
        self.assertEqual(len(report['selectedFrames']), 2)
        flags = h.read(self.out/'review/editor/001-frame-0.json')['shapes'][0]['flags']
        self.assertFalse(flags['focused']); self.assertFalse(flags['unfocused'])
        self.assertEqual(report['frames'][0]['findings'], ['unknown_focus'])

    def test_deferred_exceptions_and_empty_supported_subset(self):
        batch = h.read(self.batch)
        for f in batch['frames']: f['proposals'][0]['state'] = 'unknown'
        self.reseal(self.batch, batch)
        report = a.plan(self.batch, count=1, exception_limit=1)
        self.assertEqual(report['exceptions']['deferred'], ['frame-1'])
        for f in batch['frames']: f['nativeUnresolved'] = True
        self.reseal(self.batch, batch)
        report = a.prepare(self.batch, self.out)
        self.assertEqual(report['counts']['excluded'], 2)
        self.assertEqual(report['selectedFrames'], [])
        self.assertIsNone(report['sampling']['inclusionProbability'])

    def test_aliases_accounted_not_silently_deduplicated(self):
        batch = h.read(self.batch); batch['frames'][1]['duplicateOf'] = 'frame-0'
        self.reseal(self.batch, batch)
        report = a.plan(self.batch)
        self.assertEqual(report['sampling']['denominator'], 1)
        self.assertEqual(report['frames'][1]['excluded'], ['existing_exact_duplicate_alias'])

    def test_protected_changed_hash_bad_geometry_and_duplicate_ids_rejected(self):
        original = h.read(self.batch)
        for change in (lambda d: d.update(partition='test'),
                       lambda d: d['frames'][0]['proposals'][0].update(bounds=[0,0,101,20]),
                       lambda d: d['frames'][0]['proposals'][0].update(state='invented'),
                       lambda d: d['frames'][1].update(id=d['frames'][0]['id']),
                       lambda d: d['frames'][1].update(editorStem=d['frames'][0]['editorStem']),
                       lambda d: d['frames'][0]['image'].update(sha256='0'*64)):
            doc = copy.deepcopy(original); change(doc); self.reseal(self.batch, doc)
            with self.assertRaises(ValueError): a.prepare(self.batch, self.out)
            self.assertFalse(self.out.exists())

    def test_resealed_selection_or_baseline_changes_rejected(self):
        a.prepare(self.batch, self.out, count=1)
        q = self.out/'combined-queue.json'
        original = h.read(q)
        doc = copy.deepcopy(original); doc['selectedFrames'] = ['frame-1']; self.reseal(q, doc)
        with self.assertRaises(ValueError): r.validate_queue(q)
        self.reseal(q, original)
        baseline = h.checked(h.ROOT, original['baseline'][0]['document'])
        doc = h.read(baseline); doc['shapes'][0]['label'] = 'listRow'; self.f.dump(baseline, doc)
        original['baseline'][0]['document'] = h.ref(baseline); self.reseal(q, original)
        with self.assertRaisesRegex(ValueError, 'baseline_annotations_changed'): r.validate_queue(q)

    def test_actual_finish_scoped_correction_summary_and_crop_qa(self):
        a.prepare(self.batch, self.out, count=1)
        batch = self.out/'review/batch.json'; queue = self.out/'combined-queue.json'
        ids = r.queue_scope(queue, batch)
        hidden = self.out/'review/editor/002-frame-1.json'; old_hidden = h.sha(hidden)
        edited = self.out/'review/editor/001-frame-0.json'
        doc = h.read(edited); doc['shapes'][0]['points'][0][0] += 1; self.f.dump(edited, doc)
        receipt = finish.apply_preview(finish.preview(batch, ids), self.out/'finished',
                                       reviewer='generated-fixture-only', attested=True)
        self.assertEqual(receipt['appliedFrames'], ids)
        self.assertEqual(old_hidden, h.sha(hidden))
        revision = self.out/'finished/revision/revision.json'
        summary = a.summarize(queue, revision)
        self.assertEqual(summary['lanes']['random'], dict(selected=1,completed=1,pending=0,changedAmongCompleted=1))
        self.assertFalse(summary['trainingEligible'])
        qa = h.crop_qa(batch, self.out/'crops', revision)
        self.assertEqual(qa['completed'], 2)  # Pending frames are diagnostics, not admitted labels.

    def test_software_completion_not_counted_as_human(self):
        a.prepare(self.batch, self.out)
        batch = self.out/'review/batch.json'
        finish.apply_preview(finish.preview(batch), self.out/'finished', reviewer='software',
                             reviewer_kind='software-test', attested=True)
        summary = a.summarize(self.out/'combined-queue.json', self.out/'finished/revision/revision.json')
        self.assertEqual(summary['lanes']['random']['completed'], 0)
        self.assertEqual(summary['lanes']['random']['pending'], 2)

    def test_invalid_sampling_limits(self):
        for options in (dict(seed=True),dict(count=0),dict(count=257),dict(exception_limit=-1)):
            with self.assertRaises(ValueError): a.plan(self.batch, **options)

    def test_actual_cli_and_wrong_revision_binding(self):
        command = [sys.executable, str(h.ROOT/'scripts/human_intake_audit.py'), 'prepare',
                   str(self.batch),str(self.out),'--count','1','--seed','42']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['random'], 1)
        self.f.annotate(); self.f.finish()
        with self.assertRaisesRegex(ValueError, 'revision_wrong_batch'):
            a.summarize(self.out/'combined-queue.json', self.f.root/'revision/revision.json')


if __name__ == '__main__': unittest.main()
