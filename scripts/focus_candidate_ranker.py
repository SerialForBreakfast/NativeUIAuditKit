"""RANK75: image-only proposal ranking through the existing experiment dispatcher."""
import argparse
import base64
import io
import hashlib
import inspect
import os
import time
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image
import focus_direct_transition as d
import focus_runtime as runtime
from prepare_proposal74 import load_inputs, targets
from focus_recorded_transition_eval import iou

VERSION = 'focus-candidate-ranking-v1'
ARM = 'transition-candidate-ranker'
CONFIG = dict(model=ARM, epochs=600, batch=50, lr=.001, seed=42,
              optimizer='adam', backend='cpu', threads=2, selection='fixed-last',
              maxSeconds=None, maxOutputBytes=2*1024**3,
              encoding='production-crop256-rgb16-bilinear-v1')
NATIVE_CONFIG = dict(CONFIG,batch=74)
SIZE_CONFIG = dict(NATIVE_CONFIG,geometryFeatures='normalized-size-v1')
ACTION_CONFIG = dict(SIZE_CONFIG,batch=122)


def sealed(path, version):
    doc=d.h.read(path)
    d.h.require(doc.get('version')==version and doc.get('seal')==d.h.digest({k:v for k,v in doc.items() if k!='seal'}), 'ranking_manifest_seal')
    return doc


def pins():
    return dict(code=d.pins()['code'] + [d.h.ref(d.h.ROOT/p) for p in
        ('scripts/focus_candidate_ranker.py', 'scripts/focus_runtime.py',
         'scripts/prepare_proposal74.py', 'scripts/focus_learning_experiment.py',
         'Tools/FocusRingTool/main.swift')], dependencies=d.pins()['dependencies'],
        runtime=runtime.identity())


def supervision(inputs, labels, rows):
    frames = {f['id']: f for f in inputs['frames']}
    expected_pairs = [dict(id=r['id'], split=r['split'], group=r['group'],
                          frames=[v['sha256'] for v in r['images']]) for r in rows]
    d.h.require(inputs['pairs'] == expected_pairs, 'ranking_pair_binding')
    expected, positives = [], {}
    for r in rows:
        for endpoint, ref, box in zip(('before','after'), r['images'], r['boxes']):
            f = frames[ref['sha256']]
            d.h.require(f['split'] == r['split'] and f['size'] == r['size'], 'ranking_frame_role')
            target = targets(f['candidates'], box)
            expected.append(dict(pairID=r['id'], endpoint=endpoint, frameID=f['id'], split=r['split'], **target))
            ids = frozenset(target['positiveIDs'])
            d.h.require(ids and positives.setdefault(f['id'], ids) == ids, 'ranking_positive_conflict_or_missing')
    d.h.require(labels == expected and set(positives) == set(frames), 'ranking_supervision_binding')
    return positives


def bank(path):
    manifest = sealed(d.h.local(path), 'ranking-encodings-v1')
    if 'derivativeIdentity' in manifest:
        d.h.require(manifest['derivativeIdentity']==derivative_identity(), 'ranking_derivative_changed')
    d.h.require(manifest['runtime'] == runtime.identity() and manifest['encoding'] == CONFIG['encoding'], 'ranking_encoding_changed')
    dependencies=manifest.get('encodingDependencies')
    if dependencies is None:
        # Initial v1 banks predate the explicit field. Their adjacent original
        # preparation protocol binds this exact bank; do not trust a new run's pins.
        origin=d.h.read(d.h.local(path).parent/'protocol.json')
        d.h.require(origin['protocolSHA256']==d.h.digest({k:v for k,v in origin.items() if k!='protocolSHA256'}) and
            origin['bank']==d.h.ref(d.h.local(path)) and origin['configuration']['encoding']==manifest['encoding'] and
            origin['pins']['runtime']==manifest['runtime'], 'ranking_encoding_origin')
        dependencies=origin['pins']['dependencies']
    current=d.pins()['dependencies']
    d.h.require(all(dependencies[k]==current[k] for k in ('numpy','pillow')), 'ranking_encoding_dependencies')
    inputs = load_inputs(d.h.checked(d.h.ROOT, manifest['inputs']))
    data = np.load(d.h.checked(d.h.ROOT, manifest['tensor']), allow_pickle=False)
    expected = [[f['id'], c['id']] for f in inputs['frames'] for c in f['candidates']]
    d.h.require(manifest['items'] == expected and data.dtype == np.float32 and
        data.shape == (len(expected),768) and np.isfinite(data).all() and
        ((data >= 0) & (data <= 1)).all(), 'ranking_tensor_contract')
    return manifest, inputs, data


