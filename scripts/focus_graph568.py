"""Compile native corpus, matched training, scoring, and a bounded replay follow-up."""
from pathlib import Path
import research_queue as q
from template_inputs398 import checked,pin


def compile_request(path,destination):
    r=q.load(path);q.require(r['version']=='focus-graph568-v1','focus_graph_version')
    corpus=q.load(checked(r['corpusRequest']));q.require(corpus['version']=='native-focus-corpus568-v1','focus_graph_corpus')
    base=checked(r['base']);reference=q.load(checked(r['reference']))
    q.require(reference['suiteSHA256']==r['suite']['sha256'] and reference['threshold']==.85,'focus_graph_reference')
    jobs=[]
    def make(ident,module,step,inputs,deps=(),training=False,parameters=None):
        sources=[pin(q.MODULES/(module+'.py'))]
        for name in ('train_focus556.py','focus_ring_backbone.py','focus_corpus568.py','focus_replay568.py'):
            if module=='focus_replay568':sources.append(pin(q.MODULES/name))
        refs=[ref for ref in inputs.values() if set(ref)=={'path','sha256'}]
        spec=dict(version='research-spec-v2',id=ident,task='FOCUS568',owner='Maximum-mini-NUIAK',kind='screen',
            authority='training' if training else 'diagnostic',jobKind='training' if training else 'artifact',
            question=r['question'],hypothesis=r['question'],controlledComparison='Matched replay versus native additions. Fixed initialization, seed 42, 30 epochs, batch 64, rate 0.00003, and equal presentations.',
            decisionRule='Reject any lost previous success or new wrong selection. Keep results provisional. No promotion.',
            nextActionByOutcome=dict(supported='Propose independent runtime and application qualification.',contradicted='Preserve failed candidates and diagnose exact losses without repeating unchanged training.'),
            inputs=list({ref['path']:ref for ref in sources+refs}.values()),dependencies=list(deps),
            template=dict(id='native-focus-graph568',inputs=inputs,parameters=parameters or {}),
            adapter=dict(type='python-callable',steps=[module+'.'+step],outputAttributes=[module+'.OUT']),
            limits=dict(timeoutSeconds=1800 if training else 800,maxOutputBytes=2<<30 if training else 100000000,maxAttempts=1),
            evidence=dict(reads=[ref['path'] for ref in refs],**(dict(weights='final.pt',history='history.json',trainingReport='fit.json') if training else dict(artifactReceipt='artifact-receipt.json'))))
        if training:spec['training']=dict(experimentLogRunId=ident.upper(),initialization=r['base'],membership=[r['corpusRequest'],corpus['manifest'],corpus['replayProtocol']],epochs=30,storageBudgetBytes=2<<30,acceptanceEvidence='Preserve legacy and ancillary decisions. Require all focus development gates. No model promotion.',resume='restart')
        if training:
            declared=spec['training']['membership']
            spec['inputs']=list({v['path']:v for v in spec['inputs']+declared}.values())
            spec['evidence']['reads']=list(dict.fromkeys(spec['evidence']['reads']+[v['path'] for v in declared]))
        jobs.append(spec);return spec
    def dep(spec,*outputs):return dict(job=spec['id'],specSHA256=q.text_digest(spec),outputs=list(outputs))
    producer=make(r['id']+'-corpus','focus_corpus568','prepare',dict(request=r['corpusRequest']))
    # The producer uses its first input as its request. Pin the source and Swift runtime explicitly.
    producer['inputs']=[r['corpusRequest']]+[v for v in producer['inputs'] if v!=r['corpusRequest']]+corpus['sourceFiles']+[corpus['manifest'],corpus['replayProtocol'],corpus['approval'],corpus['runtimeTool'],corpus['runtimeSource']]
    producer['inputs']=list({v['path']:v for v in producer['inputs']}.values())
    scores={}
    for arm in ('control','native'):
        train=make(r['id']+'-'+arm+'-train','focus_replay568','train',dict(corpus=dict(job=producer['id'],output='corpus.json'),model=r['base']),[dep(producer,'corpus.json')],True,dict(arm=arm))
        score=make(r['id']+'-'+arm+'-score','focus_replay568','score',dict(model=dict(job=train['id'],output='model.json'),suite=r['suite'],base=r['base']),[dep(train,'model.json')]);scores[arm]=score
    comparison=make(r['id']+'-compare','focus_replay568','compare',dict(reference=r['reference'],control=dict(job=scores['control']['id'],output='benchmark_summary.json'),native=dict(job=scores['native']['id'],output='benchmark_summary.json')),[dep(scores[arm],'benchmark_summary.json') for arm in ('control','native')])
    boost=make(r['id']+'-boost-train','focus_replay568','train',dict(corpus=dict(job=producer['id'],output='corpus.json'),model=r['base']),[dep(producer,'corpus.json'),dep(comparison,'replay-boost-condition.json')],True,dict(arm='boost'))
    boost['conditions']=[dict(job=comparison['id'],output='replay-boost-condition.json',outcome='supported')]
    score=make(r['id']+'-boost-score','focus_replay568','score',dict(model=dict(job=boost['id'],output='model.json'),suite=r['suite'],base=r['base']),[dep(boost,'model.json')])
    make(r['id']+'-boost-compare','focus_replay568','compare',dict(reference=r['reference'],control=dict(job=scores['control']['id'],output='benchmark_summary.json'),native=dict(job=score['id'],output='benchmark_summary.json')),[dep(scores['control'],'benchmark_summary.json'),dep(score,'benchmark_summary.json')])
    destination.mkdir(exist_ok=False);entries=[]
    for spec in jobs:
        q.validate(spec);target=destination/(spec['id']+'.json');q.save(target,spec)
        entries.append(dict(job=spec['id'],spec=pin(target),specSHA256=q.text_digest(spec)))
    result=dict(version='model-decision-compiled-v1',plan=pin(path),existing=[],jobs=entries,executionStarted=False)
    q.save(destination/'compiled.json',result);return result
