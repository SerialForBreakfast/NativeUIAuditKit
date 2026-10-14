"""Register 8 fixed historical replays. Registration does not grant approval."""
import copy

import research_queue as q
from trust_replay import prediction_rows

SAMPLE = [
    ('focus358-control-train', 'training', None),
    ('focus346-01-whole-floor', 'evaluation', 'diagnostic.json'),
    ('focus347-02-regression-replay', 'evaluation', 'diagnostic.json'),
    ('focus347-01-regression-native', 'evaluation', 'diagnostic.json'),
    ('hcf369-small-dark-spatial', 'aggregation', 'summary.json'),
    ('hcf370-artwork-exchange-spatial', 'aggregation', 'summary.json'),
    ('focus373-repair-decision-v2', 'aggregation', 'decision.json'),
    ('focus358-duration-decision', 'aggregation', 'summary.json'),
]

# Only execution cost changes are excluded. Labels, scores, dates, and margins remain compared.
TIMING_FIELDS = {'seconds', 'encodeSeconds', 'decodeSeconds', 'preprocessingSeconds',
                 'inferenceSeconds', 'totalSeconds'}


def timing_paths(value, prefix=''):
    paths = set()
    if isinstance(value, dict):
        for key, item in value.items():
            path = prefix + '.' + key if prefix else key
            if key in TIMING_FIELDS and isinstance(item, (int, float)):
                paths.add(path)
            else:
                paths.update(timing_paths(item, path))
    elif isinstance(value, list):
        for item in value:
            paths.update(timing_paths(item, prefix + '[]'))
    return paths


def pin(path):
    return dict(path=q.relative(path), sha256=q.digest(path))


def register(owner):
    folder = q.ROOT / 'Research/ResearchSpecs/TRUST-REPLAY'
    folder.mkdir(parents=True, exist_ok=True)
    for number, (original_id, kind, result_name) in enumerate(SAMPLE, 1):
        job = q.QUEUE / 'jobs' / original_id
        original = q.load(job / 'spec.json')
        q.verify_pins(original)
        attempts = [a for a in q.attempts_of(job) if (a / 'result.json').exists()
                    and q.load(a / 'result.json')['status'] == 'complete']
        q.require(attempts, 'replay_original_missing')
        attempt = attempts[0]
        recorded = q.load(attempt / 'result.json')
        # The unsent compression specification uses unsupported field syntax. Preserve it without approval.
        ident = f'trust-replay-{number:02d}-v' + ('2' if number == 4 else '1')
        config_path = folder / (ident + '-config.json')
        config = dict(original=original_id, step=original['adapter']['steps'][0],
                      jobKind=kind, result=result_name)
        q.require(len(original['adapter']['steps']) == 1, 'replay_single_step_required')
        if config_path.exists():
            q.require(q.load(config_path) == config, 'immutable_config_changed')
        else:
            q.save(config_path, config)
        spec = copy.deepcopy(original)
        spec.update(version='research-spec-v2', id=ident, task='TRUST-REPLAY', owner=owner,
            kind='replay', jobKind=kind,
            question='Does the recorded result reproduce from its pinned inputs and resident code?',
            controlledComparison='Replay ' + original_id + ' with the same settings and compare every recorded output.',
            decisionRule='Compare exact scientific values and binary hashes. Exclude only named execution timing fields. Do not promote models.',
            nextActionByOutcome={'matched': 'Review the replay receipt before changing the historical trust label.',
                                 'mismatched': 'Keep the original and replay. Diagnose each changed field before using the claim.'})
        spec['adapter'] = dict(type='python-callable', steps=['trust_replay.run'], outputAttributes=['trust_replay.OUT'])
        spec['inputs'] += [pin(q.ROOT / 'scripts/trust_replay.py')]
        spec['stage'] = original.get('stage', []) + [dict(**{'from': pin(config_path)}, to='replay-config.json')]
        spec['limits'] = dict(timeoutSeconds=1800 if kind == 'training' else 800,
                              maxOutputBytes=2 << 30 if kind == 'training' else 100_000_000, maxAttempts=1)
        files = []
        for item in recorded['outputs']:
            path = attempt / 'out' / item['path']
            q.require(q.digest(path) == item['sha256'], 'replay_original_output_changed')
            compare = 'json' if path.suffix == '.json' else 'sha256'
            entry = dict(name=item['path'], sha256=item['sha256'], compare=compare)
            if compare == 'json':
                entry['ignore'] = [dict(path=p, reason='Measured execution time varies across runs; scientific values remain exact.')
                                   for p in sorted(timing_paths(q.load(path)))]
            files.append(entry)
        spec['replay'] = dict(recordedDirectory=q.relative(attempt / 'out'), files=files)
        if kind == 'training':
            spec['training']['experimentLogRunId'] = 'TRUST-REPLAY'
            spec['evidence'] = dict(reads=[p['path'] for p in spec['training']['membership']] +
                                         [spec['training']['initialization']['path']],
                weights='last.pt', history='epoch-evidence.json', trainingReport='training-evidence.json')
        elif kind == 'evaluation':
            model, = [p for p in original['inputs'] if p['path'].endswith('.pt')]
            spec['evidence'] = dict(model=model['path'], reads=[model['path']],
                predictions='prediction-evidence.json',
                membershipCount=len(prediction_rows(q.load(attempt / 'out' / result_name))))
        else:
            spec['evidence'] = dict(citations='sources.json')
        path = folder / (ident + '.json')
        if path.exists():
            q.require(q.load(path) == spec, 'immutable_spec_changed')
        else:
            q.save(path, spec)
        print(ident, q.submit(path))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', required=True)
    register(parser.parse_args().owner)
