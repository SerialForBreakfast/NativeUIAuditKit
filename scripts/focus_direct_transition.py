"""Direct ordered-image experimental baseline; labels never enter prediction."""
import argparse
from collections import Counter
import os
from pathlib import Path
import re
import time
import sys
from importlib.metadata import version as dependency_version
from PIL import Image
import human_annotation_review as h
from focus_dataset_contract import digest
import focus_transition_learning as old

VERSION='focus-direct-transition-v1'
ARM='transition-direct-pixels'
CONFIG=dict(model=ARM,epochs=30,batch=8,lr=.001,seed=42,maxSeconds=None,
            maxOutputBytes=2*1024**3,width=96,height=64,confidence=.85,
            selection='fixed-last',backend='cpu',optimizer='adam')
LOCALIZATION_CONFIG=dict(CONFIG,boxLoss='giou-l1-v1')
SPATIAL_CONFIG=dict(CONFIG,representation='spatial-cells-v1',boxLoss='cell-ce-offset-size-l1')
SPATIAL_DIAGNOSTIC=dict(SPATIAL_CONFIG,epochs=120,trainingSubset='first-two-per-change')
CONTEXT_CONFIG=dict(SPATIAL_CONFIG,representation='spatial-global-context-v1')
CONTEXT_DIAGNOSTIC=dict(CONTEXT_CONFIG,epochs=120,trainingSubset='first-two-per-change')
GEOMETRY_CONFIG=dict(CONTEXT_CONFIG,boxLoss='cell-ce-geometry-bce-logits')
GEOMETRY_DIAGNOSTIC=dict(GEOMETRY_CONFIG,epochs=120,trainingSubset='first-two-per-change')
OVERLAP_CONFIG=dict(GEOMETRY_CONFIG,boxLoss='cell-ce-geometry-bce-giou')
OVERLAP_DIAGNOSTIC=dict(OVERLAP_CONFIG,epochs=120,trainingSubset='first-two-per-change')
LOGIT_CONFIG=dict(OVERLAP_CONFIG,boxLoss='cell-ce-geometry-logit-smoothl1-giou')
LOGIT_DIAGNOSTIC=dict(LOGIT_CONFIG,epochs=120,trainingSubset='first-two-per-change')
FULL_FIT_CONFIG=dict(LOGIT_CONFIG,epochs=120)
TRANSLATION_CONFIG=dict(FULL_FIT_CONFIG,augmentation='paired-translation-4pct-v1')
EXPOSURE_CONFIG=dict(TRANSLATION_CONFIG,epochs=600)
TEMPORAL_CONFIG=dict(EXPOSURE_CONFIG,changeRepresentation='absolute-difference-v1')
PAIRED_TEMPORAL_CONFIG=dict(TEMPORAL_CONFIG,changeRepresentation='paired-context-difference-v1')
BROAD_CONFIG=dict(TEMPORAL_CONFIG,augmentation='paired-translation-25x15pct-v1')
COMPRESSED_CONFIG=dict(TEMPORAL_CONFIG,augmentation='paired-halfwidth-25x15pct-v1')
COVERAGE_CONFIGURATIONS=(BROAD_CONFIG,COMPRESSED_CONFIG)
TEMPORAL_CONFIGURATIONS=(TEMPORAL_CONFIG,*COVERAGE_CONFIGURATIONS)
TRANSLATION_CONFIGURATIONS=(TRANSLATION_CONFIG,EXPOSURE_CONFIG,*TEMPORAL_CONFIGURATIONS)
SPATIAL_CONFIGURATIONS=(SPATIAL_CONFIG,SPATIAL_DIAGNOSTIC,CONTEXT_CONFIG,CONTEXT_DIAGNOSTIC,
                        GEOMETRY_CONFIG,GEOMETRY_DIAGNOSTIC,OVERLAP_CONFIG,OVERLAP_DIAGNOSTIC,LOGIT_CONFIG,LOGIT_DIAGNOSTIC,FULL_FIT_CONFIG,*TRANSLATION_CONFIGURATIONS)
DIAGNOSTIC_CONFIGURATIONS=(SPATIAL_DIAGNOSTIC,CONTEXT_DIAGNOSTIC,GEOMETRY_DIAGNOSTIC,OVERLAP_DIAGNOSTIC,LOGIT_DIAGNOSTIC)


def valid_configuration(config):
    return config in (CONFIG,LOCALIZATION_CONFIG,*SPATIAL_CONFIGURATIONS)


