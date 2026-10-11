"""Keep original training views and add one bounded scale objective."""
from pathlib import Path
import time
import numpy as np
import effect312 as audit
import scale311 as scale

s=scale.s;b=s.base;torch=s.torch;OUT=audit.OUT


def run():
    b.require((OUT/'effect-audit.json').is_file(),'audit_missing')
    b.require(not (OUT/'registration.json').exists(),'output_collision')
    torch.set_num_threads(2);start=time.monotonic()
    manifest,membership,full,labels,weights,extra,controls,_,reg=s.c.prepare()
    added=s.previous.prior.mix(full[controls],extra,labels[1660:1740],True)
    values=np.concatenate((full,added,b.reporting.reverse(added)));del full,added,extra
    parent=b.read(s.OUT/'registration.json')
    for key,value in [('training',values),('labels',labels),('weights',weights)]:
        b.require(b.sha(value.tobytes())==parent[key+'SHA256'],'original_'+key)
    initializer=b.checked(parent['initializer']);rows=s.schedule_rows(membership,reg,labels)
    config=dict(parent['configuration'])
    b.write(OUT/'registration.json',dict(version='retain312-v1',runner=b.ref(Path(__file__)),
        trainer=b.ref(Path(b.trainer.__file__)),cropper=b.ref(b.ROOT/'scripts/detail307.py'),
        viewHelper=b.ref(Path(s.__file__)),scaleHelper=b.ref(Path(scale.__file__)),
        audit=b.ref(OUT/'effect-audit.json'),initializer=b.ref(initializer),configuration=config,
        trainingSHA256=parent['trainingSHA256'],labelsSHA256=parent['labelsSHA256'],weightsSHA256=parent['weightsSHA256'],
        hypothesis='Retaining original views reduces losses while the scale objective teaches small changes.',
        control='Cached FOCUS310 source-detail; same initializer, architecture, labels, weights, updates, and evaluation.',
        auxiliaryWeight=.25,objective='Original weighted BCE plus 0.25 times scaled weighted BCE in each optimizer step.',
        exposure=dict(originalPerEpoch=1820,auxiliaryPerEpoch=1820,updatesPerEpoch=114,epochs=30,
                      totalUpdates=3420,originalCoefficient=1.,auxiliaryCoefficient=.25),
        limits=dict(threads=2,memoryGiB=8,outputMiB=128,wallTime=None),
        acceptance='Improve tiny changed decisions without lost previous correct decisions at thresholds 0.15/0.85.',
        rolesChanged=False,productionEligible=False))
    low,original_detail,_=s.prepare_views(values,rows);del low
    b.require(b.sha(original_detail.tobytes())==b.read(s.OUT/'views.json')['sourceSHA256'],'original_detail')
    native=np.load(b.PACKAGE/'native.npy',allow_pickle=False);tiny,trows,tpin=s.tiny_rows()
    protected=dict(groups={r['group'] for r in membership['rows'] if r['role']!='train'},
        frames={b.sha(v.tobytes()) for i,r in enumerate(membership['rows']) if r['role']!='train'
                for v in (native[i,:3],native[i,3:])})
    protected['frames'].update(b.sha(v.tobytes()) for pair in tiny for v in (pair[:3],pair[3:]))
    auxiliary=values.copy();aux_detail,records=scale.prepare_training(auxiliary,rows,weights,protected)
    previous=b.read(scale.OUT/'inputs.json')
    b.require(b.sha(auxiliary.tobytes())==previous['trainingSHA256'],'scaled_input')
    b.require(b.sha(aux_detail.tobytes())==previous['detailSHA256'],'scaled_detail')
    b.require(b.sha(values.tobytes())==parent['trainingSHA256'],'original_preserved')
    b.write(OUT/'inputs.json',dict(originalSHA256=parent['trainingSHA256'],
        originalDetailSHA256=b.sha(original_detail.tobytes()),auxiliary=previous,
        scaleCounts=records['counts'],scaleWeights=records['weights'],
        originalWeightSum=float(weights.sum()),auxiliaryWeightSum=float(weights.sum())*.25,
        note='Each original label, group, and condition keeps its coefficient. Auxiliary totals add 25% uniformly.'))
    del records
    low,native_detail,_=s.prepare_views(native,membership['rows']);del low
    low,tiny_detail,_=s.prepare_views(tiny,trows);del low
    for name,value in [('native',native_detail),('tiny',tiny_detail)]:
        b.require(b.sha(value.tobytes())==b.read(s.OUT/(name+'-views.json'))['sha256'],'evaluation_identity')
    torch.manual_seed(42);net=s.extend(s.c.model.load_candidate(initializer));baseline=s.c.model.load_candidate(initializer)
    sanity=np.concatenate((values[:8],original_detail[:8]),1)
    b.require(np.max(np.abs(b.worker.score(net,sanity)-b.worker.score(baseline,values[:8])))<=1e-6,'initial_parity')
    def progress(row):
        b.write(OUT/f"epoch-{row['epoch']:04d}.json",row);print('retained-original',row,flush=True)
    begin=time.monotonic()
    net,history=b.trainer.fit(net,torch.from_numpy(values),torch.from_numpy(labels),config,progress,
        torch.from_numpy(weights),detail_inputs=torch.from_numpy(original_detail),
        auxiliary_inputs=torch.from_numpy(auxiliary),auxiliary_detail=torch.from_numpy(aux_detail),auxiliary_weight=.25)
    torch.save(dict(state=net.state_dict(),representation=s.VERSION,registration=b.ref(OUT/'registration.json')),OUT/'last.pt')
    restored=s.load_candidate(OUT/'last.pt')
    b.require(np.array_equal(b.worker.score(net,sanity),b.worker.score(restored,sanity)),'reload_parity')
    b.require(sum(r['updates'] for r in history)==3420,'update_budget')
    b.write(OUT/'fit.json',dict(history=history,seconds=time.monotonic()-begin,checkpointParity=True,
                              model=b.ref(OUT/'last.pt')))
    del values,original_detail,auxiliary,aux_detail
    def transform(key,x):
        if key=='native.npy':return np.concatenate((x,native_detail),1)
        if key=='reverse_native.npy':return np.concatenate((x,b.reporting.reverse(native_detail)),1)
        return x
    evaluation=b.evaluate_full(restored,{'DTM085':baseline},manifest,input_transform=transform)
    b.write(OUT/'evaluation.json',evaluation)
    scores=b.worker.score(restored,np.concatenate((tiny,tiny_detail),1));results=[]
    for condition in sorted({r['condition'] for r in trows}):
        ids=[i for i,r in enumerate(trows) if r['condition']==condition]
        results.append(dict(condition=condition,summary=b.trainer.w.summary(scores[ids],
            np.array([trows[i]['changed'] for i in ids])),probabilities=scores[ids].tolist()))
    b.write(OUT/'tiny.json',dict(input=tpin,results=results,finalAudit=False));scale.report(OUT,membership)
    size=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file());b.require(size<128*1024**2,'output_cap')
    b.write(OUT/'completion.json',dict(seconds=time.monotonic()-start,outputBytes=size,
        regressionPassed=evaluation['regressionPassed'],productionEligible=False,rolesChanged=False))
    print('Original-view retention comparison complete.',flush=True)


if __name__=='__main__':run()
