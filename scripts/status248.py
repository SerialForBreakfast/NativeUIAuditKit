"""Publish bounded lifecycle feedback and its exact receiver receipt."""
import argparse
from datetime import datetime,timezone,timedelta
import hashlib
import shared_transfer as s
import transition245 as t


def run(publish=False):
    s.mounted();base=s.ROOT/'reports/work/TRANSITION-248/coordination'
    offer=s.document(s.SHARE/'joe-big-dog/joe-big-dog-coord248-lifecycle-result01.json')
    a=offer['review_payload'];path=base/'lifecycle.json'
    tx=dict(bytes=a['bytes'],sha256=a['sha256'],sharedPath=a['file'],requestID=offer['id'])
    s.verified(path,tx)
    now=datetime.now(timezone.utc)
    receipt=dict(schema_version=1,id='nuiak-receipt-coord248-lifecycle-v1',request_id=offer['id'],
        **{'from':'NUIAK','to':'joe-big-dog'},state='copied_and_verified',created_at=now.isoformat(),
        artifact=dict(file=a['file'],verified_bytes=a['bytes'],verified_sha256=a['sha256']),
        intake='Accepted expected metadata states. Live effects remain unqualified. Sender owns exact shared-copy cleanup.')
    response=dict(schema_version=1,id='nuiak-coordination-priorities248-v1',request_id=offer['id'],
        **{'from':'NUIAK','to':['joe-big-dog','TVTestRig']},created_at=now.isoformat(),
        expires_at=(now+timedelta(days=7)).isoformat(),state='review_completed',
        message='NUIAK accepts the lifecycle expected-state mapping. TTR still owns production wire mapping and verification.',
        acknowledgment='Read joe-big-dog-coord249-r2-host-prep01. Its reported 29 checks and 9 tests are not production verification.',
        priorities=['Complete current adapter checks against the existing 10 NUIAK cases.',
                    'Bind transfer receipts to exact receivers and permitted uses.',
                    'Measure one complete batch through pickup, results, review, and cleanup.',
                    'Keep live service deployment separate from model work. No new capture is requested.'],
        constraints=['Verify proof flags independently in production.',
                     'Do not infer deployment permission from this review.',
                     'The absent backup volume blocks the proposed service, not model experiments.'],
        evidence='nuiak/responses/nuiak-coordination-priorities248-v1.md',
        training='NUIAK runs the matched 2-fit sampling comparison locally. No replacement model is offered yet.')
    for name,doc in [('nuiak-receipt-coord248-lifecycle-v1.json',receipt),('nuiak-coordination-priorities248-v1.json',response)]:
        local=base/name
        if not local.exists():t.h.write(local,doc)
    items=[(base/'nuiak-receipt-coord248-lifecycle-v1.json','nuiak-receipt-coord248-lifecycle-v1.json'),
           (base/'nuiak-coordination-priorities248-v1.json','nuiak-coordination-priorities248-v1.json'),
           (base/'priorities.md','nuiak-coordination-priorities248-v1.md')]
    if publish:
        for local,name in items:
            relative='nuiak/responses/'+name
            tx=dict(requestID=response['id'],sharedPath=relative,bytes=local.stat().st_size,
                    sha256=hashlib.sha256(local.read_bytes()).hexdigest())
            dest=s.path_under(s.SHARE,relative);s.copy_verified(local,dest,tx);s.verified(dest,tx)
            print(relative,'published and read back')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');args=p.parse_args();run(args.publish)