def box_loss(prediction,target,configuration):
    """Paired normalized cx/cy/w/h; differentiable overlap loss, no truth inputs."""
    torch=torch_runtime()
    h.require(valid_configuration(configuration),'direct_configuration')
    if configuration==CONFIG:return torch.nn.functional.mse_loss(prediction,target)
    p=prediction.reshape(-1,4);t=target.reshape(-1,4)
    plo,phi=p[:,:2]-p[:,2:]/2,p[:,:2]+p[:,2:]/2
    tlo,thi=t[:,:2]-t[:,2:]/2,t[:,:2]+t[:,2:]/2
    intersection=(torch.minimum(phi,thi)-torch.maximum(plo,tlo)).clamp(min=0).prod(dim=1)
    union=p[:,2:].prod(dim=1)+t[:,2:].prod(dim=1)-intersection
    enclosure=(torch.maximum(phi,thi)-torch.minimum(plo,tlo)).clamp(min=0).prod(dim=1)
    giou=intersection/union.clamp(min=1e-8)-(enclosure-union)/enclosure.clamp(min=1e-8)
    return (1-giou).mean()+torch.nn.functional.l1_loss(prediction,target)


def pins():
    return dict(code=[h.ref(h.ROOT/'scripts'/name) for name in
        ('focus_direct_transition.py','focus_transition_learning.py','focus_corrected_transition_audit.py','focus_structural_transition_audit.py',
         'focus_recorded_semantics.py','focus_recorded_readiness.py','human_annotation_review.py',
         'artifact_storage.py','focus_dataset_contract.py','photos_focus_pilot.py','focus_spatial_transition.py',
         'prepare_spatial56.py','prepare_context57.py','prepare_fit61.py','prepare_robustness63.py',
         'focus_pair_translation.py','focus_translation_training.py','prepare_transition_inputs.py',
         'propose_negative_admission65.py','evaluate_retained_negatives64.py',
         'synth05_intake.py','fixture_owned_pairs.py','inventory_transition_sources.py',
         'prepare_data67.py','admit_negatives65.py',
         'focus_temporal_transition.py','prepare_temporal68.py',
         'prepare_coverage70.py',
         'propose_native77.py','propose_native86.py','prepare_collection103.py','evaluate_collection102.py','harvest_sidecar_v2.py',
         'fixture_native_visibility.py','fixture_semantic_inventory.py','fixture_rendered_body.py','intake_native76.py',
         'evaluate_direct_transition.py','train_focus_ring_detector.py')],
        dependencies={name:dependency_version(name) for name in ('torch','numpy','pillow')},python=sys.version)


def geometry(size):
    w,ht=size;scale=min(CONFIG['width']/w,CONFIG['height']/ht)
    rw,rh=max(1,round(w*scale)),max(1,round(ht*scale))
    return rw,rh,(CONFIG['width']-rw)//2,(CONFIG['height']-rh)//2


def pixels(ref):
    path=h.checked(h.ROOT,ref)
    with Image.open(path) as im:
        h.require(im.format=='PNG' and im.width*im.height<=20_000_000,'invalid_endpoint_image')
        im.load();return im.convert('RGB')


def encode(before,after):
    """Pixels only; ordered full frames, no cropper, boxes or metadata features."""
    import numpy as np
    h.require(before.size==after.size,'viewport_changed')
    arrays=[]
    for image in (before,after):
        w,ht,x,y=geometry(image.size);canvas=Image.new('RGB',(96,64))
        canvas.paste(image.resize((w,ht),Image.Resampling.BILINEAR),(x,y))
        arrays.append(np.asarray(canvas,dtype=np.float32).transpose(2,0,1)/255)
    return np.concatenate(arrays,axis=0)


def target_box(bounds,size):
    import math
    h.require(len(bounds)==4 and all(type(v) in (int,float) and math.isfinite(v) for v in bounds),'invalid_box')
    x,y,w,ht=bounds;W,H=size
    h.require(w>0 and ht>0 and x>=0 and y>=0 and x+w<=W and y+ht<=H,'box_outside')
    rw,rh,px,py=geometry(size)
    return [((x+w/2)*rw/W+px)/96,((y+ht/2)*rh/H+py)/64,w*rw/W/96,ht*rh/H/64]


