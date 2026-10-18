"""Test source gamma augmentation against an equal-budget retained control."""
import gc
import time
from pathlib import Path
import numpy as np
import followup347 as f

q=f.q;a=f.a;t=a.t
OUT=None
BASE=q.ROOT/'reports/work/FOCUS-348'


def emit(step,completed,total):
    q.save(OUT.parent/'progress.json',dict(step=step,completed=completed,total=total,updatedAt=time.time()),replace=True)
    print(step,completed,total,flush=True)


def check_inputs(config):
    for ref in config['inputs']:
        q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'input_changed')


def raw_logits(net,x,d):
    result=[]
    with t.inference_mode():
        for i in range(0,len(x),8):
            result.append(net.change(t.from_numpy(np.concatenate((x[i:i+8],d[i:i+8]),1))).flatten())
    return t.cat(result)


def training():
    start=time.monotonic();config=q.load(OUT/'config.json');check_inputs(config);t.set_num_threads(2)
    q.require(config['arm'] in ('control','gamma'),'arm')
    reg=q.load(a.e.OUT/'inputs.json');reg['trainer']=a.b.ref(Path(a.b.trainer.__file__))
    a.e.f.OUT=OUT
    emit('Verify original training views',0,10)
    x,d,y,w,aux,ad,ay,indices=a.e.f.prepare(reg)
    rows=q.load(OUT/'preparation.json')['rows']
    q.require(all(row['role']=='train' for row in rows),'training_role')
    net=a.e.load_candidate(a.e.OUT/'run/last.pt')
    original=raw_logits(net,x,d);aux_original=raw_logits(net,aux,ad)
    # Both arms retain every original view in the primary loss.
    # Only the auxiliary images differ between arms.
    if config['arm']=='gamma':
        changed=0
        for i in range(0,len(rows),8):
            v,n=f.source_views(rows[i:i+8],'08-gamma');changed+=n
            aux[i:i+len(v)]=v[:,:6].numpy();ad[i:i+len(v)]=v[:,6:].numpy()
            emit('Prepare source gamma views',i+len(v),len(rows))
        q.save(OUT/'augmentation.json',dict(gamma=1.5,changedProposalPairs=changed,
            auxiliarySHA256=a.e.f.digest(aux),detailSHA256=a.e.f.digest(ad),rolesChanged=False))
    initial={k:v.clone() for k,v in net.state_dict().items()}
    settings=dict(reg['configuration'],epochs=10,seed=42,threads=2)
    def progress(row):
        q.save(OUT/f"epoch-{row['epoch']:04d}.json",row)
        emit('Train '+config['arm'],row['epoch'],10)
    net,history=a.b.trainer.fit(net,t.from_numpy(x),t.from_numpy(y),settings,progress,
        weights=t.from_numpy(w),detail_inputs=t.from_numpy(d),auxiliary_inputs=t.from_numpy(aux),
        auxiliary_detail=t.from_numpy(ad),auxiliary_indices=t.from_numpy(indices),auxiliary_weight=.25,
        preservation_logits=original,auxiliary_preservation_logits=aux_original,preservation_weight=1.)
    changed=[k for k,v in net.state_dict().items() if not t.equal(v,initial[k])]
    q.require(changed and all(k.startswith(('change.detail.','change.correction.')) for k in changed),'changed_scope')
    t.save(dict(state=net.state_dict(),representation=a.e.VERSION,windows=2),OUT/'last.pt')
    restored=a.e.load_candidate(OUT/'last.pt')
    sample=np.concatenate((x[:8],d[:8]),1)
    q.require(np.array_equal(a.b.worker.score(net,sample),a.b.worker.score(restored,sample)),'reload_parity')
    q.save(OUT/'fit.json',dict(history=history,configuration=settings,changedTensors=changed,
        seconds=time.monotonic()-start,originalViews=len(x),auxiliaryViews=len(aux),
        checkpointParity=True,productionEligible=False,model=f.pin(OUT/'last.pt')))
    emit('Training complete; evaluation required',10,10)


