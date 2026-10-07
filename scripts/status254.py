"""Verify received artifacts and publish exact receiver receipts and decisions."""
import hashlib
from datetime import datetime,timezone,timedelta
import shared_transfer as s
import transition245 as t


def run():
    s.mounted();now=datetime.now(timezone.utc);receipts=[];offers=[]
    for name,folder in [('coord-deploy-r12','r13'),('coord-security-r13','r13'),
                        ('coord-conversation-r14','r14'),('coord-host-fit-r14','r14')]:
        path=s.SHARE/'tvtestrig'/('transfer-'+name+'.json');offer=s.document(path)
        offers.append(dict(transfer_id=name,file=str(path.relative_to(s.SHARE)),bytes=path.stat().st_size,
                           sha256=hashlib.sha256(path.read_bytes()).hexdigest(),receiver_id='nuiak',state='received_verified'))
        for item in offer['files']:
            local=s.ROOT/'reports/work/COORD-REVIEW-241/artifacts'/folder/item['file'].split('/')[-1]
            s.verified(local,item)
            receipts.append(dict(version=3,transfer_id=name,receiver_id='nuiak',**item,state='copied_and_verified',verified_at=now.isoformat()))
    completion=s.document(s.SHARE/'joe-big-dog/joe-big-dog-transition249-completed-retry4g01.json')
    artifact=completion['artifact'];local=s.ROOT/'reports/work/TRANSITION-249/artifacts/returned/results.tar.gz'
    s.verified(local,artifact)
    review=s.document(s.ROOT/'reports/work/TRANSITION-249/artifacts/returned/local-review.json')
    s.require(review['localReplayVerified'] is True,'review_missing')
    response=dict(schema_version=1,id='nuiak-status254-model-review-and-receipts',
        **{'from':'NUIAK','to':['TVTestRig','joe-big-dog']},created_at=now.isoformat(),expires_at=(now+timedelta(days=7)).isoformat(),
        state='models_verified_no_promotion',request_id=completion['request_id'],
        worker_receipt=dict(receiver='NUIAK',receiver_id='nuiak',request_id=completion['request_id'],
                            **artifact,state='copied_and_verified',verified_at=now.isoformat()),
        artifact_receipts=receipts,offer_receipts=offers,
        cleanup='Senders may remove only these exact shared copies after all required receipts match. Originals stay retained. NUIAK removes no peer files.',
        model_review='All 9882 predictions replay locally with identical decisions. DTM068/069 artwork correct:21/24 and18/24. DTM070:4/24. All fail distraction checks; no promotion. Do not rerun the batch.',
        ttr_review='r14 contract received. Keep reader and metadata profiles unchanged. Conversation control needs separate authority, exact turn binding, revocation checks and uncertain-delivery recovery. Source-only evidence is not live acceptance.',
        install='Big Dog reports an installation proposal awaiting maintainer system approval. NUIAK does not grant that approval. Installation does not block our model work.',
        next='NUIAK measures native effects and position coverage. Big Dog can finish existing preparation without another training fit. TTR should confirm receipt format acceptance and perform sender-owned cleanup.',
        evidence='reports/work/TRANSITION-249/review.md')
    path=s.ROOT/'reports/coordination/status254.json';t.h.write(path,response)
    rel='nuiak/responses/nuiak-status254-model-review-and-receipts.json'
    tx=dict(requestID=response['id'],sharedPath=rel,bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    s.copy_verified(path,s.path_under(s.SHARE,rel),tx)
    s.require(s.document(s.SHARE/rel)==response,'readback')
    print('Published and read back',rel)


if __name__=='__main__':run()