def raw_image_box(values,size):
    import math
    h.require(len(values)==4 and all(math.isfinite(float(v)) for v in values),'invalid_model_box')
    cx,cy,w,ht=values;W,H=size;rw,rh,px,py=geometry(size)
    return [((cx-w/2)*96-px)*W/rw,((cy-ht/2)*64-py)*H/rh,w*96*W/rw,ht*64*H/rh]


def image_box(values,size):
    box=raw_image_box(values,size);W,H=size
    if box[2]<=0 or box[3]<=0 or box[0]<0 or box[1]<0 or box[0]+box[2]>W or box[1]+box[3]>H:return None
    return box


def record(ident,group,role,before,after,changed,evidence,baseline):
    boxes=[];refs=[];hashes=[];size=None
    for frame in (before,after):
        focused=[c for c in frame['controls'] if c['state']=='focused']
        h.require(len(focused)==1,'unique_known_focus_required')
        ref=frame['image'];frame_size,pixel_hash=old.decoded_identity(ref)
        h.require(size is None or size==frame_size,'viewport_changed');size=frame_size
        target_box(focused[0]['bounds'],frame_size)
        boxes.append(focused[0]['bounds']);refs.append(ref);hashes.append(pixel_hash)
    h.require(type(changed)is bool,'change_label_required')
    return dict(id=ident,group=group,sourceRole=role,images=refs,size=list(size),boxes=boxes,
                changed=changed,decodedPixelHashes=hashes,evidence=evidence,
                completeScene=False,baseline=baseline)


def baseline_change(controls,native):
    arm='guardedStability' if native else 'combined'
    values=[c['arms'][arm]['decision'] for c in controls if c['expected'] is not None]
    if not values or any(v in ('unknown','unavailable') for v in values):return None
    if all(v=='unchanged' for v in values):return False
    if values.count('arrival')==values.count('departure')==1:return True
    return None


def collect(sources):
    import focus_corrected_transition_audit as native
    import focus_recorded_semantics as semantic
    h.require({'reference','settings'} <= set(sources) <= {'reference','settings','negatives','nativeTable','nativeActions','nativeCollection'},'source_fields')
    rows=[];excluded=[]
    path=h.checked(h.ROOT,sources['reference']);doc=h.sealed(path,'reference-transition-audit-v1')
    h.require(doc.get('tracker','template')=='template','baseline_tracker')
    root=h.checked(h.ROOT,doc['manifest']).parent
    for pair in doc['pairs']:
        ident=sources['reference']['sha256']+':'+pair['id']
        try:
            h.require(pair['status']=='diagnostic','source_pair_blocked')
            evidence=h.checked(h.ROOT,pair['inputs'][2]);campaign=h.read(h.checked(h.ROOT,pair['inputs'][3]))
            case=next(c for c in campaign['cases'] if c['case_id']==pair['id'])
            raw,b,a=native.validate_case(root,evidence,case)
            h.require(raw.get('cleanup')=='verified','cleanup_unverified')
            h.require(b['image']==pair['inputs'][0] and a['image']==pair['inputs'][1],'changed_source_pixels')
            rows.append(record(ident,'fixture-procedural-renderer-v1','calibration',b,a,b['focus']!=a['focus'],
                pair['inputs'][2:],baseline_change(pair['controls'],True)))
        except (ValueError,KeyError,StopIteration) as e:excluded.append(dict(id=ident,reason=str(e)))
    path=h.checked(h.ROOT,sources['settings']);doc=h.sealed(path,'settings-stability-v1')
    comparison=h.sealed(h.checked(h.ROOT,doc['baseline']),'focus-recorded-comparison-v1')
    sem=h.sealed(h.checked(h.ROOT,comparison['semantics']),'focus-recorded-semantics-v1')
    args={k:str(h.checked(h.ROOT,v)) for k,v in sem['inputs'].items() if k!='events'}
    _,truth,_,_=semantic.inputs(**args)
    semantics={a['actionID']:a for a in sem['actions']}
    for action in doc['actions']:
        ident=sources['settings']['sha256']+':'+action['actionID']
        try:
            b,a=[truth[action['endpoints'][k]['sha256']] for k in ('before','after')]
            relation=semantics[action['actionID']];h.require(relation['sameTitle'],'screen_changed')
            bf=[c for c in b['controls'] if c['state']=='focused'];af=[c for c in a['controls'] if c['state']=='focused']
            h.require(len(bf)==len(af)==1,'unique_known_focus_required')
            match=next(m for m in relation['matches'] if m['before']==bf[0]['id'])
            h.require(match['after'] is not None,'focus_identity_unresolved')
            rows.append(record(ident,'reviewed-settings-journey-v1','development',b,a,match['after']!=af[0]['id'],
                [comparison['semantics'],*sem['inputs'].values()],baseline_change(action['guardedControls'],False)))
        except (ValueError,KeyError,StopIteration) as e:excluded.append(dict(id=ident,reason=str(e)))
    if 'negatives' in sources:
        from propose_negative_admission65 import verified_records
        negative_rows=verified_records(h.checked(h.ROOT,sources['negatives']))
        rows.extend(dict(r,id=sources['negatives']['sha256']+':'+r['id']) for r in negative_rows)
    if 'nativeTable' in sources:
        from propose_native77 import verified_records as native_table_records
        additions=native_table_records(h.checked(h.ROOT,sources['nativeTable']))
        rows.extend(dict(r,id=sources['nativeTable']['sha256']+':'+r['id']) for r in additions)
    if 'nativeActions' in sources:
        from propose_native86 import source_records
        additions=source_records(h.checked(h.ROOT,sources['nativeActions']))
        rows.extend(dict(r,id=sources['nativeActions']['sha256']+':'+r['id']) for r in additions)
    if 'nativeCollection' in sources:
        from prepare_collection103 import source_records as collection_records
        additions=collection_records(h.checked(h.ROOT,sources['nativeCollection']))
        rows.extend(dict(r,id=sources['nativeCollection']['sha256']+':'+r['id']) for r in additions)
    return corpus_document(sources,rows,excluded)


