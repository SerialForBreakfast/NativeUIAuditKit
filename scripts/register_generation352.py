"""Freeze a small producer and its dependent comparisons without simulator mutations."""
import copy
import dataset351
import research_queue as q
from research_campaign340 import pin


def main():
    folder = q.ROOT / 'Research/ResearchSpecs/GENERATION352'
    folder.mkdir(exist_ok=True)
    q.require(not (q.QUEUE / 'jobs/generation352-00-capture').exists(), 'already_registered')
    plan = dataset351.run(None)
    plan['cases'] = [c for c in plan['cases'] if c['id'] in ('corners-native', 'corners-combined')]
    for case in plan['cases']:
        case['id'] += '-160'
        for definition in case['recipe']['appearance']['composition']['definitions'].values():
            definition['width'] = definition['height'] = 160
    plan['expectedFrames'] = 10
    plan['group'] = 'fixture351-related-scenes'
    plan_path = folder / 'plan.json'
    q.save(plan_path, plan)
    inputs = [pin(q.ROOT / 'scripts' / name) for name in (
        'generation352.py', 'dataset351.py', 'compare351.py', 'native343.py', 'direct_tvos_capture.py')]
    producer = dict(version=q.SPEC_VERSION, id='generation352-00-capture', task='GENERATION352',
        owner='research-host-NUIAK', kind='screen', authority='capture',
        hypothesis='Larger controls test whether the prior movement misses depend on control size.',
        decisionRule='Require 10 frames, 6 observed endpoint pairs, verified hashes, and successful scene restoration.',
        capture=dict(target=plan['binding']['simulatorUDID'], endpoint=plan['binding']['endpoint'],
            plan=pin(plan_path), approval='User approves scripted queue generation with the existing Simulator and Fixture.'),
        inputs=inputs, adapter=dict(type='python-callable', steps=['generation352.run'], outputAttributes=['generation352.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1))
    path = folder / (producer['id'] + '.json')
    q.save(path, producer)
    print(producer['id'], q.submit(path))
    models = q.load(q.ROOT / 'Research/ResearchSpecs/DATASET351/dataset351-00-movement-config.json')['models']
    for index, mode in enumerate(('movement', 'content', 'recapture', 'timing'), 1):
        spec = copy.deepcopy(producer)
        spec.pop('capture')
        spec.update(id=f'generation352-{index:02d}-{mode}', authority='diagnostic',
            hypothesis='Compare '+mode+' with retained models and unchanged preprocessing.',
            decisionRule='Report counts and exclusions. Do not change weights or thresholds.',
            dependencies=[dict(job=producer['id'], specSHA256=q.text_digest(producer), outputs=['capture/capture.json'])],
            adapter=dict(type='python-callable', steps=['generation352.compare'], outputAttributes=['generation352.OUT']))
        config = folder / (spec['id'] + '-config.json')
        q.save(config, dict(mode=mode, models=models))
        spec['inputs'] += list(models.values())
        spec['stage'] = [dict(to='comparison.json', **{'from': pin(config)})]
        path = folder / (spec['id'] + '.json')
        q.save(path, spec)
        print(spec['id'], q.submit(path))


if __name__ == '__main__':
    main()
