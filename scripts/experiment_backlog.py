"""Validate scientific task definitions. Tasks.md owns status; this tool never dispatches."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
STATES = {'Existing execution', 'Ready to register', 'Waiting for dependency', 'Needs adapter',
          'Needs data', 'Needs decision', 'Conditional', 'Completed or superseded', 'Awaiting review'}


def require(value, reason):
    if not value:
        raise ValueError(reason)


def validate(catalog, root=ROOT):
    require(catalog.get('version') == 'scientific-backlog-v1', 'catalog_version')
    require(catalog.get('ownerAuthority') == 'Tasks.md', 'status_authority')
    rows = catalog['experiments']
    ids = [r['id'] for r in rows]
    require(ids and len(ids) == len(set(ids)), 'duplicate_id')
    require(all(re.fullmatch(r'B405-\d{3}', x) for x in ids), 'task_id')
    seen_questions, seen_comparisons = set(), set()
    for row in rows:
        require(not {'status', 'ready', 'approved'} & row.keys(), 'duplicate_status_store')
        for key in ('parentTask', 'track', 'title', 'question', 'hypothesis', 'comparison', 'changedVariable', 'requiredInputs'):
            require(isinstance(row.get(key), str) and row[key].strip(), 'missing_' + key)
        question = ' '.join(row['question'].lower().split())
        comparison = ' '.join(row['comparison'].lower().split())
        require(question not in seen_questions, 'duplicate_question')
        require(comparison not in seen_comparisons, 'duplicate_comparison')
        seen_questions.add(question); seen_comparisons.add(comparison)
        require(row['profile'] in catalog['profiles'], 'unknown_profile')
        profile = catalog['profiles'][row['profile']]
        require(all(profile.get(k) for k in ('roles', 'controls', 'metrics', 'budget', 'acceptance', 'reviewMinutes', 'preparationMinutes')), 'profile_incomplete')
        require(type(row['priority']) is int and 0 <= row['priority'] <= 4, 'priority')
        require(set(row['outcomes']) == {'supported', 'contradicted', 'inconclusive'} and all(row['outcomes'].values()), 'decision_branches')
        require(row['acceptance'].get('rule') and row['acceptance'].get('numericLimits'), 'acceptance_missing')
        require(isinstance(row.get('baseline'), str) and row['baseline'].strip(), 'baseline_missing')
        cost = row.get('cost', {})
        require(all(cost.get(k) for k in ('preparationMinutes', 'reviewMinutes', 'executionCeiling', 'estimateBasis')), 'cost_missing')
        for key in ('preparationMinutes', 'reviewMinutes'):
            limits = cost[key]
            require(isinstance(limits, list) and len(limits) == 2 and
                    all(type(v) in (int, float) and v >= 0 for v in limits) and
                    limits[0] <= limits[1], 'cost_range')
        require(row['template'].get('id') and row['template'].get('variant') and row['template'].get('qualification'), 'template_missing')
        require(row['sourceEvidence'], 'source_missing')
        for source in row['sourceEvidence']:
            path = Path(source)
            require(not path.is_absolute() and '..' not in path.parts, 'unsafe_source')
            require((root / path).is_file(), 'source_unavailable:' + source)
        require(row['reconciliation']['disposition'] in ('answered', 'unresolved'), 'reconciliation_state')
        require(row['reconciliation'].get('reason'), 'reconciliation_reason')
        if row['reconciliation']['disposition'] == 'unresolved':
            require(row['requirements'], 'requirement_missing')
            for item in row['requirements']:
                require(all(item.get(k) for k in ('owner', 'kind', 'missing', 'unblock')), 'blocker_incomplete')
        else:
            require(row['reconciliation'].get('reuse'), 'completed_evidence_missing')
        require(len(row['dependencies']) == len(set(row['dependencies'])), 'duplicate_dependency')
        require(all(x in ids and x != row['id'] for x in row['dependencies']), 'missing_dependency')
    indexed = {r['id']: r for r in rows}
    visiting, visited = set(), set()
    def visit(ident):
        require(ident not in visiting, 'dependency_cycle')
        if ident in visited:
            return
        visiting.add(ident)
        for parent in indexed[ident]['dependencies']:
            visit(parent)
        visiting.remove(ident); visited.add(ident)
    for ident in ids:
        visit(ident)
    pending = [r for r in rows if r['reconciliation']['disposition'] == 'unresolved']
    # BACKLOG410: answered records leave the open count. The earlier 100-record floor was a tranche target.
    return dict(records=len(rows), outstandingScientificTasks=len(pending), answered=len(rows)-len(pending),
                byTrack=dict(Counter(r['track'] for r in pending)), executionStarted=False,
                limitation='Definition checks do not establish input eligibility, executable readiness, or model quality.')


def task_states(text):
    rows = {}
    for line in text.splitlines():
        match = re.match(r'\| (B405-\d{3}) \| ([^|]+) \| ([^|]+) \|', line)
        if match:
            ident, owner, state = (s.strip() for s in match.groups())
            require(ident not in rows, 'duplicate_task_status')
            require(state in STATES and owner, 'task_status_invalid')
            rows[ident] = dict(owner=owner, state=state)
    return rows


def validate_engineering(engineering, catalog, tasks):
    require(engineering.get('version') == 'engineering-backlog-v1' and
            engineering.get('statusAuthority') == 'Tasks.md', 'engineering_authority')
    ids = set()
    science = {row['id'] for row in catalog['experiments']}
    for row in engineering['tasks']:
        ident = row['id']
        require(re.fullmatch(r'ENG405-\d{2}', ident) and ident not in ids, 'engineering_id')
        ids.add(ident)
        require(not {'status', 'approved', 'ready'} & row.keys(), 'duplicate_status_store')
        require(all(row.get(k) for k in ('parent', 'title', 'comparison', 'blocker', 'owner', 'acceptance')), 'engineering_incomplete')
        require(row['unlocks'] and set(row['unlocks']) <= science, 'engineering_science_link')
        hours = row['engineeringHours']
        require(len(hours) == 2 and all(type(h) in (int, float) and h >= 0 for h in hours)
                and hours[0] <= hours[1], 'engineering_estimate')
    recorded = re.findall(r'^\| (ENG405-\d{2}) \|', tasks, re.MULTILINE)
    require(len(recorded) == len(set(recorded)) and set(recorded) == ids, 'engineering_tasks_membership')
    return dict(engineeringTasks=len(ids))


def report(catalog, tasks, root=ROOT):
    result = validate(catalog, root)
    states = task_states(tasks)
    pending = {r['id']: r for r in catalog['experiments'] if r['reconciliation']['disposition'] == 'unresolved'}
    require(set(states) == set(pending), 'tasks_catalog_membership')
    for ident, value in states.items():
        require(value['state'] != 'Completed or superseded', 'completed_in_open_queue')
        if value['state'] in ('Ready to register', 'Existing execution') and 'plan' not in pending[ident]:
            # BACKLOG410: a plan binds its jobs through its arms. Older records list them by hand.
            require(pending[ident]['existingJobs'], 'readiness_without_job_binding')
            for job in pending[ident]['existingJobs']:
                require(re.fullmatch(r'[A-Za-z0-9_.-]+', job) and (root/'reports/work/research-queue/jobs'/job/'spec.json').is_file(), 'job_binding_missing')
    result['byStatus'] = dict(Counter(s['state'] for s in states.values()))
    result['estimatedReadySeconds'] = None
    result['durationNote'] = 'Use research_readiness and exact live specifications for ready duration. Task budgets are not queue duration.'
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog', type=Path)
    parser.add_argument('--tasks', type=Path)
    parser.add_argument('--engineering', type=Path)
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text())
    result = report(catalog, args.tasks.read_text()) if args.tasks else validate(catalog)
    if args.engineering:
        require(args.tasks, 'engineering_requires_tasks')
        result.update(validate_engineering(json.loads(args.engineering.read_text()), catalog, args.tasks.read_text()))
    print(json.dumps(result, indent=2, sort_keys=True))
