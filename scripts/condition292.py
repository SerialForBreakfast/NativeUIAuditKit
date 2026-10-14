"""Separate positive additions from identity negatives with 2 fixed runs."""
import argparse
from pathlib import Path
import numpy as np
import condition291 as prior
import report291

base = prior.base
OUT = base.ROOT / 'reports/work/TRANSITION-292'
OLD = prior.OUT


def mix(old, new, labels, use_new_positive):
    base.require(old.shape == new.shape and len(labels) == len(old), 'mix_shape')
    base.require(np.isin(labels, [0, 1]).all(), 'mix_labels')
    mask = labels == (1 if use_new_positive else 0)
    result = old.copy()
    result[mask] = new[mask]
    base.require(np.array_equal(result[~mask], old[~mask]), 'unchanged_class')
    return result


def report(membership):
    paths = {name: OLD / name for name in ('DTM083', 'DTM084')}
    paths.update({name: OUT / name for name in ('DTM085', 'DTM086')})
    evaluations = {name: base.read(path / 'evaluation.json') for name, path in paths.items()}
    contrasts = {}
    for label, before, after in [
        ('positive_with_old_negatives', 'DTM083', 'DTM085'),
        ('positive_with_identity_negatives', 'DTM086', 'DTM084'),
        ('negative_with_old_positives', 'DTM083', 'DTM086'),
        ('negative_with_new_positives', 'DTM085', 'DTM084'),
    ]:
        conditions, cases = report291.summarize_comparison(evaluations[before], evaluations[after], membership)
        contrasts[label] = dict(before=before, after=after, conditions=conditions, cases=cases)
    interactions = {}
    for condition in evaluations['DTM083']['conditions']:
        counts = {name: record['conditions'][condition]['summary']['correct']
                  for name, record in evaluations.items()}
        interactions[condition] = dict(correct=counts,
            positiveEffectOldNegatives=counts['DTM085']-counts['DTM083'],
            positiveEffectIdentityNegatives=counts['DTM084']-counts['DTM086'],
            interaction=counts['DTM084']-counts['DTM086']-counts['DTM085']+counts['DTM083'])
    base.write(OUT / 'comparison.json', dict(version='condition292-v1', contrasts=contrasts,
        interactions=interactions,
        trainingFit=report291.added_condition_results(base.read(OLD / 'registration.json'),
            {name: base.read(path / 'result.json') for name, path in paths.items()}),
        inputs={name: base.ref(path / 'evaluation.json') for name, path in paths.items()},
        strengths={name: record['strengths'] for name, record in evaluations.items()},
        productionEligible=False, independentEvaluation=False,
        limitations=['One seed; no repeatability claim.', 'Repeatedly inspected development checks are not a final audit.']))
    return interactions


def run():
    base.require(not OUT.exists(), 'output_collision')
    base.torch.set_num_threads(2)
    manifest, membership, full, labels, weights, extra, controls, initializer, registration = prior.prepare()
    old_registration = base.read(OLD / 'registration.json')
    base.require(registration == old_registration, 'retained_registration_changed')
    for name in ('DTM083', 'DTM084'):
        base.require(base.read(OLD / name / 'result.json')['checkpointParity'], 'retained_parity')
        base.checked(base.read(OLD / name / 'result.json')['model'])
        base.require((OLD / name / 'completion.json').exists(), 'retained_incomplete')
    added_labels = labels[1660:1740]
    plans = {'DTM085': mix(full[controls], extra, added_labels, True),
             'DTM086': mix(full[controls], extra, added_labels, False)}
    schedules = {}
    for name, added in plans.items():
        values = np.concatenate((full, added, base.reporting.reverse(added)))
        base.require(np.array_equal(values[:1660], full), 'prefix_changed')
        base.require(np.array_equal(labels[1660:1740], labels[1740:]), 'reverse_labels')
        schedules[name] = dict(trainingSHA256=base.sha(values.tobytes()),
            addedSHA256=base.sha(added.tobytes()), newPositive=name=='DTM085', newNegative=name=='DTM086')
        del values
    OUT.mkdir()
    base.write(OUT / 'registration.json', dict(registration, schedules=schedules,
        parent=base.ref(OLD / 'registration.json'), factorialRunner=base.ref(Path(__file__)),
        hypothesis='Separate positive coverage from the effect of replacing harder negative examples with identical frames.',
        retained={name: base.ref(OLD / name / 'result.json') for name in ('DTM083','DTM084')}))
    references = {'DTM067': base.load_model(initializer)}
    for name, folder in [('DTM078', 'CONFLICT-281'), ('DTM081', 'TRANSITION-287'), ('DTM083','TRANSITION-291')]:
        checkpoint = base.checked(base.read(base.ROOT / f'reports/work/{folder}/{name}/result.json')['model'])
        references[name] = base.load_model(checkpoint) if name=='DTM078' else prior.model.load_candidate(checkpoint)
    prior.OUT = OUT
    print('Registered DTM085 and DTM086. Reuse DTM083 and DTM084 without training.', flush=True)
    for name, added in plans.items():
        prior.train_one(name, full, added, labels, weights, initializer, registration, references, manifest, extra)
        base.require(base.read(OUT/name/'registration.json')['trainingSHA256']==schedules[name]['trainingSHA256'], 'schedule_identity')
    interactions = report(membership)
    size = sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    base.require(size < 256*1024**2, 'output_budget')
    base.write(OUT/'completion.json', dict(outputBytes=size, trained=['DTM085','DTM086'],
        reused=['DTM083','DTM084'], productionEligible=False,
        regressionPassed={name:base.read(OUT/name/'evaluation.json')['regressionPassed'] for name in plans}))
    print(interactions, flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', required=True)
    parser.parse_args()
    run()