def encode_crop(raw):
    """Image-only encoding; its source is independently pinned by derivative caches."""
    with Image.open(io.BytesIO(raw)) as im:
        d.h.require(im.size == (256,256), 'ranking_crop_size')
        return np.asarray(im.convert('RGB').resize((16,16), Image.Resampling.BILINEAR), dtype=np.float32).reshape(-1)/255


def derivative_identity():
    return dict(version='ranking-derivative-identity-v1', encoding=CONFIG['encoding'],
        encoderSHA256=hashlib.sha256(inspect.getsource(encode_crop).encode()).hexdigest(),
        pipelineSHA256=hashlib.sha256(inspect.getsource(encode_frames).encode()).hexdigest(),
        adapter=d.h.ref(d.h.ROOT/'scripts/focus_runtime.py'),
        preprocessing=runtime.RUNTIME_PREPROCESSING, runtime=runtime.identity(),
        dependencies={k:d.dependency_version(k) for k in ('numpy','pillow')})


def validate_frames(frames):
    """Validate image-only cache inputs; data admission is deliberately elsewhere."""
    from diagnose_proposals73 import valid
    d.h.require(0 < len(frames) <= 512, 'derivative_frame_budget')
    ids=set()
    for f in frames:
        d.h.require(f['id']==f['image']['sha256'] and f['id'] not in ids, 'derivative_frame_identity')
        ids.add(f['id']); path=d.h.checked(d.h.ROOT,f['image'])
        d.h.require(len(f['size'])==2 and all(type(v)is int and v>0 for v in f['size']) and
            f['size'][0]*f['size'][1]<=40_000_000, 'derivative_image_size')
        with Image.open(path) as im:
            d.h.require(list(im.size)==f['size'], 'derivative_actual_size')
        candidates=f['candidates']
        d.h.require(0<len(candidates)<=80 and all(set(c)=={'id','bounds'} for c in candidates) and
            all(isinstance(c['id'],str) and c['id'] for c in candidates) and
            len({c['id'] for c in candidates})==len(candidates), 'derivative_candidates')
        d.h.require(all(valid(c['bounds']) and c['bounds'][0]+c['bounds'][2]<=f['size'][0] and
            c['bounds'][1]+c['bounds'][3]<=f['size'][1] for c in candidates), 'derivative_bounds')


def encode_frames(frames, cache_root=None):
    """Reuse immutable image-only entries; no labels, split or model weights in keys."""
    validate_frames(frames)
    identity=derivative_identity(); cache=Path(cache_root).absolute() if cache_root else None
    if cache:
        d.h.require(any(cache.is_relative_to(d.h.ROOT/p) for p in ('.build','reports/work')) and
            not any(p.is_symlink() for p in (cache,*cache.parents)), 'derivative_cache_boundary')
        cache.mkdir(parents=True,exist_ok=True)
    encoded=[];items=[];hashes=[];entries=[]
    stats=dict(cacheHits=0,cacheMisses=0,invocations=0)
    for f in frames:
        binding=dict(imageSHA256=f['image']['sha256'],size=f['size'],
            bounds=[c['bounds'] for c in f['candidates']],identity=identity)
        key=d.h.digest(binding);entry=cache/key if cache else None
        if entry and entry.exists():
            manifest=sealed(entry/'entry.json','ranking-derivative-entry-v1')
            d.h.require(manifest['binding']==binding, 'derivative_binding')
            tensor=d.h.checked(d.h.ROOT,manifest['tensor'])
            d.h.require(tensor==entry/'encodings.npy', 'derivative_tensor_location')
            data=np.load(tensor,allow_pickle=False);crop_hashes=manifest['cropPNGHashes']
            stats['cacheHits']+=1
        else:
            if entry:entry.mkdir(exist_ok=False)  # Partial attempts are never overwritten.
            image=d.h.checked(d.h.ROOT,f['image']);data=[];crop_hashes=[]
            requests=[dict(id=c['id'],path=str(image),sha256=f['image']['sha256'],bounds=c['bounds']) for c in f['candidates']]
            for batch in runtime.bounded_batches(requests,shared_images=True):
                reply=runtime.invoke(batch,image_root=image.parent);stats['invocations']+=1
                d.h.require([r['id'] for r in reply['results']]==[r['id'] for r in batch], 'derivative_reply_order')
                for row in reply['results']:
                    raw=base64.b64decode(row['png'],validate=True)
                    data.append(encode_crop(raw));crop_hashes.append(hashlib.sha256(raw).hexdigest())
            data=np.stack(data);stats['cacheMisses']+=1
            d.h.checked(d.h.ROOT,f['image'])
            d.h.require(identity==derivative_identity(), 'derivative_runtime_changed')
            if entry:
                with (entry/'encodings.npy').open('xb') as stream:np.save(stream,data,allow_pickle=False)
                d.h.write(entry/'entry.json',dict(version='ranking-derivative-entry-v1',binding=binding,
                    tensor=d.h.ref(entry/'encodings.npy'),cropPNGHashes=crop_hashes),sealed=True)
        d.h.require(data.dtype==np.float32 and data.shape==(len(f['candidates']),768) and
            np.isfinite(data).all() and ((data>=0)&(data<=1)).all(), 'derivative_tensor_contract')
        d.h.require(len(crop_hashes)==len(data) and all(isinstance(v,str) and len(v)==64 and
            all(c in '0123456789abcdef' for c in v) for v in crop_hashes), 'derivative_crop_hashes')
        encoded.extend(data);hashes.extend(crop_hashes)
        items.extend([[f['id'],c['id']] for c in f['candidates']])
        if entry:entries.append(d.h.ref(entry/'entry.json'))
    for f in frames:d.h.checked(d.h.ROOT,f['image'])
    d.h.require(identity==derivative_identity(), 'derivative_runtime_changed')
    return np.stack(encoded),items,hashes,stats,entries


