"""Native26 matched representation experiment, dispatched by the existing trainer.

Reuses the existing MobileNet prefix/tail and weighted gradient implementation.
Evaluation is performed once, after a fixed final checkpoint; it never selects weights.
"""
import argparse
from datetime import datetime, timezone
import json
import os
import platform
import resource
import time
from pathlib import Path

import native_focus_spike as n

VERSION='native-focus-spike-model-v1'
ARMS={'native26-normalized':'fdr035-native26-normalized',
      'native26-common':'fdr036-native26-common'}
BASE=n.ROOT/'reports/work/FOCUS-CAMPAIGN-09/artifacts/protocol/artwork-added-partial/protocol.json'
AUTHORITY=n.ROOT/'Research/Plans/NativeFocusEffectSpike26.md'
BASELINE=n.ROOT/'NativeUITrainer/focus_ring_runs/fdr021-reviewed-contrast/weights/best.pt'
CONFIG=dict(epochs=1000,batch=32,lr=.001,seed=42,maxSeconds=300,
    model='mobilenet_v3_small_partial_visual',augmentation='none',testDuringTraining=False)


def remaining(deadline):
    seconds=deadline-time.time()
    n.require(seconds>0,'model_tranche_wall_budget_exhausted')
    return seconds


def validate_samples(rows,plan,arm):
    expected={r['caseID']:r for r in plan['members']}
    n.require(len(rows)==2500 and len({r['id'] for r in rows})==2500 and
        len(expected)==1250 and {r['caseID'] for r in rows}==set(expected),'arm_membership')
    seen={};pixels={}
    for row in rows:
        source=expected[row['caseID']]
        n.require(row['role']==source['role'] and row['configurationGroup']==source['configurationGroup']
            and row['arm']==arm.split('-')[-1] and type(row['label']) is int and row['label'] in (0,1),
            'arm_split_or_label')
        seen.setdefault(row['caseID'],[]).append(row['label'])
        pixels.setdefault(row['sha256'],set()).add((row['role'],row['label']))
    n.require(all(sorted(v)==[0,1] for v in seen.values()) and
        sum(r['role']=='train' for r in rows)==2000,'arm_pair_balance')
    n.require(all(len(v)==1 for v in pixels.values()),'ambiguous_crop_pixels_or_split_overlap')


def local_ref(path):
    path=Path(path).resolve();n.require(path.is_relative_to(n.ROOT),'metadata_root')
    return dict(path=str(path.relative_to(n.ROOT)),sha256=n.sha(path))


def metric(rows,scores,threshold):
    n.require(len(rows)==len(scores),'score_count')
    pairs={};tp=tn=fp=fn=0
    for row,p in zip(rows,scores):
        n.require(isinstance(p,(int,float)) and 0<=p<=1,'invalid_probability')
        y=row['label'];positive=p>=threshold
        tp+=int(y==1 and positive);fn+=int(y==1 and not positive)
        fp+=int(y==0 and positive);tn+=int(y==0 and not positive)
        pairs.setdefault(row['caseID'],[]).append(positive==bool(y))
    n.require(all(len(v)==2 for v in pairs.values()),'incomplete_scored_pair')
    return dict(threshold=threshold,tp=tp,tn=tn,fp=fp,fn=fn,controls=len(rows),
        accuracy=(tp+tn)/len(rows),bothCorrectPairs=sum(all(v) for v in pairs.values()),pairs=len(pairs))


