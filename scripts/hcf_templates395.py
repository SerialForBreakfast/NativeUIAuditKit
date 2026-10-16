"""Compile simple HCF descriptions into existing queue jobs. Never approve implicitly."""
import argparse
import json
from pathlib import Path

import research_queue as q
from experiment_templates import checked, pin

CATALOG_FIELDS={'task','outcomes','hypothesis','controlledComparison'}

CONTRACTS={
 'T42':({'bundle'},{'slice','classes','groups','matching'},'detector_case_match411.run','artifact','diagnostic'),
 'T50':({'labels','baseline','tool'},{'proposals','slice'},'vision_proposals415.run','artifact','diagnostic'),
 'T51':({'bundle','tool'},{'arm','elementType'},'swift_fallback416.run','artifact','diagnostic'),
 'T43':({'labels','baseline','model'},{'engine','confidence','imageSize','slice'},'detector_inference412.run','artifact','diagnostic'),
 'T44':({'manifests','quotas'},{'quotaSet','eligibility','dimensions'},'quota_comparison413.run','artifact','diagnostic'),
 'T46':({'recipe','generator'},{'target','timeoutSeconds'},'ios_native_capture_t46.run','artifact','diagnostic'),
 'T47':({'pairs','model'},{'direction','thresholds'},'temporal_pairs414.run','artifact','diagnostic'),
 'T49':({'configuration','initialization','membership','admission','pairs','prior'},{'arm','seed'},'transition_training415.training','training','training'),
 'T41':({'bundle','model','tool'},{'source','intervention'},'box_intervention410.run','artifact','diagnostic'),
 'T48':({'bundle','model','tool'},{'source','representation'},'representation_t48.run','artifact','diagnostic'),
 'T40':({'bundle'},set(),'cached_selection405.run','artifact','diagnostic'),
 'T37':({'capture','proposals','geometry','mapping','model','tool'},set(),'native_selection404.run','artifact','diagnostic'),
 'T39':({'qualification'},set(),'checkpoint_negative404.run','artifact','diagnostic'),
 'T38':({'configuration','initialization','membership'},set(),'checkpoint404.qualify','training','training'),
 'T01':({'catalog'},set(),'template_adapters395.run','artifact','diagnostic'),
 'T02':({'catalog','policy'},set(),'template_adapters395.run','artifact','diagnostic'),
 'T03':({'recipe'},set(),'template_bridge395.capture','capture','capture'),
 'T04':(set(),set(),'hcf_study371.admit','aggregation','diagnostic'),
 'T05':({'configuration'},set(),'hcf_study371.prepare_crops','aggregation','diagnostic'),
 'T06':({'configuration','initialization','membership'},set(),'hcf_factor_train376.train','training','training'),
 'T07':({'manifest','model','prepared','tensors'},{'batchSize'},'template_bridge395.score','evaluation','diagnostic'),
 'T08':({'predictions'},set(),'template_bridge395.report','artifact','diagnostic'),
 'T09':({'review','checkpoint'},{'method'},'template_adapters395.run','artifact','diagnostic'),
 'T10':({'candidate','environment'},{'experimentalID','precision'},'template_adapters395.run','artifact','export'),
 'T11':({'export','membership'},set(),'template_adapters395.run','artifact','diagnostic'),
 'T12':({'export','membership','parity'},{'repetitions'},'template_adapters395.run','artifact','diagnostic'),
 'T13':({'export','parity','runtime','license'},set(),'template_adapters395.run','artifact','diagnostic'),
 'T14':({'bundle','receipt','expected'},set(),'template_adapters395.run','artifact','diagnostic'),
 'T15':({'baseline','candidate'},{'comparison'},'template_analysis397.run','artifact','diagnostic'),
 'T16':({'qualification'},{'suite'},'template_analysis397.run','artifact','diagnostic'),
 'T17':({'catalog'},{'repetitions','maxFrames'},'template_analysis397.run','artifact','diagnostic'),
 'T18':({'catalog','retained','rules','model','tool'},set(),'template_analysis397.run','evaluation','diagnostic'),
 'T19':({'export','membership'},{'sourceRevision'},'template_analysis397.run','artifact','diagnostic'),
 'T20':({'catalog','retained','rules','selection'},set(),'template_analysis397.run','artifact','diagnostic'),
 'T21':({'catalog','retained','rules','model','tool'},{'scale'},'template_analysis397.run','evaluation','diagnostic'),
 'T22':({'export','membership'},{'sourceRevision'},'template_analysis397.run','artifact','diagnostic'),
 'T23':({'receipt','expected'},set(),'template_analysis397.run','artifact','diagnostic'),
 'T24':({'catalog','retained','rules','selection'},{'scale'},'template_analysis397.run','artifact','diagnostic'),
 'T25':({'catalog','retained','membership','sourceManifest','kernel','geometry','errors','driver'},set(),'outer_ring398.run','artifact','diagnostic'),
 'T26':({'catalog','retained','proposals','selection'},{'mode'},'geometry399.run','artifact','diagnostic'),
 'T27':({'kernel'},set(),'geometry399.run','artifact','diagnostic'),
 'T28':({'export','membership','parity','bundle','tool'},{'sourceRevision'},'geometry399.run','artifact','diagnostic'),
 'T29':({'proposals','geometry'},set(),'ring_body399.run','artifact','diagnostic'),
 'T30':({'primary','fallback'},{'enabled'},'fallback400.run','artifact','diagnostic'),
 'T31':({'proposals','geometry','partition'},set(),'fixed_insets401.run','artifact','diagnostic'),
 'T32':({'baseline','candidate','partition'},set(),'fixed_insets401.run','artifact','diagnostic'),
 'T33':({'evaluation'},{'className'},'coverage_reports402.run','artifact','diagnostic'),
 'T34':({'capture','mapping','kernel'},set(),'coverage_reports402.run','artifact','diagnostic'),
 'T36':({'capture'},set(),'profile_pixels402.run','artifact','diagnostic'),
}


