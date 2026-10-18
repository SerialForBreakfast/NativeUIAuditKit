"""Inspect exhausted jobs and restart them as new successors with larger limits (EXTENSION408).

The parent job and its attempts stay unchanged. Each restart is 1 new immutable job with its own approval.
A restart starts from step 0. Use research_continuations.py for a qualified checkpoint resume.
"""
import argparse
import copy
import json
import math
import time

import research_queue as q
import research_approval
import research_execution_policy as policy

VERSION = 'research-extension-v1'
MAX_SECONDS = 86400  # The spec validator maximum.
MAX_BYTES = 1 << 34  # The spec validator maximum.
LIMIT_FAILURES = {'timeout', 'output_limit'}
MARGIN = 1.25


def folder(queue):
    return queue / 'extensions'


def records(queue):
    return {p.stem: q.load(p) for p in sorted(folder(queue).glob('*.json'))}


def order(queue):
    """Return {successor job: save time}. Later saves run later."""
    return {ident: record['queuedAt'] for ident, record in records(queue).items()}


def estimate(attempt):
    """Estimate the restart time from the last recorded progress of an attempt."""
    try:
        started = q.load(attempt / 'attempt.json')['startedAt']
        progress = q.load(attempt / 'progress.json')
    except (OSError, KeyError, ValueError):
        return dict(available=False, basis='The attempt has no progress record.')
    done, total, at = progress.get('completed'), progress.get('total'), progress.get('updatedAt')
    numbers = all(type(v) in (int, float) and math.isfinite(v) for v in (done, total, at, started))
    if not numbers or done <= 0 or total <= 0 or at <= started:
        return dict(available=False, basis='The attempt has no completed progress unit.')
    rate = (at - started) / done
    unit = progress.get('unit') or 'units'
    return dict(available=True, unit=unit, step=progress.get('step'), completed=done, total=total,
                secondsPerUnit=rate, restartSeconds=rate * total,
                remainingAfterProgressSeconds=rate * max(0, total - done),
                basis=f'{done} of {total} {unit} in {at - started:.0f} s, including setup. '
                      'A linear estimate does not include slower final steps.')


def suggest(limits, reason, guess):
    seconds = limits['timeoutSeconds']
    if guess.get('available'):
        seconds = max(seconds, math.ceil(guess['restartSeconds'] * MARGIN / 60) * 60)
    elif reason == 'timeout':
        seconds = seconds * 2
    size = limits['maxOutputBytes'] * 2 if reason == 'output_limit' else limits['maxOutputBytes']
    return dict(timeoutSeconds=int(min(seconds, MAX_SECONDS)), maxOutputBytes=int(min(size, MAX_BYTES)))


def successor_id(parent, queue):
    base = parent
    head, _, tail = parent.rpartition('-r')
    if head and tail.isdigit():
        base = head
    for number in range(2, 1000):
        suffix = f'-r{number}'
        ident = base[:64 - len(suffix)] + suffix
        if not (queue / 'jobs' / ident).exists():
            return ident
    raise ValueError('extension_id_exhausted')


def blocker(job, spec, queue):
    """Return the reason that a restart cannot be saved, or None."""
    if spec['authority'] == 'capture':
        return 'extension_capture_unsupported: capture failures need diagnosis. Capture limits stay at 800 s.'
    if spec.get('training', {}).get('resume') == 'checkpoint-v1':
        return 'extension_checkpoint_contract: use a qualified continuation for checkpoint resume.'
    if (queue / 'continuation-reviews' / (job.name + '.json')).exists():
        return 'extension_parent_superseded: a completed successor answers this question.'
    from research_continuations import records as continuations
    if any(r['parent'] == job.name for r in continuations(queue).values()):
        return 'extension_continuation_exists: a continuation successor is registered.'
    if any(r['parent'] == job.name for r in records(queue).values()):
        return 'extension_successor_exists: extend the successor if it is exhausted.'
    return None


def describe(ident, queue=q.QUEUE):
    """Describe 1 exhausted job for inspection. This does not change the queue."""
    job = q.local_path(queue, 'jobs/' + ident)
    spec = q.load(job / 'spec.json')
    current, attempts = q.state(job, display_cache=True)
    q.require(current == 'exhausted', 'extension_parent_not_exhausted:' + current)
    result = q.load(attempts[-1] / 'result.json')
    reason = result.get('reason')
    guess = estimate(attempts[-1])
    limits = spec['limits']
    return dict(job=ident, attempts=len(attempts), status=result.get('status'), reason=reason,
                wallSeconds=result.get('wallSeconds'), limits=limits, estimate=guess,
                suggested=suggest(limits, reason, guess),
                defaultLimits=dict(timeoutSeconds=policy.seconds(q.text_digest(spec), spec['authority'], q.DIAGNOSTIC_SECONDS),
                                   maxOutputBytes=policy.output_bytes(q.text_digest(spec), spec['authority'], q.DIAGNOSTIC_BYTES)),
                limitFailure=reason in LIMIT_FAILURES,
                warning=None if reason in LIMIT_FAILURES else
                    'More time or output does not fix this failure. Repair the cause before a restart.',
                successors=[r['job'] for r in records(queue).values() if r['parent'] == ident],
                blocker=blocker(job, spec, queue), successorId=successor_id(ident, queue))


