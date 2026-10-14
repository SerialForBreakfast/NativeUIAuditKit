"""Register 3-seed control evidence, reusing the approved seed-42 replay."""
import copy
import research_queue as q


def pin(path):
    return dict(path=q.relative(path), sha256=q.digest(path))


def register(owner):
    folder = q.ROOT / 'Research/ResearchSpecs/PROGRAM384-D1'
    folder.mkdir(parents=True, exist_ok=True)
    code = pin(q.ROOT / 'scripts/seed_review384.py')
    specs = []

    def staged(name, value, target):
        path = folder / (name + '-' + target)
        q.require(not path.exists(), 'immutable_config_exists')
        q.save(path, value)
        return dict(**{'from': pin(path)}, to=target)

    def dependency(ident, outputs):
        spec = next((s for s in specs if s['id'] == ident), None)
        if spec is None:
            spec = q.load(q.QUEUE / 'jobs' / ident / 'spec.json')
        return dict(job=ident, specSHA256=q.text_digest(spec), outputs=outputs)

    def base(ident, kind, step):
        return dict(version='research-spec-v2', id=ident, task='PROGRAM384-D1', owner=owner,
            kind='confirm', jobKind=kind, authority='diagnostic',
            hypothesis='Matched control runs reveal decision variation on fixed retained cases.',
            question='Which retained decisions vary when the same training recipe uses seeds 42, 43, and 44?',
            controlledComparison='Keep initialization, membership, original views, 30 epochs, and thresholds fixed. Change only the training seed.',
            decisionRule='Report every seed and role separately. Keep current model gates. Do not treat training cases as independent evaluation.',
            nextActionByOutcome={'varied': 'Inspect variable cases and margins before proposing a retention-rule change.',
                                 'stable': 'Keep the current retention rule for this tested recipe and membership.'},
            inputs=[code], adapter=dict(type='python-callable', steps=['seed_review384.' + step], outputAttributes=['seed_review384.OUT']),
            limits=dict(timeoutSeconds=800, maxOutputBytes=100_000_000, maxAttempts=1))

    bridge = base('program384-d1-control42', 'aggregation', 'retained_control')
    bridge.update(dependencies=[dependency('trust-replay-01-v1', ['last.pt'])], evidence=dict(citations='sources.json'))
    specs.append(bridge)
    source = q.load(q.QUEUE / 'jobs/focus358-control-train/spec.json')
    for seed in (43, 44):
        ident = f'program384-d1-train{seed}'
        spec = base(ident, 'training', 'training')
        spec.update(authority='training', inputs=source['inputs'] + [code],
            stage=source['stage'] + [staged(ident, dict(seed=seed), 'seed.json')], training=copy.deepcopy(source['training']),
            dependencies=[dependency(bridge['id'], ['model.json'])],
            limits=dict(timeoutSeconds=1800, maxOutputBytes=2 << 30, maxAttempts=1))
        spec['training']['experimentLogRunId'] = 'PROGRAM384-D1'
        spec['evidence'] = dict(reads=[p['path'] for p in spec['training']['membership']] + [spec['training']['initialization']['path']],
            weights='last.pt', history='history.json', trainingReport='training-report.json')
        specs.append(spec)
    evaluation = q.load(q.QUEUE / 'jobs/focus346-01-whole-floor/spec.json')
    config = q.load(q.ROOT / evaluation['stage'][0]['from']['path'])
    manifest = q.load(q.ROOT / config['manifest']['path'])
    evaluation_ids = []
    for seed in (42, 43, 44):
        ident = f'program384-d1-evaluate{seed}'
        spec = base(ident, 'evaluation', 'evaluate')
        spec.update(inputs=evaluation['inputs'] + [code],
            stage=[staged(ident, dict(manifest=config['manifest']), 'seed-evaluation.json')],
            dependencies=[dependency(bridge['id'] if seed == 42 else f'program384-d1-train{seed}', ['model.json'])],
            evidence=dict(reads=[config['manifest']['path']], predictions='predictions.json', membershipCount=len(manifest['rows'])))
        specs.append(spec)
        evaluation_ids.append(ident)
    report = base('program384-d1-report', 'aggregation', 'report')
    report.update(dependencies=[dependency(ident, ['predictions.json']) for ident in evaluation_ids], evidence=dict(citations='sources.json'))
    specs.append(report)
    for spec in specs:
        path = folder / (spec['id'] + '.json')
        q.require(not path.exists(), 'immutable_spec_exists')
        q.save(path, spec)
        print(spec['id'], q.submit(path))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', required=True)
    register(parser.parse_args().owner)