def prepare_derivatives(output, input_path, cache_root):
    """Inspection-only CLI path: never create an experiment protocol or approval."""
    start=time.monotonic();out=d.h.fresh(output);path=d.h.local(input_path)
    reference=d.h.ref(path);doc=d.h.read(path)
    if doc.get('version')=='calibration-proposals-v1':
        doc=sealed(path,'calibration-proposals-v1')
        d.h.require(doc.get('trainingEligible') is False, 'derivative_calibration_role')
    else:doc=load_inputs(path)
    data,items,hashes,stats,entries=encode_frames(doc['frames'],cache_root)
    d.h.require(reference==d.h.ref(path), 'derivative_inputs_changed')
    out.mkdir(parents=True);np.save(out/'encodings.npy',data,allow_pickle=False)
    report=dict(version='ranking-inspection-derivatives-v1',trainingEligible=False,executionEligible=False,
        inputs=reference,identity=derivative_identity(),tensor=d.h.ref(out/'encodings.npy'),
        items=items,cropPNGHashes=hashes,entries=entries,statistics=stats,
        elapsedSeconds=time.monotonic()-start)
    d.h.write(out/'derivatives.json',report,sealed=True)
    print(stats);return report


def prepare(output, cache_root=None):
    start = time.monotonic(); out = d.h.fresh(output)
    root = d.h.ROOT/'reports/work/PROPOSAL-RANK-74/union-bank'
    inputs = load_inputs(root/'inputs.json')
    labels = sealed(root/'supervision.json', 'transition-candidate-supervision-v1')
    corpus = d.h.read(d.h.checked(d.h.ROOT, labels['corpus']))
    d.h.require(corpus == d.collect(corpus['sources']), 'ranking_source_changed')
    rows = d.admitted(corpus, d.h.read(d.h.checked(d.h.ROOT, labels['admission'])))
    d.h.require(Counter(r['split'] for r in rows) == {'train':32,'development':5}, 'ranking_membership')
    supervision(inputs, labels['labels'], rows)
    before_runtime = runtime.identity(); out.mkdir(parents=True)
    encoded,items,hashes,stats,entries=encode_frames(inputs['frames'],cache_root)
    d.h.require(before_runtime == runtime.identity(), 'ranking_runtime_changed')
    np.save(out/'encodings.npy', np.stack(encoded), allow_pickle=False)
    d.h.write(out/'bank.json', dict(version='ranking-encodings-v1', inputs=d.h.ref(root/'inputs.json'),
        tensor=d.h.ref(out/'encodings.npy'), runtime=before_runtime, encoding=CONFIG['encoding'],
        encodingDependencies={k:v for k,v in d.pins()['dependencies'].items() if k in ('numpy','pillow')},
        items=items, cropPNGHashes=hashes, invocations=stats['invocations'],derivativeStatistics=stats,
        derivativeEntries=entries,derivativeIdentity=derivative_identity(),elapsedSeconds=time.monotonic()-start), sealed=True)
    seal_protocol(out, out/'bank.json')


