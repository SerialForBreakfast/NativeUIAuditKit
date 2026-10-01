"""Reviewed additions → sealed protocol; encoding requires separate explicit approval."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
import re
import time

import human_annotation_review as h
import human_review_audit as review
import focus_full_fit_experiment as full
from focus_dataset_contract import digest
from human_corpus_inventory import metadata_hashes

VERSION='focus-reviewed-full-fit-v1'
ARM='reviewed-full-fit'
BASE_SEAL='b650da4919583d57180ca0f29c6577529c2b6984f7582ce0c2c3ab695b5644b7'


def checked(ref):
    return h.read(h.checked(h.ROOT,ref))


def sealed(ref,key):
    doc=checked(ref); content=dict(doc); seal=content.pop(key)
    h.require(digest(content)==seal,'changed_seal'); return doc


def pixels(row):
    return row.get('pixelSHA256',row['crop'].get('pixelSHA256'))


def weights(base, additions):
    train=[r for r in base['samples'] if r['split']=='train']+additions
    h.require(len({r['id'] for r in train})==len(train),'duplicate_training_id')
    native=[r for r in train if r['use']=='train-candidate']
    human=[r for r in train if r['use']=='human-static-auxiliary']
    h.require(len(native)+len(human)==len(train),'unsupported_training_role')
    result={r['id']:base['fullFit']['weights'][r['id']] for r in native}
    h.require(math.isclose(sum(result.values()),.8),'changed_native_mass')
    groups=defaultdict(lambda:defaultdict(list)); labels={}
    for r in train:
        px=pixels(r); y=r['label']
        h.require(px and type(y) is int and y in (0,1),'invalid_label_or_pixels')
        h.require(px not in labels or labels[px]==y,'conflicting_duplicate_labels');labels[px]=y
    for r in human:
        h.require('pairID' not in r,'fabricated_human_pair')
        groups[r['frameID'],r['label']][pixels(r)].append(r['id'])
    frames={r['frameID'] for r in human}
    h.require(frames and set(groups)=={(f,y) for f in frames for y in (0,1)},'missing_human_frame_label_bucket')
    for buckets in groups.values():
        for ids in buckets.values():
            for sid in ids: result[sid]=.2/(2*len(frames)*len(buckets)*len(ids))
    h.require(math.isclose(sum(result.values()),1),'invalid_weight_mass')
    for y in (0,1):
        h.require(math.isclose(sum(result[r['id']] for r in train if r['label']==y),.5),'unbalanced_label_mass')
    return train,result


def admit(report, decision, revision_ref, crops_ref, base, batch, forbidden):
    h.require(report['reviewer']['kind']=='human' and report['reviewer']['confirmedBatch'] is True,'human_review_required')
    h.require(decision.get('version')=='focus-static-addition-admission-v1' and decision.get('approved') is True
              and decision.get('reviewer') and decision.get('authorizationReference'),'missing_explicit_admission')
    h.checked(h.ROOT,decision['authorizationReference'])
    h.require(decision['revision']==revision_ref and decision['crops']==crops_ref
              and decision['baseline']==base['protocolSHA256'] and decision['sessionID']==batch['sessionID'], 'stale_admission_binding')
    relation=decision['sourceReview']
    h.checked(h.ROOT,relation['evidence'])
    h.require(relation['decision']=='development-exposed-no-independent-claim'
              and relation['protectedRolesUnchanged'] is True and relation['developmentMembershipUnchanged'] is True,
              'source_relationship_review_required')
    indexed={s['id']:s for s in report['samples']}
    chosen=decision['selectedIDs']; excluded=decision['excluded']
    h.require(chosen and len(set(chosen))==len(chosen) and not set(chosen)&set(excluded)
              and set(chosen)|set(excluded)==set(indexed) and all(isinstance(v,str) and v.strip() for v in excluded.values()),'admission_membership')
    h.require(not any(i['severity']=='hard' and set(i['samples'])&set(chosen) for i in report['issues']),'unresolved_review_issue')
    frames={f['id']:f for f in report['frames']}; rows=[]
    existing={pixels(r) for r in base['samples']}
    # Reserved roles are checked against both original frame and crop pixels.
    for sid in chosen:
        s=indexed[sid];f=frames[s['frameID']]
        h.require(s['disposition']=='reviewed' and s['state'] in ('focused','unfocused'),'unconfirmed_selected_control')
        h.require(s['pixelSHA256'] not in existing,'baseline_duplicate_crop')
        h.require(not {s['pixelSHA256'],f['pixelSHA256']}&forbidden,'protected_or_validation_overlap')
        row=dict(s,id='added:'+batch['id']+':'+sid,frameID='added:'+batch['id']+':'+s['frameID'],
                 image=f['image'],sourceSessionID=batch['sessionID'],label=int(s['state']=='focused'),
                 control=h.control_label(s),split='train',use='human-static-auxiliary',
                 labelSource='human-reviewed-static',pairedTransitionEligible=False)
        rows.append(row)
    return rows


def assemble(spec):
    h.require(spec['version']=='focus-review-continuation-input-v1','unsupported_inputs')
    base=sealed(spec['baseline'],'protocolSHA256')
    h.require(base['version']=='focus-full-fit-v1' and base['protocolSHA256']==BASE_SEAL,'wrong_baseline')
    for key in ('cache','receipt','preflight'):
        h.checked(h.ROOT,base['inputs'][key])
    batch=h.validate_batch(h.checked(h.ROOT,spec['batch']))
    h.require(batch['sessionID']==full.s.SESSION,'unapproved_source_session')
    # Check referenced pixels without invoking the historical trainer or its output guard.
    verified=set()
    for r in base['samples']:
        for ref in (r['crop'],r.get('frame',r.get('image'))):
            if ref['path'] not in verified:
                h.checked(h.ROOT,ref);verified.add(ref['path'])
        h.require(h.pixel_digest(h.ROOT,r['crop'])==pixels(r),'changed_baseline_pixels')
    static=sealed(base['inputs']['base'],'protocolSHA256')
    assembly=sealed(static['inputs']['assembly'],'assemblySHA256')
    protected=metadata_hashes(checked(assembly['protectedMetadata']))
    reserved=sealed(assembly['reservedPixels'],'seal')
    forbidden=protected|{v for r in reserved['samples'] for v in (r['framePixelSHA256'],r['crop']['pixelSHA256'])}
    validation=[r for r in base['samples'] if r['split']=='validation']
    forbidden|={pixels(r) for r in validation}
    blockers=[]; additions=[]; accounting=None
    if not spec.get('revision'): blockers.append('missing_human_review_revision')
    elif not spec.get('crops'): blockers.append('missing_production_crop_qa')
    else:
        revision=h.read_revision(h.checked(h.ROOT,spec['revision']))
        h.require(revision['batch']==spec['batch'],'wrong_review_batch')
        report=review.audit(h.checked(h.ROOT,spec['revision']),h.checked(h.ROOT,spec['crops']))
        accounting=dict(counts=report['counts'],issues=report['issues'])
        if not spec.get('admission'): blockers.append('missing_explicit_admission_and_source_review')
        else: additions=admit(report,checked(spec['admission']),spec['revision'],spec['crops'],base,batch,forbidden)
    train,loss_weights=weights(base,additions)
    if not additions: blockers.append('no_admitted_new_controls')
    features=spec.get('newFeatures')
    if not features: blockers.append('missing_new_feature_cache')
    else:
        receipt=checked(features['receipt']);h.checked(h.ROOT,features['cache'])
        h.require(receipt['version']=='focus-static-addition-features-v1' and
                  receipt['members']==[dict(id=r['id'],label=r['label'],crop=r['crop']) for r in additions]
                  and receipt['representation']==base['representation'] and receipt['backboneUnchanged'] is True,
                  'changed_feature_membership_or_representation')
        h.require(re.fullmatch('[0-9a-f]{64}',receipt.get('featureSHA256','')) is not None,'missing_feature_hash')
        h.require(receipt.get('featureStateSHA256')==checked(base['inputs']['receipt'])['featureStateSHA256'],
                  'changed_encoder_state')
    cfg={**base['configuration'],'batch':len(train)}
    runtime=full.s.rep.retention.runtime_identity()
    runtime['code'] += [full.s.a.reference(h.ROOT/'scripts'/n) for n in
                       ('focus_review_continuation.py','focus_full_fit_experiment.py','human_review_audit.py','human_annotation_review.py')]
    doc=dict(version=VERSION,inputs=spec,samples=train+validation,configuration=cfg,
             selection=base['selection'],representation=base['representation'],warmCheckpoint=None,
             runtime=runtime,counts=dict(training=len(train),added=len(additions),development=base['counts']['development'],retention=base['counts']['retention']),
             fullFit={**base['fullFit'],'weights':loss_weights},baseCachedInputs=base['inputs'],
             reviewAccounting=accounting,blockers=blockers,releaseEligible=False,
             unmetQualificationBlockers=base['unmetQualificationBlockers'])
    doc['protocolSHA256']=digest(doc);return doc


def load_protocol(path,arm,run_name,approval_path=None):
    ref=h.ref(h.local(path));doc=sealed(ref,'protocolSHA256')
    h.require(doc['version']==VERSION and doc==assemble(doc['inputs']),'changed_reviewed_protocol')
    h.require(arm==ARM and isinstance(run_name,str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',run_name),'wrong_reviewed_arm_or_run')
    out=h.ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    h.require(not out.exists() and not any(p.is_symlink() for p in (out,*out.parents)),'output_collision')
    blockers=list(doc['blockers']);approval_ref=None
    if not approval_path: blockers.append('missing_run_approval')
    else:
        approval_ref=h.ref(h.local(approval_path));approval=checked(approval_ref)
        h.require(approval.get('version')=='focus-reviewed-full-fit-approval-v1' and approval.get('approved') is True
                  and approval.get('protocolSHA256')==doc['protocolSHA256'] and approval.get('arm')==arm
                  and approval.get('runName')==run_name and approval.get('scope')=='one-run-no-export-no-promotion'
                  and approval.get('authorizationReference'),'stale_or_missing_run_approval')
        h.checked(h.ROOT,approval['authorizationReference'])
    rows=[{**r,'path':h.checked(h.ROOT,r['crop'])} for r in doc['samples']]
    return dict(formatVersion=full.s.rep.FORMAT,protocolVersion=VERSION,configurationValid=True,
                executionAuthorized=False,launchEligible=not blockers,blockers=blockers,releaseEligible=False,
                **{k:doc[k] for k in ('configuration','selection','representation','warmCheckpoint','runtime','counts','fullFit','protocolSHA256','unmetQualificationBlockers','baseCachedInputs')},
                reviewedExtension=doc['inputs'].get('newFeatures'),protocolFile=ref,approval=approval_ref,arm=arm),rows


def prepare_features(report,train,validation,device,output):
    import torch
    spec=report['baseCachedInputs'];base=checked(spec['base'])
    old_train=[r for r in base['samples'] if r['split']=='train']
    old_val=[r for r in base['samples'] if r['split']=='validation']
    cache=torch.load(h.checked(h.ROOT,spec['cache']),map_location='cpu',weights_only=True)
    original_receipt=checked(spec['receipt'])
    full.s.paired.validate_tensors(cache,original_receipt,old_train,old_val)
    h.require([r['id'] for r in train[:len(old_train)]]==[r['id'] for r in old_train]
              and [r['id'] for r in validation]==[r['id'] for r in old_val],'changed_cached_order')
    extra=train[len(old_train):];spec=report['reviewedExtension'];receipt=checked(spec['receipt'])
    h.require(receipt.get('members')==[dict(id=r['id'],label=r['label'],crop=r['crop']) for r in extra]
              and receipt.get('featureStateSHA256')==original_receipt['featureStateSHA256'],
              'changed_extra_membership_or_encoder')
    cached=torch.load(h.checked(h.ROOT,spec['cache']),map_location='cpu',weights_only=True)
    h.require(cached['receipt']==receipt,'changed_extra_receipt')
    x,y=cached['train']
    h.require(x.dtype==torch.float32 and y.dtype==torch.float32 and x.shape==(len(extra),576)
              and y.shape==(len(extra),1) and bool(torch.isfinite(x).all())
              and torch.equal(y,torch.tensor([[r['label']] for r in extra],dtype=torch.float32)),'invalid_extra_features')
    h.require(hashlib.sha256(x.contiguous().numpy().tobytes()).hexdigest()==receipt['featureSHA256'],'changed_extra_features')
    torch.manual_seed(42);head=torch.nn.Linear(576,1).to(device)
    joined=torch.utils.data.TensorDataset(torch.cat([cache['train'][0],x]),torch.cat([cache['train'][1],y]))
    h.write(output/'reviewed-feature-receipt.json',dict(encoderLoaded=False,baseline=report['baseCachedInputs'],addition=spec,trainCount=len(train),validationCount=len(validation)))
    return head,joined,torch.utils.data.TensorDataset(*cache['validation'])


def encode_new(protocol_path,approval_path,output):
    """Separately authorized encoding only; never optimize weights or select a model."""
    doc=sealed(h.ref(h.local(protocol_path)),'protocolSHA256')
    h.require(doc==assemble(doc['inputs']),'changed_encoding_protocol')
    h.require(doc['counts']['added']>0 and doc['blockers']==['missing_new_feature_cache'],'encoding_data_not_ready')
    approval=checked(h.ref(h.local(approval_path)))
    h.require(approval.get('version')=='focus-addition-encoding-approval-v1' and approval.get('approved') is True
              and approval.get('protocolSHA256')==doc['protocolSHA256']
              and approval.get('scope')=='encode-new-controls-only-no-training'
              and approval.get('authorizationReference'),'missing_encoding_approval')
    h.checked(h.ROOT,approval['authorizationReference'])
    out=h.fresh(output)
    import torch
    import numpy as np
    from PIL import Image
    from torchvision.models import mobilenet_v3_small
    from focus_pretrained_experiment import encode, WEIGHTS_SHA
    h.require(torch.backends.mps.is_available(),'encoding_requires_mps')
    rows=[r for r in doc['samples'] if r['id'].startswith('added:')]
    h.require(len(rows)==doc['counts']['added'],'encoding_membership')
    rep=doc['representation'];h.require(rep['weights']['sha256']==WEIGHTS_SHA,'wrong_encoder_weights')
    class Crops(torch.utils.data.Dataset):
        def __len__(self):return len(rows)
        def __getitem__(self,index):
            with Image.open(h.checked(h.ROOT,rows[index]['crop'])) as im:
                h.require(im.size==(256,256),'wrong_crop_dimensions')
                x=torch.from_numpy(np.array(im.convert('RGB'),copy=True)).permute(2,0,1).float()/255
            return x,torch.tensor([rows[index]['label']],dtype=torch.float32)
    started=time.monotonic();network=mobilenet_v3_small(weights=None)
    network.load_state_dict(torch.load(h.checked(h.ROOT,rep['weights']),map_location='cpu',weights_only=True),strict=True)
    device=torch.device('mps');features=torch.nn.Sequential(network.features,network.avgpool).to(device)
    encoded,state=encode(features,Crops(),device,started+300)
    old_receipt=checked(doc['baseCachedInputs']['receipt'])
    h.require(state==old_receipt['featureStateSHA256'],'encoder_state_differs_from_baseline')
    receipt=dict(version='focus-static-addition-features-v1',members=[dict(id=r['id'],label=r['label'],crop=r['crop']) for r in rows],
                 representation=rep,backboneUnchanged=True,featureStateSHA256=state,
                 featureSHA256=hashlib.sha256(encoded.tensors[0].contiguous().numpy().tobytes()).hexdigest(),
                 protocolSHA256=doc['protocolSHA256'],device='mps',elapsedSeconds=time.monotonic()-started)
    out.mkdir(parents=True);h.write(out/'receipt.json',receipt)
    torch.save(dict(receipt=receipt,train=encoded.tensors),out/'features.pt')
    h.write(out/'features-reference.json',dict(cache=h.ref(out/'features.pt'),receipt=h.ref(out/'receipt.json')))
    return out/'features-reference.json'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline');p.add_argument('--batch');p.add_argument('--output',required=True)
    p.add_argument('--encode-protocol');p.add_argument('--encoding-approval')
    p.add_argument('--revision');p.add_argument('--crops');p.add_argument('--admission');p.add_argument('--new-features')
    p.add_argument('--crop-qa',action='store_true',help='Generate production crops from an explicit reviewed revision; never annotate')
    args=p.parse_args()
    if args.encode_protocol:
        h.require(args.encoding_approval and not any((args.baseline,args.batch,args.revision,args.crops,args.admission,args.new_features,args.crop_qa)),'encoding_arguments')
        print(encode_new(args.encode_protocol,args.encoding_approval,args.output));return 0
    h.require(args.baseline and args.batch and not args.encoding_approval,'baseline_and_batch_required')
    out=h.fresh(args.output);out.mkdir(parents=True)
    spec=dict(version='focus-review-continuation-input-v1',baseline=h.ref(h.local(args.baseline)),batch=h.ref(h.local(args.batch)))
    for key in ('revision','crops','admission'):
        if getattr(args,key): spec[key]=h.ref(h.local(getattr(args,key)))
    try:
        if args.crop_qa:
            h.require(args.revision and not args.crops,'explicit_revision_required_for_crop_qa')
            revision=h.read_revision(h.local(args.revision))
            h.require(revision['reviewer']['kind']=='human' and revision['reviewer']['confirmedBatch'] is True,'human_review_required')
            h.crop_qa(h.local(args.batch),out/'crops',h.local(args.revision));spec['crops']=h.ref(out/'crops/crop-qa.json')
        if args.new_features: spec['newFeatures']=h.read(h.local(args.new_features))
        doc=assemble(spec);h.write(out/'protocol.json',doc)
        if spec.get('revision') and spec.get('crops') and not spec.get('admission'):
            audit=review.audit(h.checked(h.ROOT,spec['revision']),h.checked(h.ROOT,spec['crops']))
            h.write(out/'review-audit.json',audit)
            h.write(out/'admission-draft.json',dict(version='focus-static-addition-admission-v1',approved=False,
                reviewer='',authorizationReference=None,revision=spec['revision'],crops=spec['crops'],
                baseline=BASE_SEAL,sessionID=h.validate_batch(h.checked(h.ROOT,spec['batch']))['sessionID'],
                selectedIDs=[s['id'] for s in audit['samples']],excluded={},
                sourceReview=dict(evidence=None,decision='development-exposed-no-independent-claim',
                    protectedRolesUnchanged=False,developmentMembershipUnchanged=False)))
        h.write(out/'readiness.json',dict(configurationValid=True,launchEligible=False,counts=doc['counts'],blockers=doc['blockers']+['missing_run_approval']))
        print(json.dumps(dict(counts=doc['counts'],blockers=doc['blockers']+['missing_run_approval'])))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        h.write(out/'failure.json',dict(launchEligible=False,error=str(e)));print(str(e));return 2


if __name__=='__main__':raise SystemExit(main())
