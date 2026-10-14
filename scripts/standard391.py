"""Verify completed Standard reviews and prepare an isolated suite comparison."""
import argparse
from collections import Counter
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time

import research_queue as q
import evaluation_suite391 as suite

JOBS = ['standard390-' + suffix for suffix in (
    '01-retained-appearance', '02-native-transfer', '03-context-regression',
    '04-identical-neighbors', '05-data-priorities')]


def pin(path):
    return dict(path=q.relative(path), sha256=q.digest(path))


def completed(job, name):
    folder = q.QUEUE / 'jobs' / job
    spec = q.load(folder / 'spec.json')
    for attempt in q.attempts_of(folder):
        result = attempt / 'result.json'
        if not result.exists():
            continue
        doc = q.load(result)
        if doc['status'] != 'complete':
            continue
        q.require(doc['specSHA256'] == q.text_digest(spec), 'result_spec_changed')
        q.require(q.outputs_intact(attempt, doc), 'result_outputs_changed')
        path = attempt / 'out' / name
        q.require(name in {r['path'] for r in doc['outputs']}, 'missing_output')
        return attempt, q.load(path), [pin(folder / 'spec.json'), pin(result), pin(path)]
    raise ValueError('completed_input_missing:' + job)


def prepare(output):
    q.require(not output.exists(), 'output_collision')
    refs, slices, cases, summaries, producer_refs = [], [], [], [], []
    for job in JOBS[:4]:
        attempt, review, pins = completed(job, 'review.json')
        refs.extend(pins)
        deps = q.load(attempt / 'out/dependencies.json')
        by_job = {d['job']: d for d in deps}
        for dep in deps:
            q.require(q.digest(q.ROOT / dep['result']['path']) == dep['result']['sha256'], 'producer_receipt_changed')
            producer_refs.append(dep['result'])
            result = q.load(q.ROOT / dep['result']['path'])
            q.require(result['status'] == 'complete' and result['specSHA256'] == dep['specSHA256'], 'producer_status')
            spec_path = q.QUEUE / 'jobs' / dep['job'] / 'spec.json'
            q.require(q.text_digest(q.load(spec_path)) == dep['specSHA256'], 'producer_spec_changed')
            producer_refs.append(pin(spec_path))
            for ref in dep['outputs']:
                q.require(q.digest(q.ROOT / ref['path']) == ref['sha256'], 'producer_output_changed')
        for index, comp in enumerate(review['comparisons']):
            ident = job.removeprefix('standard390-') + '-' + str(index)
            control = by_job[comp['controlJob']]['outputs'][0]
            candidate = by_job[comp['candidateJob']]['outputs'][0]
            slices.append(dict(id=ident, control=control, candidate=candidate, expected=pins[-1],
                controlJob=comp['controlJob'], candidateJob=comp['candidateJob'], cases=len(comp['cases'])))
            # Preserve model identity independently of saved scores.
            for model_group in comp['models'].values():
                for ref in model_group.values():
                    q.require(q.digest(q.local_path(q.ROOT, ref['path'])) == ref['sha256'], 'model_changed')
                    producer_refs.append(ref)
            for row in comp['cases']:
                cases.append(dict(comparison=ident, inputHashes=dict(control=control['sha256'], candidate=candidate['sha256']),
                    osFocusStyle='not_verified_by_comparison', **row))
            summaries.extend(dict(comparison=ident, **r) for r in comp['slices'])
    _, prep, prep_refs = completed(JOBS[4], 'preparation.json')
    refs.extend(prep_refs)
    for ref in prep['externalEvidence']:
        q.require(q.digest(q.local_path(q.ROOT, ref['path'])) == ref['sha256'], 'detector_evidence_changed')
    refs.extend(prep['externalEvidence'])
    unique = {r['path']: r for r in refs + producer_refs}
    manifest = dict(version=suite.VERSION, slices=slices, evidence=list(unique.values()) +
        [pin(q.ROOT / 'scripts' / name) for name in ('standard390.py', 'evaluation_suite391.py')])
    suite.validate(manifest)
    losses = [c for c in cases if c['candidateLoss']]
    q.require(len(losses) == len(prep['retainedLosses']), 'retained_loss_count_changed')
    report = dict(version='standard391-inventory-v1', cases=cases, slices=summaries,
        detector=prep['detector'], losses=losses, modelAccepted=False, sources=list(unique.values()),
        limits=['Repeated and reversed views are not independent trials.',
                'Historical OS profile and full taxonomy compatibility remain unverified.',
                'This report does not admit examples for training.'],
        selection=[
            dict(priority=1, task='S391-03', reason='Measure missed proposals and complete focus selection before changing crop weights.'),
            dict(priority=2, task='S391-04', reason='Use matched movement and content-only scenes for weak native movement and strong distraction errors.'),
            dict(priority=3, task='S391-05', reason='Preserve the 6 recorded losses; review matched seeds before another correction.')])
    output.mkdir(parents=True)
    q.save(output / 'manifest.json', manifest)
    q.save(output / 'inventory.json', report)
    return report


def benchmark(output, rounds):
    q.require(1 <= rounds <= 3, 'benchmark_rounds')
    manifest_path = output / 'manifest.json'
    manifest = q.load(manifest_path)
    rows = []
    for trial in range(rounds):
        # Alternate order to reduce a consistent warm-cache advantage.
        for mode in (('separate', 'shared') if trial % 2 == 0 else ('shared', 'separate')):
            tick = time.monotonic()
            targets = [s['id'] for s in manifest['slices']] if mode == 'separate' else [None]
            records = []
            for index, ident in enumerate(targets):
                folder = output / f'{mode}-{trial}-{index}'
                command = [sys.executable, str(q.ROOT / 'scripts/evaluation_suite391.py'), str(manifest_path), str(folder)]
                if ident:
                    command.extend(['--slice', ident])
                process = subprocess.run(command, capture_output=True, text=True, timeout=800, check=True)
                records.append(json.loads(process.stdout))
            rows.append(dict(mode=mode, trial=trial, seconds=time.monotonic()-tick,
                jsonReads=sum(r['jsonReads'] for r in records), cacheHits=sum(r['cacheHits'] for r in records),
                loadSeconds=sum(r['loadSeconds'] for r in records), compareSeconds=sum(r['compareSeconds'] for r in records),
                peakWorkerResidentBytes=max(r['peakResidentBytes'] for r in records),
                parity=all(r['parity'] == 'exact' for r in records)))
    medians = {mode: statistics.median(r['seconds'] for r in rows if r['mode'] == mode) for mode in ('separate', 'shared')}
    result = dict(version='standard391-benchmark-v1', runs=rows, medianSeconds=medians,
        ratio=medians['separate']/medians['shared'], inferenceExecuted=False, modelAccepted=False,
        limitation='Cached JSON comparisons only. This does not measure image decoding or model inference. Filesystem cache is not cleared.')
    q.save(output / 'benchmark.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'benchmark'])
    parser.add_argument('output')
    parser.add_argument('--rounds', type=int, default=3)
    args = parser.parse_args()
    output = q.local_path(q.ROOT, args.output)
    result = prepare(output) if args.action == 'prepare' else benchmark(output, args.rounds)
    print({k: v for k, v in result.items() if k in ('version', 'medianSeconds', 'ratio')})


if __name__ == '__main__':
    main()
