"""Attribute retained nuisance failures without fitting or changing data roles."""
import hashlib
from collections import Counter
import numpy as np
import native_adapt152 as n
from audit_transition119 import endpoint_bank
from diagnose_reflow115 import decisions
h=n.h


def nearest_positive(example,images,labels):
    h.require(images.ndim==4 and example.shape==images.shape[1:] and labels.shape==(len(images),) and
        np.isfinite(images).all() and np.isfinite(example).all() and np.isin(labels,[0,1]).all(),'distance_inputs')
    ids=np.flatnonzero(labels==1);h.require(len(ids)>0,'no_positive')
    best=(float('inf'),-1)
    for chunk in np.array_split(ids,max(1,(len(ids)+15)//16)):
        distances=np.sqrt(np.mean((images[chunk]-example)**2,axis=(1,2,3)))
        for i,value in zip(chunk,distances):best=min(best,(float(value),int(i)))
    return dict(index=best[1],rms=best[0],exactEncodedAlias=best[0]==0)


def run():
    x,y,mask,groups,_,_,_,_,tx,ty=n.inputs()
    parent,source_rows,_,_,_=n.content.a.inputs()
    region=h.read(h.checked(h.ROOT,parent['admission']))['images']
    pairs=[r['images'] for r in source_rows]+[[a,b] for a,b in zip(region,region[1:])]
    bank=endpoint_bank(pairs,x[:207]);by={}
    for entry in bank:
        key=hashlib.sha256(entry['pixels'].tobytes()).hexdigest()
        by.setdefault(key,[]).append(entry)
    reports={};source_refs=[]
    for name,path in [('DTM053','residual154-dtm053-attempt2'),('DTM054','residual158-dtm054')]:
        root=h.ROOT/'NativeUITrainer/focus_ring_runs'/path;r=h.read(root/'result.json');p=h.read(root/'protocol.json')
        h.require(r['seal']==h.digest({k:v for k,v in r.items() if k!='seal'}),'result_seal')
        h.require(p['trainingSHA256']==hashlib.sha256(tx.tobytes()).hexdigest() and
            p['labelsSHA256']==hashlib.sha256(ty.tobytes()).hexdigest(),'membership_binding')
        h.checked(h.ROOT,r['model']);source_refs.append(h.ref(root/'result.json'))
        reports[name]=np.asarray(r['stress']['center8']['probabilities'])
        h.require(reports[name].shape==(226,) and np.isfinite(reports[name]).all(),'score_membership')
    changed=n.nuisance.localized(x[207:],mask[207:],'center8');rows=[];counts=Counter()
    for i in range(226):
        ds={name:int(decisions(p[i:i+1])[0]) for name,p in reports.items()}
        if all(v==0 for v in ds.values()):continue
        origins=by[hashlib.sha256(x[207+i,:3].tobytes()).hexdigest()]
        memberships=sorted({g for entry in origins for j,_ in entry['origins'] for g,ids in groups.items() if j in ids})
        counts.update(memberships)
        rows.append(dict(endpointIndex=i,sourceGroups=memberships,
            sources=[dict(image=e['image'],origins=e['origins']) for e in origins],decisions=ds,
            probabilities={name:float(p[i]) for name,p in reports.items()},
            changedPixelFraction=float(np.any(changed[i,3:]!=x[207+i,3:],axis=0).mean()),
            nearestPositive=nearest_positive(changed[i],tx,ty)))
    false={name:set(np.flatnonzero(decisions(p)==1).tolist()) for name,p in reports.items()}
    doc=dict(version='residual160-attribution-v1',sources=source_refs,rows=rows,sourceGroupCounts=dict(counts),
        sharedFalseChanges=sorted(false['DTM053']&false['DTM054']),
        onlyBalancedFalseChanges=sorted(false['DTM053']-false['DTM054']),
        onlyUniformFalseChanges=sorted(false['DTM054']-false['DTM053']),
        training=False,independentEvaluation=False,localizedDiagnosticTrainingEligible=False,
        limitation='Synthetic content-local photometry, not observed native focus transitions; nearest distance is descriptive, not semantic identity.')
    out=h.ROOT/'reports/work/RESIDUAL-160/artifacts';out.mkdir(parents=True)
    h.write(out/'report.json',doc,sealed=True)
    print({k:v for k,v in doc.items() if k not in ('rows','sources','seal')})


if __name__=='__main__':run()
