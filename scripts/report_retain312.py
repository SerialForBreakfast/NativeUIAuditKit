"""Compare cached results and score only the new candidate on retained training checks."""
from pathlib import Path
import numpy as np
import retain312 as run
import report291

b=run.b;s=run.s;scale=run.scale


def main():
    out=run.OUT;b.require((out/'completion.json').exists(),'incomplete_run')
    b.require(not (out/'diagnosis.json').exists(),'output_collision')
    registration=b.read(out/'registration.json')
    for key in ('runner','trainer','cropper','viewHelper','scaleHelper','audit','initializer'):b.checked(registration[key])
    membership=b.read(b.PACKAGE/'membership.json')
    old=b.read(scale.OUT/'evaluation.json');new=b.read(out/'evaluation.json')
    summary,cases=report291.summarize_comparison(old,new,membership)
    prior=b.read(scale.OUT/'training-diagnostic.json');audit=b.read(scale.OUT/'scale-audit.json')
    lookup={r['index']:r for r in audit['rows']};results=[]
    s.torch.set_num_threads(2);net=s.load_candidate(out/'last.pt')
    for retained in prior['rows']:
        row=lookup[retained['index']]
        images=[s.image(r['path'],r['sha256']) for r in row['sourceImages']]
        scaled,_=scale.scale_pair(images,row['scale']);scores={}
        for name,frames in [('original',images),('scaled',scaled)]:
            value=s.encoded(*frames,(192,128))[0];detail=scale.detail(value,frames)
            if name=='scaled':
                b.require(b.sha(value.tobytes())==row['tensorSHA256'],'scaled_identity')
                b.require(b.sha(detail.tobytes())==row['detailSHA256'],'detail_identity')
            scores[name]=float(b.worker.score(net,np.concatenate((value,detail))[None])[0])
        results.append(dict(retained,scores=dict(retained['scores'],FOCUS312=scores)))
    totals=[]
    for target in sorted({str(r['targetPixels']) for r in results}):
        rows=[r for r in results if str(r['targetPixels'])==target];labels=np.array([r['changed'] for r in rows])
        for model in ('FOCUS310','FOCUS311','FOCUS312'):
            for view in ('original','scaled'):
                p=np.array([r['scores'][model][view] for r in rows])
                totals.append(dict(target=target,model=model,view=view,summary=b.trainer.w.summary(p,labels),
                    changed=b.trainer.w.summary(p[labels==1],labels[labels==1])))
    b.write(out/'diagnosis.json',dict(runner=b.ref(Path(__file__)),previous=b.ref(scale.OUT/'training-diagnostic.json'),
        comparisonWithFOCUS311=dict(summaries=summary,cases=cases),trainingRows=results,trainingSummaries=totals,
        sourcePinsVerified=True,limitation='Training checks reuse fixed membership. They are not independent accuracy evidence.'))
    for r in totals:
        if r['model']=='FOCUS312':print(r,flush=True)


if __name__=='__main__':main()
