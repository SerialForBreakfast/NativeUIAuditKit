"""T49 transition training: unit and compiler checks. Set T49_TRAIN=1 to run the seed-42 qualification (about 8 min)."""
import copy
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import research_queue as q
import experiment_batch402 as batches
from transition_training415 import parameters, configuration, check_configuration, RECIPE_CONFIGS

BASELINE = 'reports/work/FOCUS-329/run/last.pt'
MEMBERSHIP = 'reports/work/TRANSITION-249/artifacts/package/membership.json'
PAIRS = 'reports/work/TEMPORAL414/pairs-graph364.json'
RECORDED = {'control': 'focus366-control-train', 'notification': 'focus366-notification-train'}


def description(ident, arm, seed, epochs=10):
    initialization = dict(path=BASELINE, sha256=q.digest(q.ROOT / BASELINE))
    membership = [dict(path=MEMBERSHIP, sha256=q.digest(q.ROOT / MEMBERSHIP))]
    return dict(version='hcf-template-description-v1', id=ident, owner='test-NUIAK', template='T49',
                question='Does the notification correction keep its gain over control at this seed?',
                decision='Compare the gain with the control seed range.',
                inputs=dict(configuration=dict(file=f'Research/ResearchSpecs/T49/{arm}-{seed}-config.json'),
                            initialization=dict(file=BASELINE), membership=dict(file=MEMBERSHIP),
                            admission=dict(job='focus366-admission', output='admission.json'), pairs=dict(file=PAIRS),
                            prior=dict(job='b405-061-forward', output='predictions.json')),
                parameters=dict(arm=arm, seed=seed), dependencies=[],
                training=dict(experimentLogRunId='B405-126', membership=membership, initialization=initialization,
                              epochs=epochs, storageBudgetBytes=2 << 30, resume='restart',
                              acceptanceEvidence='Seed-42 runs reproduce FOCUS366 counts. Screening only; no promotion.'))


def copy_jobs(queue, *jobs):
    for job in jobs:
        shutil.copytree(q.QUEUE / 'jobs' / job, queue / 'jobs' / job)


class UnitTests(unittest.TestCase):
    def test_parameters(self):
        self.assertEqual(parameters(dict(arm='notification', seed=43)), ('notification', 43))
        for value, error in [(dict(arm='gamma', seed=42), 'transition_arm'), (dict(arm='control', seed=7), 'transition_seed_not_predefined'),
                             (dict(arm='control'), 'transition_parameters')]:
            with self.assertRaisesRegex(ValueError, error): parameters(value)

    def test_configuration_keeps_recipe(self):
        init = dict(path=BASELINE, sha256=q.digest(q.ROOT / BASELINE))
        for arm in ('control', 'notification'):
            value = configuration(arm, 44, init)
            recipe = q.load(q.ROOT / RECIPE_CONFIGS[arm])
            changed = [a['path'] for a, b in zip(value['inputs'], recipe['inputs']) if a != b]
            self.assertEqual(changed, ['scripts/graph364.py', 'scripts/visibility364.py'][:len(changed)])
            self.assertEqual(len(value['inputs']), len(recipe['inputs']))
            self.assertEqual(q.load(q.ROOT / f'Research/ResearchSpecs/T49/{arm}-44-config.json'), value)
            check_configuration(value, arm, 44)
            bad = copy.deepcopy(value); bad['inputs'][0]['sha256'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'transition_recipe_changed'): check_configuration(bad, arm, 44)
            with self.assertRaisesRegex(ValueError, 'transition_configuration_binding'): check_configuration(value, arm, 43)

    def test_compiler(self):
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='transition415-') as folder:
            queue = Path(folder) / 'queue'; copy_jobs(queue, 'focus366-admission', 'b405-061-forward')
            spec, = batches.compile_batch(dict(version='experiment-batch-v1', jobs=[description('t49-ok', 'control', 43)]), queue)
            self.assertEqual({d['job'] for d in spec['dependencies']}, {'focus366-admission', 'b405-061-forward'})
            for doc, error in [(description('t49-epochs', 'control', 43, epochs=30), 'training_variant'),
                               (dict(description('t49-seed', 'control', 43), parameters=dict(arm='control', seed=45)),
                                'transition_seed_not_predefined')]:
                with self.assertRaisesRegex(ValueError, error):
                    batches.compile_batch(dict(version='experiment-batch-v1', jobs=[doc]), queue)


class EvidenceTests(unittest.TestCase):
    """Regression: b405-126-control-42 trained but failed with training_history_epoch_mismatch."""

    def test_finish_writes_trusted_evidence(self):
        import research_trust as trust
        import transition_training415 as t49
        source = q.QUEUE / 'jobs/b405-126-control-42'
        if not (source / 'attempts/1/out/last.pt').is_file():
            self.skipTest('retained failed attempt is not available')
        with tempfile.TemporaryDirectory(dir=q.ROOT / '.build', prefix='transition415-evidence-') as folder:
            job = Path(folder) / 'b405-126-control-42'; shutil.copytree(source, job)
            attempt = job / 'attempts/1'; out = attempt / 'out'; spec = q.load(job / 'spec.json')
            fit = q.load(out / 'fit.json'); fit.pop('epochs', None); q.save(out / 'fit.json', fit, replace=True)
            self.assertEqual(trust.check_evidence(spec, attempt, out), 'training_history_epoch_mismatch')
            t49.OUT = out
            t49.finish('control', 42)
            self.assertIsNone(trust.check_evidence(spec, attempt, out))
            with self.assertRaisesRegex(ValueError, 'transition_seed_not_applied'): t49.finish('control', 43)


@unittest.skipUnless(os.environ.get('T49_TRAIN') == '1', 'Set T49_TRAIN=1 for the 8-minute seed-42 qualification.')
class QualificationTests(unittest.TestCase):
    """The seed-42 notification run must reproduce the FOCUS366 counts (342 correct of 392 authored pairs)."""

    def test_seed42_notification_reproduces_focus366(self):
        root = q.ROOT / '.build/debug-output/t49-qualify'
        shutil.rmtree(root, ignore_errors=True); queue = root / 'queue'
        copy_jobs(queue, 'focus366-admission', 'b405-061-forward')
        doc = description('t49-notification-42', 'notification', 42)
        batches.register_batch(dict(version='experiment-batch-v1', jobs=[doc]), queue, [doc['id']], approver='test')
        self.assertEqual(q.run(queue, max_jobs=1, lock=root / 'lock', job_ids=[doc['id']]), [(doc['id'], 'complete')])
        out = queue / 'jobs' / doc['id'] / 'attempts/1/out'
        report = q.load(out / 'benchmark_summary.json')
        authored = report['slices']['domain:authored']
        self.assertEqual((authored['correct'], authored['falseChange'], authored['abstentions']), (342, 18, 28))
        self.assertEqual((authored['gained'], authored['lost']), (34, 0))
        recorded = q.QUEUE / 'jobs' / RECORDED['notification'] / 'attempts/1/out/last.pt'
        print('weights equal to FOCUS366:', q.digest(out / 'final.pt') == q.digest(recorded))


if __name__ == '__main__':
    unittest.main()
