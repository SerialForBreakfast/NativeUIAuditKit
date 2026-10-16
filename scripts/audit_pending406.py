"""Read pending jobs and report exact changed inputs. Do not approve or execute jobs."""
import argparse
import json
from pathlib import Path
import research_queue as q
from research_readiness import check


def audit():
    rows = []
    for folder in sorted((q.QUEUE/'jobs').iterdir()):
        if not (folder/'spec.json').is_file() or q.state(folder)[0] != 'pending':
            continue
        spec = q.load(folder/'spec.json')
        row = check(folder.name)
        pins = list(spec.get('inputs', [])) + [x['from'] for x in spec.get('stage', [])]
        if spec['authority'] == 'training':
            pins += spec['training']['membership'] + [spec['training']['initialization']]
        if spec['authority'] == 'capture':
            pins.append(spec['capture']['plan'])
        changed = {}
        for pin in pins:
            path = q.local_path(q.ROOT, pin['path'])
            actual = q.digest(path) if path.is_file() else None
            if actual != pin['sha256']:
                changed[pin['path']] = dict(path=pin['path'], expected=pin['sha256'], actual=actual,
                                            problem='missing' if actual is None else 'changed')
        row['changedInputs'] = list(changed.values())
        row['approved'] = __import__('research_approval').is_approved(q.QUEUE, spec)
        row['limits'] = spec['limits']
        rows.append(row)
    return dict(version='pending-audit-v1', jobs=rows, executionStarted=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.relative_to(q.ROOT)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = audit()
    q.save(output, report)
    print(json.dumps([dict(job=r['job'], approved=r['approved'], blockers=r['blockers'],
                           changedInputs=[p['path'] for p in r['changedInputs']]) for r in report['jobs']], indent=2))