def seal_protocol(out, prepared):
    """Reuse image-only encodings after a model/dispatcher change; never recrop."""
    out=d.h.local(out); bank(prepared)
    root=d.h.ROOT/'reports/work/PROPOSAL-RANK-74/union-bank'
    doc = dict(version=VERSION, configuration=CONFIG, pins=pins(), bank=d.h.ref(prepared),
        supervision=d.h.ref(root/'supervision.json'), control=d.h.ref(d.h.ROOT/'reports/work/COVERAGE-70/comparison.json'))
    doc['protocolSHA256'] = d.h.digest(doc); d.h.write(out/'protocol.json',doc)
    d.h.write(out/'approval.json',dict(version='ranking-approval-v1', approved=True, protocolSHA256=doc['protocolSHA256'],
        arm=ARM, runName='rank75-dtm016', decisionReference='Active goal/standing RANK75 tranche: one 600epoch visual ranker,32/5roles unchanged,2GiB,no wall-time cap; no capture/export/promotion.'))
    print(doc['protocolSHA256'])


def load_protocol(path, arm, run_name, approval_path=None):
    doc = d.h.read(d.h.local(path))
    d.h.require(doc['version'] == VERSION and doc['configuration'] in (CONFIG,NATIVE_CONFIG,SIZE_CONFIG,ACTION_CONFIG) and arm == ARM, 'ranking_configuration')
    d.h.require(doc['protocolSHA256'] == d.h.digest({k:v for k,v in doc.items() if k != 'protocolSHA256'}), 'ranking_protocol_hash')
    d.h.require(doc['pins'] == pins(), 'ranking_code_or_dependencies_changed')
    _, inputs, data = bank(d.h.checked(d.h.ROOT, doc['bank']))
    label = sealed(d.h.checked(d.h.ROOT,doc['supervision']), 'transition-candidate-supervision-v1')
    d.h.require(label['inputs'] == d.h.read(d.h.checked(d.h.ROOT,doc['bank']))['inputs'], 'ranking_inputs_binding')
    corpus = d.h.read(d.h.checked(d.h.ROOT,label['corpus']))
    rows = d.admitted(corpus, d.h.read(d.h.checked(d.h.ROOT,label['admission'])))
    expected_counts={'train':32,'development':5} if doc['configuration']==CONFIG else {'train':44,'development':5}
    if doc['configuration']==ACTION_CONFIG:expected_counts={'train':68,'development':5}
    d.h.require(Counter(r['split'] for r in rows)==expected_counts, 'ranking_membership')
    positives = supervision(inputs,label['labels'],rows)
    d.h.require(sum(f['split']=='train' for f in inputs['frames'])==doc['configuration']['batch'], 'ranking_unique_training_frames')
    control = d.h.sealed(d.h.checked(d.h.ROOT,doc['control']), 'data67-batched-comparison-v1')
    d.h.require(control['corpusSHA256'] == corpus['corpusSHA256'], 'ranking_control_corpus')
    d.h.checked(d.h.ROOT,control['models']['DTM013'])
    scores = [r for r in control['results'] if r['model']=='DTM013' and r['condition']=='baseline']
    d.h.require(len(scores)==len(rows) and {r['id'] for r in scores}=={r['id'] for r in rows}, 'ranking_control_membership')
    d.h.require(all(type(r['prediction']['changeProbability']) in (int,float) and
        np.isfinite(r['prediction']['changeProbability']) and 0<=r['prediction']['changeProbability']<=1 for r in scores),'ranking_control_probabilities')
    if doc['configuration'] in (NATIVE_CONFIG,SIZE_CONFIG,ACTION_CONFIG):
        reference=sealed(d.h.checked(d.h.ROOT,doc['reference']),'native-ranking-reference-v1')
        d.h.require(reference['inputs']==label['inputs'] and len(reference['results'])==len(rows) and
            {r['id'] for r in reference['results']}=={r['id'] for r in rows}, 'ranking_reference_membership')
        d.h.checked(d.h.ROOT,reference['model'])
    approved = None
    if approval_path:
        approved = d.h.ref(d.h.local(approval_path)); a=d.h.read(d.h.checked(d.h.ROOT,approved))
        d.h.require(a.get('approved') is True and a.get('version')=='ranking-approval-v1' and
            a.get('protocolSHA256')==doc['protocolSHA256'] and a.get('arm')==arm and
            a.get('runName')==run_name and a.get('decisionReference'), 'ranking_approval_binding')
    out=d.old.fresh_run(run_name)
    return dict(formatVersion='focus-ranking-preflight-v1',protocolVersion=VERSION,configuration=doc['configuration'],
        launchEligible=approved is not None,blockers=[] if approved else ['missing_approval'],
        protocolFile=d.h.ref(d.h.local(path)),protocolSHA256=doc['protocolSHA256'],approval=approved,
        output=str(out.relative_to(d.h.ROOT)),releaseEligible=False), (inputs,data,positives,rows,scores)


