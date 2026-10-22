"""Select reviewed, bounded continuation jobs without retrying old attempts."""
import argparse
import json
import math
from pathlib import Path
import research_queue as q
import research_approval as approval

VERSION = 'research-continuation-v1'
# RECOVERY488: a v2 record names the earlier chunk whose last checkpoint it resumes.
# All chunks still reserve time and storage against the original exhausted attempt.
CHAIN_VERSION = 'research-continuation-v2'
RELEASE_VERSION = 'research-continuation-release-v1'


def records(queue):
    folder = queue / 'continuations'
    return {p.stem: q.load(p) for p in sorted(folder.glob('*.json'))}


def released(queue):
    """Return {job: release} for verified releases of reservations that never ran."""
    out = {}
    for path in sorted((queue / 'continuation-releases').glob('*.json')):
        doc = q.load(path)
        if validate_release(doc, queue) is None:
            out[doc['job']] = doc
    return out


def validate_release(doc, queue):
    """A release frees a reservation only for an unapproved job that never started. Return the problem or None."""
    try:
        q.require(isinstance(doc, dict) and set(doc) == {'version', 'job', 'specSHA256', 'reason'} and
                  doc['version'] == RELEASE_VERSION, 'continuation_release_fields')
        q.require(isinstance(doc['reason'], str) and len(doc['reason'].strip()) >= 20, 'continuation_release_reason')
        job = q.local_path(queue, 'jobs/' + doc['job'])
        spec = q.load(job / 'spec.json')
        q.require(q.text_digest(spec) == doc['specSHA256'], 'continuation_release_spec_changed')
        q.require(not q.attempts_of(job), 'continuation_release_started')
        q.require(doc['job'] not in approval.approved_map(queue), 'continuation_release_still_approved')
        return None
    except (ValueError, OSError, KeyError, TypeError) as error:
        return str(error)


def release(doc, queue=q.QUEUE):
    """Record that a revoked, unstarted continuation no longer reserves budget. The record stays as history."""
    with q.host_lock(queue/'continuation-registration.lock'):
        problem = validate_release(doc, queue)
        q.require(problem is None, problem or '')
        q.require(doc['job'] in records(queue), 'continuation_release_unknown')
        path = queue/'continuation-releases'/(doc['job']+'.json')
        if path.exists():
            q.require(q.load(path) == doc, 'continuation_release_immutable')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            q.save(path, doc)


def checked(ref):
    q.check_pin(ref)
    path = q.local_path(q.ROOT, ref['path'])
    q.require(path.is_file() and q.digest(path) == ref['sha256'], 'continuation_input_changed')
    return path


def validate(record, queue):
    fields = {'version', 'job', 'specSHA256', 'parent', 'parentAttempt',
              'parentResult', 'checkpoint', 'qualification', 'reason', 'budget'}
    chain = record.get('version') == CHAIN_VERSION
    q.require(set(record) == (fields | {'previous'} if chain else fields), 'continuation_fields')
    q.require(record['version'] in (VERSION, CHAIN_VERSION), 'continuation_version')
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
    pins = spec['inputs']
    if chain:
        # The previous chunk must share this parent and budget. Its last checkpoint is a declared dependency.
        previous = records(queue).get(record['previous'])
        q.require(previous is not None and previous['job'] != record['job'] and
                  (previous['parent'], previous['parentAttempt'], previous['budget']) ==
                  (record['parent'], record['parentAttempt'], record['budget']), 'continuation_previous')
        q.require(record['checkpoint'] == dict(job=record['previous'], output='last.pt') and
                  any(d['job'] == record['previous'] and 'last.pt' in d['outputs'] for d in spec.get('dependencies', [])),
                  'continuation_previous_checkpoint')
        q.require(record['qualification'] in pins, 'continuation_inputs_not_pinned')
    else:
        checkpoint = checked(record['checkpoint'])
        q.require(source.parent.resolve() in checkpoint.parents, 'continuation_checkpoint_owner')
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
    for ident in released(queue):
        if ident != record['job']:
            siblings.pop(ident, None)
    siblings[record['job']] = record
    seconds = elapsed
    size = q.live_output_bytes(source.parent/'out')
    for sibling in siblings.values():
        if (sibling['parent'], sibling['parentAttempt']) != (record['parent'], record['parentAttempt']):
            continue
        q.require(sibling['budget'] == budget, 'continuation_budget_conflict')
        other = q.load(queue/'jobs'/sibling['job']/'spec.json')
        q.require(q.text_digest(other) == sibling['specSHA256'], 'continuation_sibling_changed')
        used = sibling_usage(queue/'jobs'/sibling['job'], other)
        seconds += used[0]
        size += used[1]
    q.require(seconds <= budget['totalSeconds'] and size <= budget['totalOutputBytes'], 'continuation_budget_exhausted')
    return spec


def sibling_usage(job, spec):
    """Return (seconds, bytes) that 1 sibling uses or may use.

    A finished attempt counts its measured wall time and retained outputs. An unfinished or unknown attempt
    and a job that has not run count the worst case: the spec time and output limits.
    """
    attempts = q.attempts_of(job)
    if not attempts:
        return spec['limits']['timeoutSeconds'], spec['limits']['maxOutputBytes']
    seconds = size = 0
    for attempt in attempts:
        result = attempt/'result.json'
        wall = q.load(result).get('wallSeconds') if result.is_file() else None
        if type(wall) not in (int, float) or not math.isfinite(wall) or wall < 0:
            return spec['limits']['timeoutSeconds'] * len(attempts), spec['limits']['maxOutputBytes'] * len(attempts)
        seconds += wall
        size += q.live_output_bytes(attempt/'out') if (attempt/'out').exists() else 0
    return seconds, size


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
    parser.add_argument('action', choices=['inventory', 'register', 'release'])
    parser.add_argument('record', nargs='?', type=Path)
    args = parser.parse_args()
    if args.action in ('register', 'release'):
        if args.record is None:
            parser.error('record is required')
        (register if args.action == 'register' else release)(q.load(args.record))
    print(json.dumps(inventory(), indent=2))
