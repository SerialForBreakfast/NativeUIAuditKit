"""Bounded context ablations through the existing focus trainer; no default execution."""
import argparse
import hashlib
import io
import math
import re
import time
from collections import defaultdict

import human_annotation_review as h
import focus_native_body_experiment as native
import focus_context_inputs as context

VERSION = 'focus-context-experiment-v1'
ARMS = {'context-local':'fdr024-local-mlp', 'context-geometry':'fdr025-geometry-mlp',
        'context-scene':'fdr026-scene-mlp'}
WIDTH = 1736


def read(ref):
    return h.read(h.checked(h.ROOT,ref),limit=32*1024*1024)


def sealed(ref):
    doc=read(ref)
    h.require(doc.get('protocolSHA256')==h.digest({k:v for k,v in doc.items() if k!='protocolSHA256'}),
              'changed_context_experiment')
    return doc


def envelope(ref):
    e=read(ref)
    h.require(e.get('version')=='focus-context-tranche-v1' and e.get('approved') is True
              and e.get('runs')==ARMS and e.get('scope')=='local-context-comparison-no-export', 'context_tranche_scope')
    h.checked(h.ROOT,e['authorizationReference'])
    h.require(e['limits']==dict(maxRuns=3,trainingSeconds=300,encodingSeconds=300,
                                wallSeconds=1800,outputBytes=2*1024**3,cacheBytes=64*1024**2),
              'context_tranche_limits')
    return e


def verified_base(ref):
    old=sealed(ref)
    h.require(old.get('version')==native.VERSION,'context_base_version')
    current=native.make_protocol(old['inputs'])
    # Historical training-code identity is not current execution authority. Every
    # data, weight, encoder and selection field must still reconstruct identically.
    strip=lambda d:{k:v for k,v in d.items() if k not in ('runtime','protocolSHA256')}
    h.require(strip(old)==strip(current),'changed_context_base')
    return current


def verified_context(ref, base):
    doc=read(ref); rows=base['samples']
    h.require(doc.get('version')==context.VERSION and not doc['blocked'] and
              doc['counts']['prepared']==len(rows)==doc['counts']['input'], 'incomplete_context')
    source=sealed(doc['protocol'])
    h.require(source['samples']==rows,'context_source_membership')
    members={m['id']:m for m in doc['members']}
    h.require(len(members)==len(rows)==len(doc['members']) and set(members)=={r['id'] for r in rows},
              'context_member_identity')
    h.require(all((r['split'],r['use']) in {('train','train-candidate'),('train','human-static-auxiliary'),
                ('validation','representative-selection'),('validation','retention-validation')} for r in rows),
              'protected_context_input')
    recovered,_=context.geometry_index([h.checked(h.ROOT,r) for r in doc['geometryManifests']])
    checked=set()
    def check(ref):
        key=(ref['path'],ref['sha256'])
        if key not in checked:h.checked(h.ROOT,ref);checked.add(key)
    from PIL import Image
    for r in rows:
        m=members[r['id']]; frame=r.get('frame',r.get('image'));check(frame);check(r['crop'])
        h.require(m['localCrop']==r['crop'] and m['sceneKey']==frame['sha256'],'context_crop_binding')
        scene=doc['scenes'][m['sceneKey']]
        h.require(scene['original']['sha256']==frame['sha256'],'context_frame_binding')
        check(scene['original'])
        check(scene['scene']);check(m['mask'])
        bounds=r.get('bounds')
        if bounds is None:bounds=recovered.get((r.get('pairID'),frame['sha256'],r['crop']['sha256']))
        with Image.open(h.ROOT/frame['path']) as im:tx=context.transform(im.size)
        geo=context.geometry(bounds,tx)
        h.require(scene['transform']==tx and geo==m['geometry'],'context_geometry_changed')
        with Image.open(h.ROOT/m['mask']['path']) as im:
            h.require(im.mode=='L' and im.size==context.SIZE and
                      im.tobytes()==context.candidate_mask(geo).tobytes(),'context_mask_changed')
    h.require(set(doc['scenes'])=={m['sceneKey'] for m in members.values()},'extra_context_scene')
    return doc