def corpus_document(sources, rows, excluded):
    """Seal already verified records; callers own source validation, not admission."""
    h.require(0<len(rows)<=256 and len({r['id'] for r in rows})==len(rows),'direct_membership')
    result=dict(version='focus-direct-corpus-v1',sources=sources,records=rows,excluded=excluded,
                groups={g:dict(Counter('changed' if r['changed'] else 'unchanged' for r in rows if r['group']==g))
                        for g in sorted({r['group'] for r in rows})},trainingEligible=False)
    result['corpusSHA256']=digest(result);return result


def admitted(corpus,admission):
    h.require(admission.get('version')=='focus-direct-admission-v1' and admission.get('approved') is True and
              admission.get('decisionReference') and admission.get('reviewer') and
              admission.get('corpusSHA256')==corpus['corpusSHA256'],'direct_admission_binding')
    assignments=admission['assignments']
    h.require(set(assignments)=={r['id'] for r in corpus['records']} and
              set(assignments.values())<= {'train','development','excluded'},'direct_assignment_accounting')
    ledgers=[{},{}];rows=[]
    for r in corpus['records']:
        split=assignments[r['id']]
        if split=='excluded':continue
        for ledger,keys in zip(ledgers,([r['group']],[r['id'],*r['decodedPixelHashes'],*(i['sha256'] for i in r['images'])])):
            for key in keys:h.require(ledger.setdefault(key,split)==split,'direct_group_or_pixel_leakage')
        rows.append(dict(r,split=split))
    return rows