def plan(queue, parent, seconds, size, reason, modules=q.MODULES):
    """Build the successor specification. This does not write files."""
    q.require(isinstance(parent, str) and q.ID.fullmatch(parent), 'job_id')
    job = q.local_path(queue, 'jobs/' + parent)
    q.require((job / 'spec.json').is_file(), 'unknown_job')
    spec = q.validate(q.load(job / 'spec.json'), modules)
    current, attempts = q.state(job)
    q.require(current == 'exhausted', 'extension_parent_not_exhausted:' + current)
    problem = blocker(job, spec, queue)
    q.require(problem is None, (problem or '').split(':')[0])
    q.require(isinstance(reason, str) and len(reason.strip()) >= 20, 'extension_reason')
    q.require(type(seconds) is int and type(size) is int, 'extension_limit_type')
    old = spec['limits']
    q.require(old['timeoutSeconds'] <= seconds <= MAX_SECONDS, 'extension_timeout_range')
    q.require(old['maxOutputBytes'] <= size <= MAX_BYTES, 'extension_output_range')
    successor = copy.deepcopy(spec)
    successor['id'] = successor_id(parent, queue)
    successor['limits'] = dict(timeoutSeconds=seconds, maxOutputBytes=size, maxAttempts=1)
    if spec['authority'] == 'training':
        training = successor['training']
        training['storageBudgetBytes'] = max(training['storageBudgetBytes'], size)
        q.require(training['resume'] == 'restart', 'extension_requires_restart_contract')
    q.validate(successor, modules)
    result_path = attempts[-1] / 'result.json'
    return spec, successor, dict(path=q.relative(result_path), sha256=q.digest(result_path)), len(attempts)


def record_limits(queue, spec, by, reason):
    """Record a maintainer override for 1 exact specification hash."""
    digest = q.text_digest(spec)
    path = queue / policy.OVERRIDES
    with q.host_lock(queue / 'execution-limits.lock'):
        doc = q.load(path) if path.is_file() else dict(version=policy.OVERRIDE_VERSION, specs={}, events=[])
        q.require(doc.get('version') == policy.OVERRIDE_VERSION, 'execution_limits_version')
        entry = dict(job=spec['id'], timeoutSeconds=spec['limits']['timeoutSeconds'],
                     maxOutputBytes=spec['limits']['maxOutputBytes'], by=by, reason=reason.strip(), at=time.time())
        existing = doc['specs'].get(digest)
        if existing is not None:
            q.require({k: existing[k] for k in ('job', 'timeoutSeconds', 'maxOutputBytes')} ==
                      {k: entry[k] for k in ('job', 'timeoutSeconds', 'maxOutputBytes')}, 'execution_limits_immutable')
            return existing
        doc['specs'][digest] = entry
        doc['events'].append(dict(action='override', specSHA256=digest, **entry))
        q.save(path, doc, replace=True)
    return entry


def save(queue, parent, seconds, size, reason, by='maintainer', modules=q.MODULES):
    """Save 1 restart at the end of the deferred queue and approve it. The runner starts it later."""
    q.require(by == 'maintainer' or by == 'test' and queue.resolve() != q.QUEUE.resolve(), 'extension_requires_maintainer')
    with q.host_lock(queue / 'extension-registration.lock'):
        old, spec, parent_result, attempt = plan(queue, parent, seconds, size, reason, modules)
        digest = q.text_digest(spec)
        override = None
        if (seconds > policy.seconds(digest, spec['authority'], q.DIAGNOSTIC_SECONDS) or
                size > policy.output_bytes(digest, spec['authority'], q.DIAGNOSTIC_BYTES)):
            override = record_limits(queue, spec, by, reason)
        source = folder(queue) / 'specs' / (spec['id'] + '.json')
        source.parent.mkdir(parents=True, exist_ok=True)
        if not source.exists() or q.load(source) != spec:
            q.save(source, spec)
        q.submit(source, queue, modules)
        guess = estimate(q.attempts_of(queue / 'jobs' / parent)[-1])
        record = dict(version=VERSION, job=spec['id'], specSHA256=digest, parent=parent, parentAttempt=attempt,
                      parentResult=parent_result, mode='restart', reason=reason.strip(), by=by,
                      previousLimits=old['limits'], limits=spec['limits'], limitOverride=override is not None,
                      estimate=guess, queuedAt=time.time())
        q.save(folder(queue) / (spec['id'] + '.json'), record)
    outcome = dict(job=spec['id'], specSHA256=digest, approved=False, executionStarted=False)
    try:
        research_approval.approve(queue, spec['id'], by, reason, modules)
        outcome['approved'] = True
    except (ValueError, OSError, KeyError) as error:
        # The successor stays saved and unapproved. The normal approval action can retry after a repair.
        outcome['approvalError'] = str(error)[:300]
    return outcome


def inventory(queue=q.QUEUE):
    rows = []
    for job in sorted((queue / 'jobs').iterdir()) if (queue / 'jobs').exists() else []:
        try:
            if q.state(job, display_cache=True)[0] == 'exhausted':
                rows.append(describe(job.name, queue))
        except (ValueError, OSError, KeyError, TypeError) as error:
            rows.append(dict(job=job.name, error=str(error)[:200]))
    return dict(version=VERSION, jobs=rows, executionStarted=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('inventory')
    saver = sub.add_parser('save')
    saver.add_argument('job')
    saver.add_argument('--timeout-seconds', type=int, required=True)
    saver.add_argument('--max-output-bytes', type=int, required=True)
    saver.add_argument('--reason', required=True)
    args = parser.parse_args()
    if args.command == 'save':
        print(json.dumps(save(q.QUEUE, args.job, args.timeout_seconds, args.max_output_bytes, args.reason), indent=2))
    else:
        print(json.dumps(inventory(), indent=2))


if __name__ == '__main__':
    main()