def prepare(spec):
    h.require(set(spec)=={'envelope','contextFeatures'},'context_spec_fields')
    e=envelope(spec['envelope']);base=verified_base(e['baseProtocol'])
    doc=verified_context(e['context'],base)
    h.require(len(doc['scenes'])<=693 and len(base['samples'])==1883,'context_scope_size')
    runtime=dict(base['runtime'])
    runtime['code']=runtime['code']+[h.ref(h.ROOT/'scripts'/n) for n in
                                           ('focus_context_experiment.py','focus_context_inputs.py')]
    result=dict(version=VERSION,inputs=spec,baseProtocol=e['baseProtocol'],context=e['context'],
                samples=base['samples'],configuration=dict(base['configuration'],model='context_mlp_64'),
                runtime=runtime,baseRuntime=base['runtime'],
                **{k:base[k] for k in ('selection','representation','fullFit','counts','baseCachedInputs',
                    'reviewedExtension','baselineTraining','unmetQualificationBlockers')},
                nativeExtension=base['inputs']['newFeatures'],warmCheckpoint=None,
                blockers=[] if spec['contextFeatures'] else ['missing_context_features'],releaseEligible=False)
    if spec['contextFeatures']:
        refs=spec['contextFeatures'];h.checked(h.ROOT,refs['cache'])
        receipt=read(refs['receipt'])
        h.require(receipt['version']=='focus-context-features-v1' and receipt['context']==e['context']
                  and receipt['envelope']==spec['envelope'] and receipt['backboneUnchanged'] is True
                  and receipt['ids']==[r['id'] for r in base['samples']]
                  and receipt['featureStateSHA256']==read(base['baseCachedInputs']['receipt'])['featureStateSHA256'],
                  'context_feature_receipt')
    result['protocolSHA256']=h.digest(result)
    return result


def approval(doc):
    return dict(version='focus-tranche-derived-run-approval-v1',authorityKind='tranche-derived',
                protocolSHA256=doc['protocolSHA256'],envelope=doc['inputs']['envelope'],runs=ARMS,
                scope='one-run-per-arm-no-export-no-promotion')


def load_protocol(path,arm,run_name,approval_path=None):
    ref=h.ref(h.local(path));doc=sealed(ref)
    h.require(doc==prepare(doc['inputs']),'changed_context_protocol_inputs')
    h.require(arm in ARMS and run_name==ARMS[arm],'context_arm_binding')
    out=h.ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    h.require(not out.exists() and not any(p.is_symlink() for p in (out,*out.parents)), 'output_collision')
    blockers=list(doc['blockers']);ar=None
    if approval_path:
        ar=h.ref(h.local(approval_path));h.require(read(ar)==approval(doc),'context_approval_binding')
    else:blockers.append('missing_tranche_approval')
    report=dict(formatVersion='focus-representative-preflight-v1',protocolVersion=VERSION,
        configurationValid=True,launchEligible=not blockers,executionAuthorized=False,
        releaseEligible=False,blockers=blockers,protocolSHA256=doc['protocolSHA256'],protocolFile=ref,
        approval=ar,arm=arm,contextFeatures=doc['inputs']['contextFeatures'],
        **{k:doc[k] for k in ('configuration','selection','representation','fullFit','counts','runtime',
            'baseCachedInputs','reviewedExtension','baselineTraining','nativeExtension','warmCheckpoint',
            'unmetQualificationBlockers')})
    return report,[dict(r,path=h.checked(h.ROOT,r['crop'])) for r in doc['samples']]


def pooled(features,masks):
    """Mask-area-weighted feature pooling, with no dependence on focus labels."""
    import torch
    # MPS area pooling rejects 432→14 (non-divisible sizes). Resize the small
    # label-free mask on CPU explicitly; encoder features remain on MPS.
    mask=torch.nn.functional.interpolate(masks.cpu(),size=features.shape[-2:],mode='area').to(features.device)
    mass=mask.sum((-2,-1))
    h.require(bool((mass>0).all()),'empty_context_pool')
    return (features*mask).sum((-2,-1))/mass


def tensor_digest(x):
    return hashlib.sha256(x.contiguous().numpy().tobytes()).hexdigest()


