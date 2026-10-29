from sdk_semantics529 import transition
"""Prepare SDK control crops and temporal rows through qualified existing interfaces."""
import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from PIL import Image
import research_queue as q
from experiment_templates import checked, pin
from sdk_campaign508 import packet, observed

OUT = None


def portable(request, path):
    source = q.load(checked(request['source']))
    q.require(len(source['commit']) == 40 and source['files'], 'sdk513_source_identity')
    files = [checked(ref) for ref in source['files']]
    tool = next((p for p in files if p.name == 'export-evidence.rb'), None)
    q.require(tool is not None and {p.name for p in tool.parent.glob('*.rb')} == {p.name for p in files},
              'sdk513_source_closure')
    result = subprocess.run(['/usr/bin/ruby', str(tool), 'verify-action-pair', str(path.parent)],
                            capture_output=True, text=True, timeout=30)
    q.require(result.returncode == 0, 'sdk513_pair_verification:' + result.stderr[-500:])
    receipt = json.loads(result.stdout)
    q.require(receipt['manifestSHA256'] == q.digest(path), 'sdk513_pair_receipt')
    return receipt


def intake(request):
    q.require(set(request)-{'products'} == {'version', 'id', 'pairs', 'source', 'exclusions', 'admission', 'tool'},
              'sdk513_request_fields')
    q.require(request['version'] == 'sdk-preparation-v1' and q.ID.fullmatch(request['id']), 'sdk513_request_version')
    q.require(0 < len(request['pairs']) <= 32 and len({p['sha256'] for p in request['pairs']}) == len(request['pairs']),
              'sdk513_pair_membership')
    products=request.get('products',['crops','temporal'])
    q.require(products in (['crops'],['temporal'],['crops','temporal']), 'sdk513_products')
    exclusions = request['exclusions']
    q.require(set(exclusions) == {'groups','contentGroups','sourceFamilies','images'}, 'sdk513_exclusions')
    q.require(all(isinstance(v,list) and all(isinstance(x,str) and x for x in v) for v in exclusions.values()),
              'sdk513_exclusion_values')
    admission = request['admission']
    if admission is not None:
        q.require(set(admission)-{'withinFamilyDevelopment'} == {'reviewer','reason','pairs'} and admission['reviewer'] and admission['reason'],
                  'sdk513_admission_contract')
        q.require(type(admission.get('withinFamilyDevelopment',False)) is bool,'sdk513_family_policy')
        q.require(set(admission['pairs']) == {r['sha256'] for r in request['pairs']} and
                  all(role in ('train','development') for role in admission['pairs'].values()), 'sdk513_admission_membership')
    frames=[]; pairs=[]; gaps=[]; ancestry={}; pixel_labels={}; decoded={}; family_overlap=set()
    for index, ref in enumerate(request['pairs']):
        path=checked(ref); receipt=portable(request,path); doc=q.load(path)
        q.require(doc['schemaVersion'] in (1,2), 'sdk513_pair_version')
        role='review_only' if admission is None else admission['pairs'][ref['sha256']]
        endpoint=[]
        for side in ('before','after'):
            p=q.local_path(path.parent,doc[side]['packet'])/'manifest.json'
            q.require(q.digest(p)==doc[side]['manifestSHA256'], 'sdk513_endpoint_hash')
            f=packet(p,doc[side]['caseID']); m=q.load(p); family=m['source']['sourceFamily']
            visual=doc.get('visualProvenance',{}).get(side,{})
            profile=visual.get('profile',{}).get('state','unknown')
            profile_time=visual.get('profile',{}).get('observationTime')
            if profile == 'unknown': profile=f['profile']
            missing=[]
            if profile not in ('standard','hcf') or not profile_time: missing.append('observed_profile_unqualified')
            if doc['coverage'][side]['truncated']:missing.append('registered_inventory_truncated')
            if visual.get('inventory',{}).get('alignment')!='bracketed':missing.append('geometry_alignment_unqualified')
            if profile=='hcf' and (visual.get('appearance',{}).get('state') not in ('ring','filled','other') or
                                  not visual.get('appearance',{}).get('observationTime')):
                missing.append('hcf_appearance_unqualified')
            if role=='train' and f['split']!='train':missing.append('producer_split_not_training')
            if role=='development' and f['split']!='validation':missing.append('producer_split_not_validation')
            vals={'groups':f['group'],'contentGroups':f['contentGroup'],'sourceFamilies':family,'images':f['sha256']}
            if role=='train':
                missing += ['excluded_'+k for k,v in vals.items() if v in exclusions[k]]
            # A source family can share roles only through an explicit future contract, never implicitly.
            for kind,value in vals.items():
                if kind=='images':continue
                key=(kind,value);prior=ancestry.setdefault(key,role)
                if prior!=role and kind=='sourceFamilies' and admission and admission.get('withinFamilyDevelopment',False):
                    family_overlap.add(value)
                else:q.require(prior==role, 'sdk513_cross_role_'+kind)
            with Image.open(checked(f['image'])) as image:
                digest=hashlib.sha256(str(image.size).encode()+image.convert('RGB').tobytes()).hexdigest()
            q.require(decoded.setdefault(digest,role)==role, 'sdk513_cross_role_pixels')
            labels=sorted((c['identity']['id'],c['pixelBounds'],int(c['identity']['id']==f['focusID'])) for c in f['controls'])
            label_hash=q.text_digest(labels)
            q.require(pixel_labels.setdefault(digest,label_hash)==label_hash, 'sdk513_conflicting_pixel_labels')
            item=dict(f,id=request['id']+f'-{index:03}-{side}',sourceFrameID=f['id'],family=family,role=role,profile=profile,
                      pair=ref,endpoint=side,visual=visual,decodedSHA256=digest,missing=missing,
                      trainingEligible=role=='train' and not missing)
            frames.append(item);endpoint.append(item)
            gaps.extend(dict(pair=index,endpoint=side,requirement=x) for x in missing)
        a,b=endpoint; label=observed(a['focusID'],b['focusID'])
        q.require(label==doc['observed'], 'sdk513_observed_transition')
        # Requested content-only motion is not a verified motion label.
        issues=[x for x in receipt['issues'] if x!='content_motion_not_independently_verified']
        crop_issues=[x for x in issues if x!='supervisor_timing_unavailable']
        blocking_issues=issues if 'temporal' in products else crop_issues
        if blocking_issues:gaps.append(dict(pair=index,requirement='pair_issues',details=blocking_issues))
        identity=transition(a,b)
        if not identity['eligible']:
            issues.append('focus_identity_unavailable')
            if 'temporal' in products:gaps.append(dict(pair=index,requirement='pair_issues',details=['focus_identity_unavailable']))
        common_missing=[m for f in endpoint for m in f['missing'] if m.startswith(('producer_split_', 'excluded_'))]
        pairs.append(dict(id=request['id']+f'-pair-{index:03}',manifest=ref,group=a['group'],contentGroup=a['contentGroup'],family=a['family'],
            role=role,split=a['split'],profile=a['profile'],observed=identity['observed'],producerObserved=label,identityTransition=identity,expected=doc['expected'],
            changed=(int(identity['observed'] in ('move','arrival','departure')) if identity['eligible'] else None),images=[a['image'],b['image']],
            endpoints=dict(before=a['focusID'],after=b['focusID']),issues=receipt['issues'],
            backgroundMotionVerified=False,trainingEligible=role=='train' and not issues and not common_missing))
    if admission is not None:
        fatal=[x for x in gaps if x['requirement'].startswith(('producer_split_', 'excluded_')) or x['requirement']=='pair_issues']
        q.require(not fatal, 'sdk513_training_gaps:'+','.join(sorted({x['requirement'] for x in fatal})))
    return dict(version='sdk-prepared-intake-v1',frames=frames,pairs=pairs,gaps=gaps,
        capabilities=dict(actionLinkedPairs=len(pairs),observedFocusStates=dict(Counter(p['observed'] for p in pairs)),
                          controlCropRows=sum(len(f['controls']) for f in frames),completeDetectorLabels=False),
        trainingEligible=(('crops' in products and any(f['trainingEligible'] for f in frames)) or
                          ('temporal' in products and any(p['trainingEligible'] for p in pairs))),
        sourceFamilyOverlap=sorted(family_overlap),crossApplicationQualification=False,
        products=products,source=request['source'],requestSHA256=q.text_digest(request),admission=admission,modelAccepted=False,
        limitation='Registered controls only. No complete detector labels. Selected flags remain registration metadata. Motion is not independently verified.')