def build(doc):
    required={'version','id','owner','template','question','decision','inputs','parameters','dependencies'}
    # BACKLOG410: optional catalog identity and decision text. Absent fields keep the original spec bytes.
    q.require(set(doc)<=required|{'capture','training'}|CATALOG_FIELDS and required<=set(doc),'description_fields')
    if 'task' in doc:q.require(isinstance(doc['task'],str) and q.ID.fullmatch(doc['task']),'description_task')
    if 'outcomes' in doc:
        q.require(isinstance(doc['outcomes'],dict) and {'supported','contradicted'}<=set(doc['outcomes'])
                  <={'supported','contradicted','inconclusive'} and
                  all(isinstance(v,str) and len(v.strip())>=12 for v in doc['outcomes'].values()),'description_outcomes')
    for key in ('hypothesis','controlledComparison'):
        if key in doc:q.require(isinstance(doc[key],str) and len(doc[key].strip())>=12,'description_'+key)
    q.require(doc['version']=='hcf-template-description-v1','description_version')
    q.require(doc['template'] in CONTRACTS,'template_unknown')
    inputs,parameters,step,kind,authority=CONTRACTS[doc['template']]
    optional={'T03':{'staging'},'T10':{'sourceReport','sourcePackage'},'T18':{'membership'},'T21':{'membership'},'T41':{'candidate'},'T47':{'prior','rule'}}.get(doc['template'],set())
    q.require(inputs<=set(doc['inputs']) and set(doc['inputs'])<=inputs|optional,'template_inputs')
    # T47 `scorer` is optional so that registered T47 specifications keep their identity.
    # B405-125/B405-119: T20 `taxonomy` and T25 `kernelSettings` are optional for the same reason.
    q.require(set(doc['parameters'])-{'T47':{'scorer'},'T20':{'taxonomy'},'T25':{'kernelSettings'}}.get(doc['template'],set())==parameters,'template_parameters')
    if doc['template']=='T41':
        from box_intervention410 import parameters as intervention
        intervention(doc['parameters'])
    if doc['template']=='T48':
        from representation_t48 import parameters as representation
        representation(doc['parameters'])
    if doc['template']=='T42':
        from detector_case_match411 import parameters as case
        case(doc['parameters'])
    if doc['template']=='T50':
        from vision_proposals415 import parameters as proposals
        proposals(doc['parameters'])
    if doc['template']=='T43':
        from detector_inference412 import parameters as inference
        inference(doc['parameters'])
    if doc['template']=='T49':
        from transition_training415 import parameters as transition
        transition(doc['parameters'])
    if doc['template']=='T47':
        from temporal_pairs414 import parameters as temporal
        temporal(doc['parameters'])
    if doc['template']=='T44':
        from quota_comparison413 import parameters as quota
        quota(doc['parameters'])
    if doc['template']=='T46':
        from ios_native_capture_t46 import parameters as native
        native(doc['parameters'])
    if doc['template']=='T51':
        from swift_fallback416 import parameters as fallback
        fallback(doc['parameters'])
    if doc['template']=='T25' and 'kernelSettings' in doc['parameters']:
        from outer_ring398 import KERNEL_SETTINGS
        q.require(doc['parameters']['kernelSettings'] in KERNEL_SETTINGS,'kernel_settings')
    if doc['template']=='T20' and 'taxonomy' in doc['parameters']:
        from template_analysis397 import TAXONOMY
        q.require(doc['parameters']['taxonomy']==TAXONOMY,'taxonomy_unknown')
    for ref in doc['inputs'].values():
        if set(ref)=={'job','output'}:
            q.check_name(ref['output'])
            q.require(any(d['job']==ref['job'] and ref['output'] in d['outputs'] for d in doc['dependencies']),
                      'input_dependency_not_declared')
            q.require(doc['template'] not in ('T03','T05','T06','T07'),'binding_requires_pinned_inputs')
        else:checked(ref)
    if doc['template']=='T10':
        compressed=doc['parameters']['precision'] in ('int8weights','palette6weights')
        q.require(('sourceReport' in doc['inputs'])==compressed and
                  ('sourcePackage' in doc['inputs'])==compressed,'compression_inputs')
    q.require(('capture' in doc)==(authority=='capture'),'capture_contract')
    q.require(('training' in doc)==(authority=='training'),'training_contract')
    if authority=='capture':
        q.require(doc['capture']['plan']==doc['inputs']['recipe'],'capture_recipe_binding')
    if authority=='training':
        q.require(doc['training']['initialization']==doc['inputs']['initialization'],'training_initialization_binding')
        q.require(doc['inputs']['membership'] in doc['training']['membership'],'training_membership_binding')
        # T49 keeps the frozen 10-epoch FOCUS366 recipe. Other training templates use 30 epochs.
        q.require(doc['training']['epochs']==(10 if doc['template']=='T49' else 30) and doc['training']['resume']=='restart','training_variant')
        config=q.load(checked(doc['inputs']['configuration']))
        q.require(config['initialization']==doc['inputs']['initialization'],'training_configuration_binding')
    module=step.split('.')[0]
    # The immutable spec records compiler provenance. Only execution sources are runtime inputs.
    sources=[pin(q.MODULES/(module+'.py'))]
    if doc['template']=='T10':
        sources.extend(pin(q.MODULES/name) for name in
            ('export_focus_ring_coreml.py','compress_focus_ring_coreml.py','focus_ring_backbone.py','focus_ring_baseline.py'))
    if doc['template'] in ('T11','T12'):
        sources += [pin(q.ROOT/'.build/standard392-swift/arm64-apple-macosx/debug/FocusRingTool'),
                    pin(q.ROOT/'Tools/FocusRingTool/main.swift')]
    stage=[]
    if 'configuration' in doc['inputs']:stage=[dict(to='config.json',**{'from':doc['inputs']['configuration']})]
    pinned=[r for r in doc['inputs'].values() if 'path' in r]
    reads=list(dict.fromkeys(r['path'] for r in pinned))
    evidence=dict(reads=reads,artifactReceipt='artifact-receipt.json')
    if kind=='aggregation':evidence=dict(reads=reads,citations='sources.json')
    if kind=='capture':evidence=dict(reads=reads,captureReceipt='capture-evidence.json')
    if kind=='training':
        evidence=dict(reads=reads,weights='final.pt',history='history.json',trainingReport='fit.json')
    if kind=='evaluation':
        reference=doc['inputs']['rules' if doc['template'] in ('T18','T21') else 'manifest']
        if 'job' in reference:
            q.require('membership' in doc['inputs'],'dependency_membership_required')
            membership=q.load(checked(doc['inputs']['membership']))
        else: membership=q.load(checked(reference))
        evidence=dict(reads=reads,model=doc['inputs']['model']['path'],
            predictions='proposal-selection.json' if doc['template'] in ('T18','T21') else 'predictions.json',membershipCount=len(membership['rows']))
    # Legacy native operations retain their adapters. The bridge adds receipts only.
    if doc['template'] in ('T04','T05','T06'):
        step='template_bridge395.native';module='template_bridge395'
        sources.append(pin(q.MODULES/(module+'.py')))
    spec=dict(version='research-spec-v2',id=doc['id'],task=doc.get('task','TEMPLATE395'),owner=doc['owner'],kind='screen',
        authority=authority,jobKind=kind,question=doc['question'],hypothesis=doc.get('hypothesis',doc['question']),
        controlledComparison=doc.get('controlledComparison',
            'Use fixed inputs and existing implementations. Keep data roles and Standard models unchanged.'),
        decisionRule=doc['decision'],nextActionByOutcome=doc.get('outcomes',dict(supported='Review the verified output before preparing a dependent job.',
            contradicted='Preserve the failure and repair its exact requirement before an explicit successor.')),
        inputs=list({p['path']:p for p in sources+pinned}.values()),
        dependencies=doc['dependencies'],stage=stage,evidence=evidence,
        adapter=dict(type='python-callable',steps=[step],outputAttributes=[module+'.OUT']),
        limits=dict(timeoutSeconds=1800 if authority in ('training','export') else 800,
                    maxOutputBytes=2<<30 if authority in ('training','export') else 100_000_000,maxAttempts=1),
        template=dict(id=doc['template'],version=1,inputs=doc['inputs'],parameters=doc['parameters'],
                      compiler=pin(Path(__file__))))
    for name in ('capture','training'):
        if name in doc:spec[name]=doc[name]
    q.validate(spec)
    return spec


