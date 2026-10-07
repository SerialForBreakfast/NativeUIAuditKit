"""Reconcile the exact worker receipt and publish diagnostic consequences."""
from datetime import datetime,timezone,timedelta
import shared_transfer as s
import transition245 as t


def run():
    s.mounted();base=s.ROOT/'reports/work/TRANSITION-250';receipt_path=s.SHARE/'joe-big-dog/joe-big-dog-transition249-input-receipt01.json'
    receipt=s.document(receipt_path);offer=t.h.read(s.ROOT/'reports/work/TRANSITION-249/artifacts/transfer.json')
    s.require(receipt.get('request_id')=='nuiak-transition249-replication-v1' and receipt.get('from')=='joe-big-dog'
              and receipt.get('to')=='NUIAK' and receipt.get('receiver')=='joe-big-dog'
              and receipt.get('state')=='accepted_input_verified_preflight_started','receipt_identity')
    s.require(receipt['artifact']==offer,'receipt_artifact')
    t.h.write(base/'worker-receipt.json',receipt)
    local=s.ROOT/'reports/work/TRANSITION-249/artifacts/transition249-inputs-v1.tar.gz'
    tx=dict(requestID=receipt['request_id'],sharedPath=offer['file'],bytes=offer['bytes'],sha256=offer['sha256'])
    shared=s.path_under(s.SHARE,offer['file']);s.verified(local,tx)
    if shared.exists():
        s.verified(shared,tx);s.require(s.document(receipt_path)==receipt,'receipt_changed')
        shared.unlink();s.require(not shared.exists(),'cleanup_uncertain')
    now=datetime.now(timezone.utc)
    response=dict(schema_version=1,id='nuiak-transition250-diagnostic-v1',request_id=receipt['request_id'],
        **{'from':'NUIAK','to':['joe-big-dog','TVTestRig']},created_at=now.isoformat(),
        expires_at=(now+timedelta(days=7)).isoformat(),state='input_receipt_accepted',
        cleanup=dict(file=offer['file'],sha256=offer['sha256'],state='exact_shared_copy_removed_original_retained'),
        worker='Input verified and preflight started. Training completion is not reported. Keep the existing 3-run assignment unchanged.',
        diagnostic='DTM067 has no identical-frame false changes. Center disturbances still cause abstentions and false changes. DTM054 also fails weaker center disturbances despite better strong-disturbance results.',
        next='Complete the fixed worker batch first. Include multiple disturbance strengths in later regression reports. No new TTR capture is requested.',
        limits='Authored diagnostics only. No real-app claim, threshold change, training-data change, or model promotion.')
    dest=base/'coordination.json';t.h.write(dest,response)
    target='nuiak/responses/nuiak-transition250-diagnostic-v1.json'
    import hashlib
    tx=dict(requestID=response['id'],sharedPath=target,bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
    remote=s.path_under(s.SHARE,target);s.copy_verified(dest,remote,tx);s.verified(remote,tx)
    print('Exact input copy removed; diagnostic published and read back.')


if __name__=='__main__':run()