def encode(envelope_ref,output):
    e=envelope(envelope_ref);base=verified_base(e['baseProtocol']);doc=verified_context(e['context'],base)
    out=h.fresh(output)
    h.require(len(doc['scenes'])<=693 and len(base['samples'])==1883,'context_encoding_scope')
    started=time.monotonic()
    import torch
    import numpy as np
    from PIL import Image
    from torchvision.models import mobilenet_v3_small
    from focus_pretrained_experiment import state_digest,WEIGHTS_SHA
    h.require(torch.backends.mps.is_available(),'context_requires_mps')
    rep=base['representation'];h.require(rep['weights']['sha256']==WEIGHTS_SHA,'context_encoder_identity')
    network=mobilenet_v3_small(weights=None)
    network.load_state_dict(torch.load(h.checked(h.ROOT,rep['weights']),map_location='cpu',weights_only=True))
    wrapped=torch.nn.Sequential(network.features,network.avgpool).eval().to('mps')
    for p in wrapped.parameters():p.requires_grad_(False)
    before=state_digest(wrapped)
    h.require(before==read(base['baseCachedInputs']['receipt'])['featureStateSHA256'],'context_encoder_state')
    mean=torch.tensor(rep['normalization']['mean'],device='mps').reshape(1,3,1,1)
    std=torch.tensor(rep['normalization']['std'],device='mps').reshape(1,3,1,1)
    members=defaultdict(list)
    for m in doc['members']:members[m['sceneKey']].append(m)
    vectors={};keys=sorted(doc['scenes'])
    with torch.no_grad():
        for start in range(0,len(keys),8):
            h.require(time.monotonic()-started<e['limits']['encodingSeconds'],'context_encoder_deadline')
            batch=keys[start:start+8];pixels=[]
            for key in batch:
                with Image.open(h.checked(h.ROOT,doc['scenes'][key]['scene'])) as im:
                    h.require(im.size==context.SIZE,'context_scene_dimensions')
                    pixels.append(torch.from_numpy(np.array(im.convert('RGB'),copy=True)).permute(2,0,1).float()/255)
            maps=wrapped[0]((torch.stack(pixels).to('mps')-mean)/std)
            for j,key in enumerate(batch):
                feature=maps[j:j+1];global_mean=feature.mean((-2,-1)).cpu().flatten()
                for m in members[key]:
                    with Image.open(h.checked(h.ROOT,m['mask'])) as im:
                        mask=torch.from_numpy(np.array(im,copy=True)).float().reshape(1,1,432,768)/255
                    target=pooled(feature,mask).cpu().flatten()
                    geometry=torch.tensor(m['geometry']['normalizedBounds']+m['geometry']['clipped'],dtype=torch.float32)
                    vectors[m['id']]=torch.cat((global_mean,target,geometry))
            print(f'encoded scenes {min(start+8,len(keys))}/{len(keys)}',flush=True)
    x=torch.stack([vectors[r['id']] for r in base['samples']])
    h.require(x.shape==(1883,1160) and bool(torch.isfinite(x).all()) and state_digest(wrapped)==before,
              'context_encoder_output')
    receipt=dict(version='focus-context-features-v1',envelope=envelope_ref,context=e['context'],
                 ids=[r['id'] for r in base['samples']],featureSHA256=tensor_digest(x),featureStateSHA256=before,
                 backboneUnchanged=True,elapsedSeconds=time.monotonic()-started,sceneCount=len(keys))
    buffer=io.BytesIO();torch.save(dict(receipt=receipt,features=x),buffer)
    h.require(buffer.tell()<=e['limits']['cacheBytes'] and time.monotonic()-started<=300,'context_encoding_budget')
    out.mkdir(parents=True);(out/'features.pt').write_bytes(buffer.getbuffer());h.write(out/'receipt.json',receipt)
    refs=dict(cache=h.ref(out/'features.pt'),receipt=h.ref(out/'receipt.json'));h.write(out/'references.json',refs)
    return refs


def make_head(device):
    import torch
    torch.manual_seed(42)
    head=torch.nn.Sequential(torch.nn.Linear(WIDTH,64),torch.nn.ReLU(),torch.nn.Linear(64,1))
    with torch.no_grad():head[0].weight[:,576:]=0
    return head.to(device)


def fuse(local,extra,arm):
    import torch
    h.require(arm in ARMS and local.shape[0]==extra.shape[0] and local.shape[1]==576
              and extra.shape[1]==1160,'context_fusion_shape')
    result=torch.cat((local,extra),1).clone()
    if arm=='context-local':result[:,576:]=0
    elif arm=='context-geometry':result[:,576:1728]=0
    return result


def prepare_features(report,train,validation,device,output):
    import torch
    _,old,val=native.prepare_features(report,train,validation,device,output)
    refs=report['contextFeatures'];receipt=read(refs['receipt'])
    cache=torch.load(h.checked(h.ROOT,refs['cache']),map_location='cpu',weights_only=True)
    x=cache['features']
    h.require(cache['receipt']==receipt and receipt['ids']==[r['id'] for r in train+validation]
              and x.dtype==torch.float32 and x.shape==(len(train)+len(validation),1160)
              and bool(torch.isfinite(x).all()) and tensor_digest(x)==receipt['featureSHA256'],
              'context_feature_tensors')
    n=len(train);arm=report['arm']
    train_data=torch.utils.data.TensorDataset(fuse(old.tensors[0],x[:n],arm),old.tensors[1])
    val_data=torch.utils.data.TensorDataset(fuse(val.tensors[0],x[n:],arm),val.tensors[1])
    h.write(output/'context-feature-receipt.json',dict(encoderLoaded=False,arm=arm,features=refs,
                                                    inputWidth=WIDTH,hiddenWidth=64))
    return make_head(device),train_data,val_data


def main():
    p=argparse.ArgumentParser(description=__doc__);mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--encode-envelope');mode.add_argument('--inputs');p.add_argument('--output',required=True)
    args=p.parse_args()
    try:
        if args.encode_envelope:
            print(encode(h.ref(h.local(args.encode_envelope)),args.output));return 0
        doc=prepare(h.read(h.local(args.inputs)));out=h.fresh(args.output);out.mkdir(parents=True)
        h.write(out/'protocol.json',doc);h.write(out/'approval.json',approval(doc))
        print(dict(protocolSHA256=doc['protocolSHA256'],blockers=doc['blockers']));return 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print('Context experiment rejected: '+str(error));return 2


if __name__=='__main__':raise SystemExit(main())
