"""Compare fixed full-frame and native-region adaptations with old regressions."""
import argparse
import ast
import time
import numpy as np
import transition244 as diagnostic

p=diagnostic.p
n=p.n
h=p.h
OUT=h.ROOT/'reports/work/TRANSITION-245/artifacts'


def sealed(path):
    doc=h.read(path)
    p.review.require(doc['seal']==h.digest({k:v for k,v in doc.items() if k!='seal'}),'invalid_seal')
    return doc


def union_mask(regions,transform,shape=(128,192)):
    mask=np.zeros(shape,dtype=bool)
    for box in regions:mask |= diagnostic.rect(box,transform,shape,1.2)
    p.review.require(mask.any(),'empty_mask')
    return mask


def shifted(mask,dx):
    result=np.zeros_like(mask)
    if dx>0:result[...,dx:]=mask[...,:-dx]
    elif dx<0:result[...,:dx]=mask[...,-dx:]
    else:result[:]=mask
    return result


def reverse(x):return np.concatenate([x[:,3:],x[:,:3]],axis=1)


def prepare():
    old,rows,x=p.load_inputs()
    newer=sealed(diagnostic.c.OUT/'inputs.json')
    admission=h.read(diagnostic.c.OUT/'admission.json')
    p.review.require(admission['approved'] and admission['inputs']==h.ref(diagnostic.c.OUT/'inputs.json'),'admission')
    nx=np.load(h.checked(h.ROOT,newer['tensor'],512*1024**2),allow_pickle=False)
    p.review.require(len(nx)==len(newer['rows']),'tensor_membership')
    rows=rows+newer['rows'];x=np.concatenate([x,nx]);p.check_roles(rows)
    for row,value in zip(rows,x):p.review.require(p.sha(value.tobytes())==row['tensorSHA256'],'tensor_hash')
    prior=sealed(diagnostic.OUT/'result.json')
    p.review.require(prior['inputs']==[h.ref(p.OUT/'inputs.json'),h.ref(diagnostic.c.OUT/'inputs.json')],'diagnostic_inputs')
    supported={r['id'] for r in prior['results']}
    ids=[i for i,r in enumerate(rows) if r['id'] in supported]
    p.review.require(len(ids)==prior['scoredRows']==640,'diagnostic_membership')
    rows=[rows[i] for i in ids];x=x[ids]
    masks=[];metadata={};sizes={};verified=set()
    from PIL import Image
    for row in rows:
        candidates=[];transforms=[]
        for image,meta in zip(row['images'],row['metadata']):
            if meta['sha256'] not in metadata:
                metadata[meta['sha256']]=h.read(h.checked(h.ROOT,meta))
            m=metadata[meta['sha256']]
            scene=next(m[s] for e,s in [('unfocused','baseline_scene'),('focused','focused_scene')]
                       if m[e+'_sha256']==image['sha256'])
            p.label(scene,scene);candidates.append(diagnostic.boxes(scene))
            if image['sha256'] not in verified:
                path=h.checked(h.ROOT,image)
                with Image.open(path) as im:
                    im.load();sizes[image['sha256']]=im.size
                verified.add(image['sha256'])
            width,height=sizes[image['sha256']]
            # Match the existing encoder's rounded letterbox dimensions.
            scale=min(192/width,128/height)
            nw,nh=max(1,round(width*scale)),max(1,round(height*scale))
            transforms.append((nw/width,nh/height,(192-nw)//2,(128-nh)//2))
        p.review.require(transforms[0]==transforms[1],'frame_geometry')
        masks.append(union_mask(diagnostic.common_boxes(*candidates),transforms[0]))
    return rows,x,np.stack(masks),prior


def summaries(probabilities,rows):
    result=p.summaries(probabilities,rows)
    labels=np.array([r['changed'] for r in rows])
    for key in ('content_contrast',):
        for label in (0,1):
            ids=[i for i,r in enumerate(rows) if key in r['conditions'] and r['changed']==label]
            result[f'{key}_{label}']=n.w.summary(probabilities[ids],labels[ids])
    return result


def retained(net,torch,replay,labels,old_x,mask):
    out={}
    for name,values,truth in [('replay',replay,labels),('reversedReplay',reverse(replay),labels)]:
        prob=n.score(net,torch.from_numpy(values))
        out[name]=dict(summary=n.w.summary(prob,truth),probabilities=prob.tolist())
    for mode in ('global8','left8','center8'):
        prob=n.score(net,torch.from_numpy(n.nuisance.localized(old_x[207:],mask[207:],mode)))
        out[mode]=dict(summary=n.w.summary(prob,np.zeros(len(prob))),probabilities=prob.tolist())
    return out


def preservation(baseline,candidate):
    failures=[]
    for name,b in baseline.items():
        if not name.endswith('8'):continue
        bp=p.decisions(np.asarray(b['probabilities']))
        cp=p.decisions(np.asarray(candidate[name]['probabilities']))
        # The reference report already provides truth for replay; pass truth separately below.
        if name.endswith('8'):
            lost=int(((bp==0)&(cp!=0)).sum())
            if lost:failures.append(dict(condition=name,previousCorrectLost=lost))
    return failures


def run(resume=False,experiments=None,linear_only=False,matched_control=None):
    p.review.require((resume and OUT.exists() and not (OUT/'completion.json').exists()) or
                     (not resume and not OUT.exists()),'output_collision')
    started=time.monotonic();rows,x,masks,diagnostic_report=prepare()
    torch=n.d.torch_runtime();torch.set_num_threads(2)
    old_x,_,old_mask,_,_,_,_,_,replay,labels=n.inputs()
    reference=h.read(p.CONTROL/'result.json');checkpoint=h.checked(h.ROOT,reference['model'])
    protocol=h.read(p.CONTROL/'protocol.json')
    p.review.require(p.sha(replay.tobytes())==protocol['trainingSHA256'] and
                     p.sha(labels.tobytes())==protocol['labelsSHA256'],'replay_changed')
    endpoints={p.sha(v.tobytes()) for pair in replay for v in (pair[:3],pair[3:])}
    p.review.require(not any(p.sha(v.tobytes()) in endpoints for i,pair in enumerate(x)
                    if rows[i]['role']!='train' for v in (pair[:3],pair[3:])),'replay_role_overlap')
    state=torch.load(checkpoint,weights_only=True,map_location='cpu')['state']
    net=n.make_model(torch,paired_context=True);net.load_state_dict(state);net.eval()
    baseline=retained(net,torch,replay,labels,old_x,old_mask)
    p.review.require(np.array_equal(np.asarray(baseline['replay']['probabilities'],np.float32),
                     np.asarray(reference['probabilities'],np.float32)),'baseline_parity')
    train=[i for i,r in enumerate(rows) if r['role']=='train']
    p.review.require(len(train)==548,'train_membership')
    native_y=np.array([r['changed'] for r in rows],np.float32)
    OUT.mkdir(parents=True,exist_ok=resume)
    membership=dict(rows=rows,excluded=diagnostic_report['excluded'],
        sourceReport=h.ref(diagnostic.OUT/'result.json'),maskSHA256=p.sha(masks.tobytes()),
        labelsSHA256=p.sha(native_y.tobytes()),independentEvaluation=False)
    if resume:
        prior=sealed(OUT/'membership.json')
        p.review.require({k:v for k,v in prior.items() if k!='seal'}==membership,'resume_membership')
    else:
        h.write(OUT/'membership.json',membership,sealed=True)
        h.write(OUT/'baseline-regression.json',dict(baseline),sealed=True)
    results={}
    for experiment,regional in (experiments or [('DTM063',False),('DTM064',True)]):
        p.review.require(experiment in (h.ROOT/'Research/ExperimentLog.md').read_text(),'unregistered')
        values=x*masks[:,None] if regional else x
        init=n.make_model(torch,paired_context=True);init.load_state_dict(state);init.eval()
        before=n.score(init,torch.from_numpy(values))
        extra=values[train]
        tx=np.concatenate([replay,extra,reverse(extra)])
        ty=np.concatenate([labels,native_y[train],native_y[train]])
        target=OUT/experiment
        recovering=target.exists()
        p.review.require(not recovering or (resume and (target/'last.pt').is_file() and not (target/'result.json').exists()),'run_collision')
        target.mkdir(exist_ok=recovering)
        config=dict(n.CONFIG)
        if linear_only:config['linearOnly']=True
        registration=dict(experiment=experiment,initializer=h.ref(checkpoint),
            source=h.ref(__file__),trainer=h.ref(n.__file__),modelSource=h.ref(h.ROOT/'scripts/focus_temporal_transition.py'),
            configuration=config,membership=h.ref(OUT/'membership.json'),trainingSHA256=p.sha(tx.tobytes()),
            labelsSHA256=p.sha(ty.tobytes()),count=len(tx),representation='nominal_union_120' if regional else 'whole',
            replayRepresentation='unchanged_whole',authority='Standing training; fixed two-run tranche; no wall limit',
            outputCapBytes=2*1024**3,productionEligible=False)
        if matched_control is not None:
            control=sealed(matched_control)
            for key in ('initializer','trainingSHA256','labelsSHA256','count','representation','replayRepresentation'):
                p.review.require(registration[key]==control[key],'unmatched_control')
            p.review.require({k:v for k,v in config.items() if k!='linearOnly'}==control['configuration'],'unmatched_configuration')
            registration['matchedControl']=h.ref(matched_control)
        if recovering:
            previous=sealed(target/'protocol.json')
            for key in registration:
                if key!='source':p.review.require(previous[key]==registration[key],'resume_protocol')
            p.review.require(p.sha((OUT/'execution-source-v1.py').read_bytes())==previous['source']['sha256'],'resume_source')
            saved=torch.load(target/'last.pt',weights_only=True,map_location='cpu')
            p.review.require(saved['protocol']==h.ref(target/'protocol.json'),'resume_checkpoint')
            init.load_state_dict(saved['state']);fitted=init.eval()
            history=[ast.literal_eval(line.split(' ',1)[1]) for line in (OUT.parent/'run.log').read_text().splitlines()
                     if line.startswith(experiment+' {')]
            p.review.require(history and history[-1]['epoch']==config['epochs'],'resume_completion')
            duration=history[-1]['seconds']
            h.write(target/'recovery.json',dict(model=h.ref(target/'last.pt'),source=h.ref(__file__),
                historyScope='Only logged epochs survived. No training repeats.',log=h.ref(OUT.parent/'run.log')),sealed=True)
        else:
            h.write(target/'protocol.json',registration,sealed=True)
            tick=time.monotonic()
            fitted,history=n.fit(init,torch.from_numpy(tx),torch.from_numpy(ty),config,
                               lambda row:print(experiment,row,flush=True))
            duration=time.monotonic()-tick
            h.write(target/'history.json',dict(history=history,trainingSeconds=duration),sealed=True)
            torch.save(dict(version='transition245-v1',state=fitted.state_dict(),protocol=h.ref(target/'protocol.json')),target/'last.pt')
        restored=n.make_model(torch,paired_context=True)
        restored.load_state_dict(torch.load(target/'last.pt',weights_only=True,map_location='cpu')['state']);restored.eval()
        prob=n.score(restored,torch.from_numpy(values))
        p.review.require(np.array_equal(prob,n.score(fitted,torch.from_numpy(values))),'reload_parity')
        frozen_features=all(torch.equal(value,restored.state_dict()[name]) for name,value in state.items()
                            if not name.startswith(('change.8.','change.10.')))
        if linear_only:p.review.require(frozen_features,'feature_weights_changed')
        regression=retained(restored,torch,replay,labels,old_x,old_mask)
        violations=preservation(baseline,regression)
        for name in ('replay','reversedReplay'):
            lost=int(((p.decisions(np.array(baseline[name]['probabilities']))==labels)&
                      (p.decisions(np.array(regression[name]['probabilities']))!=labels)).sum())
            if lost:violations.append(dict(condition=name,previousCorrectLost=lost))
        reverse_prob=n.score(restored,torch.from_numpy(reverse(values)))
        sensitivity={}
        if regional:
            for dx in (-2,2):
                q=n.score(restored,torch.from_numpy(x*shifted(masks,dx)[:,None]))
                sensitivity[str(dx)]=dict(summary=summaries(q,rows),probabilities=q.tolist())
            full=n.score(restored,torch.from_numpy(x))
            sensitivity['without_regions']=dict(summary=summaries(full,rows),probabilities=full.tolist())
        result=dict(experiment=experiment,model=h.ref(target/'last.pt'),summary=summaries(prob,rows),
            probabilities=prob.tolist(),initializerSummary=summaries(before,rows),initializerProbabilities=before.tolist(),
            training=n.w.summary(n.score(restored,torch.from_numpy(tx)),ty),regression=regression,
            reverseSummary=summaries(reverse_prob,rows),reverseProbabilities=reverse_prob.tolist(),
            sensitivity=sensitivity,preservationFailures=violations,history=history,trainingSeconds=duration,
            checkpointParity=True,geometryFrozen=True,frozenFeatures=frozen_features,
            productionEligible=False,independentEvaluation=False)
        h.write(target/'result.json',result,sealed=True)
        results[experiment]=h.ref(target/'result.json')
        print(experiment,'DONE',result['summary'],violations,flush=True)
        del tx,values,extra,fitted,restored,init
    h.write(OUT/'completion.json',dict(results=results,seconds=time.monotonic()-started,productionEligible=False),sealed=True)
    p.review.require(sum(f.stat().st_size for f in OUT.rglob('*') if f.is_file())<2*1024**3,'output_budget')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true',required=True)
    parser.add_argument('--resume-verification',action='store_true')
    args=parser.parse_args();run(args.resume_verification)
