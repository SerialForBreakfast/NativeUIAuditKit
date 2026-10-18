"""BACKLOG410 pipeline: plan validation, expansion, review, confirmation, and the generated Tasks.md table."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

import research_queue as q
import backlog_pipeline as p

INPUTS = {'bundle': {'file': 'Research/Experiments/backlog405-native-inputs.json'},
          'model': {'file': 'reports/work/research-queue/jobs/hcf375c-70-crop-train/attempts/1/out/final.pt'},
          'tool': {'file': '.build/standard392-swift/arm64-apple-macosx/debug/FocusRingTool'}}


def record(**plan):
    value = dict(template='T41', owner='Maximum-mini-NUIAK', jobPrefix='t410', rule='any-loss', control='control',
                 question='Does a fixed one-pixel shift of the known box lose previous correct selections?',
                 decision='Record the smallest losing shift as the localization tolerance.',
                 outcomes=dict(supported='Prioritize localization repair.', contradicted='Shift is tolerated.',
                               inconclusive='Complete every arm first.'),
                 shared=dict(inputs=INPUTS, parameters=dict(source='known-box')),
                 arms=[dict(id='control', parameters=dict(intervention=dict(kind='none'))),
                       dict(id='dxp1', parameters=dict(intervention=dict(kind='translate', dx=1, dy=0)))])
    value.update(plan)
    return dict(id='B405-999', title='Test record', priority=3, hypothesis='Small shifts change decisions.',
                comparison='Known box versus shifted box', requirements=[dict(owner='Maximum-mini-NUIAK')],
                reconciliation=dict(disposition='unresolved', reason='open'), plan=value)


class PlanTests(unittest.TestCase):
    def test_valid_plan_expands_with_task_identity(self):
        docs = p.descriptions(record())
        self.assertEqual([d['id'] for d in docs], ['t410-control', 't410-dxp1'])
        self.assertTrue(all(d['task'] == 'B405-999' and d['outcomes']['supported'] for d in docs))
        self.assertEqual(docs[1]['parameters'], dict(source='known-box', intervention=dict(kind='translate', dx=1, dy=0)))

    def test_existing_job_arm_is_not_registered(self):
        docs = p.descriptions(record(arms=[dict(id='control', job='b405-002-known-none'),
                                          dict(id='dxp1', parameters=dict(intervention=dict(kind='translate', dx=1, dy=0)))]))
        self.assertEqual([d['id'] for d in docs], ['t410-dxp1'])

    def test_rejections(self):
        cases = [(dict(template='T99'), 'plan_template_unknown'),
                 (dict(question='What does this controlled test establish: something important here?'), 'plan_question_generic'),
                 (dict(control='missing'), 'plan_control_missing'),
                 (dict(rule='vote'), 'plan_rule'),
                 (dict(arms=[dict(id='control', parameters=dict(intervention=dict(kind='scale')))]), 'intervention_fields')]
        for change, error in cases:
            with self.assertRaisesRegex(ValueError, error):
                p.validate_plan(record(**change))

    def test_compiles_through_existing_template(self):
        import experiment_batch402 as batches
        temp = tempfile.TemporaryDirectory(dir=q.ROOT / '.build'); self.addCleanup(temp.cleanup)
        docs = batches.compile_batch(dict(version='experiment-batch-v1', jobs=p.descriptions(record())), Path(temp.name))
        import hcf_templates395 as templates
        spec = templates.build(docs[1])
        self.assertEqual(spec['task'], 'B405-999')
        self.assertEqual(spec['nextActionByOutcome']['supported'], 'Prioritize localization repair.')

    def test_expand_writes_batch_and_skips_existing_jobs(self):
        temp = tempfile.TemporaryDirectory(dir=q.ROOT / '.build'); self.addCleanup(temp.cleanup)
        queue, batches = Path(temp.name) / 'queue', Path(temp.name) / 'batches'
        (queue / 'jobs' / 't410-control').mkdir(parents=True)
        result = p.expand(dict(experiments=[record()]), 'B405-999', queue=queue, batches=batches)
        self.assertEqual(result['newJobs'], ['t410-dxp1'])
        self.assertEqual(result['existingJobs'], ['t410-control'])
        self.assertEqual(result['blocked'], [])
        self.assertFalse(result['registered'])
        self.assertEqual(json.loads((batches / 'B405-999.json').read_text())['jobs'][0]['id'], 't410-dxp1')


class ReviewTests(unittest.TestCase):
    def test_rules(self):
        rows = [dict(arm='control', state='complete', gains=[], lostPriorSuccesses=[]),
                dict(arm='a', state='complete', gains=['x'], lostPriorSuccesses=[])]
        self.assertEqual(p.propose('any-loss', 'control', rows), 'contradicted')
        self.assertEqual(p.propose('gain-without-loss', 'control', rows), 'supported')
        rows[1]['lostPriorSuccesses'] = ['y']
        self.assertEqual(p.propose('any-loss', 'control', rows), 'supported')
        self.assertEqual(p.propose('gain-without-loss', 'control', rows), 'contradicted')
        rows[1]['state'] = 'running'
        self.assertEqual(p.propose('any-loss', 'control', rows), 'inconclusive')
        self.assertEqual(p.propose('manual', 'control', rows[:1]), 'inconclusive')

    def test_review_and_confirm_on_retained_jobs(self):
        temp = tempfile.TemporaryDirectory(dir=q.ROOT / '.build'); self.addCleanup(temp.cleanup)
        results = Path(temp.name)
        rec = record(arms=[dict(id='control', job='b405-002-known-none'), dict(id='shift', job='b405-002-known-translate')])
        catalog = dict(experiments=[rec])
        value = p.review(catalog, 'B405-999', results=results)
        self.assertTrue(value['complete'])
        self.assertEqual(value['proposedOutcome'], 'supported')
        self.assertEqual(len(value['arms'][1]['lostPriorSuccesses']), 2)
        with self.assertRaisesRegex(ValueError, 'confirm_note'):
            p.confirm(catalog, 'B405-999', 'supported', 'agent:test', 'short', results=results)
        p.confirm(catalog, 'B405-999', 'supported', 'agent:test', 'Two retained successes are lost after a 1 px shift.',
                  results=results)
        self.assertEqual(rec['reconciliation']['disposition'], 'answered')
        self.assertEqual(json.loads((results / 'B405-999.json').read_text())['confirmed']['outcome'], 'supported')
        # A later review keeps the confirmation.
        self.assertEqual(p.review(catalog, 'B405-999', results=results)['confirmed']['outcome'], 'supported')

    def test_review_skips_reconciled_failed_job(self):
        from unittest import mock
        import research_dashboard_states as states
        temp = tempfile.TemporaryDirectory(dir=q.ROOT / '.build'); self.addCleanup(temp.cleanup)
        rec = record(arms=[dict(id='control', job='b405-002-known-none'), dict(id='shift', job='b405-002-known-translate')])
        catalog = dict(experiments=[rec])
        with mock.patch.object(p, 'task_jobs', return_value=['t46-old-failed']):
            # Without a reviewed successor the unknown job stays an open row and blocks confirmation.
            with mock.patch.object(states, 'successors', return_value={}):
                self.assertFalse(p.review(catalog, 'B405-999', results=Path(temp.name))['complete'])
            mapping = {'t46-old-failed': ('b405-002-known-translate', 'Repaired successor.')}
            with mock.patch.object(states, 'successors', return_value=mapping):
                value = p.review(catalog, 'B405-999', results=Path(temp.name))
        self.assertTrue(value['complete'])
        self.assertEqual(value['superseded'], [dict(job='t46-old-failed', supersededBy='b405-002-known-translate')])


class AddTests(unittest.TestCase):
    def short(self, **change):
        value = dict(title='New test', parentTask='TASK-6a-10', track='IOS', priority=2,
                     question='On withheld iOS images, does confidence 0.10 recover lost label detections?',
                     comparison='Confidence 0.10 versus 0.25 on the same cached predictions',
                     baseline='B405-011 at 0.25.', sourceEvidence=['Research/Plans/Backlog410.md'], template='T42',
                     outcomes=dict(supported='Calibrate thresholds.', contradicted='Review labels.'),
                     requirements=[dict(owner='Maximum-mini-NUIAK', kind='data', missing='x', unblock='y')])
        value.update(change)
        return value

    def test_add_assigns_next_id_and_defaults(self):
        catalog = json.loads(p.CATALOG.read_text())
        before = max(int(r['id'][5:]) for r in catalog['experiments'])
        record = p.add(catalog, self.short())
        self.assertEqual(record['id'], 'B405-%03d' % (before + 1))
        self.assertEqual(record['cost']['executionCeiling'], catalog['profiles']['diagnostic']['budget'])
        self.assertIn('inconclusive', record['outcomes'])
        self.assertEqual(p.KIND_STATE[record['requirements'][0]['kind']], 'Needs data')

    def test_add_rejections(self):
        catalog = json.loads(p.CATALOG.read_text())
        for change, error in [(dict(question='What does this controlled test establish: anything at all here?'), 'add_question_generic'),
                              (dict(requirements=None), 'add_requirements_or_plan'),
                              (dict(sourceEvidence=['missing/file.md']), 'source_unavailable')]:
            short = self.short(**change)
            if short.get('requirements') is None:
                short.pop('requirements')
            with self.assertRaisesRegex(ValueError, error):
                p.add(json.loads(json.dumps(catalog)), short)
        with self.assertRaisesRegex(ValueError, 'add_fields'):
            p.add(catalog, dict(self.short(), unknown=1))


class BlockerTests(unittest.TestCase):
    def test_rank_by_dependents(self):
        def row(ident, template, deps=(), owner='Maximum-mini-NUIAK'):
            return dict(id=ident, template=dict(id=template), dependencies=list(deps),
                        reconciliation=dict(disposition='unresolved'),
                        requirements=[dict(owner=owner, kind='data', missing='m ' + ident)])
        catalog = dict(experiments=[row('B405-001', 'missing-adapter'), row('B405-002', 'T03', owner='Maximum-mini-TTR'),
                                    row('B405-003', 'T41', ['B405-002']), row('B405-004', 'T41', ['B405-003'])])
        catalog['experiments'][3]['plan'] = {}
        ranked = p.blockers(catalog)
        self.assertEqual([(g['template'], g['unblocks']) for g in ranked[:2]], [('T03', 3), ('T41', 2)])
        self.assertEqual(next(g for g in ranked if g['template'] == 'missing-adapter')['kind'], 'adapter')


class TableTests(unittest.TestCase):
    TEXT = ('# Tasks\n\n| ID | Owner | Status | Priority | Scientific question |\n| --- | --- | --- | --- | --- |\n'
            '| B405-998 | Maximum-mini-TTR | Needs data | P1 | Old |\n| B405-999 | Maximum-mini-NUIAK | Needs adapter | P3 | Old |\n\nAfter.\n')

    def catalog(self):
        other = record(); del other['plan']; other.update(id='B405-998', title='Unplanned')
        return dict(experiments=[other, record(arms=[dict(id='control', job='b405-002-known-none')])])

    def test_render_replaces_then_round_trips(self):
        first = p.render_tasks(self.catalog(), self.TEXT)
        self.assertIn(p.TABLE_BEGIN, first)
        self.assertIn('| B405-998 | Maximum-mini-TTR | Needs data | P3 | Unplanned | – | – |', first)
        self.assertIn('| B405-999 | Maximum-mini-NUIAK | Awaiting review | P3 | Test record | 1/1 | – |', first)
        self.assertTrue(first.endswith('After.\n'))
        self.assertEqual(p.render_tasks(self.catalog(), first), first)
        import experiment_backlog
        self.assertEqual(experiment_backlog.task_states(first)['B405-999']['state'], 'Awaiting review')

    def test_status_counts_ready_time(self):
        rows = [dict(job='a', task='B405-999', authority='diagnostic', state='complete', wallSeconds=10, displayState='complete'),
                dict(job='b', task='B405-999', authority='diagnostic', state='pending', displayState='ready'),
                dict(job='c', task='OTHER', authority='training', state='pending', displayState='ready')]
        value = p.status(self.catalog(), rows)
        self.assertEqual((value['readyJobs'], value['readySeconds'], value['readyUnknown']), (2, 10, 1))
        self.assertTrue(value['refill'])
        self.assertEqual([r['ready'] for r in value['records']], [0, 1])
        # B405-999's only planned arm is complete and has no result, so it waits for review.
        rows[1]['state'] = 'complete'; rows[1]['displayState'] = 'complete'
        self.assertEqual([r['id'] for r in p.status(self.catalog(), rows)['reviewPending']], ['B405-999'])


if __name__ == '__main__':
    unittest.main()