def prepare_crops(data, destination, tool):
    import focus_runtime as runtime
    from hcf_study371 import write_crops
    q.require(all(f['role']=='review_only' or not f['missing'] for f in data['frames']), 'sdk513_crop_prerequisites')
    destination.mkdir(exist_ok=False)
    old=runtime.TOOL;runtime.TOOL=checked(tool)
    rows=[];items=[];metadata={}
    try:
        for frame in data['frames']:
            for index,control in enumerate(frame['controls']):
                ident=frame['id']+f'-control-{index:03}'
                item=dict(id=ident,path=str(checked(frame['image'])),sha256=frame['sha256'],bounds=control['pixelBounds'])
                metadata[ident]=(frame,control);items.append(item)
        q.require(items, 'sdk513_no_visible_control_crops')
        for batch in runtime.bounded_batches(items,shared_images=True):
            response=runtime.invoke(batch,image_root=q.ROOT)
            for item,(path,digest) in zip(batch,write_crops(batch,response['results'],destination)):
                frame,control=metadata[item['id']]
                rows.append(dict(id=item['id'],frame=frame['sourceFrameID'],path=str(path),sha256=digest,
                    label=int(control['identity']['id']==frame['focusID']),control=control['identity']['id'],
                    role=frame['role'],profile=frame['profile'],group=frame['contentGroup'],family=frame['family'],
                    box=control['pixelBounds'],sourceImage=frame['image'],pair=frame['pair'],
                    parentID=control.get('parentID'),nativeClass=control.get('className'),
                    identity=control['identity'],semanticEvidence=control.get('semanticEvidence'),
                    registeredSelected=control.get('registeredSelected'),selectionProvenance=control.get('selectionProvenance'),
                    trainingEligible=frame['trainingEligible']))
        return dict(rows=rows,frames=data['frames'],runtime=runtime.identity(),preprocessing=runtime.RUNTIME_PREPROCESSING,
                    trainingEligible=any(r['trainingEligible'] for r in rows),modelAccepted=False)
    finally:runtime.TOOL=old



