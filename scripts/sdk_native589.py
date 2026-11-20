"""Admit explicitly scoped SDK data and reuse the resident crop training pipeline."""
import copy
import hashlib
from collections import Counter
from pathlib import Path
from PIL import Image
import research_queue as q
from template_inputs398 import checked,pin
from template_adapters395 import resolve_inputs,document
import sdk_training513 as sdk
OUT=None
POLICY='owned-session-bracket-v2-development-only'


def pixel(ref):
    with Image.open(checked(ref)) as image:
        rgb=image.convert('RGB')
        return hashlib.sha256(str(rgb.size).encode()+rgb.tobytes()).hexdigest()


def request():
    spec=q.load(OUT.parents[2]/'spec.json')
    return spec,q.load(checked(spec['request'])),resolve_inputs(spec['template'],OUT)


def consent(config):
    approval=q.load(checked(config['approval']))
    q.require(approval['version']=='native-profile-policy589-v1' and approval['decision']=='approved','native589_approval')
    q.require(approval['userMessage'] and approval['chatContext'] and approval['policy']==POLICY,'native589_approval_scope')
    q.require(approval['captures']==config['captures'] and approval['researchOnly'] is True and approval['independentQualification'] is False,'native589_approval_membership')
    q.require(config.get('withinFamilyDevelopment') is True,'native589_family_policy')
    q.require(len(config['captures'])==8 and len({r['group'] for r in config['captures']})==8,'native589_construction_count')
    q.require(Counter(r['split'] for r in config['captures'])=={'train':6,'validation':2},'native589_construction_roles')
    return approval


def profile_evidence(doc,frame):
    a=doc.get('continuityAssessment') or {};c=doc.get('focusStyleContinuity') or {}
    q.require(a.get('state')=='bounded_session_inference' and a.get('basis')=='supervisor_ledger_and_native_read_receipts' and a.get('policy')=='owned_session_bracket_v2','native589_continuity')
    q.require(a.get('value')=='standard' and a.get('unavailable')==['external_setting_mutations'],'native589_standard_scope')
    q.require(c.get('coverage')=='owned_commands_only' and c.get('externalChangesObserved') is False and c['targetID']==frame['sourceID'],'native589_profile_target')
    q.require(doc['coverage'][frame['endpoint']]['coordinateSpace']=='screen_pixels' and doc['coverage'][frame['endpoint']]['truncated'] is False,'native589_inventory')
    q.require(a['endpoints'][frame['endpoint']]==c['endpoints'][frame['endpoint']]['captureID'],'native589_endpoint')
    return dict(policy=POLICY,state='bounded_session_inference',value='standard',
        observationClockID=c['clockID'],nativeReads=doc['focusStyleEvidence'],readIntervals=c['profileReads'],
        externalChangesObserved=False,unavailable=['external_setting_mutations'],directFrameObservation=False)


