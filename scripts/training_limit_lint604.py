"""RESET604 T0.4: list training specifications whose time limit is below the training policy.

Hand-written specifications can bypass the template compiler, which applies `research_execution_policy.TRAINING_SECONDS`.
COMP600 lost 2 fits at 1,800 s for this reason. This tool is read-only. It does not change the queue or any approval.
Fix a listed job with an EXTENSION408 restart (`research_extensions.save`) or compile it through `hcf_templates395.py`.
Usage: training_limit_lint604.py [--queue QUEUE] [--all]   (default: jobs without a complete result)
"""
import argparse
from pathlib import Path
import research_queue as q
import research_execution_policy as policy


def short(queue, include_complete=False):
    out = []
    for path in sorted((Path(queue)/'jobs').glob('*/spec.json')):
        spec = q.load(path)
        if spec.get('authority') != 'training' or spec['limits']['timeoutSeconds'] >= policy.TRAINING_SECONDS:
            continue
        results = sorted(path.parent.glob('attempts/*/result.json'))
        status = q.load(results[-1]).get('status') if results else 'not_started'
        reason = q.load(results[-1]).get('reason') if results else None
        if include_complete or status != 'complete':
            out.append(dict(job=spec['id'], task=spec.get('task'), timeoutSeconds=spec['limits']['timeoutSeconds'], status=status, reason=reason))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--queue', type=Path, default=q.QUEUE); parser.add_argument('--all', action='store_true')
    args = parser.parse_args()
    rows = short(args.queue, args.all)
    for r in rows:
        print(r)
    print(f'{len(rows)} training specifications below {policy.TRAINING_SECONDS} s')


if __name__ == '__main__':
    main()
