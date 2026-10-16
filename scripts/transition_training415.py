"""T49: retrain the FOCUS366 transition recipe with 1 fixed seed, then score it with T47.

The recipe is notification366.training: FOCUS329 initialization, 10 epochs, detail and correction layers only,
original-view preservation, and the 252 admitted notification pairs (notification arm) or label-matched
retained examples (control arm). Only the seed changes, the same way seed_review384 changes it for PROGRAM384-D1.
After training, the job scores `final.pt` on a pinned T47 manifest against a pinned prior at 0.15/0.85.
The job never promotes a model or changes a threshold.
"""
import shutil

import research_queue as q
from template_inputs398 import checked

OUT = None
ARMS = ('control', 'notification')
SEEDS = (42, 43, 44)
EPOCHS = 10
RECIPE_CONFIGS = {'control': 'Research/ResearchSpecs/FOCUS366/focus366-control-train-config.json',
                  'notification': 'Research/ResearchSpecs/FOCUS366/focus366-notification-train-config.json'}
# These 2 files changed after FOCUS366 only in the owner text of their register() functions.
# The original copies are in reports/work/PUBLIC-CLEANUP-20261013/originals/scripts. Training code is unchanged.
REPINNED = {'scripts/graph364.py': '37be8fbb22d34f755c7c97028d247af3370da6fb1794288cf717d66c558b2ca1',
            'scripts/visibility364.py': 'f446a1677f0ae86dad276040c8c3678359b740553ea8bf47ff5a93a620a97be7'}


def parameters(value):
    q.require(isinstance(value, dict) and set(value) == {'arm', 'seed'}, 'transition_parameters')
    q.require(value['arm'] in ARMS, 'transition_arm')
    q.require(value['seed'] in SEEDS, 'transition_seed_not_predefined')
    return value['arm'], value['seed']


def configuration(arm, seed, initialization):
    """Build the T49 configuration from the frozen FOCUS366 recipe. Only REPINNED entries get current hashes."""
    recipe = q.load(q.ROOT / RECIPE_CONFIGS[arm])
    q.require(recipe['arm'] == arm and set(recipe) == {'arm', 'inputs'}, 'transition_recipe')
    inputs = []
    for ref in recipe['inputs']:
        if ref['path'] in REPINNED:
            q.require(ref['sha256'] == REPINNED[ref['path']], 'transition_recipe_pin')
            ref = dict(path=ref['path'], sha256=q.digest(q.ROOT / ref['path']))
        inputs.append(ref)
    return dict(arm=arm, seed=seed, epochs=EPOCHS, initialization=initialization, inputs=inputs,
                recipe=dict(path=RECIPE_CONFIGS[arm], sha256=q.digest(q.ROOT / RECIPE_CONFIGS[arm])))


def check_configuration(config, arm, seed):
    q.require(set(config) == {'arm', 'seed', 'epochs', 'initialization', 'inputs', 'recipe'}, 'transition_configuration')
    q.require((config['arm'], config['seed'], config['epochs']) == (arm, seed, EPOCHS), 'transition_configuration_binding')
    checked(config['recipe'])
    expected = configuration(arm, seed, config['initialization'])
    q.require(config['inputs'] == expected['inputs'], 'transition_recipe_changed')


def finish(arm, seed):
    """Write the training evidence that the queue trust check reads: final.pt, history.json, and fit.json epochs."""
    result = q.load(OUT / 'fit.json')
    q.require(result['configuration']['seed'] == seed and result['configuration']['epochs'] == EPOCHS, 'transition_seed_not_applied')
    q.require(len(result['history']) == EPOCHS, 'transition_history_length')
    # The compiler names fit.json as the training report. The trust check requires its `epochs` field.
    q.save(OUT / 'fit.json', dict(result, epochs=EPOCHS), replace=True)
    shutil.copyfile(OUT / 'last.pt', OUT / 'final.pt')
    q.save(OUT / 'history.json', [dict(epoch=i + 1, trainLoss=row['loss']) for i, row in enumerate(result['history'])],
           replace=True)
    q.save(OUT / 'training-report.json', dict(arm=arm, seed=seed, epochs=EPOCHS, modelAccepted=False), replace=True)


def training():
    import appearance348 as m
    import notification366 as n
    import temporal_pairs414 as temporal
    from template_adapters395 import resolve_inputs
    spec = q.load(OUT.parents[2] / 'spec.json')
    cfg = spec['template']
    arm, seed = parameters(cfg['parameters'])
    config = q.load(OUT / 'config.json')
    check_configuration(config, arm, seed)
    refs = resolve_inputs(cfg, OUT)
    q.require(refs['initialization']['path'] == 'reports/work/FOCUS-329/run/last.pt', 'transition_initialization')
    trainer = m.a.b.trainer
    previous = trainer.fit

    def fit(net, x, y, settings, progress, **kwargs):
        # notification366 fixes seed 42 and 10 epochs. Change only the seed.
        q.require(settings['seed'] == 42 and settings['epochs'] == EPOCHS, 'transition_recipe_settings')
        settings.update(seed=seed)
        return previous(net, x, y, settings, progress, **kwargs)

    trainer.fit = fit
    n.OUT = OUT
    try:
        n.training()  # Reads config.json (arm, inputs) and the admission dependency. Writes last.pt and fit.json.
    finally:
        trainer.fit = previous
    finish(arm, seed)
    temporal.OUT = OUT
    temporal.score_model(dict(path=q.relative(OUT / 'final.pt'), sha256=q.digest(OUT / 'final.pt')),
                         refs['pairs'], refs['prior'])
    report = q.load(OUT / 'benchmark_summary.json')
    report.update(arm=arm, seed=seed, epochs=EPOCHS, training=dict(fit='fit.json', history='history.json'))
    q.save(OUT / 'benchmark_summary.json', report, replace=True)


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arm', choices=ARMS)
    parser.add_argument('seed', type=int, choices=SEEDS)
    args = parser.parse_args()
    folder = q.ROOT / 'Research/ResearchSpecs/T49'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f'{args.arm}-{args.seed}-config.json'
    value = configuration(args.arm, args.seed, dict(path='reports/work/FOCUS-329/run/last.pt',
                          sha256=q.digest(q.ROOT / 'reports/work/FOCUS-329/run/last.pt')))
    if path.exists():
        q.require(q.load(path) == value, 'configuration_changed')
    else:
        q.save(path, value)
    print(q.relative(path), q.digest(path), json.dumps(dict(arm=args.arm, seed=args.seed)))
