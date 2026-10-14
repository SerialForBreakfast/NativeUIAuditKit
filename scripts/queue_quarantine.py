"""Move named queue items into an incident quarantine with a hash receipt (RCA-20261013-01).

Quarantine preserves evidence. It never deletes and never overwrites.
Usage: queue_quarantine.py INCIDENT --reason TEXT PATH [PATH ...]
Each PATH is relative to the repository root and must be inside the queue or Research/ResearchSpecs.
"""
import argparse
import os
from pathlib import Path
import time

import research_queue as q

ALLOWED = ('reports/work/research-queue/', 'Research/ResearchSpecs/')


def inventory(path, root):
    files = [path] if path.is_file() else sorted(p for p in path.rglob('*') if p.is_file())
    return [dict(path=str(f.relative_to(root)), bytes=f.stat().st_size, sha256=q.digest(f)) for f in files]


def quarantine(incident, reason, paths, root=q.ROOT, queue=q.QUEUE):
    q.require(isinstance(incident, str) and q.ID.fullmatch(incident), 'incident_id')
    q.require(isinstance(reason, str) and reason.strip(), 'reason_missing')
    q.require(paths, 'paths_missing')
    target_root = queue / 'quarantine' / incident
    moves = []
    for rel in paths:
        source = q.local_path(root, rel)
        q.require(any(rel.startswith(prefix) for prefix in ALLOWED), 'path_not_allowed')
        q.require(source.exists(), 'path_missing:' + rel)
        q.require(target_root not in [source, *source.parents], 'already_quarantined')
        q.require(source not in target_root.parents, 'quarantine_ancestor')
        target = target_root / rel
        q.require(not target.exists(), 'quarantine_target_exists:' + rel)
        moves.append((rel, source, target, inventory(source, root)))
    target_root.mkdir(parents=True, exist_ok=True)
    receipt_path = target_root / f'receipt-{time.strftime("%Y%m%dT%H%M%S")}.json'
    q.require(not receipt_path.exists(), 'receipt_exists')
    receipt = dict(version='queue-quarantine-v1', incident=incident, reason=reason.strip(), createdAt=time.time(),
                   state='prepared', moved=[],
                   items=[dict(source=rel, target=str(target.relative_to(root)), files=files)
                          for rel, _, target, files in moves])
    q.save(receipt_path, receipt)
    for rel, source, target, files in moves:
        target.parent.mkdir(parents=True, exist_ok=True)
        os.rename(source, target)
        for item in files:
            moved = target_root / item['path']
            q.require(moved.is_file() and q.digest(moved) == item['sha256'], 'quarantine_hash_mismatch:' + item['path'])
        receipt['moved'].append(rel)
        q.save(receipt_path, receipt, replace=True)
    receipt['state'] = 'verified'
    q.save(receipt_path, receipt, replace=True)
    return receipt_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('incident')
    parser.add_argument('--reason', required=True)
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()
    print(quarantine(args.incident, args.reason, args.paths).relative_to(q.ROOT))


if __name__ == '__main__':
    main()
