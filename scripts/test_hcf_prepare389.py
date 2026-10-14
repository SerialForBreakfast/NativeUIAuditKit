"""Test HCF preparation with isolated evidence, never the active queue."""
import copy
import shutil
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import hcf_prepare389 as h
import research_approval


class PrepareTests(unittest.TestCase):
    def methods(self):
        item = dict(gains=['a'], losses=[], counts=dict(frames=2, correct=2, wrong=0, misses=0))
        return {name: copy.deepcopy(item) for name in
                ('bright-closed-stroke-v1', 'crop-baseline', 'crop-candidate', 'full-screen-candidate')}

    def test_no_best_seed_selection(self):
        rows = h.choose(self.methods(), dict(previousSuccessesPreserved=True))
        self.assertEqual(set(rows), {'crop-candidate', 'full-screen-candidate'})
        self.assertTrue(rows['crop-candidate']['eligibleForExportQualification'])

    def test_repeat_loss_blocks_crop_not_detector(self):
        rows = h.choose(self.methods(), dict(previousSuccessesPreserved=False))
        self.assertFalse(rows['crop-candidate']['eligibleForExportQualification'])
        self.assertTrue(rows['full-screen-candidate']['eligibleForExportQualification'])

    def test_loss_blocks_candidate(self):
        methods = self.methods(); methods['full-screen-candidate']['losses'] = ['lost']
        self.assertFalse(h.choose(methods, dict(previousSuccessesPreserved=True))['full-screen-candidate']['eligibleForExportQualification'])

    def test_missing_repeat_evidence(self):
        with self.assertRaisesRegex(ValueError, 'seed_evidence_missing'):
            h.choose(self.methods(), {})

    def test_invalid_counts(self):
        methods = self.methods(); methods['crop-candidate']['counts']['correct'] = 3
        with self.assertRaisesRegex(ValueError, 'counts'):
            h.choose(methods, dict(previousSuccessesPreserved=True))

    def test_zero_support(self):
        methods = self.methods(); methods['crop-candidate']['counts'] = dict(frames=0, correct=0, wrong=0, misses=0)
        with self.assertRaisesRegex(ValueError, 'counts'):
            h.choose(methods, dict(previousSuccessesPreserved=True))

    def frame(self, ident='a', role='development', **kwargs):
        return dict(id=ident, group=kwargs.pop('group', ident), role=role, profile='hcf', family='cards', **kwargs)

    def test_no_focus_unknown_is_not_negative(self):
        result = h.coverage_rows([self.frame(), self.frame('b', focus=None)])
        self.assertEqual(result['noFocusLabelCount'], 1)
        self.assertFalse(result['auditImagesOpened'])

    def test_group_leak(self):
        with self.assertRaisesRegex(ValueError, 'group_leak'):
            h.coverage_rows([self.frame(group='g'), self.frame('b', 'audit', group='g')])

    def test_duplicate_frames(self):
        with self.assertRaisesRegex(ValueError, 'duplicate_or_empty'):
            h.coverage_rows([self.frame(), self.frame()])

    def test_model_scope(self):
        with self.assertRaisesRegex(ValueError, 'model_scope'):
            h.checked_model(dict(path='/etc/passwd', sha256='0'*64, kind='crop'))

    def test_dependency_hash_and_citations(self):
        base = h.q.ROOT / '.build/debug-output'
        with tempfile.TemporaryDirectory(dir=base) as name:
            root = Path(name); source = root / 'source.json'; h.q.save(source, {'rows': [self.frame()]})
            ref = dict(path=h.q.relative(source), sha256=h.q.digest(source))
            h.q.save(root / 'dependencies.json', [dict(job='producer', outputs=[ref])])
            with patch.object(h, 'OUT', root):
                docs, refs = h.inputs()
                self.assertEqual(refs, [ref]); self.assertEqual(len(docs), 1)
                source.write_text('{}')
                with self.assertRaisesRegex(ValueError, 'input_changed'):
                    h.inputs()

    def test_real_queue_dependency_and_coverage_adapter(self):
        with tempfile.TemporaryDirectory(dir=h.q.ROOT / '.build/debug-output') as name:
            root = Path(name); queue = root / 'queue'; modules = root / 'modules'
            modules.mkdir(); fixture = root / 'fixture.json'
            h.q.save(fixture, {'rows': [self.frame()]})
            (modules / 'producer389.py').write_text(
                "import research_queue as q\nOUT=None\ndef run():\n"
                f"    q.save(OUT/'admission.json',q.load(q.ROOT/{h.q.relative(fixture)!r}))\n")
            shutil.copyfile(Path(h.__file__), modules / 'hcf_prepare389.py')
            producer = dict(version='research-spec-v1', id='test389-producer', task='TEST389', owner='test',
                kind='screen', authority='diagnostic', hypothesis='Read isolated test data.', decisionRule='Test only.',
                inputs=[dict(path=h.q.relative(fixture), sha256=h.q.digest(fixture))], stage=[],
                adapter=dict(type='python-callable', steps=['producer389.run'], outputAttributes=['producer389.OUT']),
                limits=dict(timeoutSeconds=15, maxOutputBytes=1_000_000, maxAttempts=1))
            consumer = dict(version='research-spec-v2', id='test389-coverage', task='TEST389', owner='research-host-NUIAK',
                kind='screen', authority='diagnostic', jobKind='aggregation',
                hypothesis='Count isolated test evidence.', question='Does the actual queue resolve and read producer evidence?',
                controlledComparison='Use isolated fixtures only, never active experiment inputs.',
                decisionRule='Require one counted frame and exact producer citations.',
                nextActionByOutcome=dict(passed='Retain the tested dependency adapter.', failed='Fix the adapter before live dispatch.'),
                inputs=[], stage=[], dependencies=[dict(job=producer['id'], specSHA256=h.q.text_digest(producer), outputs=['admission.json'])],
                evidence=dict(citations='sources.json'),
                adapter=dict(type='python-callable', steps=['hcf_prepare389.coverage'], outputAttributes=['hcf_prepare389.OUT']),
                limits=dict(timeoutSeconds=15, maxOutputBytes=1_000_000, maxAttempts=1))
            for spec in (producer, consumer):
                path = root / (spec['id'] + '.json'); h.q.save(path, spec)
                h.q.submit(path, queue, modules)
                research_approval.approve(queue, spec['id'], 'test', 'Isolated HCF389 dependency test.', modules)
            results = list(h.q.run(queue, modules, 2, lock=root / 'runner.lock', job_ids=[producer['id'], consumer['id']]))
            results += list(h.q.run(queue, modules, 2, lock=root / 'runner.lock', job_ids=[consumer['id']]))
            self.assertEqual([value for _, value in results], ['complete', 'complete'])
            result = h.q.load(queue / 'jobs/test389-coverage/attempts/1/out/coverage.json')
            self.assertEqual(result['frames'], 1)
            self.assertFalse(result['modelAccepted'])


if __name__ == '__main__':
    unittest.main()
