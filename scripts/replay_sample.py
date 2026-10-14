"""Replay completed queue jobs in an isolated queue and compare outputs with the recorded run (RCA-20261013-01).

The live queue is read only. Each replay copies the job specification and its dependency outputs into
`.build/replay-<id>/`, runs the job there, and compares every recorded output.
Timing and memory fields are the only ignored fields. Paths that point into the attempt folder are mapped.
"""
import argparse
import json
import shutil
import sys
import time
import uuid

import research_approval as approval
import research_queue as q

TIMING_KEYS = {'seconds', 'wallSeconds', 'peakBytes', 'timestamp', 'generatedAt', 'createdAt', 'updatedAt',
               'startedAt', 'finishedAt', 'elapsedSeconds', 'durationSeconds', 'runtimeSeconds'}
COPY_LIMIT = 2 << 30


def complete_attempt(job):
    for attempt in q.attempts_of(job):
        path = attempt / 'result.json'
        if path.exists() and q.load(path).get('status') == 'complete':
            return attempt, q.load(path)
    raise ValueError('no_complete_attempt:' + job.name)


def copy_job(source_job, target_queue, with_outputs):
    target = target_queue / 'jobs' / source_job.name
    target.mkdir(parents=True)
    shutil.copyfile(source_job / 'spec.json', target / 'spec.json')
    if not with_outputs:
        return 0
    attempt, result = complete_attempt(source_job)
    out = target / 'attempts' / attempt.name
    (out / 'out').mkdir(parents=True)
    shutil.copyfile(attempt / 'result.json', out / 'result.json')
    copied = 0
    for item in result['outputs']:
        destination = out / 'out' / item['path']
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(attempt / 'out' / item['path'], destination)
        copied += item['bytes']
    return copied


def strip(value):
    if isinstance(value, dict):
        return {k: strip(v) for k, v in value.items() if k not in TIMING_KEYS}
    if isinstance(value, list):
        return [strip(v) for v in value]
    return value


def compare(recorded_attempt, recorded, replay_attempt, replayed):
    old_prefix = q.relative(replay_attempt / 'out') + '/'
    new_prefix = q.relative(recorded_attempt / 'out') + '/'
    produced = {o['path']: o for o in replayed.get('outputs', [])}
    files = []
    for item in recorded['outputs']:
        name = item['path']
        if name not in produced:
            files.append(dict(name=name, matched=False, reason='missing_output'))
            continue
        same = produced[name]['sha256'] == item['sha256']
        row = dict(name=name, bytesIdentical=same, matched=same)
        if not same and name.endswith('.json') and item['bytes'] <= 50_000_000:
            a = strip(q.load(recorded_attempt / 'out' / name))
            b = strip(q.map_paths(q.load(replay_attempt / 'out' / name), old_prefix, new_prefix))
            diff = q.differences(a, b)
            row.update(matched=diff['count'] == 0, differenceCount=diff['count'],
                       differencePaths=diff['paths'], maxNumericDiff=diff['maxNumericDiff'])
        files.append(row)
    extra = sorted(set(produced) - {o['path'] for o in recorded['outputs']})
    return dict(matched=all(f['matched'] for f in files) and not extra, files=files, extraOutputs=extra)


def head_digest(path):
    import hashlib
    import subprocess
    done = subprocess.run(['git', 'show', 'HEAD:' + path], cwd=q.ROOT, capture_output=True)
    return hashlib.sha256(done.stdout).hexdigest() if done.returncode == 0 else None


def changed_pins(spec):
    pins = list(spec.get('inputs', [])) + [s['from'] for s in spec.get('stage', [])]
    if 'training' in spec:
        pins += spec['training']['membership'] + [spec['training']['initialization']]
    rows = []
    for pin in pins:
        path = q.ROOT / pin['path']
        if not path.is_file() or q.digest(path) != pin['sha256']:
            rows.append(dict(path=pin['path'], pinnedVersionAtHEAD=head_digest(pin['path']) == pin['sha256']))
    return rows


def replay(ident, queue=q.QUEUE, modules=q.MODULES, keep=False):
    source = queue / 'jobs' / ident
    spec = q.load(source / 'spec.json')
    recorded_attempt, recorded = complete_attempt(source)
    changed = changed_pins(spec)
    if changed:
        # The current working tree no longer holds the code or data this job used. Do not replay it here.
        return dict(job=ident, task=spec['task'], status='not-replayed', reason='pinned_inputs_changed',
                    changedPins=changed, replaySeconds=0.0)
    base = q.ROOT / '.build' / f'replay-{ident}-{uuid.uuid4().hex[:8]}'
    replay_queue = base / 'queue'
    try:
        copied = copy_job(source, replay_queue, with_outputs=False)
        for dep in spec.get('dependencies', []):
            copied += copy_job(queue / 'jobs' / dep['job'], replay_queue, with_outputs=True)
            q.require(copied <= COPY_LIMIT, 'replay_copy_limit')
        approval.approve(replay_queue, ident, 'test', 'isolated replay of a recorded job', modules)
        started = time.time()
        report = q.run(replay_queue, modules, 1, sys.executable, base / 'lock', job_ids=[ident])
        attempt = replay_queue / 'jobs' / ident / 'attempts/1'
        replayed = q.load(attempt / 'result.json') if (attempt / 'result.json').exists() else {}
        value = dict(job=ident, task=spec['task'], runReport=report, status=replayed.get('status'),
                     reason=replayed.get('reason'), recordedSeconds=recorded.get('wallSeconds'),
                     replaySeconds=time.time() - started, copiedDependencyBytes=copied)
        if replayed.get('status') == 'complete':
            value['comparison'] = compare(recorded_attempt, recorded, attempt, replayed)
        else:
            value['stderrTail'] = (attempt / 'stderr.log').read_text()[-2000:] if (attempt / 'stderr.log').exists() else None
        return value
    finally:
        if not keep:
            shutil.rmtree(base, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jobs', nargs='+')
    parser.add_argument('--output', required=True, help='Repository-relative path for the replay report.')
    args = parser.parse_args()
    rows = []
    for ident in args.jobs:
        try:
            row = replay(ident)
        except (ValueError, OSError, KeyError) as error:
            row = dict(job=ident, status='replay-error', reason=str(error)[:300], replaySeconds=0.0)
        rows.append(row)
        print(ident, row['status'], row.get('comparison', {}).get('matched'), round(row['replaySeconds'], 1), flush=True)
    target = q.local_path(q.ROOT, args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    q.save(target, dict(version='queue-replay-sample-v1', generatedAt=time.time(), jobs=rows), replace=True)


if __name__ == '__main__':
    main()
