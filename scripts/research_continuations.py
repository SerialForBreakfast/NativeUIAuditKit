"""Select reviewed, bounded continuation jobs without retrying old attempts."""
import argparse
import json
import math
from pathlib import Path
import research_queue as q
import research_approval as approval

VERSION = 'research-continuation-v1'


def records(queue):
    folder = queue / 'continuations'
    return {p.stem: q.load(p) for p in sorted(folder.glob('*.json'))}


def checked(ref):
    q.check_pin(ref)
    path = q.local_path(q.ROOT, ref['path'])
    q.require(path.is_file() and q.digest(path) == ref['sha256'], 'continuation_input_changed')
    return path


def validate(record, queue):
    q.require(set(record) == {'version', 'job', 'specSHA256', 'parent', 'parentAttempt',
        'parentResult', 'checkpoint', 'qualification', 'reason', 'budget'}, 'continuation_fields')
    q.require(record['version'] == VERSION, 'continuation_version')
    for key in ('job', 'parent'):
        q.require(isinstance(record[key], str) and q.ID.fullmatch(record[key]), 'continuation_id')
    q.require(record['job'] != record['parent'], 'continuation_self')
    q.require(type(record['parentAttempt']) is int and record['parentAttempt'] > 0, 'continuation_attempt')
    q.require(isinstance(record['reason'], str) and len(record['reason'].strip()) >= 20, 'continuation_reason')
    spec = q.load(queue/'jobs'/record['job']/'spec.json')
    q.require(q.text_digest(spec) == record['specSHA256'], 'continuation_spec_changed')
    parent = queue/'jobs'/record['parent']
    source = parent/'attempts'/str(record['parentAttempt'])/'result.json'
    q.require(checked(record['parentResult']) == source.resolve(), 'continuation_parent_result')
    result = q.load(source)
    q.require(result.get('status') == 'failed' and result.get('reason') == 'timeout', 'continuation_not_exhausted')
    parent_spec = q.load(parent/'spec.json')
    q.require(result.get('specSHA256') == q.text_digest(parent_spec), 'continuation_parent_changed')
    q.require(all(pin in spec['inputs'] for pin in parent_spec['inputs']), 'continuation_controls_changed')
    for field in ('authority', 'hypothesis', 'decisionRule', 'templateConfig'):
        q.require(spec.get(field) == parent_spec.get(field), 'continuation_controls_changed:' + field)
    if spec.get('authority') == 'training':
        old=dict(parent_spec['training']);new=dict(spec['training'])
        old.pop('resume');new.pop('resume')
        q.require(old==new,'continuation_training_controls_changed')
    checkpoint = checked(record['checkpoint'])
    q.require(source.parent.resolve() in checkpoint.parents, 'continuation_checkpoint_owner')
    pins = spec['inputs']
    q.require(record['checkpoint'] in pins and record['qualification'] in pins, 'continuation_inputs_not_pinned')
    proof = q.load(checked(record['qualification']))
    q.require(proof.get('version') == 'resume-qualification-v1' and
              proof.get('passed') is True and proof.get('checkpoint') == record['checkpoint'] and
              proof.get('adapter') == spec['adapter'] and proof.get('preservesControls') is True,
              'continuation_resume_unqualified')
    # A restart-only training contract cannot claim exact checkpoint resume.
    q.require(spec.get('authority') != 'training' or spec.get('training', {}).get('resume') == 'checkpoint-v1',
              'training_resume_not_supported')
    budget = record['budget']
    q.require(set(budget) == {'totalSeconds', 'totalOutputBytes', 'maxChunkSeconds'}, 'continuation_budget_fields')
    q.require(all(type(v) is int and v > 0 for v in budget.values()), 'continuation_budget')
    q.require(proof.get('budget') == budget and proof.get('parentResult') == record['parentResult'],
              'continuation_budget_not_pinned')
    q.require(budget['maxChunkSeconds'] <= 800 and spec['limits']['timeoutSeconds'] <= budget['maxChunkSeconds'],
              'continuation_chunk_limit')
    elapsed = result.get('wallSeconds')
    q.require(type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0, 'continuation_usage_unknown')
    # Reserve worst-case resources for every sibling, including pending jobs.
    siblings = records(queue)
    q.require(record['parent'] not in siblings, 'continuation_nested_budget_unsupported')
    siblings[record['job']] = record
    seconds = elapsed
    size = q.live_output_bytes(source.parent/'out')
    for sibling in siblings.values():
        if (sibling['parent'], sibling['parentAttempt']) != (record['parent'], record['parentAttempt']):
            continue
        q.require(sibling['budget'] == budget, 'continuation_budget_conflict')
        other = q.load(queue/'jobs'/sibling['job']/'spec.json')
        q.require(q.text_digest(other) == sibling['specSHA256'], 'continuation_sibling_changed')
        seconds += other['limits']['timeoutSeconds']
        size += other['limits']['maxOutputBytes']
    q.require(seconds <= budget['totalSeconds'] and size <= budget['totalOutputBytes'], 'continuation_budget_exhausted')
    return spec


