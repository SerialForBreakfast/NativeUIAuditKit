"""Reusable retained comparisons, qualification, preparation, and delivery checks."""
import json
from pathlib import Path
import statistics
import sys
import time

import research_queue as q
from template_inputs398 import checked, pin
from template_adapters395 import document, resolve_inputs, command, verified_export, runtime_items

OUT = None
SUITES = {
    'batch-registration': ['test_experiment_batch402'],
    'source-and-observer': ['test_template_isolation398', 'test_observer_identity398', 'test_research_trust'],
    'contracts': ['test_templates395', 'test_template_native395', 'test_template_inference395', 'test_hcf396', 'test_analysis397'],
    'queue-recovery': ['test_research_queue', 'test_research_dashboard'],
}


def matched(baseline, candidate):
    def index(doc):
        rows=doc['rows']
        q.require(rows and len({r['id'] for r in rows})==len(rows),'comparison_duplicate_or_empty')
        q.require(all(r['role'] in ('development','retained','calibration') for r in rows),'audit_locked')
        q.require(all(r['outcome'] in ('correct','wrong','miss') for r in rows),'comparison_outcome')
        groups={}
        for row in rows:
            q.require(groups.setdefault(row['group'],row['role'])==row['role'],'comparison_role_leak')
        return {r['id']:r for r in rows}
    left,right=index(baseline),index(candidate)
    q.require(left.keys()==right.keys(),'comparison_membership')
    rows=[]
    for ident,a in left.items():
        b=right[ident]
        q.require(all(a[k]==b[k] for k in ('sha256','group','role','profile','family')),'comparison_identity')
        rows.append(dict(id=ident,group=a['group'],profile=a['profile'],role=a['role'],family=a['family'],
            baseline=a['outcome'],candidate=b['outcome'],gain=a['outcome']!='correct' and b['outcome']=='correct',
            loss=a['outcome']=='correct' and b['outcome']!='correct'))
    slices={}
    for profile in sorted({r['profile'] for r in rows}):
        subset=[r for r in rows if r['profile']==profile]
        slices[profile]=dict(frames=len(subset),groups=len({r['group'] for r in subset}),
            gains=[r['id'] for r in subset if r['gain']],losses=[r['id'] for r in subset if r['loss']],
            baseline={k:sum(r['baseline']==k for r in subset) for k in ('correct','wrong','miss')},
            candidate={k:sum(r['candidate']==k for r in subset) for k in ('correct','wrong','miss')})
    return dict(rows=rows,slices=slices,previousSuccessesPreserved=not any(r['loss'] for r in rows),
        noFocusAccuracy=None,physicalAccuracy=None,modelAccepted=False,
        limitation='Inspected groups only. Known boxes remain an upper bound. Zero losses do not establish deployment safety.')


def compare(inputs,params,out):
    result=matched(document(inputs['baseline']),document(inputs['candidate']))
    q.save(out/'comparison.json',dict(result,version='matched-selection-v1',comparison=params['comparison'],sources=inputs))


def qualify(inputs,params,out):
    suite=params['suite'];q.require(suite in SUITES,'qualification_suite')
    cfg=document(inputs['qualification'])
    q.require(cfg.get('version')=='template-qualification-v1' and cfg.get('suite')==suite,'qualification_contract')
    expected={name+'.py' for name in SUITES[suite]}
    q.require({Path(ref['path']).name for ref in cfg['tests']}==expected,'qualification_tests')
    for ref in cfg['tests']:checked(ref)
    command([sys.executable,'-m','unittest',*SUITES[suite]],out,'qualification',timeout=700)
    q.save(out/'qualification-summary.json',dict(suite=suite,passed=True,modelAccepted=False,
        scope='Positive and negative software checks. No model accuracy claim.'))


