"""Publish bounded exact-job approvals after individual checks."""
import time

import research_queue as q
import research_approval as approval


def qualify(queue, entries, modules=q.MODULES, *, allow_live=False):
    """Keep individual authorization checks. Publish all records with one atomic save.

    Live callers must explicitly opt in. This function never dispatches jobs.
    A revoked ID requires a successor, not automatic reapproval.
    """
    q.require(allow_live or queue.resolve() != q.QUEUE.resolve(), 'transaction_live_disabled')
    q.require(isinstance(entries, list) and 1 <= len(entries) <= 10, 'transaction_limit')
    ids = []
    for entry in entries:
        q.require(set(entry) == {'job', 'sha256', 'approver', 'reason'}, 'transaction_fields')
        ident = entry['job']
        q.require(isinstance(ident, str) and q.ID.fullmatch(ident), 'job_id')
        q.require(isinstance(entry['approver'], str) and approval.APPROVER.fullmatch(entry['approver']), 'approver_format')
        q.require(entry['approver'] != 'test' or queue.resolve() != q.QUEUE.resolve(), 'test_approver_on_live_queue')
        q.require(isinstance(entry['reason'], str) and len(entry['reason'].strip()) >= 12, 'approval_reason')
        q.require(isinstance(entry['sha256'], str) and len(entry['sha256']) == 64, 'transaction_hash')
        ids.append(ident)
    q.require(len(set(ids)) == len(ids), 'transaction_duplicate_id')
    started = time.monotonic()
    with q.host_lock(queue / 'approval.lock', wait=30):
        locked = time.monotonic()
        doc = approval.load(queue)
        q.require(not any(e.get('action') == 'revoke' and e.get('job') in ids for e in doc['events']),
                  'transaction_revoked')
        records = {}
        changed = False
        for entry in entries:
            ident = entry['job']
            spec = q.load(queue / 'jobs' / ident / 'spec.json')
            q.require(q.text_digest(spec) == entry['sha256'], 'transaction_spec_changed')
            # Capture ownership has separate side effects. Keep it outside this pilot.
            q.require(spec['authority'] != 'capture', 'transaction_capture_deferred')
            existing = doc['jobs'].get(ident)
            if existing is not None:
                q.require(existing['sha256'] == entry['sha256'], 'approval_changed')
                q.require(approval.is_approved(queue, spec, doc=doc), 'approval_checks_changed')
                records[ident] = existing
                continue
            spec, checks = approval.checks(queue, ident, modules, entry['approver'])
            q.require(q.text_digest(spec) == entry['sha256'], 'transaction_spec_changed')
            record = dict(sha256=entry['sha256'], approver=entry['approver'], reason=entry['reason'].strip(),
                          approvedAt=time.time(), checks=checks, checksSHA256=q.text_digest(checks))
            doc['jobs'][ident] = record
            doc['events'].append(dict(action='approve', job=ident, **record))
            records[ident] = record
            changed = True
        # Recheck exact specs and source pins after all checks, before atomic publication.
        for entry in entries:
            spec = q.load(queue / 'jobs' / entry['job'] / 'spec.json')
            q.require(q.text_digest(spec) == entry['sha256'], 'transaction_spec_changed')
            q.verify_pins(spec)
            q.require(approval.is_approved(queue, spec, doc=doc), 'approval_checks_changed')
        if changed:
            q.save(approval.path(queue), doc, replace=True)
        lock_seconds = time.monotonic()-locked
    return dict(records=records, seconds=time.monotonic()-started, lockSeconds=lock_seconds,
                storeWrites=int(changed), executionStarted=False)
