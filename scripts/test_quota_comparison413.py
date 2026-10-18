"""T44 quota comparison: parameter and quota checks, ancestry, and actual-queue runs on 2 pinned HCF402 captures."""
import json
import tempfile
import unittest
from pathlib import Path

import research_queue as q
import experiment_batch402 as batches
from quota_comparison413 import parameters, quotas, ancestry, DIMENSIONS

QUOTAS = 'Research/Experiments/focus-quotas413.json'
MANIFESTS = 'Research/Experiments/quota-manifests413.json'
FROZEN = ['scene', 'sceneTheme', 'hardNegative', 'total']


def small_manifests():
    """The focused and no-focus HCF402 captures: 18 frames, 2 related groups, real role ancestry."""
    entries = q.load(q.ROOT / MANIFESTS)['manifests']
    pick = [e for e in entries if '/hcf402-focused-r3/' in e['capture']['path'] or '/hcf402-no-focus-r4/' in e['capture']['path']]
    assert len(pick) == 2
    return pick


class UnitTests(unittest.TestCase):
    def test_parameters(self):
        self.assertEqual(parameters(dict(quotaSet='frozen', eligibility='admitted', dimensions=['scene']))[0], 'frozen')
        for value, error in [(dict(quotaSet='draft', eligibility='any', dimensions=['scene']), 'quota_set'),
                             (dict(quotaSet='frozen', eligibility='all', dimensions=['scene']), 'quota_eligibility'),
                             (dict(quotaSet='frozen', eligibility='any', dimensions=[]), 'quota_dimensions'),
                             (dict(quotaSet='frozen', eligibility='any', dimensions=['scene', 'scene']), 'quota_dimensions'),
                             (dict(quotaSet='frozen', eligibility='any', dimensions=['color']), 'quota_dimensions'),
                             (dict(quotaSet='frozen', eligibility='any'), 'quota_parameters')]:
            with self.assertRaisesRegex(ValueError, error):
                parameters(value)

    def test_unfrozen_quota_refusal(self):
        doc = q.load(q.ROOT / QUOTAS)
        self.assertEqual(len(quotas(doc, 'frozen', tuple(FROZEN))), 17)
        for dim in ('family', 'familyTheme'):
            with self.assertRaisesRegex(ValueError, 'quota_unfrozen:' + dim):
                quotas(doc, 'frozen', ('scene', dim))
        self.assertEqual(len(quotas(doc, 'proposed', DIMENSIONS)), len(doc['quotas']))
        # A single proposed entry inside a frozen dimension also blocks a frozen run.
        changed = json.loads(json.dumps(doc))
        changed['quotas'][0]['status'] = 'proposed'
        with self.assertRaisesRegex(ValueError, 'quota_unfrozen:scene'):
            quotas(changed, 'frozen', ('scene',))

    def test_ancestry(self):
        elements = {e['id']: e for e in [dict(id='region-0', role='layout_region'),
                                         dict(id='item-0', role='control_wrapper', declared_parent_id='region-0'),
                                         dict(id='item-1', role='control_wrapper', parent_id='item-2'),
                                         dict(id='item-2', role='control_wrapper', parent_id='item-1')]}
        self.assertEqual(ancestry(elements, 'item-0'), 'region-0')
        self.assertIsNone(ancestry(elements, 'item-1'))  # cycle
        self.assertIsNone(ancestry(elements, 'missing'))