def model(torch,configuration=None):
    configuration=CONFIG if configuration is None else configuration
    d.h.require(configuration in (CONFIG,NATIVE_CONFIG,SIZE_CONFIG,ACTION_CONFIG),'ranking_model_configuration')
    net=torch.nn.Sequential(torch.nn.Linear(768,32),torch.nn.ReLU(),torch.nn.Linear(32,1))
    if configuration in (SIZE_CONFIG,ACTION_CONFIG):
        first=torch.nn.Linear(770,32)
        with torch.no_grad():
            first.weight[:,:768].copy_(net[0].weight);first.weight[:,768:].zero_();first.bias.copy_(net[0].bias)
        net[0]=first
    return net


def features(data,inputs,configuration):
    """Candidate scale only, never location, labels or source identity."""
    d.h.require(configuration in (CONFIG,NATIVE_CONFIG,SIZE_CONFIG,ACTION_CONFIG),'ranking_feature_configuration')
    if configuration not in (SIZE_CONFIG,ACTION_CONFIG):return data
    sizes=[]
    for frame in inputs['frames']:
        w,h=frame['size']
        d.h.require(type(w)is int and type(h)is int and w>0 and h>0,'ranking_feature_dimensions')
        for c in frame['candidates']:
            cw,ch=c['bounds'][2:]
            d.h.require(np.isfinite([cw,ch]).all() and 0<cw<=w and 0<ch<=h,'ranking_feature_size')
            sizes.append([cw/w,ch/h])
    d.h.require(data.dtype==np.float32 and data.shape==(len(sizes),768),'ranking_feature_shape')
    return np.concatenate((data,np.asarray(sizes,dtype=np.float32)),axis=1)


def frame_loss(torch, scores, positive_indices):
    d.h.require(len(positive_indices)>0, 'ranking_missing_positive')
    return torch.logsumexp(scores,0)-torch.logsumexp(scores[positive_indices],0)


def choose(candidates, scores):
    """Label-free deterministic selector; scores are not calibrated confidence."""
    if not candidates:return None
    d.h.require(len(scores)==len(candidates) and np.isfinite(scores).all(), 'ranking_invalid_scores')
    return min(zip(candidates,scores),key=lambda v:(-float(v[1]),v[0]['id']))[0]


def run(report, experiment_id):
    start=time.monotonic()
    fresh,payload=load_protocol(d.h.checked(d.h.ROOT,report['protocolFile']),ARM,Path(report['output']).name,
        d.h.checked(d.h.ROOT,report['approval']))
    d.h.require(fresh==report and fresh['launchEligible'],'ranking_preflight_changed')
    inputs,data,positives,rows,control=payload
    configuration=report['configuration']
    torch=d.torch_runtime();torch.set_num_threads(2);torch.manual_seed(configuration['seed'])
    net=model(torch,configuration);optimizer=torch.optim.Adam(net.parameters(),lr=configuration['lr'])
    x=torch.from_numpy(features(data,inputs,configuration));offset=0;groups=[]
    for f in inputs['frames']:
        n=len(f['candidates']); groups.append((f,offset,offset+n));offset+=n
    train=[(f,a,b) for f,a,b in groups if f['split']=='train']
    d.h.require(len(train)==configuration['batch'],'ranking_training_frames')
    train_indices=[i for _,a,b in train for i in range(a,b)]
    train_x=x[train_indices];train_groups=[];cursor=0
    for f,a,b in train:
        train_groups.append((f,cursor,cursor+b-a));cursor+=b-a
    out=d.old.fresh_run(Path(report['output']).name);out.mkdir(parents=True)
    d.h.write(out/'execution.json',dict(status='started',pid=os.getpid(),experimentID=experiment_id,protocol=report['protocolFile']))
    history=[];fit_start=time.monotonic()
    for epoch in range(configuration['epochs']):
        optimizer.zero_grad();scores=net(train_x).flatten()
        loss=torch.stack([frame_loss(torch,scores[a:b],[i for i,c in enumerate(f['candidates']) if c['id'] in positives[f['id']]]) for f,a,b in train_groups]).mean()
        d.h.require(bool(torch.isfinite(loss)),'ranking_nonfinite_loss');loss.backward();optimizer.step()
        history.append(dict(epoch=epoch+1,loss=float(loss.detach())))
    fit_seconds=time.monotonic()-fit_start;net.eval()
    torch.save(dict(version=VERSION,configuration=configuration,state=net.state_dict()),out/'last.pt')
    with torch.inference_mode():scores=net(x).flatten().numpy()
    selections={f['id']:choose(f['candidates'],scores[a:b]) for f,a,b in groups}
    frozen={r['id']:r for r in control};results=[]
    for r in rows:
        picked=[selections[v['sha256']] for v in r['images']]
        overlaps=[iou(p['bounds'],truth) if p else 0 for p,truth in zip(picked,r['boxes'])]
        prob=frozen[r['id']]['prediction']['changeProbability']
        decided=max(prob,1-prob)>=d.CONFIG['confidence'] and all(picked)
        results.append(dict(id=r['id'],split=r['split'],selected=picked,boxIoUs=overlaps,
            bothBoxesCorrect=min(overlaps)>=.5,changeProbability=prob,rawChangeCorrect=(prob>=.5)==r['changed'],
            decision=('changed' if prob>=.5 else 'unchanged') if decided else 'unknown'))
    summary={split:dict(pairs=len(rs),correctEndpoints=sum(v>=.5 for r in rs for v in r['boxIoUs']),
        pairedBoxes=sum(r['bothBoxesCorrect'] for r in rs),joint=sum(r['bothBoxesCorrect'] and r['rawChangeCorrect'] for r in rs),
        abstentions=sum(r['decision']=='unknown' for r in rs))
        for split in ('train','development') for rs in ([r for r in results if r['split']==split],)}
    d.h.write(out/'result.json',dict(version=VERSION,protocol=report['protocolFile'],model=d.h.ref(out/'last.pt'),
        history=history,results=results,summary=summary,fitSeconds=fit_seconds,elapsedSeconds=time.monotonic()-start,
        developmentExposed=True,releaseEligible=False),sealed=True)
    d.h.require(sum(p.stat().st_size for p in out.iterdir())<CONFIG['maxOutputBytes'],'ranking_output_budget')
    print(summary);return 0


