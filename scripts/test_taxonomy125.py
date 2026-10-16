"""B405-125: check the frozen outline failure taxonomy of T20."""
from pathlib import Path
import tempfile
import unittest

import research_queue as q
import hcf_templates395 as templates
import template_analysis397 as analysis

JOBS = q.QUEUE / 'jobs'
SOURCE = JOBS / 'hcf397-proposal-failure-audit/spec.json'
FRAME = dict(focus='item-0', boxes={'item-0': [100, 100, 100, 50], 'item-1': [300, 100, 100, 50]})


class ModeTests(unittest.TestCase):
    def test_each_mode(self):
        self.assertEqual(analysis.failure_mode([300, 100, 100, 50], FRAME)[0], 'neighbor')
        self.assertEqual(analysis.failure_mode([100, 100, 40, 50], FRAME)[0], 'clipping')
        self.assertEqual(analysis.failure_mode([900, 900, 50, 50], FRAME)[0], 'decoration')
        self.assertEqual(analysis.failure_mode([100, 100, 100, 50], dict(FRAME, focus=None))[0], 'no-focus')
        # No focus overlap and neighbor IoU 0.33: below the neighbor limit, so not a named mode.
        self.assertEqual(analysis.failure_mode([250, 100, 100, 50], FRAME)[0], 'other')

    def test_unknown_taxonomy_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'taxonomy_unknown'):
            analysis.failure_taxonomy('outline-failure-v2', dict(rows=[]), {}, Path('.'))


@unittest.skipUnless(SOURCE.is_file(), 'HCF397 queue evidence is not present')
class HCF397Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='taxonomy125-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = q.load(SOURCE)['template']['inputs']

    def description(self, parameters):
        return dict(version='hcf-template-description-v1', id='taxonomy-test', owner='research-host-NUIAK', template='T20',
                    question='Which frozen modes explain the wrong selections of the outline rule?',
                    decision='Test only; the job decides nothing about the models.', inputs=self.inputs,
                    dependencies=[], parameters=parameters)

    def test_old_spec_is_unchanged_and_taxonomy_is_optional(self):
        old = q.load(SOURCE)
        new = templates.build(self.description({}))
        self.assertEqual(new['template']['parameters'], old['template']['parameters'])
        self.assertEqual(new['template']['inputs'], old['template']['inputs'])
        templates.build(self.description(dict(taxonomy='outline-failure-v1')))
        with self.assertRaisesRegex(ValueError, 'template_parameters'):
            templates.build(self.description(dict(taxonomy='outline-failure-v1', extra=1)))

    def test_hcf397_wrong_selections_are_all_classified(self):
        analysis.proposal_audit(self.inputs, dict(taxonomy='outline-failure-v1'), self.root)
        doc = q.load(self.root / 'failure-taxonomy.json')
        self.assertEqual(doc['wrong'], 25)
        self.assertEqual(sum(doc['total'].values()), 25)
        old = q.load(JOBS / 'hcf397-proposal-failure-audit/attempts/1/out/proposal-audit.json')
        self.assertEqual(q.load(self.root / 'proposal-audit.json')['rows'], old['rows'])

    def test_audit_without_taxonomy_writes_no_taxonomy(self):
        analysis.proposal_audit(self.inputs, {}, self.root)
        self.assertFalse((self.root / 'failure-taxonomy.json').exists())


if __name__ == '__main__':
    unittest.main()