def load_protocol(path,arm,run_name,approval_path=None):
    doc=h.read(h.local(path));h.require(doc.get('version')==VERSION and valid_configuration(doc.get('configuration')),'direct_configuration')
    h.require(arm==ARM and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',run_name),'direct_arm_name')
    h.require(doc.get('protocolSHA256')==digest({k:v for k,v in doc.items() if k!='protocolSHA256'}),'direct_protocol_hash')
    h.require(doc['implementation']==h.ref(Path(__file__)),'direct_implementation_changed')
    h.require(doc['pins']==pins(),'direct_dependency_or_code_changed')
    if doc.get('preparedInputs') is not None:
        from prepare_transition_inputs import manifest,load
        prepared_path=h.checked(h.ROOT,doc['preparedInputs'])
        prepared,corpus,prepared_rows=manifest(prepared_path)
        h.require(prepared['admission']==doc.get('admission') and corpus['sources']==doc['sources'] and
            doc['configuration'] in TRANSLATION_CONFIGURATIONS,'prepared_protocol_binding')
        load(prepared_path,[r for r in prepared_rows if r['split']=='train'],doc['configuration']['augmentation'])
    else:corpus=collect(doc['sources'])
    h.require(corpus['corpusSHA256']==doc['corpusSHA256'],'direct_corpus_changed')
    out=old.fresh_run(run_name);rows=[];blockers=[]
    if doc.get('admission') is None:blockers.append('missing_exact_data_role_admission')
    else:rows=admitted(corpus,h.read(h.checked(h.ROOT,doc['admission'])))
    if doc['configuration']==SPATIAL_CONFIG:
        h.require(doc.get('diagnosticGate') is not None,'missing_memorization_gate')
        from prepare_spatial56 import verify_gate
        verify_gate(doc['diagnosticGate'],corpus,rows)
    if doc['configuration'] in (CONTEXT_CONFIG,GEOMETRY_CONFIG,OVERLAP_CONFIG,LOGIT_CONFIG):
        h.require(doc.get('diagnosticGate') is not None,'missing_memorization_gate')
        from prepare_context57 import verify_gate
        verify_gate(doc['diagnosticGate'],corpus,rows,
                    next(c for c in DIAGNOSTIC_CONFIGURATIONS if c['boxLoss']==doc['configuration']['boxLoss'] and c['representation']==doc['configuration']['representation']))
    if doc['configuration']==FULL_FIT_CONFIG:
        h.require(doc.get('diagnosticGate') is not None,'missing_memorization_gate')
        from prepare_fit61 import verify_gate
        verify_gate(doc['diagnosticGate'],corpus,rows)
    if doc['configuration'] in TRANSLATION_CONFIGURATIONS:
        if doc.get('expandedGate') is not None:
            h.require(doc['configuration'] in (EXPOSURE_CONFIG,*TEMPORAL_CONFIGURATIONS),'expanded_configuration')
            from prepare_data67 import verify_gate
            verify_gate(doc['expandedGate'],corpus,rows,doc['admission'])
        else:
            from prepare_robustness63 import verify_gate
            verify_gate(doc.get('diagnosticGate'),corpus,rows)
    if doc['configuration'] in TEMPORAL_CONFIGURATIONS:
        from prepare_temporal68 import verify_gate
        verify_gate(doc.get('temporalGate'),corpus,rows)
    if doc['configuration'] in COVERAGE_CONFIGURATIONS:
        from prepare_coverage70 import verify_gate
        verify_gate(doc.get('coverageGate'),corpus,rows)
    for split in ('train','development'):
        if {r['changed'] for r in rows if r['split']==split}!={True,False}:blockers.append(split+'_missing_change_states')
    approval=None
    if approval_path is None:blockers.append('missing_execution_approval')
    else:
        approval=h.ref(h.local(approval_path));a=h.read(h.checked(h.ROOT,approval))
        h.require(a.get('version')=='focus-direct-approval-v1' and a.get('approved')is True and
                  a.get('protocolSHA256')==doc['protocolSHA256'] and a.get('arm')==ARM and
                  a.get('runName')==run_name and a.get('decisionReference'),'direct_execution_binding')
    return dict(formatVersion='focus-direct-preflight-v1',protocolVersion=VERSION,
        configurationValid=True,launchEligible=not blockers,blockers=blockers,configuration=doc['configuration'],
        protocolFile=h.ref(h.local(path)),protocolSHA256=doc['protocolSHA256'],approval=approval,
        corpusSHA256=corpus['corpusSHA256'],output=str(out.relative_to(h.ROOT)),arm=ARM,
        releaseEligible=False,executionAuthorized=False),rows


def torch_runtime():
    for name,folder in [('TORCH_HOME','.build/direct53-torch'),('TMPDIR','.build/direct53-tmp')]:
        path=h.ROOT/folder;path.mkdir(parents=True,exist_ok=True);os.environ[name]=str(path)
    import torch
    return torch


def model(configuration=None):
    torch=torch_runtime();nn=torch.nn
    configuration=CONFIG if configuration is None else configuration
    if configuration in (*TEMPORAL_CONFIGURATIONS,PAIRED_TEMPORAL_CONFIG):
        from focus_temporal_transition import make_model
        return make_model(torch,configuration==PAIRED_TEMPORAL_CONFIG)
    h.require(valid_configuration(configuration),'direct_configuration')
    if configuration in SPATIAL_CONFIGURATIONS:
        from focus_spatial_transition import make_model
        return make_model(torch,configuration['representation']=='spatial-global-context-v1')
    return nn.Sequential(nn.Conv2d(6,8,3,2,1),nn.ReLU(),nn.Conv2d(8,16,3,2,1),nn.ReLU(),
        nn.Conv2d(16,24,3,2,1),nn.ReLU(),nn.Flatten(),nn.Linear(24*8*12,64),nn.ReLU(),nn.Linear(64,9))


def training_rows(rows,configuration):
    if configuration not in DIAGNOSTIC_CONFIGURATIONS:return rows
    ordered=sorted(rows,key=lambda r:r['id'])
    selected=[r for state in (False,True) for r in [v for v in ordered if v['changed']==state][:2]]
    h.require(len(selected)==4 and all(r.get('split')=='train' for r in selected),'diagnostic_train_subset')
    return selected


def fit(rows,configuration=None,prepared_inputs=None):
    import numpy as np
    configuration=CONFIG if configuration is None else configuration
    h.require(valid_configuration(configuration),'direct_configuration')
    h.require(prepared_inputs is None or configuration in TRANSLATION_CONFIGURATIONS,'prepared_configuration')
    h.require(rows and {r['changed'] for r in rows}=={False,True},'training_change_states')
    rows=training_rows(rows,configuration)
    torch=torch_runtime();torch.manual_seed(configuration['seed']);torch.set_num_threads(2)
    net=model(configuration);optimizer=torch.optim.Adam(net.parameters(),lr=configuration['lr'])
    choices=None
    if configuration in TRANSLATION_CONFIGURATIONS:
        from focus_translation_training import bank,schedule,receipt
        xa,ya,options,entries,rejected=training_bank(rows,prepared_inputs,configuration['augmentation'])
        x,y=torch.from_numpy(xa),torch.from_numpy(ya)
        choices=schedule(options,configuration['epochs'],configuration['seed'])
        net.training_augmentation=receipt(choices,entries,rejected,configuration['augmentation'])
    else:
        x=torch.from_numpy(np.stack([encode(*(pixels(i) for i in r['images'])) for r in rows]))
        y=torch.tensor([[*target_box(r['boxes'][0],r['size']),*target_box(r['boxes'][1],r['size']),float(r['changed'])] for r in rows])
    history=[]
    for epoch in range(configuration['epochs']):
        order=torch.randperm(len(rows));losses=[]
        for ids in order.split(configuration['batch']):
            if choices is not None:ids=torch.tensor([choices[epoch][i] for i in ids.tolist()])
            optimizer.zero_grad()
            if configuration in SPATIAL_CONFIGURATIONS:
                from focus_spatial_transition import loss as spatial_loss
                loss=spatial_loss(torch,net,x[ids],y[ids],
                    geometry_logits=configuration['boxLoss'] in ('cell-ce-geometry-bce-logits','cell-ce-geometry-bce-giou'),
                    overlap=configuration['boxLoss'] in ('cell-ce-geometry-bce-giou','cell-ce-geometry-logit-smoothl1-giou'),
                    logit_regression=configuration['boxLoss']=='cell-ce-geometry-logit-smoothl1-giou')
            else:
                out=net(x[ids])
                loss=box_loss(out[:,:8].sigmoid(),y[ids,:8],configuration)+torch.nn.functional.binary_cross_entropy_with_logits(out[:,8],y[ids,8])
            h.require(bool(torch.isfinite(loss)),'nonfinite_direct_loss');loss.backward();optimizer.step();losses.append(float(loss.detach()))
        history.append(dict(epoch=epoch+1,trainingLoss=sum(losses)/len(losses)))
        if choices is not None:
            history[-1]['augmentationCounts']=dict(Counter(entries[i]['condition'] for i in choices[epoch]))
    return net.eval(),history


def fit_change_head(net, x, labels, configuration):
    """Fine-tune only the existing change submodule; no geometry gradients or updates."""
    torch=torch_runtime();torch.set_num_threads(configuration['threads']);torch.manual_seed(configuration['seed'])
    width,height=configuration.get('inputSize',[96,64])
    h.require((width,height) in ((96,64),(192,128)) and x.ndim==4 and x.shape[1:]==(6,height,width) and labels.shape==(len(x),) and
        torch.isfinite(x).all() and torch.isfinite(labels).all() and
        ((x>=0)&(x<=1)).all() and ((labels==0)|(labels==1)).all(),'change_adaptation_inputs')
    for name,param in net.named_parameters():param.requires_grad_(name.startswith('change.'))
    frozen={name:value.detach().clone() for name,value in net.state_dict().items() if not name.startswith('change.')}
    optimizer=torch.optim.Adam(net.change.parameters(),lr=configuration['lr'])
    differences=net.change_inputs(x);history=[];net.train()
    group=configuration.get('originalGroupCount')
    if group is not None:
        h.require(type(group)is int and 0<group<len(x) and
            configuration.get('lossWeighting')=='equal-group-means' and
            len(x)-group==configuration.get('derivedGroupCount') and
            (labels[group:]==0).all() and torch.equal(x[group:,:3],x[group:,3:]),'change_derived_group')
    for epoch in range(configuration['epochs']):
        optimizer.zero_grad();logits=net.change(differences).flatten()
        losses=torch.nn.functional.binary_cross_entropy_with_logits(logits,labels,reduction='none')
        loss=losses.mean() if group is None else .5*(losses[:group].mean()+losses[group:].mean())
        h.require(bool(torch.isfinite(loss)),'change_adaptation_nonfinite_loss')
        loss.backward();optimizer.step();history.append(dict(epoch=epoch+1,loss=float(loss.detach())))
    h.require(all(torch.equal(value,net.state_dict()[name]) for name,value in frozen.items()),'change_adaptation_geometry_changed')
    return net.eval(),history


def training_bank(rows,prepared_inputs=None,policy='paired-translation-4pct-v1'):
    if prepared_inputs is None:
        from focus_translation_training import bank
        return bank(rows,policy)
    from prepare_transition_inputs import load
    return load(h.checked(h.ROOT,prepared_inputs),rows,policy)


def infer(net,before,after):
    torch=torch_runtime();start=time.monotonic()
    result=infer_encoded(net,encode(before,after),before.size)
    result['elapsedSeconds']=time.monotonic()-start
    return result


def infer_encoded(net,encoded,size):
    """Internal image-only encoding boundary, shared by frozen model comparisons."""
    import numpy as np
    h.require(isinstance(encoded,np.ndarray) and encoded.dtype==np.float32 and encoded.shape==(6,64,96) and
        np.isfinite(encoded).all() and ((encoded>=0)&(encoded<=1)).all(),'invalid_encoded_input')
    h.require(len(size)==2 and all(type(v)is int and v>0 for v in size) and size[0]*size[1]<=20_000_000,'invalid_image_size')
    torch=torch_runtime();start=time.monotonic()
    with torch.inference_mode():values=net(torch.from_numpy(encoded).unsqueeze(0)).sigmoid()[0].tolist()
    h.require(len(values)==9 and all(0<=v<=1 for v in values),'invalid_direct_output')
    boxes=[image_box(values[i:i+4],size) for i in (0,4)];prob=values[8]
    decision=('changed' if prob>=.5 else 'unchanged') if max(prob,1-prob)>=CONFIG['confidence'] and all(boxes) else 'unknown'
    return dict(boxes=boxes,changeProbability=prob,decision=decision,elapsedSeconds=time.monotonic()-start,
                scope='known-focus-localization-only',controlIssued=False,releaseEligible=False)


def run(report,experiment_id):
    from focus_recorded_transition_eval import iou
    start=time.monotonic();fresh,rows=load_protocol(h.checked(h.ROOT,report['protocolFile']),ARM,
        Path(report['output']).name,h.checked(h.ROOT,report['approval']))
    h.require(fresh==report and fresh['launchEligible'],'direct_preflight_changed')
    validated=time.monotonic()
    out=old.fresh_run(Path(report['output']).name);out.mkdir(parents=True)
    h.write(out/'execution.json',dict(experimentID=experiment_id,protocol=report['protocolFile'],status='started',pid=os.getpid()))
    fit_started=time.monotonic()
    protocol=h.read(h.checked(h.ROOT,report['protocolFile']))
    net,history=fit([r for r in rows if r['split']=='train'],report['configuration'],protocol.get('preparedInputs'));torch=torch_runtime()
    fitted=time.monotonic()
    torch.save(dict(version=VERSION,configuration=report['configuration'],state=net.state_dict()),out/'last.pt')
    results=[]
    score_started=time.monotonic()
    for r in rows:
        if r['split']!='development':continue
        p=infer(net,*(pixels(i) for i in r['images']))
        overlaps=[iou(b,t) if b else 0 for b,t in zip(p['boxes'],r['boxes'])]
        results.append(dict(id=r['id'],prediction=p,expectedChange=r['changed'],boxIoUs=overlaps,
            rawChangeCorrect=(p['changeProbability']>=.5)==r['changed'],bothBoxesCorrect=min(overlaps)>=.5,
            baseline=r['baseline']))
    h.require(sum(p.stat().st_size for p in out.iterdir())<CONFIG['maxOutputBytes'],'direct_output_budget')
    h.write(out/'result.json',dict(version='focus-direct-result-v1',experimentID=experiment_id,pid=os.getpid(),model=h.ref(out/'last.pt'),
        trainingIDs=[r['id'] for r in training_rows([r for r in rows if r['split']=='train'],report['configuration'])],
        protocol=report['protocolFile'],results=results,summary=summarize(results),history=history,
        augmentation=getattr(net,'training_augmentation',None),
        phaseTiming=dict(intakeSeconds=validated-start,fitSeconds=fitted-fit_started,
            checkpointSeconds=score_started-fitted,scoringSeconds=time.monotonic()-score_started,
            scope='Run wrapper only; initial CLI preflight excluded. Fit includes tensor preparation and optimizer initialization.'),
        elapsedSeconds=time.monotonic()-start,**h.FLAGS))
    h.require(sum(p.stat().st_size for p in out.iterdir())<CONFIG['maxOutputBytes'],'direct_output_budget')
    return 0


def summarize(results):
    def counts(rows):
        decided=[r for r in rows if r['prediction']['decision']!='unknown']
        baseline=[r for r in rows if r['baseline'] is not None]
        return dict(pairs=len(rows),rawChangeCorrect=sum(r['rawChangeCorrect'] for r in rows),
            bothBoxesCorrect=sum(r['bothBoxesCorrect'] for r in rows),
            jointCorrect=sum(r['bothBoxesCorrect'] and r['rawChangeCorrect'] for r in decided),
            decided=len(decided),abstained=len(rows)-len(decided),
            baselineDecided=len(baseline),baselineCorrect=sum(r['baseline']==r['expectedChange'] for r in baseline))
    return dict(all=counts(results),byChange={str(label):counts([r for r in results if r['expectedChange']==label])
        for label in (False,True)},limitation='Known-focus development pairs; not calibrated probabilities or full-scene coverage.')


def predict(request,checkpoint):
    h.require(set(request)=={'version','before','after','context'} and request['version']=='focus-direct-request-v1','direct_request_fields')
    h.require(set(request['context'])=={'sameScene','settled','fresh'} and
              all(type(v)is bool for v in request['context'].values()),'direct_context')
    if not all(request['context'].values()):return dict(decision='unavailable',reason='context_unverified')
    torch=torch_runtime();path=h.local(checkpoint);h.require(path.stat().st_size<=CONFIG['maxOutputBytes'],'checkpoint_size')
    state=torch.load(path,map_location='cpu',weights_only=True)
    h.require(state['version']==VERSION and valid_configuration(state['configuration']),'direct_model_contract')
    net=model(state['configuration']);net.load_state_dict(state['state'],strict=True);net.eval()
    return dict(infer(net,pixels(request['before']),pixels(request['after'])),model=h.ref(path))


def main():
    p=argparse.ArgumentParser(description=__doc__);m=p.add_mutually_exclusive_group(required=True)
    m.add_argument('--sources');m.add_argument('--request');p.add_argument('--model');p.add_argument('--output',required=True)
    a=p.parse_args();out=h.fresh(a.output)
    if a.request:
        h.require(a.model is not None,'model_required');h.write(out,predict(h.read(h.local(a.request)),a.model));return
    h.require(a.model is None,'model_requires_request');corpus=collect(h.read(h.local(a.sources)))
    protocol=dict(version=VERSION,sources=corpus['sources'],corpusSHA256=corpus['corpusSHA256'],admission=None,
                  configuration=CONFIG,implementation=h.ref(Path(__file__)),pins=pins())
    protocol['protocolSHA256']=digest(protocol);out.mkdir(parents=True)
    h.write(out/'inventory.json',corpus);h.write(out/'protocol.json',protocol)
    h.write(out/'admission-proposal.json',dict(version='focus-direct-admission-v1',approved=False,
        reviewer=None,decisionReference=None,corpusSHA256=corpus['corpusSHA256'],
        assignments={r['id']:'train' if r['group']=='fixture-procedural-renderer-v1' else 'development' for r in corpus['records']},
        limitation='Proposal only. Native calibration role needs explicit approval; exposed Settings is development, not final evaluation.'))
    print('usable pairs',len(corpus['records']),'excluded',len(corpus['excluded']),corpus['groups'])


if __name__=='__main__':main()