def prepare_native(output, admission_root, derivatives):
    """Authorized native comparison preparation; no training until the trainer executes."""
    start=time.monotonic();out=d.h.fresh(output);root=d.h.local(admission_root)
    corpus=d.h.read(root/'corpus.json');admission=d.h.read(root/'admission.json')
    d.h.require(corpus==d.collect(corpus['sources']), 'native_ranking_source_changed')
    rows=d.admitted(corpus,admission)
    actions='nativeActions' in corpus['sources']
    configuration=ACTION_CONFIG if actions else NATIVE_CONFIG
    d.h.require(Counter(r['split'] for r in rows)=={'train':68 if actions else 44,'development':5},'native_ranking_roles')
    deriv_path=d.h.local(derivatives);deriv=sealed(deriv_path,'ranking-inspection-derivatives-v1')
    d.h.require(deriv['identity']==derivative_identity() and deriv['trainingEligible'] is False,'native_ranking_derivatives')
    inspection=sealed(d.h.checked(d.h.ROOT,deriv['inputs']),'calibration-proposals-v1')
    frames=inspection['frames'];validate_frames(frames)
    roles={};sizes={}
    for r in rows:
        for ref in r['images']:
            key=ref['sha256']
            d.h.require(roles.setdefault(key,r['split'])==r['split'], 'native_ranking_frame_leakage')
            d.h.require(sizes.setdefault(key,r['size'])==r['size'], 'native_ranking_size_conflict')
    d.h.require({f['id'] for f in frames}==set(roles),'native_ranking_frame_membership')
    bound_frames=[dict(id=f['id'],image=f['image'],size=f['size'],split=roles[f['id']],
        candidates=f['candidates'],source=deriv['inputs']) for f in frames]
    d.h.require(all(f['size']==sizes[f['id']] for f in frames),'native_ranking_size_binding')
    inputs=dict(version='transition-candidate-inputs-v2',frames=bound_frames,
        pairs=[dict(id=r['id'],split=r['split'],group=r['group'],frames=[v['sha256'] for v in r['images']]) for r in rows])
    pools={f['id']:f for f in bound_frames}
    labels=[dict(pairID=r['id'],endpoint=e,frameID=ref['sha256'],split=r['split'],
        **targets(pools[ref['sha256']]['candidates'],box)) for r in rows
        for e,ref,box in zip(('before','after'),r['images'],r['boxes'])]
    supervision(inputs,labels,rows)
    out.mkdir(parents=True);d.h.write(out/'inputs.json',inputs,sealed=True)
    d.h.write(out/'supervision.json',dict(version='transition-candidate-supervision-v1',inputs=d.h.ref(out/'inputs.json'),
        corpus=d.h.ref(root/'corpus.json'),admission=d.h.ref(root/'admission.json'),labels=labels),sealed=True)
    d.h.write(out/'bank.json',dict(version='ranking-encodings-v1',inputs=d.h.ref(out/'inputs.json'),
        tensor=deriv['tensor'],runtime=deriv['identity']['runtime'],encoding=CONFIG['encoding'],
        encodingDependencies=deriv['identity']['dependencies'],derivativeIdentity=deriv['identity'],
        items=deriv['items'],cropPNGHashes=deriv['cropPNGHashes'],invocations=0,reusedInspection=d.h.ref(deriv_path)),sealed=True)
    _,_,data=bank(out/'bank.json')
    torch=d.torch_runtime();torch.set_num_threads(2)
    control_path=d.h.ROOT/'NativeUITrainer/focus_ring_runs/temporal68-dtm013/last.pt'
    control_ref=d.h.ref(control_path);state=torch.load(control_path,map_location='cpu',weights_only=True)
    d.h.require(state['configuration']==d.TEMPORAL_CONFIG,'native_ranking_control_configuration')
    control_net=d.model(state['configuration']);control_net.load_state_dict(state['state'],strict=True);control_net.eval()
    scores=[]
    for r in rows:
        before,after=[d.pixels(ref) for ref in r['images']]
        prediction=d.infer(control_net,before,after)
        scores.append(dict(id=r['id'],model='DTM013',condition='baseline',prediction=prediction))
    d.h.write(out/'control.json',dict(version='data67-batched-comparison-v1',**d.h.FLAGS,
        corpusSHA256=corpus['corpusSHA256'],models={'DTM013':control_ref},results=scores),sealed=True)
    prior=d.h.read(d.h.ROOT/'reports/work/COVERAGE-70/comparison.json')
    old={r['id']:r['prediction']['changeProbability'] for r in prior['results'] if r['model']=='DTM013' and r['condition']=='baseline'}
    d.h.require(len(old)==37 and all(abs(r['prediction']['changeProbability']-old[r['id']])<=1e-6 for r in scores if r['id'] in old),'native_ranking_control_parity')
    reference=d.h.ROOT/('NativeUITrainer/focus_ring_runs/size81-dtm019/last.pt' if actions else 'NativeUITrainer/focus_ring_runs/rank75-dtm016/last.pt');reference_ref=d.h.ref(reference)
    original=torch.load(reference,map_location='cpu',weights_only=True)
    d.h.require(original['version']==VERSION and original['configuration']==(SIZE_CONFIG if actions else CONFIG),'native_ranking_reference_configuration')
    reference_net=model(torch,original['configuration']);reference_net.load_state_dict(original['state'],strict=True);reference_net.eval()
    with torch.inference_mode():values=reference_net(torch.from_numpy(features(data,inputs,original['configuration']))).flatten().numpy()
    selected={};cursor=0
    for f in bound_frames:
        n=len(f['candidates']);selected[f['id']]=choose(f['candidates'],values[cursor:cursor+n]);cursor+=n
    baseline=[dict(id=r['id'],split=r['split'],newNative=r['id'].startswith(corpus['sources']['nativeActions']['sha256']+':') if actions else r['id'] not in old,
        selected=[selected[v['sha256']] for v in r['images']],boxIoUs=[iou(selected[v['sha256']]['bounds'],box) for v,box in zip(r['images'],r['boxes'])]) for r in rows]
    d.h.write(out/'reference.json',dict(version='native-ranking-reference-v1',model=reference_ref,
        inputs=d.h.ref(out/'inputs.json'),results=baseline),sealed=True)
    d.h.require(control_ref==d.h.ref(control_path) and reference_ref==d.h.ref(reference),'native_ranking_model_changed')
    doc=dict(version=VERSION,configuration=configuration,pins=pins(),bank=d.h.ref(out/'bank.json'),
        supervision=d.h.ref(out/'supervision.json'),control=d.h.ref(out/'control.json'),reference=d.h.ref(out/'reference.json'))
    doc['protocolSHA256']=d.h.digest(doc);d.h.write(out/'protocol.json',doc)
    d.h.write(out/'approval.json',dict(version='ranking-approval-v1',approved=True,protocolSHA256=doc['protocolSHA256'],
        arm=ARM,runName='native87-dtm020' if actions else 'native79-dtm017',decisionReference=('Maintainer approved exact24pair admission and controlled comparison; NATIVE87,600epochs,68/5roles,size-aware model,2GiB,no-wall-time override,no promotion.' if actions else 'Maintainer explicitly approved BATCH79 comparison,600epochs,44/5roles,2GiB,no wall-time cap; no promotion.')))
    d.h.write(out/'preparation.json',dict(elapsedSeconds=time.monotonic()-start,images=len(bound_frames),
        nativeCropInvocations=0,controlOriginal37Parity=True,trainingLaunched=False),sealed=True)
    print(doc['protocolSHA256'])


