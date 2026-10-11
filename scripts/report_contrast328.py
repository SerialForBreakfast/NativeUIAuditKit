"""Compare retained decisions and diagnose training contrast cases."""
from collections import Counter
import numpy as np
from PIL import Image
import contrast328 as c

b=c.b;r=c.r;t=c.t;OUT=c.OUT


def boundary_audit(reg):
    """Use authored boxes for diagnosis only, never for candidate inputs."""
    rows=b.read(b.checked(reg['corpus']))['rows']['independent']
    selected={tuple(v['cell']) for v in b.read(OUT/'diagnostic.json')['rows']}
    used=set();records=[]
    for row in rows:
        key=(row['sizePixels'],row['widthPixels'],row['contrast'],row['condition'])
        if key not in selected or key in used:continue
        b.require(row['role']=='train','boundary_role')
        used.add(key);frames=[]
        for pin in row['images']:
            with Image.open(b.checked(pin)) as image:frames.append(np.asarray(image.convert('RGB')).astype(np.float32)/255)
        delta=np.abs(frames[1]-frames[0]).mean(2)
        inner=np.zeros(delta.shape,bool);band=np.zeros(delta.shape,bool)
        def fill(mask,box):
            x,y,w,h=box
            x0=max(0,int(np.ceil(x)));y0=max(0,int(np.ceil(y)))
            x1=min(mask.shape[1],int(np.floor(x+w)));y1=min(mask.shape[0],int(np.floor(y+h)))
            if x1>x0 and y1>y0:mask[y0:y1,x0:x1]=True
        for first,second in zip(row['endpoints'][0]['bodyBounds'],row['endpoints'][1]['bodyBounds']):
            x=max(first[0],second[0]);y=max(first[1],second[1])
            right=min(first[0]+first[2],second[0]+second[2]);bottom=min(first[1]+first[3],second[1]+second[3])
            fill(inner,(x,y,max(0,right-x),max(0,bottom-y)))
            x=min(first[0],second[0])-35;y=min(first[1],second[1])-35
            right=max(first[0]+first[2],second[0]+second[2])+35;bottom=max(first[1]+first[3],second[1]+second[3])+35
            fill(band,(x,y,right-x,bottom-y))
        band &= ~inner
        total=float(delta.sum())
        records.append(dict(id=row['id'],group=row['group'],cell=list(key),changed=row['changed'],
            commonBodyMean=float(delta[inner].mean()) if inner.any() else None,
            boundaryBandMean=float(delta[band].mean()) if band.any() else None,
            boundaryFraction=float(delta[band].sum()/total) if total else None))
    return dict(rows=records,oracleOnly=True,bandPixels=35,
        limitation='Authored boxes and 1 artwork family. This is not an image-only detector or native-effect measurement.')


def grouped(rows,labels,probabilities):
    result={}
    for role in sorted({v['role'] for v in rows}):
        ids=[i for i,v in enumerate(rows) if v['role']==role]
        result[role]=dict(rows=len(ids),groups=len({rows[i]['group'] for i in ids}),
            models={name:b.trainer.w.summary(p[ids],labels[ids]) for name,p in probabilities.items()})
    return result


def main():
    t.set_num_threads(2);reg=b.read(OUT/'inputs.json')
    b.checked(reg['control']);b.checked(reg['runner'])
    files={'FOCUS326':b.ROOT/'reports/work/FOCUS-326/independent/run',
           'FOCUS327':b.ROOT/'reports/work/FOCUS-327/run','FOCUS328':OUT/'run'}
    rows=b.read(b.PACKAGE/'membership.json')['rows'];labels=np.array([v['changed'] for v in rows])
    docs={name:b.read(path/'evaluation.json') for name,path in files.items()}
    probabilities={name:np.array(doc['conditions']['native.npy']['probabilities']) for name,doc in docs.items()}
    train=[i for i,v in enumerate(rows) if v['role']=='train' and 'content_contrast' in v['conditions']]
    contrast={name:b.trainer.w.summary(p[train],labels[train]) for name,p in probabilities.items()}
    contrast_by_label={str(label):{name:b.trainer.w.summary(p[[i for i in train if labels[i]==label]],
        labels[[i for i in train if labels[i]==label]]) for name,p in probabilities.items()} for label in (0,1)}
    conditions={key:{name:doc['conditions'][key]['summary'] for name,doc in docs.items()} for key in docs['FOCUS328']['conditions']}
    raw=np.load(b.PACKAGE/'native.npy',allow_pickle=False,mmap_mode='r')
    old=r.load_candidate(b.checked(reg['control']));new=c.load_candidate(OUT/'run/last.pt')
    # Score only training rows. These values cannot select the completed checkpoint.
    detail_cases=[]
    for start in range(0,len(train),8):
        ids=train[start:start+8];x=np.array(raw[ids]);selected=[rows[i] for i in ids]
        d,_=r.prepare(x,selected,2);inputs=t.from_numpy(np.concatenate((x,d),1))
        with t.inference_mode():
            whole=old.change.whole(r.s.c.model.change_inputs(None,inputs[:,:6])).flatten()
            before=old.change(inputs).flatten();after=new.change(inputs).flatten()
            signals=[c.signals(inputs[:,6:12]),c.signals(c.normalize(inputs[:,6:12]))]
        for j,i in enumerate(ids):
            detail_cases.append(dict(index=i,id=rows[i]['id'],group=rows[i]['group'],role=rows[i]['role'],changed=int(labels[i]),
                whole=float(whole[j]),oldCorrection=float(before[j]-whole[j]),newCorrection=float(after[j]-whole[j]),
                signals={name:{k:float(v[j]) for k,v in signal.items()} for name,signal in zip(('raw','normalized'),signals)}))
    result=b.read(OUT/'report.json');changes=result['comparisons']['FOCUS327']['cases']
    native=[v for v in changes if v['input']=='native.npy']
    counterfactual=b.read(OUT/'diagnostic.json')['rows'];factor={}
    for condition in ('movement','artwork-only','identical'):
        values=[v for v in counterfactual if v['cell'][3]==condition]
        factor[condition]=dict(rows=len(values),rawFeatureShift=float(np.mean([v['rawFeatureShift'] for v in values])),
            normalizedFeatureShift=float(np.mean([v['normalizedFeatureShift'] for v in values])))
    authored_labels=np.array([v['changed'] for v in b.read(b.checked(reg['corpus']))['rows']['independent']])
    authored={name:b.trainer.w.summary(np.array(b.read(path/'training.json')['probabilities'][240:]),authored_labels)
              for name,path in files.items()}
    b.write(OUT/'comparison.json',dict(inputs=b.ref(OUT/'inputs.json'),roles=grouped(rows,labels,probabilities),
        authored=authored,conditions=conditions,trainingContentContrast=contrast,trainingContrastByLabel=contrast_by_label,trainingContrastCases=detail_cases,
        lostGroups=dict(Counter(v['group'] for v in native if v['lostCorrect'])),
        gainedGroups=dict(Counter(v['group'] for v in native if v['gainedCorrect'])),counterfactualByCondition=factor,
        diagnosticCaveat='The fixed central contrast change covers the full crop content but only part of a full-frame fallback. It is not always global.',
        nativeCaveat='Content contrast pairs can replace artwork and background. They are not solely affine brightness changes.',
        comparisons=result['comparisons'],authoredBoundary=boundary_audit(reg),productionEligible=False))
    print('Training content contrast',contrast,flush=True)
    print('Roles',grouped(rows,labels,probabilities),flush=True)


if __name__=='__main__':main()
