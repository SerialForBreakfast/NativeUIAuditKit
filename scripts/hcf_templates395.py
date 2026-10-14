"""Compile simple HCF descriptions into existing queue jobs. Never approve implicitly."""
import argparse
import json
from pathlib import Path

import research_queue as q
from experiment_templates import checked, pin

CONTRACTS={
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
    q.require(set(doc)<=required|{'capture','training'} and required<=set(doc),'description_fields')
    q.require(doc['version']=='hcf-template-description-v1','description_version')
    q.require(doc['template'] in CONTRACTS,'template_unknown')
    inputs,parameters,step,kind,authority=CONTRACTS[doc['template']]
    optional={'T03':{'staging'},'T10':{'sourceReport','sourcePackage'},'T18':{'membership'},'T21':{'membership'}}.get(doc['template'],set())
    q.require(inputs<=set(doc['inputs']) and set(doc['inputs'])<=inputs|optional,'template_inputs')
    q.require(set(doc['parameters'])==parameters,'template_parameters')
    for ref in doc['inputs'].values():
        if set(ref)=={'job','output'}:
            q.check_name(ref['output'])
            q.require(any(d['job']==ref['job'] and ref['output'] in d['outputs'] for d in doc['dependencies']),
                      'input_dependency_not_declared')
            q.require(doc['template'] not in ('T03','T05','T06','T07'),'binding_requires_pinned_inputs')
        else:checked(ref)
    if doc['template']=='T10':
        compressed=doc['parameters']['precision']=='int8weights'
        q.require(('sourceReport' in doc['inputs'])==compressed and
                  ('sourcePackage' in doc['inputs'])==compressed,'compression_inputs')
    q.require(('capture' in doc)==(authority=='capture'),'capture_contract')
    q.require(('training' in doc)==(authority=='training'),'training_contract')
    if authority=='capture':
        q.require(doc['capture']['plan']==doc['inputs']['recipe'],'capture_recipe_binding')
    if authority=='training':
        q.require(doc['training']['initialization']==doc['inputs']['initialization'],'training_initialization_binding')
        q.require(doc['inputs']['membership'] in doc['training']['membership'],'training_membership_binding')
        q.require(doc['training']['epochs']==30 and doc['training']['resume']=='restart','training_variant')
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
    spec=dict(version='research-spec-v2',id=doc['id'],task='TEMPLATE395',owner=doc['owner'],kind='screen',
        authority=authority,jobKind=kind,question=doc['question'],hypothesis=doc['question'],
        controlledComparison='Use fixed inputs and existing implementations. Keep data roles and Standard models unchanged.',
        decisionRule=doc['decision'],nextActionByOutcome=dict(supported='Review the verified output before preparing a dependent job.',
            contradicted='Preserve the failure and repair its exact requirement before an explicit successor.'),
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