def crop_training_description(crop_job, configuration, initialization, ident, log_id, queue=q.QUEUE):
    """Bind completed eligible crops to T06. Never register, approve, or start training."""
    from proposal_campaign443 import completed_output
    from hcf_templates395 import build
    reference=completed_output(queue,crop_job,'crops.json');data=q.load(checked(reference))
    q.require(data.get('trainingEligible') is True and {r['role'] for r in data['rows']}=={'train','development'},
              'sdk513_crop_training_roles')
    q.require(all(r['trainingEligible'] for r in data['rows'] if r['role']=='train'), 'sdk513_crop_training_eligibility')
    cfg=q.load(checked(configuration));q.require(cfg['initialization']==initialization,'sdk513_training_initialization')
    q.require(cfg.get('profile')=='balanced','sdk513_training_profile')
    spec=q.load(queue/'jobs'/crop_job/'spec.json')
    doc=dict(version='hcf-template-description-v1',id=ident,task='SDK513',owner='Maximum-mini-NUIAK',template='T06',
        question='Does admitted SDK control-crop rehearsal recover native focus without losing retained successes?',
        decision='Reject lost retained successes and new no-focus selections. Require complete matched reports before acceptance.',
        inputs=dict(configuration=configuration,initialization=initialization,membership=reference),parameters={},
        dependencies=[dict(job=crop_job,specSHA256=q.text_digest(spec),outputs=['crops.json'])],
        training=dict(experimentLogRunId=log_id,membership=[reference],initialization=initialization,
                      epochs=30,storageBudgetBytes=2<<30,resume='restart',acceptanceEvidence='Matched native, retained, and no-focus reports. No automatic promotion.'))
    build(doc)
    return doc


