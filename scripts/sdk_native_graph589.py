"""Bind an approved SDK crop campaign to resident training and scoring components."""
from pathlib import Path
import research_queue as q
from template_inputs398 import checked,pin
from sdk_native589 import consent


def compile_request(path,destination,queue=q.QUEUE,limit_overrides=None):
    cfg=q.load(path);q.require(cfg['version']=='sdk-native-campaign589-v1' and q.ID.fullmatch(cfg['id']),'native589_campaign')
    consent(cfg)
    for name in ('base','suite','reference','replayProtocol','source'):checked(cfg[name])
    prep=q.load(queue/'jobs'/cfg['preparation']/'spec.json');q.require(prep['adapter']['steps']==['native_training587.run'],'native589_preparation_adapter')
    request=q.load(checked(prep['request']));q.require(request['captures']==cfg['captures'] and request['source']==cfg['source'] and request['exclusions']==cfg['exclusions'],'native589_preparation_scope')
    jobs=[]
    def dep(s,*outputs):return dict(job=s['id'],specSHA256=q.text_digest(s),outputs=list(outputs))
    def make(suffix,module,step,inputs,deps=(),training=False,extra=()):
        ident=cfg['id']+'-'+suffix;sources=[pin(q.MODULES/(module+'.py')),*extra]
        refs=[r for r in inputs.values() if 'path' in r]
        reads=list(dict.fromkeys(r['path'] for r in refs))
        if module=='sdk_native589':sources.append(pin(path));reads.append(q.relative(path))
        s=dict(version='research-spec-v2',id=ident,task='NATIVE589',owner='Maximum-mini-NUIAK',kind='screen',jobKind='training' if training else 'artifact',authority='training' if training else 'diagnostic',
            question='Do fresh SDK native focus crops improve development selections without losing retained successes?',
            hypothesis='Add verified native training crops to approved replay while matching presentation counts and preserving all regression gates.',
            controlledComparison='Pinned FDR-001 initialization, seed 371, 30 fixed epochs, batch 16, resident balanced trainer, equal class presentations and final checkpoint selection. Change eligible native training membership only.',
            decisionRule='Reject every lost previous success and new wrong selection. Preserve profile uncertainty and existing legacy gates. Keep results provisional.',
            nextActionByOutcome=dict(supported='Request Joe review and fresh independent qualification before model acceptance.',contradicted='Preserve failed evidence and select case-linked diagnosis. Do not repeat an unchanged fit.',inconclusive='Record missing evidence. Continue unrelated approved work.'),
            inputs=list({r['path']:r for r in sources+refs}.values()),dependencies=list(deps),
            template=dict(id='sdk-native-campaign589',inputs=inputs,parameters={}),
            adapter=dict(type='python-callable',steps=[module+'.'+step],outputAttributes=[module+'.OUT']),
            limits=dict(timeoutSeconds=43200 if training else 800,maxOutputBytes=2<<30 if training else 100000000,maxAttempts=1),
            evidence=dict(reads=list(dict.fromkeys(reads)),**(dict(weights='final.pt',history='history.json',trainingReport='fit.json') if training else dict(artifactReceipt='artifact-receipt.json'))))
        if module=='sdk_native589':s['request']=pin(path)
        if training:
            s['training']=dict(experimentLogRunId=ident.upper(),membership=[pin(path),cfg['replayProtocol']],initialization=cfg['base'],epochs=30,storageBudgetBytes=2<<30,
                acceptanceEvidence='Full retained and native development comparisons at threshold 0.85. Reject lost successes and new wrong selections. Independent qualification remains excluded. No promotion.',resume='restart')
            s['inputs']=list({r['path']:r for r in s['inputs']+[cfg['approval'],cfg['replayProtocol']]}.values())
            s['evidence']['reads']=list(dict.fromkeys(s['evidence']['reads']+[cfg['approval']['path'],cfg['replayProtocol']['path']]))
        q.validate(s);jobs.append(s);return s
    admitted=make('admission','sdk_native589','admission',dict(intakeRequest=dict(job=prep['id'],output='intake-request.json'),intake=dict(job=prep['id'],output='intake.json'),crops=dict(job=prep['id'],output='crops.json')),[dep(prep,'intake-request.json','intake.json','crops.json')])
    admitted['inputs'] += [cfg['approval'],cfg['source']]+q.load(checked(cfg['source']))['files']
    admitted['evidence']['reads'] += [cfg['approval']['path'],cfg['source']['path']]
    corpus=make('corpus','sdk_native589','corpus',dict(admitted=dict(job=admitted['id'],output='crops.json')),[dep(admitted,'crops.json')])
    corpus['inputs'] += [cfg['replayProtocol']]+cfg['protectedImages'];corpus['evidence']['reads'].append(cfg['replayProtocol']['path'])
    models={};scores={}
    for arm in ('control','native'):
        fit=make(arm+'-train','sdk_native589','train',dict(membership=dict(job=corpus['id'],output=arm+'.json'),initialization=cfg['base']),[dep(corpus,arm+'.json')],True,
            extra=[pin(q.MODULES/name) for name in ('train_focus_ring_detector.py','focus_ring_backbone.py')]);models[arm]=fit
        scores[arm]=make(arm+'-retention','focus_replay568','score',dict(model=dict(job=fit['id'],output='model.json'),suite=cfg['suite'],base=cfg['base']),[dep(fit,'model.json')])
    native=make('native-development','sdk_native589','score_native',dict(admitted=dict(job=admitted['id'],output='crops.json'),base=cfg['base'],control=dict(job=models['control']['id'],output='model.json'),native=dict(job=models['native']['id'],output='model.json')),
        [dep(admitted,'crops.json'),dep(models['control'],'model.json'),dep(models['native'],'model.json')])
    make('comparison','sdk_native589','compare',dict(reference=cfg['reference'],control=dict(job=scores['control']['id'],output='benchmark_summary.json'),native=dict(job=scores['native']['id'],output='benchmark_summary.json'),nativeScores=dict(job=native['id'],output='benchmark_summary.json')),
        [dep(scores['control'],'benchmark_summary.json'),dep(scores['native'],'benchmark_summary.json'),dep(native,'benchmark_summary.json')])
    limits=limit_overrides or {}
    q.require(isinstance(limits,dict) and set(limits)<={s['id'] for s in jobs},'native589_limit_ids')
    for s in jobs:
        if s['id'] not in limits:continue
        values=limits[s['id']]
        q.require(isinstance(values,dict) and set(values)=={'timeoutSeconds','maxOutputBytes'},'native589_limit_fields')
        q.require(all(type(v) is int and 0<v<=s['limits'][k] for k,v in values.items()),'native589_limit_expansion')
        s['limits'].update(values)
    destination.mkdir(parents=True,exist_ok=False);known={};entries=[]
    for s in jobs:
        # Final producer hashes include all explicit data and source pins above.
        for d in s['dependencies']:
            if d['job'] in known:d['specSHA256']=q.text_digest(known[d['job']])
        q.validate(s);q.verify_pins(s);target=destination/(s['id']+'.json');q.save(target,s)
        entries.append(dict(job=s['id'],spec=pin(target),specSHA256=q.text_digest(s)));known[s['id']]=s
    manifest=dict(version='model-decision-compiled-v1',plan=pin(path),existing=[dict(job=prep['id'],specSHA256=q.text_digest(prep))],jobs=entries,
        executionStarted=False,modelAccepted=False,resultsProvisional=True,budget=dict(maxJobs=len(jobs),maxSeconds=sum(s['limits']['timeoutSeconds'] for s in jobs),maxOutputBytes=sum(s['limits']['maxOutputBytes'] for s in jobs)))
    q.save(destination/'compiled.json',manifest);return manifest
