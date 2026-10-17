"""Check-gated job approval (RCA-20261013-01).

The runner executes only approved jobs. Each approval names 1 job, its exact spec hash, the approver, and a reason.
An agent approval passes the same checks as a maintainer approval. The maintainer can revoke any approval.
There is no bulk approval: each call approves 1 job.
"""
import argparse
import ast
import re
import shutil
import time
import uuid
from pathlib import Path

import research_queue as q
import research_trust as t

VERSION = 'research-approvals-v2'
APPROVER = re.compile(r'maintainer|agent:[A-Za-z0-9][A-Za-z0-9_.-]{0,63}|test')


def path(queue):
    return queue / 'approved-additions.json'


def load(queue):
    file = path(queue)
    if not file.exists():
        return dict(version=VERSION, jobs={}, events=[])
    doc = q.load(file)
    if doc.get('version') == 'research-additions-v1':
        q.require(not doc.get('jobs'), 'legacy_approvals_present')
        return dict(version=VERSION, jobs={}, events=[])
    q.require(doc.get('version') == VERSION, 'approval_version')
    return doc


def approved_map(queue):
    """Return {job: spec hash} for current, unrevoked approvals."""
    return {ident: record['sha256'] for ident, record in load(queue)['jobs'].items()}


def is_approved(queue, spec, doc=None, display_cache=False):
    """Check 1 approval. Pass `doc` from load() to check many jobs without parsing the file again.

    display_cache=True reuses stat-keyed hashes for dashboard labels. Execution and approval keep full hashing.
    """
    record = (doc if doc is not None else load(queue))['jobs'].get(spec['id'])
    if not record or record['sha256'] != q.text_digest(spec):
        return False
    checks = record.get('checks')
    if not checks or q.text_digest(checks) != record.get('checksSHA256'):
        return False
    hash_of = q.display_digest if display_cache else q.digest
    return all((q.ROOT / p['path']).is_file() and hash_of(q.ROOT / p['path']) == p['sha256']
               for p in checks.get('code', [])) and bool(checks.get('code'))


def post_run_authorization(queue, spec, attempt):
    """Return None when this job's own approval still authorizes the attempt, or the exact reason it does not.

    Only this job's record matters: other approvals and revocations do not affect it.
    Every approved code pin must keep its hash. This keeps the strict check; it does not narrow dependencies.
    """
    record = load(queue)['jobs'].get(spec['id'])
    if record is None:
        return 'approval_revoked_during_run'
    used = q.load(Path(attempt) / 'approval.json')
    checks = record.get('checks') or {}
    if (record['sha256'] != q.text_digest(spec) or record.get('checksSHA256') != used.get('checksSHA256')
            or not checks.get('code') or q.text_digest(checks) != record.get('checksSHA256')):
        return 'approval_changed_during_run'
    for pin in checks['code']:
        path = q.ROOT / pin['path']
        if not path.is_file() or q.digest(path) != pin['sha256']:
            return 'code_changed_during_run:' + pin['path']
    closure = Path(attempt) / 'closure.json'
    if not closure.is_file():
        return 'closure_record_missing'
    try:
        modules = q.load(closure)['modules']
        q.require(isinstance(modules, list) and all(isinstance(m, dict) and {'path', 'sha256'} <= set(m)
                                                    for m in modules), 'closure_record_invalid')
    except (ValueError, KeyError, TypeError, OSError):
        return 'closure_record_invalid'
    return None


