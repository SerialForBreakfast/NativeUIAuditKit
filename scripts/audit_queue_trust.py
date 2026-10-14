"""Classify every queue job by the evidence it actually recorded (RCA-20261013-01).

Classes, from strongest to weakest:
- replay-verified: an independent replay reproduced the recorded outputs (from the annotations file).
- compute-evidence: the job pinned real data or model files that still match, imported a numeric package,
  and wrote non-trivial outputs. This is consistent with real work; it is not proof of correct work.
- aggregation-evidence: the job consumed producer outputs whose hashes still match.
- analytic: closed-form arithmetic. Valid, but not an experiment.
- invalid-withdrawn: a withdrawn specification that later ran (from the annotations file).
- unverified: no recorded evidence of real inputs.
- fabricated: quarantined under FABRICATED-*.
- superseded-unreceipted: moved to quarantine by the old groomer without a receipt.
Explicit labels come only from the reviewed annotations file, never from guesses.
"""
import argparse
import time

import research_queue as q
import research_trust as t

ANNOTATIONS = q.QUEUE / 'annotations.json'
LABELS = {'replay-verified', 'analytic', 'invalid-withdrawn', 'unverified'}
DATA_SUFFIXES = ('.png', '.jpg', '.npz', '.npy', '.pt', '.mlmodelc', '.mlpackage', '.json', '.jsonl', '.csv', '.bin')


def load_annotations(path=ANNOTATIONS):
    if not path.exists():
        return {}
    doc = q.load(path)
    q.require(doc.get('version') == 'queue-annotations-v1', 'annotations_version')
    for ident, item in doc['jobs'].items():
        q.require(item.get('class') in LABELS and str(item.get('reason', '')).strip(), 'annotation_fields:' + ident)
        if item['class'] == 'replay-verified':
            verify_replay(ident, item.get('replay'))
    return doc['jobs']


def verify_replay(ident, reference):
    """Require a hash-pinned replay report. Prose cannot grant verification."""
    q.require(isinstance(reference, dict), 'replay_receipt_required')
    path = q.local_path(q.ROOT, q.check_pin(reference)['path'])
    q.require(path.is_file() and q.digest(path) == reference['sha256'], 'replay_receipt_changed')
    doc = q.load(path)
    q.require(doc.get('version') == 'queue-replay-sample-v1', 'replay_receipt_version')
    rows = [row for row in doc.get('jobs', []) if row.get('job') == ident]
    q.require(len(rows) == 1 and rows[0].get('status') == 'complete'
              and rows[0].get('comparison', {}).get('matched') is True
              and rows[0]['comparison'].get('files'), 'replay_not_matched')


def pins_of(spec):
    pins = list(spec.get('inputs', [])) + [s['from'] for s in spec.get('stage', [])]
    if 'training' in spec:
        pins += spec['training']['membership'] + [spec['training']['initialization']]
    return pins


def classify(job, annotations, queue=q.QUEUE):
    spec = q.load(job / 'spec.json')
    state, attempts = q.state(job, display_cache=True)
    result = q.load(attempts[-1] / 'result.json') if attempts and (attempts[-1] / 'result.json').exists() else {}
    row = dict(job=job.name, task=spec['task'], state=state, wallSeconds=result.get('wallSeconds'),
               outputBytes=sum(o['bytes'] for o in result.get('outputs', [])), reasons=[])
    if job.name in annotations:
        row.update(trust=annotations[job.name]['class'], reasons=[annotations[job.name]['reason']])
        row['drifted'] = t.drift(job) if state in ('complete', 'drifted') else []
        return row
    if state == 'drifted':
        row.update(trust='drifted', reasons=['Current code differs from recorded code.'], drifted=t.drift(job))
        return row
    if state != 'complete':
        row.update(trust='not-complete', reasons=[state])
        return row
    data_pins = [p for p in pins_of(spec) if not p['path'].endswith('.py') and p['path'].endswith(DATA_SUFFIXES)]
    intact = [p for p in data_pins if (q.ROOT / p['path']).is_file() and q.digest(q.ROOT / p['path']) == p['sha256']]
    packages = (q.load(attempts[-1] / 'closure.json').get('packages', {})
                if (attempts[-1] / 'closure.json').exists() else {})
    numeric = any(packages.get(name) for name in ('numpy', 'torch', 'PIL'))
    dependencies_ok = False
    if spec.get('dependencies'):
        try:
            q.dependency_inputs(spec, queue, display_cache=True)
            dependencies_ok = True
        except (ValueError, OSError, KeyError, TypeError) as error:
            row['reasons'].append('dependency_unverifiable:' + str(error)[:120])
    media = [p for p in intact if not p['path'].endswith(('.json', '.jsonl', '.csv'))]
    outputs = result.get('outputs', [])
    if spec['authority'] == 'capture' or (job.name.endswith(('-capture', '-recover')) and
                                          any(o['path'].lower().endswith('.png') for o in outputs)):
        if any(o['path'].lower().endswith('.png') for o in outputs) or row['outputBytes'] > 100_000:
            row['trust'] = 'compute-evidence'
            row['reasons'].append('capture with image outputs')
        else:
            row['trust'] = 'unverified'
            row['reasons'].append('capture without image outputs')
    elif dependencies_ok and spec['authority'] != 'training':
        row['trust'] = 'aggregation-evidence'
        row['reasons'].append(f"{len(spec['dependencies'])} producer outputs intact")
    elif spec['authority'] == 'training' and packages.get('torch') and intact:
        row['trust'] = 'compute-evidence'
        row['reasons'].append('training with intact membership and torch')
    elif media or (intact and numeric and row['outputBytes'] > 1000):
        row['trust'] = 'compute-evidence'
        row['reasons'].append(f'{len(intact)} data pins intact ({len(media)} image or model pins); '
                              f'packages {sorted(k for k, v in packages.items() if v)}')
    elif intact and len(intact) == len(data_pins):
        row['trust'] = 'aggregation-evidence'
        row['reasons'].append(f'{len(intact)} pinned reports intact')
    else:
        row['trust'] = 'unverified'
        row['reasons'].append(f'{len(intact)}/{len(data_pins)} data pins intact; numeric={numeric}; '
                              f"outputBytes={row['outputBytes']}")
    row['drifted'] = t.drift(job)
    return row


