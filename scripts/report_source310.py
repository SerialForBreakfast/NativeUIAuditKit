"""Compare cached decisions and measure the use of original tiny detail."""
from pathlib import Path
import numpy as np
import source310 as run
import report291

base=run.base


def coverage(row):
    result=[]
    for endpoint in row.get('endpoints',[]):
        if endpoint['status']!='measured':continue
        w,h=endpoint['sourceSize'];scale=min(192/w,128/h)
        rw,rh=round(w*scale),round(h*scale);px,py=(192-rw)//2,(128-rh)//2
        x,y,bw,bh=endpoint['visibleBody'];x=x*rw/w+px;y=y*rh/h+py;bw*=rw/w;bh*=rh/h
        left,top,right,bottom=row['window']
        fraction=max(0,min(right,x+bw)-max(left,x))*max(0,min(bottom,y+bh)-max(top,y))/(bw*bh)
        result.append(dict(fraction=float(min(1.,fraction)),centerInside=left<=x+bw/2<=right and top<=y+bh/2<=bottom))
    return result


def main():
    out=run.OUT
    base.require((out/'completion.json').exists(),'incomplete_run')
    reg=base.read(out/'registration.json')
    for key in ('runner','trainer','evaluator','cropper'):base.checked(reg[key])
    membership=base.read(base.checked(reg['membership']))
    paths={
        'DTM078':'CONFLICT-281/DTM078/evaluation.json',
        'DTM081':'TRANSITION-287/DTM081/evaluation.json',
        'DTM083':'TRANSITION-291/DTM083/evaluation.json',
        'DTM085':'TRANSITION-292/DTM085/evaluation.json',
        'FOCUS309':'FOCUS-309/context-detail/evaluation.json',
        'encoded-control':'FOCUS-310/encoded-control/evaluation.json'}
    candidate=base.read(out/'source-detail/evaluation.json')
    comparisons={}
    for name,path in paths.items():
        reference=base.ROOT/'reports/work'/path
        old=base.read(reference)
        summaries,cases=report291.summarize_comparison(old,candidate,membership)
        strength=[]
        for a,b in zip(old['strengths'],candidate['strengths']):
            key=lambda r:(r['condition'],r['strength'],r['order'])
            base.require(key(a)==key(b),'strength_order')
            strength.append(dict(condition=b['condition'],strength=b['strength'],order=b['order'],
                before=a['summary'],after=b['summary'],
                fewerCorrect=b['summary']['correct']<a['summary']['correct']))
        base.require(len(strength)==24,'strength_count')
        comparisons[name]=dict(reference=base.ref(reference),summaries=summaries,cases=cases,
                              strengthSummaries=strength)
    run.torch.set_num_threads(2)
    values,rows,_=run.tiny_rows()
    low,high,_=run.prepare_views(values,rows)
    net=run.load_candidate(out/'source-detail/last.pt')
    source=base.worker.score(net,np.concatenate((values,high),1))
    encoded=base.worker.score(net,np.concatenate((values,low),1))
    tests=[]
    for condition in sorted({r['condition'] for r in rows}):
        ids=[i for i,r in enumerate(rows) if r['condition']==condition]
        labels=np.array([rows[i]['changed'] for i in ids])
        tests.append(dict(condition=condition,originalDetail=base.trainer.w.summary(source[ids],labels),
            encodedDetail=base.trainer.w.summary(encoded[ids],labels),
            originalProbabilities=source[ids].tolist(),encodedProbabilities=encoded[ids].tolist()))
    audit=base.read(out/'size-audit.json')
    thresholds=[4,8,16]
    sizes={}
    window_coverage={}
    for label,records in [('training',audit['rows']),('tiny',base.read(out/'tiny-views.json')['rows'])]:
        known=[e['minimumEncodedSize'] for row in records for e in row.get('endpoints',[]) if e['status']=='measured']
        sizes[label]=dict(measuredEndpoints=len(known),minimum=min(known) if known else None,
            maximum=max(known) if known else None,
            below={str(t):sum(v<t for v in known) for t in thresholds})
        changed=[dict(index=r['index'],id=r.get('id'),endpoints=coverage(r)) for r in records if r.get('changed')]
        window_coverage[label]=dict(changedRows=len(changed),
            anyCenterInside=sum(any(e['centerInside'] for e in r['endpoints']) for r in changed),
            anyHalfBodyInside=sum(any(e['fraction']>=.5 for e in r['endpoints']) for r in changed),
            cases=changed,scope='Geometry is diagnostic only. It does not select model windows.')
    base.write(out/'comparison.json',dict(version='source310-report-v1',runner=base.ref(Path(__file__)),
        registration=base.ref(out/'registration.json'),completion=base.ref(out/'completion.json'),
        sizeAudit=base.ref(out/'size-audit.json'),sizeSupport=sizes,comparisons=comparisons,
        tinyDetailReplacement=tests,windowCoverage=window_coverage,productionEligible=False,finalAudit=False,
        limitations=['Retained reserved cases are regression checks, not untouched final evaluation.',
                    'Encoded-only cases cannot test original-image detail.',
                    'The detail replacement check is diagnostic. It does not select a new model.',
                    'Repeated and reversed rows are not independent trials.']))
    print('Cached comparisons and tiny-detail check complete.',flush=True)


if __name__=='__main__':main()