def prepare_size(output):
    """Rebind immutable pixels to one approved size-aware model; no recropping."""
    from prepare_transition_inputs import references
    start=time.monotonic();out=d.h.fresh(output)
    root=d.h.ROOT/'reports/work/BATCH-79-B/native-ready'
    previous=d.h.read(root/'protocol.json')
    d.h.require(previous['protocolSHA256']==d.h.digest({k:v for k,v in previous.items() if k!='protocolSHA256'}) and
        previous['configuration']==NATIVE_CONFIG,'size81_reference_protocol')
    manifest,inputs,data=bank(d.h.checked(d.h.ROOT,previous['bank']))
    labels=sealed(d.h.checked(d.h.ROOT,previous['supervision']),'transition-candidate-supervision-v1')
    corpus=d.h.read(d.h.checked(d.h.ROOT,labels['corpus']))
    d.h.require(corpus['corpusSHA256']==d.h.digest({k:v for k,v in corpus.items() if k!='corpusSHA256'}),'size81_corpus_digest')
    for ref in references(corpus):d.h.checked(d.h.ROOT,ref)
    rows=d.admitted(corpus,d.h.read(d.h.checked(d.h.ROOT,labels['admission'])))
    d.h.require(Counter(r['split'] for r in rows)=={'train':44,'development':5},'size81_roles')
    supervision(inputs,labels['labels'],rows);features(data,inputs,SIZE_CONFIG)
    baseline_path=d.h.ROOT/'NativeUITrainer/focus_ring_runs/native79-dtm017/result.json'
    baseline=sealed(baseline_path,VERSION)
    d.h.require(baseline['protocol']==d.h.ref(root/'protocol.json'),'size81_baseline_protocol')
    d.h.checked(d.h.ROOT,baseline['model'])
    native_prefix=corpus['sources']['nativeTable']['sha256']+':'
    out.mkdir(parents=True)
    d.h.write(out/'reference.json',dict(version='native-ranking-reference-v1',model=baseline['model'],
        inputs=manifest['inputs'],results=[dict(id=v['id'],split=v['split'],newNative=v['id'].startswith(native_prefix),
            selected=v['selected'],boxIoUs=v['boxIoUs']) for v in baseline['results']]),sealed=True)
    doc=dict(version=VERSION,configuration=SIZE_CONFIG,pins=pins(),bank=previous['bank'],
        supervision=previous['supervision'],control=previous['control'],reference=d.h.ref(out/'reference.json'))
    doc['protocolSHA256']=d.h.digest(doc);d.h.write(out/'protocol.json',doc)
    d.h.write(out/'approval.json',dict(version='ranking-approval-v1',approved=True,protocolSHA256=doc['protocolSHA256'],
        arm=ARM,runName='size81-dtm019',decisionReference='Explicit maintainer training approval; SIZE81one fixed600epoch size-aware ranker comparison on admitted44/5. Two normalized size inputs, matched common visual initialization,2GiB,no capture or promotion.'))
    d.h.write(out/'preparation.json',dict(elapsedSeconds=time.monotonic()-start,images=len(inputs['frames']),
        candidateCount=len(data),cropInvocations=0,originalTensor=manifest['tensor'],trainingLaunched=False),sealed=True)
    print(doc['protocolSHA256'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',required=True);p.add_argument('--reuse-bank')
    p.add_argument('--cache-root');p.add_argument('--inputs');p.add_argument('--derivatives-only',action='store_true')
    p.add_argument('--native-admission');p.add_argument('--inspection-derivatives');p.add_argument('--approve-native-comparison',action='store_true')
    p.add_argument('--size-comparison',action='store_true')
    a=p.parse_args()
    if a.size_comparison:
        if not a.approve_native_comparison or any((a.native_admission,a.inspection_derivatives,a.derivatives_only,a.reuse_bank,a.inputs,a.cache_root)):
            p.error('size comparison requires explicit approval and no other preparation modes')
        prepare_size(a.prepare)
    elif a.native_admission:
        if not a.approve_native_comparison or not a.inspection_derivatives or a.derivatives_only or a.reuse_bank or a.inputs or a.cache_root:
            p.error('native preparation requires explicit comparison approval and inspection derivatives; no mixed modes')
        prepare_native(a.prepare,a.native_admission,a.inspection_derivatives)
    elif a.approve_native_comparison or a.inspection_derivatives:p.error('native flags require --native-admission')
    elif a.derivatives_only:
        if not a.inputs or not a.cache_root or a.reuse_bank:
            p.error('--derivatives-only requires --inputs and --cache-root, not --reuse-bank')
        prepare_derivatives(a.prepare,a.inputs,a.cache_root)
    elif a.inputs:p.error('--inputs requires --derivatives-only')
    elif a.reuse_bank:
        if a.cache_root:p.error('--reuse-bank does not use --cache-root')
        out=d.h.fresh(a.prepare);out.mkdir(parents=True);seal_protocol(out,d.h.local(a.reuse_bank))
    else:prepare(a.prepare,a.cache_root)