def register(record, queue=q.QUEUE):
    """Reserve one successor. Registration does not approve or start it."""
    with q.host_lock(queue/'continuation-registration.lock'):
        validate(record, queue)
        path = queue/'continuations'/(record['job']+'.json')
        if path.exists():
            q.require(q.load(path) == record, 'continuation_immutable')
        else:
            q.require(not q.attempts_of(queue/'jobs'/record['job']), 'continuation_already_started')
            path.parent.mkdir(parents=True, exist_ok=True)
            q.save(path, record)


def eligible(ident, record, queue):
    try:
        q.require(review(record['parent'], queue) is None, 'continuation_superseded')
        spec = validate(record, queue)
        q.require(ident == record['job'], 'continuation_record_id')
        q.require(approval.is_approved(queue, spec), 'continuation_not_approved')
        q.require(q.state(queue/'jobs'/ident)[0] == 'pending', 'continuation_already_attempted')
        return None
    except (ValueError, OSError, KeyError, TypeError) as error:
        return str(error)


def review(job, queue):
    path = queue/'continuation-reviews'/(job+'.json')
    if not path.exists():
        return None
    doc = q.load(path)
    q.require(doc.get('state') == 'superseded', 'continuation_review_state')
    old = checked(doc['parentResult'])
    new = checked(doc['successorResult'])
    q.require(old.parent.parent.parent == queue/'jobs'/job, 'continuation_review_parent')
    result = q.load(new)
    q.require(result['status'] == 'complete' and q.outputs_intact(new.parent, result), 'continuation_review_output')
    return doc


def select(ready, queue, priority_tasks=()):
    """One continuation is one safe yield boundary. Ordinary work always wins.

    Saved restarts (EXTENSION408) run after ordinary work, in the order of their save time.
    """
    from research_extensions import order
    entries = records(queue)
    saved = order(queue)
    ordinary = [ident for ident in ready if ident not in entries and ident not in saved]
    if ordinary:
        ranks = {task: i for i, task in enumerate(priority_tasks)}
        return [min(ordinary, key=lambda ident: (ranks.get(
            q.load(queue/'jobs'/ident/'spec.json')['task'], len(ranks)), ident))]
    restarts = sorted((ident for ident in ready if ident in saved), key=lambda ident: (saved[ident], ident))
    if restarts:
        return restarts[:1]
    return next(([ident] for ident in ready if ident in entries and not eligible(ident, entries[ident], queue)), [])


def inventory(queue=q.QUEUE):
    entries = records(queue)
    rows = []
    for job in sorted((queue/'jobs').iterdir()) if (queue/'jobs').exists() else []:
        attempts = q.attempts_of(job)
        if not attempts or not (attempts[-1]/'result.json').exists():
            continue
        result = q.load(attempts[-1]/'result.json')
        if result['status'] == 'complete':
            continue
        children = [ident for ident, r in entries.items() if r['parent'] == job.name]
        ready = [ident for ident in children if eligible(ident, entries[ident], queue) is None]
        decision = review(job.name, queue)
        rows.append(dict(job=job.name, reason=result.get('reason'),
            state='superseded' if decision else 'resumable' if ready else 'needs-qualification' if result.get('reason') == 'timeout' else 'not-resumable',
            successors=children, ready=ready,
            nextAction=decision['reason'] if decision else 'Use the approved bounded successor.' if ready else
                'Review checkpoint support, unchanged controls, remaining budget, and completed successors.'
                if result.get('reason') == 'timeout' else 'Repair the failure. More execution time does not fix it.'))
    return dict(version=VERSION, jobs=rows, executionStarted=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['inventory', 'register'])
    parser.add_argument('record', nargs='?', type=Path)
    args = parser.parse_args()
    if args.action == 'register':
        parser.error('record is required') if args.record is None else register(q.load(args.record))
    print(json.dumps(inventory(), indent=2))