def diagnostic():
    start=time.monotonic();config=q.load(OUT/'config.json');check_inputs(config);t.set_num_threads(2)
    manifest=q.load(q.ROOT/config['manifest']['path'])
    models={name:a.e.load_candidate(q.ROOT/ref['path']) for name,ref in config['models'].items()}
    records={}
    if config['kind']=='regression':
        membership=q.load(a.b.PACKAGE/'membership.json')
        old=q.load(a.e.OUT/'run/evaluation.json')['conditions']
        for name in config['sets']:
            data=np.load(a.b.PACKAGE/name,allow_pickle=False,mmap_mode='r')
            labels=([r['changed'] for r in membership['rows']] if 'native' in name else
                    membership['replayLabels'] if 'replay' in name else [0]*len(data))
            rows=[dict(id=name+':'+str(i),changed=int(y),sourceDomain='retained-regression',condition=name,
                group=membership['rows'][i]['group'] if 'native' in name else 'ancestry-unavailable',
                role='retained-evaluation') for i,y in enumerate(labels)]
            predictions={k:[] for k in models}
            for i in range(0,len(data),8):
                x=np.array(data[i:i+8])
                if 'native' in name:
                    forward=np.concatenate((x[:,3:],x[:,:3]),1) if name.startswith('reverse_') else x
                    d,_=a.r.prepare(forward,membership['rows'][i:i+len(x)],2)
                    if name.startswith('reverse_'):d=a.r.reverse_details(d)
                else:d=a.r.encoded_details(t.from_numpy(x),2).numpy()
                tensor=np.concatenate((x,d),1)
                for key,net in models.items():predictions[key].extend(a.b.worker.score(net,tensor).tolist())
                emit(name,i+len(x),len(data))
            records[name]=report(rows,predictions,old[name]['probabilities'])
    else:
        predictions={k:[] for k in models};original=[]
        for chunk in manifest['chunks']:
            with np.load(q.ROOT/chunk['path'],allow_pickle=False) as data:
                tensor=t.from_numpy(data['tensor']);original.extend(data['probabilities'].tolist())
            startrow=len(predictions['control'])
            for i in range(0,len(tensor),8):
                x=tensor[i:i+8]
                if config['scope']=='source-reselect':
                    x,_=f.source_views(manifest['rows'][startrow+i:startrow+i+len(x)],config['factor'])
                elif config['scope']!='original':x=f.alter(x,f.masks(x),config['factor'],config['scope'])
                for key,net in models.items():
                    with t.inference_mode():predictions[key].extend(t.sigmoid(net.change(x)).flatten().tolist())
            emit(config['scope'],len(predictions['control']),len(manifest['rows']))
        records['appearance']=report(manifest['rows'],predictions,original)
    q.save(OUT/'comparison.json',dict(version='appearance348-v1',configuration=config,sets=records,
        seconds=time.monotonic()-start,productionEligible=False,
        limitations=['Inspected development cases are not final evaluation.',
            'Native app/build matching remains unresolved. No native development images enter training.',
            'Related cases are not independent trials. Theme and archetype coverage remains incomplete.']))


def report(rows,predictions,original):
    return dict(rows=rows,probabilities=predictions,originalProbabilities=original,
        againstOriginal={k:f.prior.count(rows,p,original) for k,p in predictions.items()},
        gammaAgainstControl=f.prior.count(rows,predictions['gamma'],predictions['control']))


def register(training_jobs=False):
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS348';folder.mkdir(exist_ok=True)
    manifest=f.pin(f.prior.BASE/'inputs.json');data=q.load(f.prior.BASE/'inputs.json')
    refs=[manifest,data['model']]+data['chunks']+[f.pin(q.ROOT/p) for p in
        ['scripts/appearance348.py','scripts/followup347.py','scripts/reserve346.py',
         'scripts/native_adapt152.py','scripts/filters327.py','scripts/edge329.py','scripts/regions313.py']]
    membership=[f.pin(q.ROOT/p) for p in ['reports/work/TRANSITION-249/artifacts/package/membership.json',
        'reports/work/FOCUS-326/corpus.json','reports/work/FOCUS-319/corpus.json']]
    if training_jobs:
        jobs=[('00-'+arm,dict(arm=arm),refs+membership) for arm in ('control','gamma')]
    else:
        models={name:f.pin(q.QUEUE/'jobs'/('focus348-00-'+name)/'attempts/1/out/last.pt') for name in ('control','gamma')}
        for name in models:q.require(q.load(q.QUEUE/'jobs'/('focus348-00-'+name)/'attempts/1/result.json')['status']=='complete','incomplete_training')
        refs+=list(models.values())
        jobs=[('01-original',dict(kind='appearance',scope='original',models=models),refs)]
        for i,(name,sets) in enumerate(f.REGRESSIONS):
            jobs.append((f'{i+2:02d}-regression-'+name,dict(kind='regression',sets=sets,models=models),
                refs+[f.pin(a.b.PACKAGE/p) for p in sets+['membership.json']]+[f.pin(a.e.OUT/'run/evaluation.json')]))
        for i,(factor,scope) in enumerate((x,y) for x in f.FACTORS for y in f.SCOPES):
            jobs.append((f'{i+7:02d}-'+factor[3:]+'-'+scope,dict(kind='appearance',factor=factor,scope=scope,models=models),refs))
    for suffix,settings,inputs in jobs:
        identity='focus348-'+suffix;config=folder/(identity+'-config.json')
        q.save(config,dict(settings,manifest=manifest,inputs=inputs))
        spec=dict(version=q.SPEC_VERSION,id=identity,task='FOCUS348',owner='Maximum-mini-NUIAK',
            kind='confirm' if training_jobs else 'screen',authority='training' if training_jobs else 'diagnostic',
            hypothesis='Source gamma augmentation reduces measured appearance errors with original-view replay.',
            decisionRule='Compare equal-budget arms. Require target gains and no lost original or retained successes. Keep thresholds 0.15/0.85.',
            inputs=inputs,stage=[{'from':f.pin(config),'to':'config.json'}],
            adapter=dict(type='python-callable',steps=['appearance348.'+('training' if training_jobs else 'diagnostic')],
                         outputAttributes=['appearance348.OUT']),
            limits=dict(timeoutSeconds=1800 if training_jobs else 800,maxOutputBytes=2*1024**3 if training_jobs else 100_000_000,maxAttempts=1))
        if training_jobs:spec['training']=dict(experimentLogRunId='FOCUS348',membership=membership,
            initialization=data['model'],epochs=10,storageBudgetBytes=2*1024**3,
            acceptanceEvidence='Original crop parity, unchanged frozen weights, reload parity, and all retained comparisons.',resume='restart')
        path=folder/(identity+'.json');q.save(path,spec);print(identity,q.submit(path),flush=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['register-training','register-evaluation'])
    register(parser.parse_args().action=='register-training')
