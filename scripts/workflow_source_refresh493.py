"""Recheck unstarted approvals after an exact, reviewed source change."""
import time
import research_queue as q
import research_approval as approval


def refresh(queue, ids, changes, reason):
    """Preserve specifications and history. Never refresh an attempted job."""
    q.require(1 <= len(ids) <= 10 and len(ids) == len(set(ids)), 'refresh_batch')
    q.require(changes and all(set(x) == {'path', 'before', 'after'} for x in changes), 'refresh_changes')
    q.require(len({x['path'] for x in changes}) == len(changes), 'refresh_duplicate_path')
    q.require(isinstance(reason, str) and len(reason) >= 12, 'refresh_reason')
    expected = {x['path']: x for x in changes}
    with q.host_lock(q.ROOT / '.build/research-queue.lock'):
        with q.host_lock(queue / 'approval.lock', wait=30):
            doc = approval.load(queue)
            records = {}
            for ident in ids:
                job = queue / 'jobs' / ident
                q.require(not list((job / 'attempts').glob('*')), 'refresh_attempt_exists')
                old = doc['jobs'].get(ident)
                q.require(old is not None, 'refresh_approval_missing')
                q.require(not any(e.get('action') == 'revoke' and e.get('job') == ident
                                  for e in doc['events']), 'refresh_revoked')
                spec = q.load(job / 'spec.json')
                q.require(q.text_digest(spec) == old['sha256'], 'refresh_spec_changed')
                q.require(q.text_digest(old['checks']) == old['checksSHA256'], 'refresh_checks_changed')
                pins = old['checks']['code']
                changed = set()
                for pin in pins:
                    actual = q.digest(q.ROOT / pin['path'])
                    if actual == pin['sha256']:
                        continue
                    change = expected.get(pin['path'])
                    q.require(change is not None and change['before'] == pin['sha256']
                              and change['after'] == actual, 'refresh_unreviewed_change')
                    changed.add(pin['path'])
                q.require(changed == set(expected), 'refresh_change_not_present')
                checked_spec, checks = approval.checks(queue, ident, q.MODULES,
                                                       approver='agent:Maximum-mini-NUIAK')
                q.require(q.text_digest(checked_spec) == old['sha256'], 'refresh_spec_changed')
                record = dict(old, checks=checks, checksSHA256=q.text_digest(checks),
                              approvedAt=time.time(), reason=reason)
                records[ident] = record
                doc['jobs'][ident] = record
                doc['events'].append(dict(action='source-refresh', job=ident,
                    previousChecksSHA256=old['checksSHA256'], changes=changes, **record))
            for ident in ids:
                spec = q.load(queue / 'jobs' / ident / 'spec.json')
                q.require(q.text_digest(spec) == records[ident]['sha256'], 'refresh_spec_changed')
                q.require(approval.is_approved(queue, spec, doc=doc), 'refresh_source_changed')
            q.save(approval.path(queue), doc, replace=True)
    return dict(jobs=ids, executionStarted=False, specificationsChanged=False)
