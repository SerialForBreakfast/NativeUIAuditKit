"""Source-bound admitted-role adapter to the existing spatial cache and trainer."""
import argparse
import hashlib
import os
from pathlib import Path
import time
import numpy as np
import train_spatial135 as t

c, d, h = t.c, t.d, t.h
ADMISSION = h.ROOT/'reports/work/ADMISSION-136/admission.json'
ADMISSION_SHA = '4c37065854bd7b0ba76cd83aa0203b3536f2b179cc82116852843e20bef29a37'
PARENT = h.ROOT/'reports/work/SPATIAL-135/artifacts/ready/protocol.json'
BASE = h.ROOT/'NativeUITrainer/focus_ring_runs/spatial135-dtm036/result.json'


def reviewed_indices(admission, peer):
    h.require(admission['version']=='retained-change-admission-v1' and
              admission['decision']=='approved_for_next_pinned_change_only_development_fit' and
              admission['effectiveRole']=='train' and admission['independentEvaluationEligible'] is False and
              admission['bodyGeometryEligible'] is False, 'admission_scope')
    ids = [v['id'] for v in peer]
    h.require(len(ids)==len(set(ids))==11, 'peer_identity')
    seen, families = set(), {'within_screen':[], 'screen_transition':[], 'identical_control':[]}
    labels = {}
    for row in admission['pairs']+admission['excluded']:
        source = admission['sourceBundles'][row['source']]
        key = f"{source['operation']}:{row['before']}:{row['after']}"
        h.require(key in ids and key not in seen, 'admission_membership')
        seen.add(key)
        index=ids.index(key)
        if 'changed' not in row:
            h.require(peer[index]['nativeHint'] is None, 'excluded_hint')
            continue
        h.require(type(row['changed']) is bool and peer[index]['nativeHint'] is row['changed'], 'label_conflict')
        family=row['family']
        if family=='within_screen_with_content_change':family='within_screen'
        h.require(family in families and (family=='identical_control') is (not row['changed']), 'family_label')
        families[family].append(index);labels[index]=float(row['changed'])
    h.require(seen==set(ids) and len(labels)==9 and
              [len(families[k]) for k in families]==[5,2,2], 'admission_coverage')
    # Exactly equal family means with the existing unweighted feature trainer.
    order=sum([families[k]*(10//len(families[k])) for k in families], [])
    return order, np.asarray([labels[i] for i in order],dtype=np.float32), families


def load():
    h.require(hashlib.sha256(ADMISSION.read_bytes()).hexdigest()==ADMISSION_SHA, 'admission_changed')
    admission=c.transfer.document(ADMISSION)
    for name,source in admission['sourceBundles'].items():
        manifest=h.ROOT/source['manifest'];root=manifest.parent
        h.require(hashlib.sha256(manifest.read_bytes()).hexdigest()==source['manifestSHA256'], 'manifest_changed')
        request=root/'transition/request.template.json'
        h.require(hashlib.sha256(request.read_bytes()).hexdigest()==source['requestSHA256'], 'request_changed')
        for ref in c.transfer.document(manifest)['files']:
            c.transfer.verified(c.transfer.path_under(root,ref['path']),ref)
        records={r['sequence']:r for r in c.transfer.document(root/'survey.json')['records']}
        for row in [v for v in admission['pairs'] if v['source']==name]:
            b,a=records[row['before']],records[row['after']];actions=a['preceding_inputs']
            h.require(len(actions)==1 and b['native_bracket_agrees'] and a['native_bracket_agrees'] and
                      b['capture_completed_monotonic_ns']<actions[0]['invoked_monotonic_ns']<=
                      actions[0]['returned_monotonic_ns']<a['capture_started_monotonic_ns'], 'interval_binding')
            h.require((b['image_sha256']==a['image_sha256']) is (not row['changed']), 'identity_label')
    p=c.audit.sealed(PARENT)
    for key in ('source','trainer','constraint','scaler','model'):h.checked(h.ROOT,p[key])
    peer=c.peer_inputs()  # Revalidates every byte and exact encoded input, never model-derived labels.
    h.require([r[2] for r in peer]==p['peer'], 'peer_cache_binding')
    order,y,families=reviewed_indices(admission,p['peer'])
    prior=c.audit.sealed(BASE)
    torch=d.a.r.d.torch_runtime();torch.set_num_threads(2)
    saved=torch.load(h.checked(h.ROOT,prior['model']),weights_only=True,map_location='cpu')
    h.require(saved['version']=='spatial135-dual-v1' and saved['configuration']['representation']=='spatial', 'initializer')
    scale=saved['scale'].numpy();net=d.model();net.change.linear.weight.data.copy_(saved['weights']);net.eval()
    cache={};reference={}
    with torch.inference_mode():
        for name,arms in p['cache'].items():
            raw=np.load(h.checked(h.ROOT,arms['spatial']),allow_pickle=False)
            f=c.scaled(raw,scale)
            logits=net.change(torch.from_numpy(f)).flatten()
            probabilities=(logits.sigmoid().numpy() if name=='peer' else d.probabilities(logits))
            expected=([r['probability'] for r in prior['records'][name]] if name=='peer'
                      else prior['records'][name]['probabilities'])
            h.require(np.array_equal(probabilities,np.asarray(expected,dtype=np.float32)), 'initializer_replay')
            f[:,0]=logits.numpy();cache[name]=f;reference[name]=probabilities
    h.require(cache['peer'].shape==(11,1153) and cache['original'].shape==(433,1153), 'feature_membership')
    return p,cache,reference,order,y,families,prior


def pins():
    return dict(source=h.ref(__file__),admission=h.ref(ADMISSION),parent=h.ref(PARENT),baseline=h.ref(BASE),
                trainer=h.ref(d.a.r.d.__file__),constraint=h.ref(t.retention.__file__))


def configuration():
    config=dict(d.CONFIG,initializer='DTM036-plus-zero-correction',lossWeighting='equal-three-family-means',batch=30)
    config.pop('originalGroupCount',None);config.pop('derivedGroupCount',None)
    h.require(config['epochs']==600 and config['lr']==.01 and config['seed']==42 and config['threads']==2,'config')
    return config


def prepare(ready):
    out=h.fresh(ready);p,cache,reference,order,y,families,prior=load()
    config=configuration()
    out.mkdir(parents=True)
    h.write(out/'protocol.json',dict(version='retained137-v1',pins=pins(),configuration=config,
        order=order,labels=y.tolist(),families=families,uniquePairs=9,weightedRows=30,
        featureSHA256={k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in cache.items()},
        sourceModel=prior['model'],independentEvaluation=False,productionEligible=False),sealed=True)
    print('Prepared9unique/30weighted rows; all frozen cache and source checks pass',flush=True)


def train(ready):
    started=time.monotonic();protocol=c.audit.sealed(ready/'protocol.json')
    h.require(protocol['pins']==pins() and protocol['configuration']==configuration() and 'Run DTM037 — RETAINED-ADAPT-137' in
              (h.ROOT/'Research/ExperimentLog.md').read_text(),'unlogged_or_changed')
    p,cache,reference,order,y,families,prior=load()
    h.require(protocol['order']==order and protocol['labels']==y.tolist() and protocol['families']==families and
              protocol['featureSHA256']=={k:hashlib.sha256(v.tobytes()).hexdigest() for k,v in cache.items()},'prepared_changed')
    labels=np.asarray(p['labels'],dtype=np.float32)
    net=t.retention.constrained_model(cache['original'][:207],labels[:207])
    torch=d.a.r.d.torch_runtime();out=d.a.r.d.old.fresh_run('retained137-dtm037');out.mkdir(parents=True)
    h.write(out/'execution.json',dict(experiment='DTM037',pid=os.getpid(),protocol=h.ref(ready/'protocol.json'),
        authority='Standing training and explicit ADMISSION136 role overlay',status='started'),sealed=True)
    tick=time.monotonic()
    net,history=d.a.r.d.fit_change_features(net,torch.from_numpy(cache['peer'][order]),torch.from_numpy(y),protocol['configuration'])
    fit=time.monotonic()-tick
    with torch.no_grad():weight,radius=net.change.effective();weight=weight.detach().clone()
    torch.save(dict(version='retained137-v1',correction=weight,baseline=prior['model'],
                    configuration=protocol['configuration'],protocol=h.ref(ready/'protocol.json')),out/'last.pt')
    saved=torch.load(out/'last.pt',weights_only=True,map_location='cpu')
    replay=d.model();replay.change.linear.weight.data.copy_(saved['correction']);records={}
    with torch.inference_mode():
        for name,f in cache.items():
            tx=torch.from_numpy(f);logits=net.change(tx)
            probs=(logits.sigmoid().flatten().numpy() if name=='peer' else d.probabilities(logits))
            again=(replay.change(tx).sigmoid().flatten().numpy() if name=='peer' else d.probabilities(replay.change(tx)))
            h.require(np.array_equal(probs,again),'checkpoint_replay')
            if name=='peer':
                records[name]=[dict(v,probability=float(q),decision=c.decision(float(q))) for v,q in zip(p['peer'],probs)]
            else:records[name]=dict(probabilities=probs.tolist(),summary=d.q.summarize(probs,labels,p['groups'],reference[name]))
    retention=all(v['correct']==v['count'] for v in records['original']['summary'].values())
    h.require(np.array_equal(np.asarray(records['original']['probabilities'],dtype=np.float32)[207:],reference['original'][207:]),'identity_changed')
    peer_probs=np.asarray([r['probability'] for r in records['peer']]);summaries={}
    for family,ids in families.items():
        truth=np.zeros(len(ids),dtype=int) if family=='identical_control' else np.ones(len(ids),dtype=int)
        decisions=d.q.decisions(peer_probs[ids]);summaries[family]=dict(count=len(ids),correct=int((decisions==truth).sum()),abstentions=int((decisions==-1).sum()))
    h.write(out/'result.json',dict(experiment='DTM037',model=h.ref(out/'last.pt'),protocol=h.ref(ready/'protocol.json'),
        history=history,records=records,admittedSummary=summaries,fitSeconds=fit,seconds=time.monotonic()-started,
        radius=float(radius),retentionPassed=retention,independentEvaluation=False,productionEligible=False),sealed=True)
    h.require(sum(v.stat().st_size for v in out.rglob('*') if v.is_file())<2*1024**3,'output_budget')
    print('retention',retention,'admitted',summaries,'fitSeconds',fit,flush=True)
    print({k:{g:v['correct'] for g,v in r['summary'].items()} for k,r in records.items() if k!='peer'},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['prepare','train'])
    parser.add_argument('--ready',type=Path,required=True);args=parser.parse_args()
    prepare(args.ready) if args.mode=='prepare' else train(args.ready)
