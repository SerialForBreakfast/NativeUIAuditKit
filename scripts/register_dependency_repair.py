"""Register immutable successors. This command does not approve or run jobs."""
import copy
import research_queue as q


def pin(path):
    return dict(path=q.relative(path), sha256=q.digest(path))


def build(owner):
    folder = q.ROOT / 'Research/ResearchSpecs/DEPENDENCY-REPAIR-385'
    folder.mkdir(parents=True, exist_ok=True)
    specs = []

    def load(ident):
        return q.load(q.QUEUE / 'jobs' / ident / 'spec.json')

    def stage(name, value):
        path = folder / (name + '-config.json')
        if path.exists():
            q.require(q.load(path) == value, 'immutable_config_changed')
        else:
            q.save(path, value)
        return dict(**{'from': pin(path)}, to='config.json')

    review = copy.deepcopy(load('program384-d1-control42'))
    review.update(id='trust-replay-01-resource-review-v1', owner=owner,
        question='Do saved model bytes and scientific outputs match when resource measurements are reported separately?',
        controlledComparison='Reuse the original and completed replay. Compare every scientific field exactly. Report peak memory separately.',
        decisionRule='Allow control reuse only when scientific outputs match. Preserve the original failed comparison.',
        adapter=dict(type='python-callable', steps=['replay_resource_review.run'], outputAttributes=['replay_resource_review.OUT']),
        inputs=[pin(q.ROOT / 'scripts/replay_resource_review.py'),
                pin(q.QUEUE / 'jobs/trust-replay-01-v1/spec.json')])
    replay = load('trust-replay-01-v1')
    review['dependencies'][0]['outputs'] = [item['name'] for item in replay['replay']['files']]
    cfg = stage(review['id'], dict(replaySpec=review['inputs'][1]))
    cfg['to'] = 'review-config.json'
    review['stage'] = [cfg]
    review['inputs'] += [pin(q.ROOT / replay['replay']['recordedDirectory'] / item['name']) for item in replay['replay']['files']]
    specs.append(review)
    mapping = {'program384-d1-control42': review['id']}
    for suffix in ('train43', 'train44', 'evaluate42', 'evaluate43', 'evaluate44', 'report'):
        old = 'program384-d1-' + suffix
        spec = copy.deepcopy(load(old))
        spec['id'] = old + '-v2'
        spec['owner'] = owner
        for dep in spec.get('dependencies', []):
            if dep['job'] in mapping:
                dep['job'] = mapping[dep['job']]
                dep['specSHA256'] = q.text_digest(next(s for s in specs if s['id'] == dep['job']))
        mapping[old] = spec['id']
        specs.append(spec)
    train = copy.deepcopy(load('hcf375c-71-detector-train'))
    train.update(id='hcf375d-71-detector-train', task='HCF375D', owner=owner)
    train['limits']['timeoutSeconds'] = 7200
    train['training']['experimentLogRunId'] = 'HCF375D'
    config = q.load(q.ROOT / train['stage'][0]['from']['path'])
    config['datasetFolder'] = 'yolo-training-hcf375d'
    train['stage'] = [stage(train['id'], config)]
    specs.append(train)
    evaluate = copy.deepcopy(load('hcf375c-81-detector-evaluate'))
    evaluate.update(id='hcf375d-81-detector-evaluate', task='HCF375D', owner=owner)
    evaluate['dependencies'][0].update(job=train['id'], specSHA256=q.text_digest(train))
    specs.append(evaluate)
    decision = copy.deepcopy(load('hcf375c-90-decision'))
    decision.update(id='hcf375d-90-decision', task='HCF375D', owner=owner)
    decision['dependencies'][-1].update(job=evaluate['id'], specSHA256=q.text_digest(evaluate))
    specs.append(decision)
    return folder, specs


def register(owner):
    folder, specs = build(owner)
    for spec in specs:
        path = folder / (spec['id'] + '.json')
        if path.exists():
            q.require(q.load(path) == spec, 'immutable_spec_changed')
        else:
            q.save(path, spec)
        print(spec['id'], q.submit(path))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', required=True)
    register(parser.parse_args().owner)
