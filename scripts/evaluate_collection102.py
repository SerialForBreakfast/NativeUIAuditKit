"""Frozen calibration replay; never admits data, trains, captures or exports models."""
import argparse
from collections import Counter
from pathlib import Path
import time
import numpy as np
import focus_candidate_ranker as r
import focus_change_adaptation as change
from intake_native76 import collection_selection, verify_selection
from focus_corrected_transition_audit import validate_case
from inventory_transition_sources import observed_scroll
from diagnose_signal95 import encoded
from prepare_proposal74 import targets

h=r.d.h
VERSION='collection102-role-proposal-v1'


def verified_records():
    roots=[('reports/work/INTAKE-94/received/ttr-native-layout-diversity-28-20261003',28),
           ('reports/work/INTAKE-99/received/ttr-native-collection-context-60-20261003',60)]
    rows=[]
    for name,count in roots:
        root=h.ROOT/name
        for entry,bundle,case in verify_selection(root,collection_selection(root,count),
                expected_pairs=count,allow_completed_cases=count==60):
            evidence=bundle/'transition-case.json'
            if not evidence.exists():continue
            condition=case['transition']['condition']
            h.require(condition in ('focus_moved','boundary_unchanged','content_only'),'collection102_condition')
            raw,b,a=validate_case(root,evidence,case,directional=condition=='focus_moved')
            changed=b['focus']!=a['focus']
            h.require(changed==(condition=='focus_moved'),'collection102_observed_relation')
            rows.append(dict(r.d.record(case['case_id'],'fixture-procedural-renderer-v1','calibration',
                b,a,changed,[h.ref(evidence),h.ref(root/entry['source_receipt'])],None),
                recipe=case['recipe'],condition=condition,observedScroll=observed_scroll(raw)[0]))
    h.require(len(rows)==40 and len({v['id'] for v in rows})==40 and
        Counter(v['condition'] for v in rows)=={'focus_moved':16,'boundary_unchanged':12,'content_only':12},
        'collection102_membership')
    return rows


def validate_proposal(doc):
    h.require(doc.get('version')==VERSION and doc.get('approved') is False and
        doc.get('executionEligible') is False,'collection102_not_approval')
    rows=doc['members']
    h.require(len(rows)==40 and len({v['id'] for v in rows})==40 and
        doc['memberSHA256']==h.digest(rows),'collection102_membership')
    h.require(all(v['sourceRole']=='calibration' and v['requestedRole']=='train' and
        v['group']=='fixture-procedural-renderer-v1' and type(v['changed']) is bool and
        v['changed']==(v['condition']=='focus_moved') for v in rows) and
        Counter(v['condition'] for v in rows)=={'focus_moved':16,'boundary_unchanged':12,'content_only':12},
        'collection102_roles')


def prepare(output):
    out=h.fresh(output);rows=verified_records()
    base=h.ROOT/'reports/work/NATIVE-87/admitted'
    corpus=h.read(base/'corpus.json');admission=h.read(base/'admission.json')
    old=r.d.admitted(corpus,admission)
    h.require(Counter(v['split'] for v in old)=={'train':68,'development':5},'collection102_existing_roles')
    for v in old:
        for image in v['images']:h.checked(h.ROOT,image)
    pixels={p for v in rows for p in v['decodedPixelHashes']}
    overlap={s:sorted(pixels & {p for v in old if v['split']==s for p in v['decodedPixelHashes']})
             for s in ('train','development')}
    h.require(not overlap['development'],'collection102_development_overlap')
    members=[dict(v,requestedRole='train') for v in rows]
    doc=dict(version=VERSION,**h.FLAGS,approved=False,executionEligible=False,members=members,
        memberSHA256=h.digest(members),overlap=overlap,existingCorpus=h.ref(base/'corpus.json'),
        existingAdmission=h.ref(base/'admission.json'),excludedAppearancePairs=48,
        prospectiveCounts=dict(train=108,development=5,independentFinal=0),
        limitation='Exact proposal only; shared Fixture ancestry never becomes independent final evidence.')
    validate_proposal(doc);out.mkdir(parents=True);h.write(out/'proposal.json',doc,sealed=True)
    return doc