def admit_rows(config,raw_request,data,crops):
    """Keep raw records immutable. This separate policy never admits old review groups."""
    consent(config)
    q.require(raw_request['admission'] is None and crops['trainingEligible'] is False,'native589_raw_admission')
    q.require(data['requestSHA256']==q.text_digest(raw_request),'native589_preparation_binding')
    q.require(crops['frames']==data['frames'],'native589_crop_frames')
    q.require({r['pair']['sha256'] for r in data['frames']}=={p['sha256'] for p in raw_request['pairs']},'native589_pairs')
    planned={r['group']:r for r in config['captures']};docs={};frames=[];lookup={};roles={};pixels={};labels={}
    for old in data['frames']:
        f=copy.deepcopy(old);plan=planned.get(f['group'])
        q.require(plan is not None and f['contentGroup']==f['group'] and f['split']==plan['split'],'native589_frozen_role')
        q.require(f['role']=='review_only' and f['trainingEligible'] is False,'native589_original_role')
        q.require(f['appID']=='example.ttr.navigation.consumer' and f['sourceID']==config['target'],'native589_source')
        ref=f['pair'];path=checked(ref)
        if ref['sha256'] not in docs:
            sdk.portable(raw_request,path);docs[ref['sha256']]=q.load(path)
        evidence=profile_evidence(docs[ref['sha256']],f)
        # Portable packet verification checks the mapping and all retained observations.
        endpoint=docs[ref['sha256']][f['endpoint']];packet_path=q.local_path(path.parent,endpoint['packet'])/'manifest.json';packet=q.load(packet_path)
        case=packet['cases'][0];e=q.load(packet_path.parent/case['frames'][0]['evidence'])
        from sdk_packet502 import review
        q.require(review(e,checked(f['image']))['reviewable'],'native589_frame_bracket')
        geometry_verified=(e.get('mapping') or {}).get('orientation')=='up'
        # An empty no-focus inventory supplies no model crop or training pixels.
        # Preserve its geometry gap; do not let it qualify an unmapped control.
        no_crops=not f['controls']
        q.require(geometry_verified or no_crops and f['focusState']=='no_focus' and f['focusID'] is None,'native589_orientation')
        q.require(set(f['missing'])<={'observed_profile_unqualified','geometry_alignment_unqualified'},'native589_unresolved_evidence')
        role='train' if f['split']=='train' else 'development'
        for key,value in [('groups',f['group']),('contentGroups',f['contentGroup']),('sourceFamilies',f['family']),('images',f['sha256'])]:
            q.require(value not in config['exclusions'][key],'native589_excluded_'+key)
        digest=pixel(f['image']);q.require(pixels.setdefault(digest,role)==role,'native589_cross_role_frames')
        q.require(roles.setdefault(f['group'],role)==role,'native589_cross_role_groups')
        q.require(f['focusState'] in ('focused','no_focus'),'native589_focus_unknown')
        f.update(role=role,producerRole='review_only',producerProfile=f['profile'],profile='standard',profileEvidence=evidence,
            missing=['geometry_alignment_unqualified'] if no_crops and not geometry_verified else [],
            cropGeometryVerified=geometry_verified,cropCount=len(f['controls']),
            trainingEligible=role=='train' and not no_crops,independentQualificationEligible=False)
        frames.append(f);lookup[(ref['sha256'],f['endpoint'])]=f
    q.require(set(roles)==set(planned),'native589_missing_construction')
    row_lookup={}
    for f in frames:
        for index,control in enumerate(f['controls']):row_lookup[f['id']+f'-control-{index:03}']=(f,control)
    q.require(set(row_lookup)=={r['id'] for r in crops['rows']},'native589_crop_membership')
    result=[]
    for old in crops['rows']:
        r=copy.deepcopy(old);f,c=row_lookup[r['id']]
        q.require(r['role']=='review_only' and r['trainingEligible'] is False and r['pair']==f['pair'] and r['sourceImage']==f['image'],'native589_crop_lineage')
        q.require(r['identity']==c['identity'] and r['control']==c['identity']['id'] and r['box']==c['pixelBounds'] and r['label']==int(c['identity']['id']==f['focusID']),'native589_crop_label')
        ref=dict(path=q.relative(Path(r['path'])),sha256=r['sha256']);digest=pixel(ref)
        q.require(pixels.setdefault(digest,f['role'])==f['role'],'native589_cross_role_crops')
        q.require(labels.setdefault(digest,r['label'])==r['label'],'native589_conflicting_labels')
        r.update(role=f['role'],profile='standard',producerRole='review_only',producerProfile=old['profile'],
            frame=f['id'],sourceFrameID=old['frame'],trainingEligible=f['role']=='train',profileEvidence=f['profileEvidence'],pixelSHA256=digest)
        result.append(r)
    q.require({r['role'] for r in result}=={'train','development'},'native589_crop_roles')
    return dict(version='sdk-native-admitted589-v1',rows=result,frames=frames,trainingEligible=True,
        profilePolicy=POLICY,approval=config['approval'],source=raw_request['source'],preprocessing=crops['preprocessing'],
        rawRequestSHA256=q.text_digest(raw_request),withinFamilyDevelopment=True,crossApplicationQualification=False,independentQualificationEligible=False,
        limitations=['Controlled sample family only.','Profile applicability uses an approved bounded inference.','External setting mutations remain unobserved.','Registered controls do not establish complete screen annotations.'],
        resultsProvisional=True,modelAccepted=False)


def admission():
    _,cfg,refs=request();raw=document(refs['intakeRequest']);data=document(refs['intake']);crops=document(refs['crops'])
    q.require(raw['source']==cfg['source'] and raw['exclusions']==cfg['exclusions'],'native589_source_binding')
    result=admit_rows(cfg,raw,data,crops)
    q.save(OUT/'crops.json',result);q.save(OUT/'benchmark_summary.json',dict(frames=len(result['frames']),crops=len(result['rows']),
        roleCounts=dict(Counter(r['role'] for r in result['rows'])),groups=len({f['group'] for f in result['frames']}),
        profilePolicy=POLICY,trainingAdmitted=True,independentQualificationEligible=False,resultsProvisional=True,modelAccepted=False))
    receipt()