def preparation(inputs,params,out):
    from hcf_prepare389 import OLD_ROOT
    from PIL import Image
    n=params['maxFrames'];repeats=params['repetitions']
    q.require(type(n) is int and 2<=n<=32 and type(repeats) is int and 3<=repeats<=5,'preparation_budget')
    rows=sorted((r for r in document(inputs['catalog'])['rows'] if r['role']=='development'),key=lambda r:r['id'])[:n]
    q.require(len(rows)==n,'preparation_support')
    def prepare(row):
        path=Path(row['path'])
        if path.is_relative_to(OLD_ROOT):path=q.ROOT/path.relative_to(OLD_ROOT)
        q.require(path.resolve()==path and path.is_relative_to('/Volumes/training-drive/data/NUIAK'),'preparation_path')
        q.require(q.digest(path)==row['sha256'],'preparation_input_changed')
        with Image.open(path) as image:
            image.load();return (row['sha256'],image.size,image.mode)
    timings=[]
    for repeat in range(repeats):
        arm={}
        for mode in (('separate','shared') if repeat%2==0 else ('shared','separate')):
            start=time.monotonic();cache={};values=[]
            for consumer in range(3):
                current=[]
                for row in rows:
                    key=(row['sha256'],row['path'])
                    if mode=='shared' and key in cache:value=cache[key]
                    else:value=prepare(row);cache[key]=value
                    current.append(value)
                values.append(current)
            q.require(values[0]==values[1]==values[2],'preparation_output_changed')
            arm[mode]=dict(seconds=time.monotonic()-start,decodedFrames=n if mode=='shared' else n*3,values=values[0])
        q.require(arm['shared']['values']==arm['separate']['values'],'preparation_arm_mismatch')
        timings.append({k:{f:v for f,v in value.items() if f!='values'} for k,value in arm.items()})
    q.save(out/'efficiency.json',dict(version='preparation-comparison-v1',frames=n,repetitions=repeats,runs=timings,
        medianSeconds={k:statistics.median(t[k]['seconds'] for t in timings) for k in ('shared','separate')},
        outputsMatch=True,modelAccepted=False,limitation='Image decode and geometry only. OS caches are uncontrolled; no inference or training speedup claim.'))


def proposals(inputs,params,out):
    import copy
    import hcf_prepare389 as legacy
    import focus_runtime
    docs={('hcf371r4-40-catalog','admission.json'):document(inputs['catalog']),
          ('hcf371-00-retained','admission.json'):document(inputs['retained']),
          ('hcf371r4-60-rules','comparison.json'):document(inputs['rules']),
          ('hcf375c-70-crop-train','model.json'):dict(path=str(checked(inputs['model'])),sha256=inputs['model']['sha256'],kind='crop')}
    if params:
        scale=params['scale'];q.require(scale in (1.05,1.10),'proposal_scale')
        frames={r['id']:r for name in ('catalog','retained') for r in document(inputs[name])['rows']}
        rules=copy.deepcopy(docs[('hcf371r4-60-rules','comparison.json')])
        for row in rules['rows']:
            frame=frames[row['id']]
            row['prediction']['candidates']=[expand(b,scale,frame['width'],frame['height']) for b in row['prediction']['candidates']]
        docs[('hcf371r4-60-rules','comparison.json')]=rules
        q.save(out/'geometry-change.json',dict(scale=scale,source=inputs['rules'],
            method='Expand candidate bounds about their center, then clip to the parent frame. No labels choose the transform.',
            originalCropsPreserved=True))
    focus_runtime.TOOL=checked(inputs['tool']);legacy.OUT=out
    legacy.proposal_selection(docs,list(inputs.values()))
    result=q.load(out/'proposal-selection.json')
    result['proposalMode']=docs[('hcf371r4-60-rules','comparison.json')].get('method','bright-closed-stroke-v1')
    result['proposalSource']=inputs['rules']
    q.save(out/'proposal-selection.json',result,replace=True)


def expand(bounds,scale,width,height):
    x,y,w,h=bounds
    left=max(0,x-w*(scale-1)/2);top=max(0,y-h*(scale-1)/2)
    right=min(width,x+w+w*(scale-1)/2);bottom=min(height,y+h+h*(scale-1)/2)
    q.require(right>left and bottom>top,'proposal_bounds')
    return [left,top,right-left,bottom-top]


def identity(inputs,params,out):
    from focus_ring_baseline import artifact_digest
    doc,compiled=verified_export(inputs['export']);rows,items=runtime_items(inputs['membership'])
    q.require(isinstance(params['sourceRevision'],str) and params['sourceRevision'],'source_revision')
    q.save(out/'observer-identity.json',dict(version='observer-identity-v1',sourceRevision=params['sourceRevision'],
        digestAlgorithm='focus-artifact-v1',compiledSHA256=artifact_digest(compiled),
        packageSHA256=artifact_digest(q.local_path(q.ROOT,doc['package'])),export=inputs['export'],
        membership=inputs['membership'],rows=rows,coordinateConvention='top-left parent-frame pixels',
        preprocessing='FocusRingClassifier.makeCrop; 16 percent expansion; 256x256 RGB; model scales by 1/255',
        thresholds=dict(focus=.85,ambiguity=.70),backend='Vision-cpuOnly',minimumModelHost='macOS 15',
        unsupportedHost='HCF unavailable; preserve Standard on macOS 14',navigationAuthority=False,modelAccepted=False,
        limitation='Identity proposal only. TTR must validate the digest algorithm and return actual loaded-artifact and inference receipts.'))