def register(doc,queue=q.QUEUE):
    spec=build(doc)
    queue=q.local_path(q.ROOT,q.relative(Path(queue).absolute()));queue.mkdir(parents=True,exist_ok=True)
    with q.host_lock(queue/'template-registration.lock'):
        folder=queue/'template-registrations'/doc['id'];folder.mkdir(parents=True,exist_ok=True)
        path=folder/'spec.json'
        if path.exists():q.require(q.load(path)==spec,'immutable_registration_conflict')
        else:q.save(path,spec)
        state=q.submit(path,queue)
    return dict(id=spec['id'],state=state,approved=False,executionStarted=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['catalog','preview','register'])
    parser.add_argument('description',type=Path,nargs='?')
    parser.add_argument('--queue',type=Path,default=q.QUEUE)
    args=parser.parse_args()
    if args.action=='catalog':
        print(json.dumps([dict(id=ident,version=1,requiredInputs=sorted(value[0]),
            requiredParameters=sorted(value[1]),jobKind=value[3],authority=value[4],
            qualification='See TEMPLATE395 results. A callable adapter does not establish native or model qualification.')
            for ident,value in CONTRACTS.items()],indent=2))
    else:
        if args.description is None:parser.error('description is required')
        doc=q.load(args.description)
        print(json.dumps(build(doc) if args.action=='preview' else register(doc,args.queue),indent=2))