def request_of(spec):
    return q.load(checked(spec['request']))


def run():
    spec=q.load(OUT.parents[2]/'spec.json');request=request_of(spec);stage=spec['preparationStep']
    if stage=='intake':
        result=intake(request);name='intake.json'
    else:
        deps=q.dependency_inputs(spec,OUT.parents[4]);q.require(len(deps)==1,'sdk513_intake_dependency')
        result=q.load(checked(deps[0]['outputs'][0]));q.require(result['version']=='sdk-prepared-intake-v1','sdk513_intake_version')
        q.require(result['requestSHA256']==q.text_digest(request),'sdk513_intake_request_changed')
        if stage=='crops':result=prepare_crops(result,OUT/'crops',request['tool']);name='crops.json'
        else:
            for row in result['pairs']:
                for image in row['images']:checked(image)
            result=dict(version='sdk-temporal-membership-v1',rows=result['pairs'],trainingEligible=any(p['trainingEligible'] for p in result['pairs']),modelAccepted=False);name='temporal.json'
    q.save(OUT/name,result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=name,sha256=q.digest(OUT/name))]))


def compile_request(path, destination):
    request=q.load(path);intake(request)  # Semantic preflight; no cropping, training, or capture.
    checked(request['tool']);source=q.load(checked(request['source']))
    destination.mkdir(parents=True,exist_ok=True);specs=[]
    for stage in ['intake',*request.get('products',['crops','temporal'])]:
        spec=dict(version='research-spec-v2',id=request['id']+'-'+stage,task='SDK513',owner='Maximum-mini-NUIAK',
            authority='diagnostic',kind='screen',jobKind='artifact',request=pin(path),preparationStep=stage,
            question='Can verified SDK observations produce reusable control crops and temporal labels without changing data roles?',
            hypothesis='Observed state and native geometry support scoped labels without complete screen annotation.',
            controlledComparison='Preserve source pixels, observed labels, ancestry, and production crop preprocessing.',
            decisionRule='Reject invalid evidence and role leakage. Do not infer motion or promote models.',
            nextActionByOutcome=dict(supported='Use eligible rows with existing trainers and matched reports.',contradicted='Repair the exact missing prerequisite or prepare an authorized replacement capture.'),
            inputs=[pin(path),pin(Path(__file__)),request['source'],request['tool'],pin(q.ROOT/'Sources/NativeUIAuditKit/Detection/FocusRingClassifier.swift'),*source['files'],*request['pairs']],
            dependencies=[] if stage=='intake' else [dict(job=specs[0]['id'],specSHA256=q.text_digest(specs[0]),outputs=['intake.json'])],
            adapter=dict(type='python-callable',steps=['sdk_training513.run'],outputAttributes=['sdk_training513.OUT']),
            evidence=dict(reads=[q.relative(path)],artifactReceipt='artifact-receipt.json'),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1))
        q.validate(spec);target=destination/(spec['id']+'.json');q.save(target,spec);specs.append(spec)
    result=dict(version='model-decision-compiled-v1',plan=pin(path),existing=[],jobs=[dict(job=s['id'],spec=pin(destination/(s['id']+'.json')),specSHA256=q.text_digest(s)) for s in specs])
    q.save(destination/'compiled.json',result);return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('request',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(compile_request(args.request,args.output),indent=2))