def observer_contract(inputs,params,out):
    from observer_identity398 import compiled_digest
    identity(inputs,params,out)
    value=q.load(out/'observer-identity.json')
    _,compiled=verified_export(inputs['export'])
    value['version']='observer-identity-v2'
    value['producerCompiledSHA256']=compiled_digest(compiled)
    value.pop('compiledSHA256')
    value['digestAlgorithm']='compiled-tree-sha256-v1'
    value['packageDigestAlgorithm']='focus-artifact-v1'
    value['consumerRequirements']=[
        'Record the actual loaded compiled digest before and after inference.',
        'Record consumer OS, architecture, compiler version, and source revision.',
        'Preserve parent image hashes, candidate IDs, bounds, and RGB crop hashes.',
        'Return explicit unavailable, failed, abstained, or scored states.',
        'Do not treat producer compiled bytes as a portable consumer compilation identity.',
        'Run the existing FocusRingTool version 1 protocol from a NUIAK checkout for the initial observer test.']
    value['limitation']='Contract preparation only. Actual TTR inference and sender verification remain required.'
    q.save(out/'observer-contract.json',value)


def observer_verify(inputs,params,out):
    from observer_identity398 import verify_receipt
    q.save(out/'observer-verification.json',verify_receipt(document(inputs['receipt']),document(inputs['expected'])))


def proposal_audit(inputs,params,out):
    from score_hcf_pilot import iou
    from hcf_compare371 import box
    rules=document(inputs['rules']);selection=document(inputs['selection'])
    # Identity checks reject role, image, group, or membership drift before diagnosis.
    matched(rules,selection)
    catalog=[r for name in ('catalog','retained') for r in document(inputs[name])['rows']]
    frames={r['id']:r for r in catalog}
    q.require(len(frames)==len(catalog),'catalog_duplicate')
    selected={r['id']:r for r in selection['rows']};rows=[]
    for rule in rules['rows']:
        frame=frames[rule['id']];observed=selected[rule['id']]
        q.require(all(frame[k]==rule[k] for k in ('sha256','group','role','profile')),'audit_identity')
        candidates=rule['prediction']['candidates'];scores=observed['prediction']['scores']
        if params:
            q.require(params['scale'] in (1.05,1.10),'audit_scale')
            candidates=[expand(b,params['scale'],frame['width'],frame['height']) for b in candidates]
        q.require(len(candidates)==len(scores),'audit_score_count')
        overlaps=[iou(box(candidate),box(frame['boxes'][frame['focus']])) for candidate in candidates]
        matched_indices=[i for i,value in enumerate(overlaps) if value>=.5]
        reason=('correct' if observed['outcome']=='correct' else 'proposal_missing' if not matched_indices
                else 'matching_proposal_not_selected')
        rows.append(dict(id=rule['id'],group=frame['group'],profile=frame['profile'],reason=reason,
            bestProposalIoU=max(overlaps,default=None),matchingScores=[scores[i] for i in matched_indices],
            outcome=observed['outcome']))
    q.save(out/'proposal-audit.json',dict(version='proposal-audit-v1',rows=rows,modelAccepted=False,
        counts={profile:{reason:sum(r['profile']==profile and r['reason']==reason for r in rows)
                        for reason in ('correct','proposal_missing','matching_proposal_not_selected')}
                for profile in sorted({r['profile'] for r in rows})},
        source=inputs['rules'],
        limitation='Proposal identity follows the pinned source. Outline/body IoU is diagnostic, not a calibrated inset.'))


OPERATIONS={'T15':compare,'T16':qualify,'T17':preparation,'T18':proposals,'T19':identity,'T20':proposal_audit,'T21':proposals,'T22':observer_contract,'T23':observer_verify,'T24':proposal_audit}


def run():
    contract=q.load(OUT.parents[2]/'spec.json')['template'];start=time.monotonic()
    try:
        inputs=resolve_inputs(contract,OUT)
        OPERATIONS[contract['id']](inputs,contract['parameters'],OUT)
        files=[dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in sorted(OUT.rglob('*')) if p.is_file()]
        q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=files))
        q.save(OUT/'template-result.json',dict(execution='complete',modelAccepted=False,seconds=time.monotonic()-start))
    except Exception as error:
        q.save(OUT/'template-result.json',dict(execution='failed',code=str(error)[:500],modelAccepted=False))
        raise
