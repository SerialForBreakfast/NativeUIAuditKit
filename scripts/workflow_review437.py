"""Review several immutable experiment graphs without controlling execution."""
import argparse
import collections
import json
import time
from pathlib import Path

import research_queue as q
import workflow_batch435 as workflow
from experiment_templates import checked


def review(request, queue=q.QUEUE):
    q.require(set(request) == {'version', 'batches'}, 'review_fields')
    q.require(request['version'] == 'workflow-review-v1', 'review_version')
    refs = request['batches']
    q.require(isinstance(refs, list) and 1 <= len(refs) <= 12, 'review_batch_limit')
    q.require(all(isinstance(r, dict) and set(r) == {'path', 'sha256'} for r in refs), 'review_pin')
    q.require(len({r['path'] for r in refs}) == len(refs), 'review_duplicate_batch')
    batches, jobs, conflicts = [], {}, set()
    for ref in refs:
        try:
            report = workflow.inspect(q.load(checked(ref)), queue)
            for row in report['rows']:
                if not row['generated']:
                    continue
                previous = jobs.get(row['job'])
                if previous and previous['expectedSHA256'] != row['expectedSHA256']:
                    conflicts.add(row['job'])
                jobs[row['job']] = row
            batches.append(dict(manifest=ref, status='inspected', report=report))
        except (ValueError, OSError, KeyError, TypeError) as error:
            batches.append(dict(manifest=ref, status='unavailable', reason=str(error)[:1000]))
    for ident in conflicts:
        jobs[ident] = dict(jobs[ident], dispatch='blocked', blockers=['conflicting_specifications'])
    return dict(version='workflow-review-result-v1', observedAt=time.time(),
                executionChanged=False, modelAccepted=False, batches=batches,
                uniqueGeneratedJobs=len(jobs), counts=dict(collections.Counter(r['dispatch'] for r in jobs.values())),
                conflicts=sorted(conflicts), incomplete=bool(conflicts or any(b['status'] != 'inspected' for b in batches)),
                eta='ETA unavailable')


def summary(result):
    lines = ['# Experiment review', '',
             f"Unique generated jobs: {result['uniqueGeneratedJobs']}.",
             'States: ' + ', '.join(f'{k}: {v}' for k, v in sorted(result['counts'].items())),
             result['eta'] + '. Budgets are not duration estimates.',
             'This report does not approve execution or model acceptance.', '']
    if result['incomplete']:
        lines += ['Review is incomplete. Resolve unavailable evidence or conflicting specifications.', '']
    for batch in result['batches']:
        lines += ['## ' + batch['manifest']['path'], '']
        if batch['status'] == 'inspected':
            lines.append(workflow.summary(batch['report']))
            for row in batch['report']['rows']:
                if not row.get('decision'):
                    continue
                decision = row['decision']
                lines += ['### Matched outcomes by profile and comparison', '',
                          'Do not add these rows as independent trials. They reuse frames and groups.', '',
                          '| Profile | Comparison | Gains | Lost successes | New wrong outcomes | Observations | Groups |',
                          '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
                for part in sorted(decision['slices'], key=lambda s: (s['profile'] != 'standard', s['profile'], s['arm'])):
                    values = [part[k] for k in ('profile', 'arm', 'gains', 'losses', 'newWrongSelections', 'observations', 'groups')]
                    lines.append('| ' + ' | '.join(str(v).replace('|', '\\|').replace('\n', ' ') for v in values) + ' |')
                lines += ['', 'Case-linked evidence: ' + decision['report'], '']
        else:
            lines += ['Unavailable: ' + batch['reason'], '']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', type=Path)
    parser.add_argument('--text', action='store_true')
    args = parser.parse_args()
    source = q.local_path(q.ROOT, q.relative(args.request.resolve()))
    result = review(q.load(source))
    print(summary(result) if args.text else json.dumps(result, indent=2))
    return 2 if result['incomplete'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