def matched_rows(admitted,replay,protected):
    q.require(admitted['version']=='sdk-native-admitted589-v1' and admitted['profilePolicy']==POLICY and admitted['trainingEligible'] is True,'native589_corpus_admission')
    native=[dict(r,image=dict(path=q.relative(Path(r['path'])),sha256=r['sha256']),source='sdk-native') for r in admitted['rows']]
    all_rows=[dict(r,pixelSHA256=pixel(r['image'])) for r in replay]+native
    groups={};pixels={};labels={}
    for r in all_rows:
        h=r.get('pixelSHA256') or pixel(r['image']);q.require(h not in protected,'native589_protected_pixels')
        q.require(groups.setdefault(r['group'],r['role'])==r['role'],'native589_replay_group_leak')
        q.require(pixels.setdefault(h,r['role'])==r['role'],'native589_replay_pixel_leak')
        q.require(labels.setdefault(h,r['label'])==r['label'],'native589_replay_label_conflict')
    train=[r for r in all_rows if r['role']=='train'];counts=Counter(r['label'] for r in train);target=max(counts.values())
    q.require(set(counts)=={0,1},'native589_class_support')
    arms={}
    for arm,source in [('control',replay),('native',train)]:
        choices={label:sorted((r for r in source if r['label']==label),key=lambda r:r['id']) for label in (0,1)}
        q.require(all(choices.values()),'native589_arm_support')
        selected=[choices[label][i%len(choices[label])] for i in range(target) for label in (0,1)]
        arms[arm]=[dict(r,path=str(checked(r['image'])),sha256=r['image']['sha256'],profile=r.get('profile','unknown')) for r in selected]
    q.require(len(arms['control'])==len(arms['native']),'native589_exposure')
    return arms


def corpus():
    _,cfg,refs=request();admitted=document(refs['admitted'])
    from focus_corpus568 import replay_members
    replay=replay_members(document(cfg['replayProtocol']))
    protected={pixel(r) for r in cfg['protectedImages']}
    arms=matched_rows(admitted,replay,protected)
    for arm,rows in arms.items():q.save(OUT/(arm+'.json'),dict(rows=rows,trainingAdmitted=True,profilePolicy=POLICY,source=refs['admitted'],approval=cfg['approval'],replayProtocol=cfg['replayProtocol'],planSHA256=q.text_digest(cfg)))
    q.save(OUT/'benchmark_summary.json',dict(presentationsPerEpoch={k:len(v) for k,v in arms.items()},
        uniqueCropCounts={k:len({r['sha256'] for r in v}) for k,v in arms.items()},
        replayRows=len(replay),protectedCrops=len(protected),resultsProvisional=True,modelAccepted=False))
    receipt()