def score_row(row, probability, predictions, frame_inputs):
    h.require(np.isfinite(probability) and 0<=probability<=1,'collection102_probability')
    coverage=[];overlaps=[];failure=[]
    for image,truth in zip(row['images'],row['boxes']):
        key=image['sha256'];candidates=frame_inputs[key]['candidates'];prediction=predictions[key]
        available=not targets(candidates,truth)['missingPositive']
        overlap=r.iou(prediction['bounds'],truth) if prediction is not None else 0
        coverage.append(available);overlaps.append(overlap)
        failure.append('none' if overlap>=.5 else 'ranking_or_geometry' if available else 'proposal_miss')
    known=max(probability,1-probability)>=.85;correct=(probability>=.5)==row['changed']
    return dict(id=row['id'],condition=row['condition'],theme=row['recipe']['theme'],
        style=row['recipe']['appearance']['canvas']['collectionStyle'],probability=float(probability),
        expectedChange=row['changed'],rawChangeCorrect=bool(correct),abstained=not known,
        confidentFalseChange=bool(known and not row['changed'] and probability>=.5),
        confidentMissedChange=bool(known and row['changed'] and probability<.5),
        boxIoUs=overlaps,proposalCoverage=coverage,endpointFailure=failure,
        bothBoxesCorrect=min(overlaps)>=.5,joint=bool(known and correct and min(overlaps)>=.5))


def summarize(rows):
    return dict(pairs=len(rows),rawChangeCorrect=sum(v['rawChangeCorrect'] for v in rows),
        abstentions=sum(v['abstained'] for v in rows),joint=sum(v['joint'] for v in rows),
        bothBoxesCorrect=sum(v['bothBoxesCorrect'] for v in rows),
        coveredEndpoints=sum(sum(v['proposalCoverage']) for v in rows),
        correctEndpoints=sum(sum(x>=.5 for x in v['boxIoUs']) for v in rows),
        confidentFalseChanges=sum(v['confidentFalseChange'] for v in rows),
        confidentMissedChanges=sum(v['confidentMissedChange'] for v in rows))


