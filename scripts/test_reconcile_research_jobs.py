"""Check successor evidence without using the live queue."""
import copy
import tempfile
import unittest
from pathlib import Path
import research_queue as q
from reconcile_research_jobs import reconcile


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT/'.build')
        self.addCleanup(self.temp.cleanup)
        self.queue = Path(self.temp.name)
        self.spec = dict(template=dict(id='T01', inputs={}, parameters={}))
        for name in ('old', 'new'):
            folder = self.queue/'jobs'/name
            folder.mkdir(parents=True)
            q.save(folder/'spec.json', self.spec)
        self.attempt = self.queue/'jobs/new/attempts/1'
        (self.attempt/'out').mkdir(parents=True)
        q.save(self.attempt/'out/result.json', {'value': 1})
        self.result = dict(status='complete', specSHA256=q.text_digest(self.spec),
                           outputs=[dict(path='result.json', sha256=q.digest(self.attempt/'out/result.json'))])
        q.save(self.attempt/'result.json', self.result)
        self.doc = dict(version='research-reconciliation-v1', pairs=[dict(
            old='old', replacement='new', comparison='template',
            reason='The corrected successor answers the original question.')])

    def test_verified_without_mutation(self):
        paths = list(self.queue.rglob('*.json'))
        before = {str(p):q.digest(p) for p in paths}
        report = reconcile(self.doc, self.queue)
        self.assertEqual(report['verifiedReplacements'], 1)
        self.assertEqual(before, {str(p):q.digest(p) for p in paths})

    def test_changed_output_rejected(self):
        q.save(self.attempt/'out/result.json', {'value': 2}, replace=True)
        with self.assertRaisesRegex(ValueError, 'outputs_changed'):
            reconcile(self.doc, self.queue)

    def test_changed_spec_rejected(self):
        q.save(self.queue/'jobs/new/spec.json', dict(self.spec, changed=True), replace=True)
        with self.assertRaisesRegex(ValueError, 'spec_changed'):
            reconcile(self.doc, self.queue)

    def test_failed_successor_rejected(self):
        q.save(self.attempt/'result.json', dict(self.result, status='failed'), replace=True)
        with self.assertRaisesRegex(ValueError, 'not_complete'):
            reconcile(self.doc, self.queue)

    def test_duplicate_source_rejected(self):
        self.doc['pairs'] *= 2
        with self.assertRaisesRegex(ValueError, 'duplicate_source'):
            reconcile(self.doc, self.queue)

    def test_changed_controls_remain_visible(self):
        new = copy.deepcopy(self.spec)
        new['template']['parameters'] = {'changed': True}
        q.save(self.queue/'jobs/new/spec.json', new, replace=True)
        q.save(self.attempt/'result.json', dict(self.result, specSHA256=q.text_digest(new)), replace=True)
        report = reconcile(self.doc, self.queue)
        self.assertFalse(report['rows'][0]['controls']['parameters']['equal'])

    def test_question_comparison_shows_changed_question(self):
        specs = dict(old=dict(question='Old question?', authority='diagnostic', adapter=dict(steps=['a.run'])),
                     new=dict(question='New question?', authority='diagnostic', adapter=dict(steps=['a.run'])))
        for name, spec in specs.items():
            q.save(self.queue/'jobs'/name/'spec.json', spec, replace=True)
        q.save(self.attempt/'result.json', dict(self.result, specSHA256=q.text_digest(specs['new'])), replace=True)
        self.doc['pairs'][0]['comparison'] = 'question'
        controls = reconcile(self.doc, self.queue)['rows'][0]['controls']
        self.assertFalse(controls['question']['equal'])
        self.assertTrue(controls['steps']['equal'])

    def test_unknown_comparison_rejected(self):
        self.doc['pairs'][0]['comparison'] = 'other'
        with self.assertRaisesRegex(ValueError, 'comparison_kind'):
            reconcile(self.doc, self.queue)


if __name__ == '__main__':
    unittest.main()
