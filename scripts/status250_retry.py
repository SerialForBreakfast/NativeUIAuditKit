"""Keep worker failure evidence and acknowledge the reported retry."""
import hashlib
from datetime import datetime, timezone
import shared_transfer as s
import transition245 as t


def run():
    s.mounted()
    base = s.ROOT / 'reports/work/TRANSITION-250'
    failure = s.document(s.SHARE / 'joe-big-dog/joe-big-dog-transition249-blocked01.json')
    retry = s.document(s.SHARE / 'joe-big-dog/joe-big-dog-transition249-retry4g-start01.json')
    for item in (failure, retry):
        s.require(item['request_id'] == 'nuiak-transition249-replication-v1', 'request_mismatch')
    artifact = failure['artifact']
    s.require(artifact['intended_receiver'] == 'NUIAK', 'receiver_mismatch')
    tx = dict(requestID=failure['request_id'], sharedPath=artifact['file'], bytes=artifact['bytes'], sha256=artifact['sha256'])
    local = base / 'artifacts/transition249-failure-evidence01.tar.gz'
    s.copy_verified(s.path_under(s.SHARE, artifact['file']), local, tx)
    t.h.write(base / 'worker-failure.json', failure)
    t.h.write(base / 'worker-retry.json', retry)
    response = dict(
        id='nuiak-transition250-failure-receipt-v1',
        request_id=failure['request_id'], receiver='NUIAK',
        created_at=datetime.now(timezone.utc).isoformat(),
        state='received_verified', artifact=artifact,
        receipt='Exact failure archive size and SHA-256 verified. Local copy retained. Sender may remove only this shared archive.',
        retry='Big Dog reports maintainer approval for 4 GiB and a fresh attempt. NUIAK records this as a peer report.',
        next='Return the 3 fixed comparisons and resource measurements. Preserve the first failed attempt. No further retry is requested.',
        outcomes=dict(software='12 focused tests and 140 Swift tests pass', data='No role changes',
                      integration='Input receipt accepted; result verification pending', model='No promotion'))
    dest = base / 'failure-receipt.json'
    t.h.write(dest, response)
    target = s.path_under(s.SHARE, 'nuiak/responses/nuiak-transition250-failure-receipt-v1.json')
    check = dict(requestID=response['id'], sharedPath=str(target.relative_to(s.SHARE)),
                 bytes=dest.stat().st_size, sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
    s.copy_verified(dest, target, check)
    s.require(s.document(target) == response, 'readback_mismatch')
    print('Failure archive verified. Receipt published and read back. Sender owns cleanup.')


if __name__ == '__main__':
    run()