def replay(proposal_path,candidates_path,output):
    start=time.monotonic();out=h.fresh(output)
    code_refs=[h.ref(h.ROOT/'scripts'/name) for name in
        ('evaluate_collection102.py','focus_candidate_ranker.py','focus_change_adaptation.py',
         'focus_direct_transition.py','diagnose_signal95.py','prepare_proposal74.py')]
    proposal=h.sealed(h.local(proposal_path),VERSION);validate_proposal(proposal)
    rows=verified_records()
    h.require(proposal['members']==[dict(v,requestedRole='train') for v in rows],'collection102_source_changed')
    inputs=r.sealed(h.local(candidates_path),'calibration-proposals-v1')
    h.require(inputs['source']==h.ref(h.local(proposal_path)) and inputs['trainingEligible'] is False,
        'collection102_candidate_binding')
    expected={im['sha256'] for row in rows for im in row['images']}
    h.require({f['id'] for f in inputs['frames']}==expected,'collection102_candidate_membership')
    # Native truth remains in rows, never in model inputs.
    frames=[{k:f[k] for k in ('id','image','size','candidates')} for f in inputs['frames']]
    h.require(all(set(f['candidates'][i])=={'id','bounds'} for f in frames for i in range(len(f['candidates']))),
        'collection102_truth_free_candidates')
    nonempty=[f for f in frames if f['candidates']]
    before=time.monotonic()
    if nonempty:
        data,items,crops,cache,entries=r.encode_frames(nonempty,h.ROOT/'.build/batch79-derivatives')
    else:
        data=np.empty((0,768),dtype=np.float32);items=[];crops=[];entries=[]
        cache=dict(cacheHits=0,cacheMisses=0,invocations=0)
    crop_seconds=time.monotonic()-before
    frozen=r.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/repair100-dtm024/result.json',change.VERSION)
    ranker=r.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/native87-dtm020/result.json',r.VERSION)
    model_refs=dict(change=frozen['model'],ranker=ranker['model'])
    torch=r.d.torch_runtime();torch.set_num_threads(2)
    state=torch.load(h.checked(h.ROOT,frozen['model']),map_location='cpu',weights_only=True)
    h.require(state['configuration']==r.d.PAIRED_TEMPORAL_CONFIG and state['adaptation']==change.REPAIR_CONFIG,
        'collection102_change_checkpoint')
    net=r.d.model(state['configuration']);net.load_state_dict(state['state'],strict=True);net.eval()
    rs=torch.load(h.checked(h.ROOT,ranker['model']),map_location='cpu',weights_only=True)
    h.require(rs['configuration']==r.ACTION_CONFIG,'collection102_rank_checkpoint')
    rank=r.model(torch,rs['configuration']);rank.load_state_dict(rs['state'],strict=True);rank.eval()
    protocol=h.read(h.checked(h.ROOT,frozen['protocol']))
    # Frozen73x6x128x192 float32 inputs exceed the generic32MiB evidence limit.
    prior=np.load(h.checked(h.ROOT,protocol['x'],64*1024**2),allow_pickle=False)
    h.require(prior.shape==(73,6,128,192) and prior.dtype==np.float32 and np.isfinite(prior).all(),
        'collection102_parity_tensor')
    with torch.inference_mode():old=change.score_change(net,torch.from_numpy(prior),change.REPAIR_CONFIG).tolist()
    h.require(all(abs(p-v['after'])<=1e-6 for p,v in zip(old,frozen['results'])) and
        len(old)==len(frozen['results']),'collection102_checkpoint_parity')
    tx=torch.from_numpy(r.features(data,dict(frames=nonempty),rs['configuration'])) if nonempty else None
    offset=0;predictions={f['id']:None for f in frames};ranked={};timings=[]
    with torch.inference_mode():
        for f in nonempty:
            count=len(f['candidates']);t=time.monotonic()
            scores=rank(tx[offset:offset+count]).flatten().numpy();timings.append(time.monotonic()-t);offset+=count
            predictions[f['id']]=r.choose(f['candidates'],scores)
            ranked[f['id']]=[dict(candidate=c,logit=float(p)) for c,p in zip(f['candidates'],scores)]
    change_scores=[];change_times=[];encode_seconds=0
    for row in rows:
        t=time.monotonic();x=encoded(*(r.d.pixels(im) for im in row['images']),size=(192,128))[0]
        encode_seconds+=time.monotonic()-t;t=time.monotonic()
        with torch.inference_mode():p=change.score_change(net,torch.from_numpy(x[None]),change.REPAIR_CONFIG).item()
        change_times.append(time.monotonic()-t);change_scores.append(p)
    out.mkdir(parents=True)
    h.write(out/'predictions.json',dict(version='collection102-predictions-v1',**h.FLAGS,
        models=model_refs,selected=predictions,ranked=ranked,
        changes=[dict(id=v['id'],probability=p) for v,p in zip(rows,change_scores)],
        inferenceInputsContainTruth=False),sealed=True)
    by={f['id']:f for f in frames}
    scored=[score_row(row,p,predictions,by) for row,p in zip(rows,change_scores)]
    for ref in model_refs.values():h.checked(h.ROOT,ref)
    for ref in code_refs:h.checked(h.ROOT,ref)
    report=dict(version='collection102-evaluation-v1',**h.FLAGS,models=model_refs,
        proposal=h.ref(h.local(proposal_path)),inputs=h.ref(h.local(candidates_path)),
        predictions=h.ref(out/'predictions.json'),results=scored,summary=summarize(scored),
        byCondition={k:summarize([v for v in scored if v['condition']==k]) for k in sorted({v['condition'] for v in scored})},
        byTheme={k:summarize([v for v in scored if v['theme']==k]) for k in ('dark','light')},
        byStyle={k:summarize([v for v in scored if v['style']==k]) for k in sorted({v['style'] for v in scored})},
        derivativeCache=cache,derivativeEntries=entries,cropSeconds=crop_seconds,encodeSeconds=encode_seconds,
        changeFirstSeconds=change_times[0],changeWarmMedianSeconds=float(np.median(change_times[1:])),
        rankFirstSeconds=timings[0] if timings else None,
        rankWarmMedianSeconds=float(np.median(timings[1:])) if len(timings)>1 else None,
        latencyScope='Offline stage timing; change model already warmed by parity; excludes capture/navigation. Not end-user latency.',
        elapsedSeconds=time.monotonic()-start,checkpointParity=True,implementation=h.ref(Path(__file__)),
        code=code_refs,dependencies={k:r.d.dependency_version(k) for k in ('torch','numpy','pillow')},
        productionCropIdentity=r.derivative_identity(),
        limitation='Calibration-only shared Fixture ancestry; no role admission, training, threshold tuning or final accuracy claim.')
    h.write(out/'evaluation.json',report,sealed=True);print(report['summary']);print(report['byCondition'])
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    p.add_argument('--proposal');p.add_argument('--candidates');a=p.parse_args()
    if bool(a.proposal)!=bool(a.candidates):p.error('both proposal and candidates required for replay')
    if a.proposal:replay(a.proposal,a.candidates,a.output)
    else:prepare(a.output)