def code_pins(spec, modules):
    """Pin entry points and their resident Python imports. This is not a security sandbox."""
    pending = [modules / (step.split('.')[0] + '.py') for step in spec['adapter']['steps']]
    pending += [q.MODULES / (name + '.py') for name in
                ('research_queue', 'research_trust', 'research_approval', 'research_readiness')]
    seen = {}
    while pending:
        path = pending.pop().resolve()
        if path in seen or not path.is_file():
            continue
        seen[path] = q.digest(path)
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            names = ([item.name for item in node.names] if isinstance(node, ast.Import)
                     else [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            for name in names:
                pending.append(path.parent / (name.split('.')[0] + '.py'))
    return [dict(path=q.relative(path), sha256=digest) for path, digest in sorted(seen.items())]


def checks(queue, ident, modules, approver='maintainer'):
    """Run the approval checks. Dependencies need not be complete; the runner checks them later."""
    spec = q.validate(q.load(queue / 'jobs' / ident / 'spec.json'), modules)
    # Only the test approver, which cannot act on the live queue, may approve legacy v1 fixtures.
    q.require(spec['version'] == t.SPEC_V2 or approver == 'test', 'approval_requires_spec_v2')
    q.verify_pins(spec)
    if spec['authority'] == 'training':
        q.check_training(spec, queue)
    q.require(not spec.get('requirements'), 'approval_requirements_unresolved')
    required_bytes = max(spec['limits']['maxOutputBytes'],
                         spec.get('training', {}).get('storageBudgetBytes', 0)) + q.STORAGE_MARGIN
    q.require(shutil.disk_usage(queue).free >= required_bytes, 'approval_storage_insufficient')
    ownership = capture_ownership(spec, queue) if spec['authority'] == 'capture' else None
    state, attempts = q.state(queue / 'jobs' / ident)
    q.require(state in ('pending', 'blocked') and not attempts, 'approval_requires_unstarted_job:' + state)
    return spec, dict(kind=spec.get('jobKind'), authority=spec['authority'], reads=spec.get('evidence', {}).get('reads', []),
                      dependencies=[d['job'] for d in spec.get('dependencies', [])],
                      limits=spec['limits'], code=code_pins(spec, modules),
                      requiredBytes=required_bytes,
                      captureOwnership=ownership,
                      limitation='File opens do not prove data use. Independent output review remains required.')


def capture_ownership(spec, queue):
    """Use the resident read-only readiness command. A receipt is not a target lease."""
    from qualify_hcf362 import Client, CLI
    q.require(CLI.is_file(), 'capture_readiness_cli_missing')
    folder = queue / 'approval-checks' / (spec['id'] + '-' + uuid.uuid4().hex)
    folder.mkdir(parents=True)
    ready = Client(folder).call('readiness', 'simulator', 'readiness', '--simulator-udid',
                                spec['capture']['target'], timeout=15)
    q.require(ready.get('can_run') is True and isinstance(ready.get('ownership'), list)
              and ready['ownership'] and all(row.get('state') == 'clear' for row in ready['ownership']),
              'capture_target_not_clear')
    receipt = folder / 'ownership.json'
    q.save(receipt, dict(checkedAt=time.time(), target=spec['capture']['target'], readiness=ready))
    return dict(path=q.relative(receipt), sha256=q.digest(receipt))


def approve(queue, ident, approver, reason, modules=q.MODULES):
    q.require(isinstance(ident, str) and q.ID.fullmatch(ident), 'job_id')
    q.require(isinstance(approver, str) and APPROVER.fullmatch(approver), 'approver_format')
    q.require(isinstance(reason, str) and len(reason.strip()) >= 12, 'approval_reason')
    q.require(approver != 'test' or queue.resolve() != q.QUEUE.resolve(), 'test_approver_on_live_queue')
    # ACTIONS417: approvals serialize on approval.lock only, with a bounded wait. They never wait for a running job.
    with q.host_lock(queue / 'approval.lock', wait=30):
        doc = load(queue)
        existing = doc['jobs'].get(ident)
        current = q.text_digest(q.load(queue / 'jobs' / ident / 'spec.json'))
        if existing is not None:
            # Repeating an approval of the same exact spec is a no-op. A changed spec needs a new job.
            q.require(existing['sha256'] == current, 'approval_changed')
            q.require(is_approved(queue, q.load(queue / 'jobs' / ident / 'spec.json')), 'approval_checks_changed')
            return existing
        spec, result = checks(queue, ident, modules, approver)
        digest = q.text_digest(spec)
        record = dict(sha256=digest, approver=approver, reason=reason.strip(), approvedAt=time.time(),
                      checksSHA256=q.text_digest(result), checks=result)
        doc['jobs'][ident] = record
        doc['events'].append(dict(action='approve', job=ident, **record))
        q.save(path(queue), doc, replace=True)
    return record


def revoke(queue, ident, by, reason):
    q.require(isinstance(by, str) and APPROVER.fullmatch(by), 'approver_format')
    q.require(isinstance(reason, str) and reason.strip(), 'revoke_reason')
    with q.host_lock(queue / 'approval.lock', wait=30):
        doc = load(queue)
        q.require(ident in doc['jobs'], 'not_approved')
        record = doc['jobs'].pop(ident)
        doc['events'].append(dict(action='revoke', job=ident, sha256=record['sha256'], by=by,
                                  reason=reason.strip(), revokedAt=time.time()))
        q.save(path(queue), doc, replace=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('approve', 'revoke', 'list'))
    parser.add_argument('job', nargs='?')
    parser.add_argument('--by', default='maintainer', help="'maintainer' or 'agent:<session>'")
    parser.add_argument('--reason')
    args = parser.parse_args()
    if args.command == 'list':
        for ident, record in sorted(load(q.QUEUE)['jobs'].items()):
            print(ident, record['approver'], record['reason'])
    elif args.command == 'approve':
        print(approve(q.QUEUE, args.job, args.by, args.reason))
    else:
        revoke(q.QUEUE, args.job, args.by, args.reason)
        print('revoked', args.job)


if __name__ == '__main__':
    main()
