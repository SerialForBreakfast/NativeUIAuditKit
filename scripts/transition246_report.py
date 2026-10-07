"""Report the fixed comparison and prepare peer receipts from verified local files."""
from datetime import datetime, timezone
import hashlib
import transition245 as t
import transition245_feedback as f


def run():
    out=t.h.ROOT/'reports/work/TRANSITION-246/artifacts'
    runs={k:t.sealed(t.h.ROOT/f'reports/work/TRANSITION-{packet}/artifacts/{k}/result.json')
          for k,packet in [('DTM063',245),('DTM065',246)]}
    result=f.feedback(t.sealed(out/'membership.json')['rows'],runs,t.sealed(out/'baseline-regression.json'))
    result['comparison']='Same inputs and settings. DTM065 freezes all layers except the final 2 decision layers.'
    result['decision']='Reject DTM065. Artwork errors remain and previous correct decisions regress.'
    result['source']=t.h.ref(__file__)
    t.h.write(out/'feedback.json',result,sealed=True)
    base=t.h.ROOT/'reports/work/STATUS-246'
    offers=[('joe-big-dog-coord246-preparation-result01','joe-big-dog-coord246-v2-preparation01.json'),
            ('joe-big-dog-coord247-v2-journal01','joe-big-dog-coord247-v2-journal-vectors01.json')]
    receipts=[]
    for request,name in offers:
        data=(base/'artifacts'/name).read_bytes()
        receipt=dict(schema_version=1,id='nuiak-receipt-'+request,request_id=request,
                     **{'from':'NUIAK','to':'joe-big-dog'},state='copied_and_verified',
                     created_at=datetime.now(timezone.utc).isoformat(),
                     artifact=dict(file='joe-big-dog/'+name,verified_bytes=len(data),
                                   verified_sha256=hashlib.sha256(data).hexdigest()),
                     intake='Reviewed metadata. No live service qualification. Sender owns exact shared-copy cleanup.')
        path=base/(receipt['id']+'.json');t.h.write(path,receipt);receipts.append(str(path))
    print('\n'.join(receipts))


if __name__=='__main__':run()
