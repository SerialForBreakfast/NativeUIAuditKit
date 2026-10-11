"""Test training-only scene scales with the existing context/detail model."""
import argparse
from collections import Counter,defaultdict
from pathlib import Path
import time
import numpy as np
from PIL import Image
import source310 as s
import report291

base=s.base
torch=s.torch
OUT=base.ROOT/'reports/work/FOCUS-311'
TARGETS=(None,3.,6.,12.)


def target(row):
    base.require(row['role']=='train','training_role')
    key='|'.join(sorted(r['sha256'] for r in row['images']))
    return TARGETS[int(base.sha(key.encode())[:8],16)%len(TARGETS)]


def scale_pair(images,factor):
    base.require(images[0].size==images[1].size and np.isfinite(factor) and 0<factor<=1,'scale_inputs')
    w,h=images[0].size;nw,nh=max(1,round(w*factor)),max(1,round(h*factor))
    result=[]
    for image in images:
        canvas=Image.new('RGB',(w,h))
        canvas.paste(image.resize((nw,nh),Image.Resampling.BILINEAR),((w-nw)//2,(h-nh)//2))
        result.append(canvas)
    return result,(nw/w,nh/h)


def detail(value,images):
    if np.array_equal(value[:3],value[3:]):return value.copy()
    x,y=s.boxes(torch.from_numpy(value[None]))[0]
    return s.crop_pair(images,[x,y,x+32,y+32],preserve_padding=True)


def prepare_training(values,rows,weights,protected):
    details=np.empty_like(values);records=[];totals=defaultdict(float);counts=Counter()
    for i,row in enumerate(rows):
        if row is None:
            details[i]=s.enlarged(torch.from_numpy(values[i:i+1])).numpy()[0]
            counts['encoded_only']+=1;continue
        base.require(row['role']=='train' and row['group'] not in protected['groups'],'protected_group')
        images=[s.image(r['path'],r['sha256']) for r in row['images']]
        original=s.encoded(*images,(192,128))[0]
        base.require(np.array_equal(original,values[i]),'source_encoding_parity')
        endpoints=s.measured(row,images)
        base.require(len(endpoints)==2 and all(e['status']=='measured' for e in endpoints),'measured_training_size')
        minimum=min(e['minimumEncodedSize'] for e in endpoints)
        selected=target(row);factor=1. if selected is None else selected/minimum
        transformed,ratios=scale_pair(images,factor)
        value=s.encoded(*transformed,(192,128))[0]
        base.require(not row['changed'] or np.any(value[:3]!=value[3:]),'collapsed_change')
        base.require(all(base.sha(v.tobytes()) not in protected['frames'] for v in (value[:3],value[3:])),
                     'protected_frame_overlap')
        values[i]=value;details[i]=detail(value,transformed)
        sizes=[min(e['encodedSize'][0]*ratios[0],e['encodedSize'][1]*ratios[1]) for e in endpoints]
        name='original' if selected is None else str(int(selected))
        counts[name]+=1;totals[name]+=float(weights[i])
        records.append(dict(index=i,id=row.get('id'),group=row['group'],role='training-derived',
            domain='authored_scene_scale',sourceImages=row['images'],changed=row['changed'],
            targetPixels=selected,scale=factor,actualRatios=ratios,encodedBodyMinimums=sizes,
            weight=float(weights[i]),tensorSHA256=base.sha(value.tobytes()),
            detailSHA256=base.sha(details[i].tobytes()),
            labelAuthority='Inherited observed identity; both frames receive the same geometric transform.'))
        if i%200==0:print('Prepared scale rows',i,'/',len(rows),flush=True)
    return details,dict(rows=records,counts=dict(counts),weights=dict(totals),
        limitation='Whole scenes shrink on a black canvas. This is not a native renderer or an isolated control-size intervention.')


def report(out,membership):
    candidate=base.read(out/'evaluation.json');comparisons={}
    paths={'DTM085':'TRANSITION-292/DTM085/evaluation.json',
           'FOCUS309':'FOCUS-309/context-detail/evaluation.json',
           'FOCUS310':'FOCUS-310/source-detail/evaluation.json'}
    for name,path in paths.items():
        ref=base.ROOT/'reports/work'/path;old=base.read(ref)
        summaries,cases=report291.summarize_comparison(old,candidate,membership)
        strengths=[]
        for a,b in zip(old['strengths'],candidate['strengths']):
            base.require(all(a[k]==b[k] for k in ('condition','strength','order')),'strength_order')
            strengths.append(dict(condition=b['condition'],strength=b['strength'],order=b['order'],
                before=a['summary'],after=b['summary'],fewerCorrect=b['summary']['correct']<a['summary']['correct']))
        comparisons[name]=dict(reference=base.ref(ref),summaries=summaries,cases=cases,strengths=strengths)
    base.write(out/'comparison.json',dict(comparisons=comparisons,productionEligible=False,finalAudit=False))


def run():
    base.require(not OUT.exists(),'output_collision');torch.set_num_threads(2);started=time.monotonic()
    manifest,membership,full,labels,weights,extra,controls,_,reg=s.c.prepare()
    added=s.previous.prior.mix(full[controls],extra,labels[1660:1740],True)
    values=np.concatenate((full,added,base.reporting.reverse(added)));del full,extra,added
    parent=base.read(s.OUT/'registration.json')
    base.require(base.sha(values.tobytes())==parent['trainingSHA256'],'original_schedule')
    for name,value in [('labels',labels),('weights',weights)]:
        base.require(base.sha(value.tobytes())==parent[name+'SHA256'],name+'_identity')
    initializer=base.checked(parent['initializer']);rows=s.schedule_rows(membership,reg,labels)
    native=np.load(base.PACKAGE/'native.npy',allow_pickle=False)
    tiny,trows,tpin=s.tiny_rows()
    protected=dict(groups={r['group'] for r in membership['rows'] if r['role']!='train'},
        frames={base.sha(v.tobytes()) for i,r in enumerate(membership['rows']) if r['role']!='train'
                for v in (native[i,:3],native[i,3:])})
    protected['frames'].update(base.sha(v.tobytes()) for pair in tiny for v in (pair[:3],pair[3:]))
    OUT.mkdir(parents=True)
    config=dict(parent['configuration'])
    base.write(OUT/'registration.json',dict(version='scale311-v1',runner=base.ref(Path(__file__)),
        trainer=base.ref(Path(base.trainer.__file__)),viewHelper=base.ref(Path(s.__file__)),
        cropper=base.ref(base.ROOT/'scripts/detail307.py'),evaluator=base.ref(Path(base.__file__)),
        parent=base.ref(s.OUT/'registration.json'),initializer=base.ref(initializer),configuration=config,
        originalTrainingSHA256=parent['trainingSHA256'],labelsSHA256=parent['labelsSHA256'],
        weightsSHA256=parent['weightsSHA256'],targets=list(TARGETS),membership=base.ref(base.PACKAGE/'membership.json'),
        hypothesis='Training views near 3, 6, and 12 pixels improve tiny native changes.',
        control='Reuse FOCUS310 source-detail. Initialization, architecture, updates, labels, weights, and evaluation remain fixed.',
        selection='Canonical image hashes assign scale without using the changed label.',
        admission='Training-only authored derivatives inherit observed endpoint identity and ancestry. No evaluation role changes.',
        thresholds=[.15,.85],outputCapBytes=128*1024**2,workingMemoryCapGiB=8,wallTimeLimit=None,
        acceptance='Improve tiny changes with no lost previous correct decisions. No threshold or checkpoint tuning.',
        productionEligible=False))
    details,audit=prepare_training(values,rows,weights,protected)
    base.write(OUT/'scale-audit.json',audit)
    base.write(OUT/'inputs.json',dict(trainingSHA256=base.sha(values.tobytes()),detailSHA256=base.sha(details.tobytes()),
        labelsSHA256=base.sha(labels.tobytes()),weightsSHA256=base.sha(weights.tobytes()),rows=len(values),
        protectedOverlap=False,trainingOnly=True))
    _,native_high,_=s.prepare_views(native,membership['rows'])
    base.require(base.sha(native_high.tobytes())==base.read(s.OUT/'native-views.json')['sha256'],'native_evaluation_identity')
    _,tiny_high,_=s.prepare_views(tiny,trows)
    base.require(base.sha(tiny_high.tobytes())==base.read(s.OUT/'tiny-views.json')['sha256'],'tiny_evaluation_identity')
    torch.manual_seed(42);net=s.extend(s.c.model.load_candidate(initializer))
    baseline=s.c.model.load_candidate(initializer)
    sanity=np.concatenate((values[:8],details[:8]),1)
    base.require(np.max(np.abs(base.worker.score(net,sanity)-base.worker.score(baseline,values[:8])))<=1e-6,'initial_parity')
    def progress(row):
        base.write(OUT/f"epoch-{row['epoch']:04d}.json",row);print('scale-candidate',row,flush=True)
    begin=time.monotonic()
    net,history=base.trainer.fit(net,torch.from_numpy(values),torch.from_numpy(labels),config,progress,
                               torch.from_numpy(weights),detail_inputs=torch.from_numpy(details))
    torch.save(dict(state=net.state_dict(),representation=s.VERSION,registration=base.ref(OUT/'registration.json')),OUT/'last.pt')
    restored=s.load_candidate(OUT/'last.pt')
    base.require(np.array_equal(base.worker.score(net,sanity),base.worker.score(restored,sanity)),'reload_parity')
    base.write(OUT/'fit.json',dict(history=history,seconds=time.monotonic()-begin,checkpointParity=True,
        model=base.ref(OUT/'last.pt'),parameters=sum(p.numel() for p in net.parameters())))
    del values,details
    def transform(key,x):
        if key=='native.npy':return np.concatenate((x,native_high),1)
        if key=='reverse_native.npy':return np.concatenate((x,base.reporting.reverse(native_high)),1)
        return x
    evaluation=base.evaluate_full(restored,{'DTM085':baseline},manifest,input_transform=transform)
    base.write(OUT/'evaluation.json',evaluation)
    scores=base.worker.score(restored,np.concatenate((tiny,tiny_high),1));results=[]
    for condition in sorted({r['condition'] for r in trows}):
        ids=[i for i,r in enumerate(trows) if r['condition']==condition]
        results.append(dict(condition=condition,summary=base.trainer.w.summary(scores[ids],
            np.array([trows[i]['changed'] for i in ids])),probabilities=scores[ids].tolist()))
    base.write(OUT/'tiny.json',dict(input=tpin,results=results,finalAudit=False))
    report(OUT,membership)
    size=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file());base.require(size<128*1024**2,'output_cap')
    base.write(OUT/'completion.json',dict(seconds=time.monotonic()-started,outputBytes=size,
        regressionPassed=evaluation['regressionPassed'],productionEligible=False,rolesChanged=False))
    print('Scale comparison complete.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',required=True,action='store_true')
    parser.parse_args();run()