def encode(plan_path,batch_root,output):
    """Explicit new-prefix encoding, bounded to 300 seconds per representation."""
    import numpy as np
    import torch
    from PIL import Image, ImageStat
    import focus_visual_experiment as visual
    from focus_pretrained_experiment import state_digest
    execution_deadline=time.time()+1800
    n.mounted();n.require(output.is_relative_to(n.ROOT) and not output.exists(),'encoding_output_collision')
    plan=json.loads(plan_path.read_text());expected={r['caseID']:r for r in plan['members']}
    accepted=[];cropdocs=[];source_evidence=[]
    for index in range(50):
        p=batch_root/f'chunk-{index:03d}/accepted.json'
        n.require(p.is_file(),'capture_incomplete')
        doc=json.loads(p.read_text());accepted+=doc['rows'];source_evidence.append(local_ref(p))
        source_evidence.extend(local_ref(p.parent/name) for name in doc.get('receipts',['receipt.json']))
        dest=n.USB/f'crops20-chunk-{index:03d}'
        if not (dest/'crops.json').exists():n.render(doc['rows'],dest)
        cropdocs.append(json.loads((dest/'crops.json').read_text()))
    n.require(len(accepted)==1250 and {r['caseID'] for r in accepted}==set(expected),'corpus_membership')
    for r in accepted:
        remaining(execution_deadline)
        n.require(r['sourceRole']==plan['sourceRole']=='calibration','unexpected_producer_data_role')
        n.require(all(r[k]==v for k,v in expected[r['caseID']].items()),'changed_membership')
        bundle=Path(r['frames'][0]['path']).parent
        n.require(bundle.resolve().is_relative_to(n.USB),'source_outside_usb')
        n.require(n.inspect(bundle,expected[r['caseID']])==r,'changed_native_evidence')
    n.require(not any(d['exceptions'] for d in cropdocs),'crop_exceptions_require_diagnosis')
    records=[dict(id=k,**r) for d in cropdocs for k,r in d['records'].items()]
    n.require(len(records)==5000 and len({r['id'] for r in records})==5000,'crop_membership')
    by_case={r['caseID']:r for r in accepted}
    luminance={}
    for key,row in by_case.items():
        frame=row['frames'][0];x,y,w,h=frame['bounds']
        with Image.open(frame['path']) as im:
            means=ImageStat.Stat(im.convert('RGB').crop((x+.1*w,y+.1*h,x+.9*w,y+.9*h))).mean
        luminance[key]=sum(a*b for a,b in zip(means,[.2126,.7152,.0722]))/255
    import focus_runtime
    n.require(all(d['runtime']==focus_runtime.identity() for d in cropdocs),'crop_runtime_changed')
    for r in records:
        source=by_case[r['caseID']];frame=source['frames'][r['label']]
        bounds=frame['bounds'] if r['arm']=='normalized' else n.common_window(source['frames'][0]['bounds'])
        n.require(r['arm'] in ('normalized','common') and r['label'] in (0,1) and
            r['role']==source['role'] and r['sourceSHA256']==frame['sha256'] and
            r['bounds']==bounds and not r['reasons'],'crop_source_binding')
        x,y,w,h=bounds;actual=[x-.16*w,y-.16*h,w*1.32,h*1.32];W,H=frame['size']
        n.require(actual[0]>=0 and actual[1]>=0 and actual[0]+actual[2]<=W and
            actual[1]+actual[3]<=H and not any(n.overlap(actual,b)>0 for eid,b in
                frame['allBounds'].items() if eid!=source['target']),'crop_context_clipped_or_neighbor')
        r['artworkLuminance']=luminance[r['caseID']]
        r['artworkLumaGroup']='dark' if r['artworkLuminance']<=.35 else 'light' if r['artworkLuminance']>=.65 else 'mid'
    base=json.loads(BASE.read_text());representation=base['representation']
    # Retained development/retention are evaluation-only. Bind the existing
    # cache, membership and scorer before any new candidate exists.
    retained=[r for r in base['samples'] if r['split']=='validation']
    n.require(len(retained)==333 and sum(r['use']=='retention-validation' for r in retained)==18,
        'retained_membership')
    for ref in base['features'].values():n.require(n.sha(n.ROOT/ref['path'])==ref['sha256'],'retained_cache_changed')
    for row in retained:n.require(n.sha(n.ROOT/row['crop']['path'])==row['crop']['sha256'],'retained_crop_changed')
    n.require(torch.backends.mps.is_available(),'mps_unavailable')
    output.mkdir(parents=True);start=time.monotonic()
    prefix=visual.make_network(representation).features[:9].eval().to('mps')
    for p in prefix.parameters():p.requires_grad_(False)
    identity=state_digest(prefix)
    norm=representation['normalization'];mean=torch.tensor(norm['mean'],device='mps')[None,:,None,None]
    std=torch.tensor(norm['std'],device='mps')[None,:,None,None]
    for arm in ARMS:
        short=arm.split('-')[-1]
        rows=sorted((r for r in records if r['arm']==short),
                    key=lambda r:(r['role']!='train',r['caseID'],r['label']))
        validate_samples(rows,plan,arm)
        for r in rows:n.require(n.sha(r['path'])==r['sha256'],'crop_changed')
        tick=time.monotonic();values=[];decode_seconds=accelerator_seconds=0
        for offset in range(0,len(rows),32):
            remaining(execution_deadline)
            n.require(time.monotonic()-tick<300,'encoding_time_cap')
            io_tick=time.monotonic();ims=[]
            for r in rows[offset:offset+32]:
                with Image.open(r['path']) as im:
                    n.require(im.size==(256,256),'crop_dimensions')
                    ims.append(torch.from_numpy(np.array(im.convert('RGB'),copy=True)).permute(2,0,1))
            decode_seconds+=time.monotonic()-io_tick;compute_tick=time.monotonic()
            x=torch.stack(ims).to('mps').float()/255
            with torch.no_grad():f=prefix((x-mean)/std).cpu()
            torch.mps.synchronize();accelerator_seconds+=time.monotonic()-compute_tick
            n.require(f.shape[1:]==(48,16,16) and bool(torch.isfinite(f).all()),'prefix_shape')
            values.append(torch.cat((f,torch.ones(len(ims),1,16,16)),1).unsqueeze(1))
        features=torch.cat(values)
        n.require(state_digest(prefix)==identity and features.numel()*4<512*1024**2,'encoder_identity_or_budget')
        cache=n.USB/f'{ARMS[arm]}-features.pt';n.require(not cache.exists(),'feature_cache_collision')
        write_tick=time.monotonic()
        torch.save(dict(features=features,ids=[r['id'] for r in rows]),cache)
        cache_digest=n.sha(cache);write_seconds=time.monotonic()-write_tick
        p=dict(version=VERSION,arm=arm,name=ARMS[arm],configuration=CONFIG,
            executionDeadlineUnix=execution_deadline,
            plan=local_ref(plan_path),authority=local_ref(AUTHORITY),samples=rows,
            sourceEvidence=source_evidence,
            baseline=local_ref(BASELINE),
            retainedProtocol=local_ref(BASE),
            representation=representation,cache=dict(path=str(cache),sha256=cache_digest),
            prefixSHA256=identity,encodingSeconds=time.monotonic()-tick,
            encodingTiming=dict(imageReadDecodeSeconds=decode_seconds,
                acceleratorAndTransferSeconds=accelerator_seconds,cacheWriteHashSeconds=write_seconds),
            environment=dict(packages=visual.packages(),platform=platform.platform(),device='mps',
                pid=os.getpid(),peakResidentBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
            code=[local_ref(n.ROOT/'scripts'/name) for name in
                ('native_focus_spike.py','native_focus_spike_model.py','focus_visual_experiment.py',
                 'focus_full_fit_experiment.py','train_focus_ring_detector.py',
                 'focus_pretrained_experiment.py','focus_learning_experiment.py',
                 'focus_representative_experiment.py','focus_representative_validation.py')],
            scope='synthetic-native-effect-input-comparison',releaseEligible=False)
        from focus_dataset_contract import digest
        p['protocolSHA256']=digest(p)
        n.write(output/f'{arm}.json',p)
        n.write(output/f'{arm}-approval.json',dict(approved=True,protocolSHA256=p['protocolSHA256'],
            authority=p['authority'],scope=p['scope'],arm=arm,name=p['name']))
        print(arm,p['protocolSHA256'],p['encodingSeconds'],flush=True)
    n.write(output/'encoding-summary.json',dict(seconds=time.monotonic()-start,arms=list(ARMS),
        trainPairs=1000,evaluationPairs=250,backbonePrefixUnchanged=True))


def load_protocol(path,arm,name,approval_path=None):
    from focus_dataset_contract import digest
    path=Path(path);p=json.loads(path.read_text())
    n.require(p['version']==VERSION and p['arm']==arm and ARMS.get(arm)==name and
        p['configuration']==CONFIG and p['protocolSHA256']==digest({k:v for k,v in p.items() if k!='protocolSHA256'}),
        'native26_protocol')
    n.mounted()
    for r in [p['plan'],p['authority'],p['baseline'],p['retainedProtocol'],*p['code'],*p['sourceEvidence']]:
        n.require(n.sha(n.ROOT/r['path'])==r['sha256'],'changed_protocol_dependency')
    validate_samples(p['samples'],json.loads((n.ROOT/p['plan']['path']).read_text()),arm)
    n.require(Path(p['cache']['path']).parent==n.USB and n.sha(p['cache']['path'])==p['cache']['sha256'],
              'changed_cache')
    for row in p['samples']:
        n.require(Path(row['path']).resolve().is_relative_to(n.USB) and
            n.sha(row['path'])==row['sha256'],'changed_training_crop')
    n.require(not (n.ROOT/'NativeUITrainer/focus_ring_runs'/name).exists(),'run_exists')
    ar=None
    if approval_path:
        a=json.loads(Path(approval_path).read_text())
        n.require(a==dict(approved=True,protocolSHA256=p['protocolSHA256'],authority=p['authority'],
            scope=p['scope'],arm=arm,name=name),'approval_mismatch')
        ar=local_ref(approval_path)
    return dict(formatVersion='focus-representative-preflight-v1',protocolVersion=VERSION,
        protocolFile=local_ref(path),protocolSHA256=p['protocolSHA256'],configuration=CONFIG,
        approval=ar,launchEligible=ar is not None,blockers=[] if ar else ['missing_approval'],
        native26=p,releaseEligible=False),p['samples']


def run(report,experiment_id):
    import torch
    import focus_visual_experiment as visual
    from focus_full_fit_experiment import weighted_backward
    from focus_pretrained_experiment import state_digest
    p=report['native26'];remaining(p['executionDeadlineUnix'])
    n.mounted();n.require(torch.backends.mps.is_available(),'mps_unavailable')
    out=n.ROOT/'NativeUITrainer/focus_ring_runs'/p['name'];out.mkdir();(out/'weights').mkdir()
    n.write(out/'execution.json',dict(experimentID=experiment_id,pid=os.getpid(),
        startedAt=datetime.now(timezone.utc).isoformat(),protocolSHA256=p['protocolSHA256'],
        wallDeadlineUnix=p['executionDeadlineUnix'],configuration=CONFIG))
    started=time.monotonic();torch.manual_seed(42)
    model=visual.make_model(p['representation'],'visual-local-partial','mps')
    data=torch.load(p['cache']['path'],map_location='cpu',weights_only=True)
    rows=p['samples'];n.require(data['ids']==[r['id'] for r in rows],'cache_order')
    x=data['features'];n.require(x.shape==(2500,1,49,16,16) and x.dtype==torch.float32 and
        bool(torch.isfinite(x).all()),'cache_dimensions')
    y=torch.tensor([r['label'] for r in rows],dtype=torch.float32).reshape(-1,1)
    train_indices=[i for i,r in enumerate(rows) if r['role']=='train']
    eval_indices=[i for i,r in enumerate(rows) if r['role']=='evaluation']
    n.require(len(train_indices)==2000 and len(eval_indices)==500,'training_counts')
    opt=torch.optim.AdamW(model.optimizer_groups(.001,.0001),weight_decay=.01)
    rng=torch.Generator().manual_seed(42);losses=[];training_start=time.monotonic()
    deadline=training_start+min(300,remaining(p['executionDeadlineUnix']))
    initial_state=state_digest(model)
    weights=torch.full((32,1),1/32,device='mps')
    for step in range(1000):
        if time.monotonic()>=deadline:break
        ids=torch.randint(0,len(train_indices),(32,),generator=rng)
        ids=torch.tensor([train_indices[i] for i in ids.tolist()])
        model.train();opt.zero_grad()
        loss=weighted_backward(model,x[ids].to('mps'),y[ids].to('mps'),weights,32,deadline)
        if loss is None:break
        opt.step();losses.append(loss)
        if (step+1)%100==0:print(p['name'],'updates',step+1,'loss',loss,flush=True)
    torch.mps.synchronize();train_seconds=time.monotonic()-training_start
    n.require(bool(losses),'no_training_updates')
    torch.save(dict(state_dict=model.state_dict(),protocolSHA256=p['protocolSHA256'],
        experimentID=experiment_id,updates=len(losses),checkpointKind='native26-final-diagnostic'),out/'weights/final.pt')
    model.eval();scores=[];tick=time.monotonic()
    with torch.no_grad():
        for offset in range(0,len(eval_indices),32):
            remaining(p['executionDeadlineUnix'])
            ids=eval_indices[offset:offset+32]
            scores+=torch.sigmoid(model(x[ids].to('mps'))).flatten().cpu().tolist()
    evaluated=[rows[i] for i in eval_indices]
    eval_seconds=time.monotonic()-tick
    fit_scores=[];fit_tick=time.monotonic()
    with torch.no_grad():
        for offset in range(0,len(train_indices),32):
            remaining(p['executionDeadlineUnix'])
            ids=train_indices[offset:offset+32]
            fit_scores+=torch.sigmoid(model(x[ids].to('mps'))).flatten().cpu().tolist()
    fit_rows=[rows[i] for i in train_indices]
    strata={}
    for field in ('background','artworkLumaGroup'):
        for value in sorted({r[field] for r in evaluated}):
            chosen=[i for i,r in enumerate(evaluated) if r[field]==value]
            strata[field+':'+value]=metric([evaluated[i] for i in chosen],[scores[i] for i in chosen],.85)
    result=dict(experimentID=experiment_id,protocolSHA256=p['protocolSHA256'],updates=len(losses),
        trainingSeconds=train_seconds,evaluationSeconds=eval_seconds,
        trainingFitSeconds=time.monotonic()-fit_tick,
        trainingFit=dict(at05=metric(fit_rows,fit_scores,.5),at085=metric(fit_rows,fit_scores,.85)),
        preparationSeconds=training_start-started,pid=os.getpid(),initialStateSHA256=initial_state,
        peakResidentBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        selection='fixed final checkpoint; no evaluation during training',
        at05=metric(evaluated,scores,.5),at085=metric(evaluated,scores,.85),strata=strata,
        predictions=[dict(id=r['id'],label=r['label'],probability=s) for r,s in zip(evaluated,scores)],
        losses=losses,releaseEligible=False,modelSHA256=state_digest(model))
    n.write(out/'result.json',result)
    if p['arm']=='native26-normalized':
        checkpoint=torch.load(n.ROOT/p['baseline']['path'],map_location='cpu',weights_only=True)
        head=torch.nn.Linear(576,1).to('mps');head.load_state_dict(checkpoint['state_dict'],strict=True)
        tail=visual.make_network(p['representation']).features[9:].eval().to('mps')
        baseline_scores=[];tick=time.monotonic()
        with torch.no_grad():
            for offset in range(0,len(eval_indices),32):
                remaining(p['executionDeadlineUnix'])
                ids=eval_indices[offset:offset+32]
                f=tail(x[ids,0,:-1].to('mps')).mean((-2,-1))
                baseline_scores+=torch.sigmoid(head(f)).flatten().cpu().tolist()
        n.write(out/'baseline.json',dict(checkpoint=p['baseline'],seconds=time.monotonic()-tick,
            at05=metric(evaluated,baseline_scores,.5),at085=metric(evaluated,baseline_scores,.85),
            scope='FDR021 on the same 500 normalized synthetic evaluation crops',
            predictions=[dict(id=r['id'],label=r['label'],probability=s) for r,s in zip(evaluated,baseline_scores)]))
        retained_replay(p,model,head,tail,out)
    print(json.dumps({k:result[k] for k in ('updates','trainingSeconds','at05','at085')}))
    return 0


def retained_replay(p,model,head,tail,out):
    import torch
    from focus_context_experiment import tensor_digest
    from focus_representative_experiment import selection_metrics
    tick=time.monotonic();ref=p['retainedProtocol']
    n.require(n.sha(n.ROOT/ref['path'])==ref['sha256'],'retained_protocol_changed')
    base=json.loads((n.ROOT/ref['path']).read_text())
    n.require(base['representation']==p['representation'],'retained_representation')
    for r in base['features'].values():n.require(n.sha(n.ROOT/r['path'])==r['sha256'],'retained_feature_changed')
    receipt=json.loads((n.ROOT/base['features']['receipt']['path']).read_text())
    data=torch.load(n.ROOT/base['features']['cache']['path'],map_location='cpu',weights_only=True)
    n.require(data['receipt']==receipt and receipt['prefixSHA256']==p['prefixSHA256'] and
        receipt['ids']==[r['id'] for r in base['samples']] and
        tensor_digest(data['features'])==receipt['featureSHA256'],'retained_feature_binding')
    ids=[i for i,r in enumerate(base['samples']) if r['split']=='validation']
    rows=[base['samples'][i] for i in ids]
    n.require(len(rows)==333 and sum(r['use']=='retention-validation' for r in rows)==18,'retained_count')
    for r in rows:n.require(n.sha(n.ROOT/r['crop']['path'])==r['crop']['sha256'],'retained_crop_changed')
    scores=[];old_scores=[];model.eval()
    with torch.no_grad():
        for offset in range(0,len(ids),32):
            remaining(p['executionDeadlineUnix'])
            z=data['features'][ids[offset:offset+32]].to('mps')
            scores+=torch.sigmoid(model(z)).flatten().cpu().tolist()
            old_scores+=torch.sigmoid(head(tail(z[:,0,:-1]).mean((-2,-1)))).flatten().cpu().tolist()
    def summary(values):
        predictions=[dict(id=r['id'],label=r['label'],probability=s) for r,s in zip(rows,values)]
        return dict(predictions=predictions,metrics=selection_metrics(predictions,rows,base['selection']))
    n.write(out/'retained-replay.json',dict(protocol=ref,seconds=time.monotonic()-tick,
        candidate=summary(scores),baseline=summary(old_scores),
        scope='unchanged repeated development/retention; not an independent final test',
        commonArmUnavailable='no before/reference boxes for compatible common-window inputs'))


def main():
    p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--batch',required=True)
    p.add_argument('--output',required=True);a=p.parse_args()
    encode(Path(a.plan),Path(a.batch),Path(a.output).resolve())


if __name__=='__main__':main()