class QueueTests(unittest.TestCase):
    """Frozen and proposed runs count real captures. A changed pin or an unfrozen dimension fails without output."""

    def test_actual_queue(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='quota413-') as folder:
            root = Path(folder); queue = root / 'queue'
            pick = small_manifests()
            q.save(root / 'small.json', dict(version='quota-manifests-v1', manifests=pick))
            q.save(root / 'one.json', dict(version='quota-manifests-v1', manifests=pick[:1]))
            q.save(root / 'quotas.json', q.load(q.ROOT / QUOTAS))

            def desc(ident, manifests, **change):
                value = dict(quotaSet='frozen', eligibility='admitted', dimensions=FROZEN); value.update(change)
                return dict(version='hcf-template-description-v1', id=ident, owner='test-NUIAK', template='T44',
                            question='How many eligible related groups do the pinned HCF402 captures add to each quota?',
                            decision='Name every quota deficit. Do not treat image count as coverage.',
                            inputs=dict(manifests=dict(file=q.relative(root / manifests)),
                                        quotas=dict(file=q.relative(root / 'quotas.json'))),
                            parameters=value, dependencies=[])
            docs = [desc('quota-frozen', 'small.json'),
                    desc('quota-proposed', 'small.json', quotaSet='proposed', eligibility='any', dimensions=list(DIMENSIONS)),
                    desc('quota-one', 'one.json', eligibility='any'),
                    desc('quota-unfrozen', 'small.json', dimensions=['scene', 'family']),
                    desc('quota-changed', 'small.json', eligibility='any')]
            batches.register_batch(dict(version='experiment-batch-v1', jobs=docs[:4]), queue,
                                   [d['id'] for d in docs[:4]], approver='test')
            for ident in ('quota-frozen', 'quota-proposed', 'quota-one'):
                outcome = q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=[ident])
                log = queue / 'jobs' / ident / 'attempts/1/stderr.log'
                self.assertEqual(outcome, [(ident, 'complete')], log.read_text()[-2000:] if log.is_file() else '')
            frozen = q.load(queue / 'jobs/quota-frozen/attempts/1/out/benchmark_summary.json')
            self.assertFalse(frozen['modelAccepted'])
            self.assertFalse(frozen['diagnosticOnly'])
            self.assertEqual((frozen['gains'], frozen['lostPriorSuccesses']), ([], []))
            self.assertEqual(frozen['frames'], 18)
            self.assertEqual(frozen['ancestry']['unresolved'], 0)
            self.assertGreater(frozen['ancestry']['resolved'], 0)
            # Study-pending captures are not admitted. Every frozen minimum is a named deficit.
            self.assertEqual(frozen['observations']['eligible'], 0)
            self.assertEqual({d['id']: d['decision'] for d in frozen['decisions']}['scene-gridMatrix'], 'deficit')
            self.assertEqual(frozen['deficitCount'], 13)
            proposed = q.load(queue / 'jobs/quota-proposed/attempts/1/out/benchmark_summary.json')
            self.assertTrue(proposed['diagnosticOnly'])
            self.assertEqual(proposed['groups']['eligible'], 2)
            self.assertEqual(proposed['slices']['family']['artwork']['groups'], 2)
            self.assertGreater(proposed['slices']['scene']['gridMatrix']['hardNegatives'], 0)
            # A changed manifest list changes the counts.
            one = q.load(queue / 'jobs/quota-one/attempts/1/out/benchmark_summary.json')
            self.assertLess(one['frames'], proposed['frames'])
            self.assertLess(one['observations']['eligible'], proposed['observations']['eligible'])
            # A frozen run that selects a proposed dimension fails before it writes a summary.
            self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=['quota-unfrozen']),
                             [('quota-unfrozen', 'failed')])
            attempt = queue / 'jobs/quota-unfrozen/attempts/1'
            self.assertFalse((attempt / 'out/benchmark_summary.json').exists())
            self.assertIn('quota_unfrozen:family', (attempt / 'stderr.log').read_text())
            # A quota file changed after registration fails the pin check.
            batches.register_batch(dict(version='experiment-batch-v1', jobs=docs[4:]), queue, ['quota-changed'], approver='test')
            q.save(root / 'quotas.json', dict(q.load(root / 'quotas.json'), date='changed'), replace=True)
            self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=['quota-changed']),
                             [('quota-changed', 'failed')])
            attempt = queue / 'jobs/quota-changed/attempts/1'
            self.assertFalse((attempt / 'out/benchmark_summary.json').exists())
            evidence = json.dumps(q.load(attempt / 'result.json'))
            if (attempt / 'stderr.log').is_file():
                evidence += (attempt / 'stderr.log').read_text()
            self.assertIn('input_changed', evidence)


if __name__ == '__main__':
    unittest.main()
