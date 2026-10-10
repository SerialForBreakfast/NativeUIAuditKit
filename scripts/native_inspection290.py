"""Cache predictions on retained native tables without asserting label approval."""
import argparse
from collections import Counter
from pathlib import Path
import time
import numpy as np
from PIL import Image
import layout290 as run
from diagnose_signal95 import encoded
from focus_corrected_transition_audit import validate_case
from fixture_owned_pairs import member

base=run.base
ROOT=base.ROOT/'reports/work/RESIDUAL-160/artifacts/native24-r1/extracted/ttr-native-table-appearance24-20261005-r1'
OUT=base.ROOT/'reports/work/TRANSITION-290/native24-inspection.json'


def agreement(probabilities,reported):
    probabilities=np.asarray(probabilities);reported=np.asarray(reported)
    base.require(probabilities.shape==reported.shape and probabilities.ndim==1,'score_shape')
    base.require(np.isfinite(probabilities).all() and ((probabilities>=0)&(probabilities<=1)).all(),'score_range')
    base.require(np.isin(reported,[0,1]).all(),'reported_labels')
    decisions=base.decisions(probabilities)
    return dict(count=len(reported),agreesWithProducer=int((decisions==reported).sum()),
        disagreesWithProducer=int(((decisions!=-1)&(decisions!=reported)).sum()),
        uncertain=int((decisions==-1).sum()))


def run_inspection():
    base.require(not OUT.exists(),'output_collision')
    base.torch.set_num_threads(2)
    started=time.monotonic()
    inventory=base.read(ROOT/'members.sha256.json')
    names=set()
    for record in inventory:
        name=record['path'];base.require(name.casefold() not in names,'duplicate_member');names.add(name.casefold())
        path=member(ROOT,name)
        base.require(path.stat().st_size==record['bytes'] and base.worker.digest(path)==record['sha256'],'member_integrity')
    actual={str(p.relative_to(ROOT)).casefold() for p in ROOT.rglob('*') if p.is_file()}
    base.require(actual==names|{'members.sha256.json'},'inventory_membership')
    rows=[];inputs=[]
    for folder in ('pilot','remaining'):
        for case in base.read(ROOT/folder/'campaign-manifest.json')['cases']:
            condition=case['transition']['condition']
            evidence=ROOT/folder/'splits/validation'/case['case_id']/'transition-case.json'
            raw,before,after=validate_case(ROOT,evidence,case,directional=condition=='focus_moved')
            base.require(case['split_group']=='validation','source_role')
            refs=[];images=[]
            for endpoint in raw['endpoints']:
                path=member(ROOT,str((evidence.parent/endpoint['image']).relative_to(ROOT)))
                with Image.open(path) as image:images.append(image.convert('RGB'))
                refs.append(base.ref(path))
            tensor,_=encoded(*images,(192,128));inputs.append(tensor)
            rows.append(dict(id=case['case_id'],condition=condition,sourceRole='calibration-inspection-only',
                group=case['independence_group'],reportedFocusBefore=before['focus'],
                reportedFocusAfter=after['focus'],reportedChanged=int(before['focus']!=after['focus']),
                images=refs,tensorSHA256=base.sha(tensor.tobytes())))
    base.require(len(rows)==24 and Counter(r['condition'] for r in rows)==
        {'focus_moved':8,'boundary_unchanged':8,'content_only':8},'case_membership')
    inputs=np.stack(inputs);reported=np.array([r['reportedChanged'] for r in rows])
    matched_path=base.ROOT/'reports/work/TRANSITION-290/matched-states.json'
    matched=base.read(matched_path)
    base.require(matched['role']=='development-training-derived' and not matched['independentEvaluation'],'matched_role')
    base.checked(matched['parentAdmission']);base.checked(matched['parentReplacements'])
    state_inputs=[]
    for row in matched['rows']:
        images=[]
        for reference in row['images']:
            with Image.open(base.checked(reference)) as image:images.append(image.convert('RGB'))
        value,_=encoded(*images,(192,128));state_inputs.append(value)
    state_inputs=np.stack(state_inputs)
    state_labels=np.array([r['changed'] for r in matched['rows']])
    models={};state_models={}
    for name,folder in [('DTM078','CONFLICT-281'),('DTM081','TRANSITION-287'),('DTM082','TRANSITION-290')]:
        path=base.ROOT/f'reports/work/{folder}/{name}/result.json'
        reference=base.read(path)['model'];checkpoint=base.checked(reference)
        net=base.load_model(checkpoint) if name=='DTM078' else run.model.load_candidate(checkpoint)
        stamp=time.monotonic();probabilities=base.worker.score(net,inputs)
        by_condition={condition:agreement(probabilities[[r['condition']==condition for r in rows]],
            reported[[r['condition']==condition for r in rows]]) for condition in sorted({r['condition'] for r in rows})}
        models[name]=dict(model=reference,probabilities=probabilities.tolist(),
            overall=agreement(probabilities,reported),byCondition=by_condition,seconds=time.monotonic()-stamp)
        state_scores=base.worker.score(net,state_inputs)
        state_models[name]=dict(model=reference,probabilities=state_scores.tolist(),
            summary=base.trainer.w.summary(state_scores,state_labels),
            byCondition={condition:base.trainer.w.summary(
                state_scores[[r['condition']==condition for r in matched['rows']]],
                state_labels[[r['condition']==condition for r in matched['rows']]])
                for condition in sorted({r['condition'] for r in matched['rows']})})
    base.write(OUT,dict(version='native-inspection290-v1',rows=rows,models=models,
        inventory=base.ref(ROOT/'members.sha256.json'),runner=base.ref(Path(__file__)),
        encoder=base.ref(base.ROOT/'scripts/diagnose_signal95.py'),verifiedMembers=len(inventory),
        inputSHA256=base.sha(inputs.tobytes()),seconds=time.monotonic()-started,
        labelAuthority='Producer-reported observations. Capture-version evidence remains unresolved.',
        performanceQualified=False,dataRolesChanged=False,trainingEligible=False,
        limitations=['Agreement is not verified accuracy.', 'These related cases are not independent final evaluation.',
                     'Do not use this report to select thresholds or approve deployment.'],
        matchedStates=dict(manifest=base.ref(matched_path),role='development-training-derived',
            inputSHA256=base.sha(state_inputs.tobytes()),models=state_models,
            independentEvaluation=False,currentCandidateTrainedOnThesePairs=False)))
    print({name:record['overall'] for name,record in models.items()},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args();run_inspection()