def train():
    spec,cfg,refs=request();membership=document(refs['membership']);consent(cfg)
    q.require(membership['trainingAdmitted'] is True and membership['profilePolicy']==POLICY and membership['approval']==cfg['approval'],'native589_training_admission')
    q.require(membership['replayProtocol']==cfg['replayProtocol'] and membership['planSHA256']==q.text_digest(cfg),'native589_training_intent')
    from focus_corpus568 import replay_members
    replay_members(document(cfg['replayProtocol']))
    rows=membership['rows'];q.require(rows and all(r['role']=='train' for r in rows),'native589_training_roles')
    q.require(Counter(r['label'] for r in rows)[0]==Counter(r['label'] for r in rows)[1],'native589_training_balance')
    for r in rows:q.require(q.digest(Path(r['path']))==r['sha256'],'native589_training_pixels')
    options={}
    if 'teacherPreservation' in refs:
        from teacher_preservation495 import validate_config,validate_anchors
        teacher=validate_config(document(refs['teacherPreservation']))
        q.require(teacher['model']==refs['initialization'] and teacher['weight']==1.0,'native589_teacher_scope')
        validate_anchors(rows,document(teacher['anchors'])['rows'])
        options['teacher_preservation']=teacher
    from train_focus_ring_detector import train_native_hcf
    result=train_native_hcf(rows,checked(refs['initialization']),OUT,epochs=30,batch=16,seed=371,
        profile='balanced',deduplicate=False,selection='fixed-last',repeat=1,**options)
    q.require(result['epochs']==30 and result['developmentCrops']==0 and result['selection']=='fixed-last','native589_training_completion')
    history=q.load(OUT/'history.json')
    q.require([r['epoch'] for r in history]==list(range(1,31)),'native589_training_history')
    exposure=result.setdefault('exposure',{})
    if 'uniqueTrainImages' in exposure:
        exposure['sourceReportedUniqueTrainImages']=exposure['uniqueTrainImages']
        exposure['sourceReportedCountMeaning']='training row occurrences, not unique images'
    exposure.update(imageOccurrencesPerEpoch=len(rows),uniqueTrainingRows=len({r['id'] for r in rows}),
        uniqueTrainImages=len({pixel(dict(path=q.relative(Path(r['path'])),sha256=r['sha256'])) for r in rows}))
    result.update(initialization=refs['initialization'],membership=refs['membership'],teacherPreservation=options.get('teacher_preservation'),profilePolicy=POLICY,resultsProvisional=True,modelAccepted=False)
    q.save(OUT/'fit.json',result)
    q.save(OUT/'ancestry.json',dict(ancestryVerified=True,method='strict-checkpoint-training-initialization',ancestry=dict(base=refs['initialization']),training=pin(OUT/'fit.json')))
    q.save(OUT/'model.json',dict(version='weight-surgery-model-v1',arm=spec['id'],checkpoint=pin(OUT/'final.pt'),edit=pin(OUT/'ancestry.json'),threshold=.85,modelAccepted=False))
    receipt()


def score_native():
    _,_,refs=request();data=document(refs['admitted'])
    from eval_focus_ring_detector import predict_torch
    from consumer_crop_comparison import summarize
    rows=[dict(r,image=r['sourceImage']) for r in data['rows'] if r['role']=='development']
    frames=[dict(id=f['id'],focusState=f['focusState'],image=f['image'],group=f['group'],role=f['role'],profile=f['profile'],family=f['family']) for f in data['frames'] if f['role']=='development']
    q.require(len(frames)==4 and len({r['group'] for r in frames})==2,'native589_development_scope')
    models=dict(baseline=refs['base'],control=document(refs['control'])['checkpoint'],native=document(refs['native'])['checkpoint'])
    reports={name:summarize(rows,predict_torch(checked(model),[dict(path=checked(dict(path=q.relative(Path(r['path'])),sha256=r['sha256']))) for r in rows]),frames) for name,model in models.items()}
    q.save(OUT/'benchmark_summary.json',dict(reports=reports,models=models,scope='Supplied SDK control boxes. Two related frames per construction. Two development constructions from one sample family.',resultsProvisional=True,modelAccepted=False))
    receipt()


def compare():
    _,_,refs=request()
    from focus_replay568 import compare_reports
    result=compare_reports(*[document(refs[k]) for k in ('reference','control','native')])
    scores=document(refs['nativeScores'])['reports'];baseline={r['id']:r for r in scores['control']['rows']};candidate={r['id']:r for r in scores['native']['rows']}
    q.require(baseline.keys()==candidate.keys(),'native589_native_comparison')
    losses=[i for i in baseline if baseline[i]['outcome']=='correct' and candidate[i]['outcome']!='correct']
    gains=[i for i in baseline if baseline[i]['outcome']!='correct' and candidate[i]['outcome']=='correct']
    wrong=[i for i in baseline if baseline[i]['outcome']!='wrong' and candidate[i]['outcome']=='wrong']
    result.update(nativeDevelopment=dict(gains=gains,lostPriorSuccesses=losses,newWrong=wrong),profilePolicy=POLICY,
        independentQualificationEligible=False,resultsProvisional=True)
    original={r['id']:r for r in scores['baseline']['rows']}
    q.require(original.keys()==candidate.keys(),'native589_baseline_cases')
    original_losses=[i for i in original if original[i]['outcome']=='correct' and candidate[i]['outcome']!='correct']
    original_wrong=[i for i in original if original[i]['outcome']!='wrong' and candidate[i]['outcome']=='wrong']
    result['nativeDevelopment'].update(lostBaselineSuccesses=original_losses,newWrongVersusBaseline=original_wrong)
    if losses or wrong or original_losses or original_wrong:result['outcome']='contradicted'
    q.save(OUT/'benchmark_summary.json',result);receipt()


def receipt():
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in OUT.rglob('*') if p.is_file()]))