def ledger(queue=q.QUEUE, annotations_path=ANNOTATIONS):
    annotations = load_annotations(annotations_path)
    rows = [classify(job, annotations, queue) for job in sorted((queue / 'jobs').iterdir())
            if job.is_dir() and (job / 'spec.json').exists()]
    quarantine = queue / 'quarantine'
    for folder in sorted(quarantine.iterdir()) if quarantine.exists() else []:
        if folder.name.startswith('FABRICATED-'):
            for spec in sorted(folder.rglob('jobs/*/spec.json')):
                rows.append(dict(job=spec.parent.name, task=q.load(spec)['task'], state='quarantined',
                                 trust='fabricated', reasons=[folder.name], drifted=[]))
        elif (folder / 'spec.json').exists():
            rows.append(dict(job=folder.name, task=q.load(folder / 'spec.json')['task'], state='quarantined',
                             trust='superseded-unreceipted', reasons=['moved by the old groomer without a receipt'],
                             drifted=[]))
        else:
            receipts = sorted(folder.glob('receipt-*.json'))
            references = {}
            for receipt_path in receipts:
                receipt = q.load(receipt_path)
                if receipt.get('version') != 'queue-quarantine-v1':
                    continue
                for item in receipt.get('items', []):
                    for file in item.get('files', []):
                        references[file['path']] = file
            for spec_path in sorted(folder.rglob('jobs/*/spec.json')):
                reference = references.get(str(spec_path.relative_to(folder)))
                verified = bool(reference and q.digest(spec_path) == reference['sha256'])
                rows.append(dict(job=spec_path.parent.name, task=q.load(spec_path)['task'], state='quarantined',
                    trust='superseded-receipted' if verified else 'superseded-unreceipted',
                    reasons=['Preserved specification matches its quarantine receipt.' if verified else 'No matching specification receipt.'],
                    drifted=[]))
    counts = {}
    for row in rows:
        counts[row['trust']] = counts.get(row['trust'], 0) + 1
    original = queue / 'quarantine/APPROVALS-REVOKED-20261013/reports/work/research-queue/approved-additions.json'
    reconciliation = None
    if original.is_file():
        approved = q.load(original)['jobs']
        by_id = {row['job']: row for row in rows}
        original_counts = {}
        for ident in approved:
            label = by_id.get(ident, {}).get('trust', 'missing')
            original_counts[label] = original_counts.get(label, 0) + 1
        reconciliation = dict(source=dict(path=q.relative(original), sha256=q.digest(original)),
            originalCount=len(approved), classes=original_counts,
            missing=sorted(set(approved) - set(by_id)),
            note='This accounts for the revoked approval population, not the later queue population.')
    return dict(version='queue-trust-ledger-v1', generatedAt=time.time(), counts=counts,
                drifted=sum(1 for r in rows if r.get('drifted')), jobs=rows,
                originalApprovals=reconciliation,
                limitation='Evidence classes describe recorded inputs and outputs. Only replay-verified rows were reproduced.')


def annotate(ident, label, reason, path=ANNOTATIONS, replay=None):
    q.require(isinstance(ident, str) and q.ID.fullmatch(ident), 'job_id')
    q.require(label in LABELS, 'annotation_label')
    q.require(isinstance(reason, str) and len(reason.strip()) >= 12, 'annotation_reason')
    q.require((q.QUEUE / 'jobs' / ident / 'spec.json').exists(), 'unknown_job')
    if label == 'replay-verified':
        verify_replay(ident, replay)
    with q.host_lock(q.QUEUE / 'approval.lock'):
        doc = q.load(path) if path.exists() else dict(version='queue-annotations-v1', jobs={}, events=[])
        doc['jobs'][ident] = dict(**{'class': label}, reason=reason.strip(), annotatedAt=time.time())
        if replay is not None:
            doc['jobs'][ident]['replay'] = replay
        doc['events'].append(dict(job=ident, **{'class': label}, reason=reason.strip(), at=time.time()))
        q.save(path, doc, replace=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    out = sub.add_parser('ledger')
    out.add_argument('--output', required=True, help='Repository-relative output path for the ledger.')
    mark = sub.add_parser('annotate')
    mark.add_argument('job')
    mark.add_argument('label', choices=sorted(LABELS))
    mark.add_argument('--reason', required=True)
    mark.add_argument('--replay-report', help='Repository-relative verified replay receipt.')
    args = parser.parse_args()
    if args.command == 'annotate':
        replay = None
        if args.replay_report:
            path = q.local_path(q.ROOT, args.replay_report)
            replay = dict(path=args.replay_report, sha256=q.digest(path))
        annotate(args.job, args.label, args.reason, replay=replay)
        print('annotated', args.job, args.label)
        return
    value = ledger()
    target = q.local_path(q.ROOT, args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    q.save(target, value, replace=True)
    print(value['counts'], 'drifted', value['drifted'])


if __name__ == '__main__':
    main()
