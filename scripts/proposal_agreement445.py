"""Test fixed spatial agreement before supplemental selection. No runtime changes."""
import math
from collections import Counter
import research_queue as q
from experiment_templates import checked
import supplemental_proposals427 as supplemental
from hcf_compare371 import iou
from coverage_reports402 import rectangle

OUT=None
SUCCESS={'correct','correct-abstention'}
WRONG={'wrong','false-selection'}


def agreement(primary, secondary, model):
    """Use predictions only. Empty sets and tied primary maxima abstain."""
    for arm in (primary,secondary):
        scores=arm['models'][model]['scores']
        q.require(len(scores)==len(arm['candidates']) and all(type(s) in (int,float) and math.isfinite(s) and 0<=s<=1 for s in scores),'agreement_scores')
        for c in arm['candidates']:
            b=c['box'];q.require(len(b)==4 and all(type(x) in (int,float) and math.isfinite(x) for x in b) and min(b[2:])>0,'agreement_box')
    a=primary['models'][model]['scores'];b=secondary['models'][model]['scores']
    if sum(v>=.85 for v in a)==1:return False,'retain-single-selection'
    if not a:return False,'primary-empty'
    top=[i for i,s in enumerate(a) if s==max(a)]
    selected=[i for i,s in enumerate(b) if s>=.85]
    if len(top)!=1:return False,'primary-tie'
    if len(selected)!=1:return False,'secondary-abstains'
    overlap=iou(rectangle(primary['candidates'][top[0]]['box']),rectangle(secondary['candidates'][selected[0]]['box']))
    return overlap>=.5, 'location-agrees' if overlap>=.5 else 'location-disagrees'


def evaluate(primary, secondary):
    original=supplemental.evaluate(primary,secondary)  # Verify receipts' compatible settings and replay decisions.
    lookup={r['id']:(r,s) for r,s in zip(primary['rows'],secondary['rows'])}
    rows=[]
    for old in original['rows']:
        a,b=lookup[old['id']];arm=old['arm'];model=old['model']
        allowed,reason=agreement(a['arms'][arm],b['arms'][arm],model)
        if old['profile']!='standard':allowed=False;reason='optional-hcf-unchanged'
        outcome=b['arms'][arm]['models'][model]['outcome'] if allowed else old['reference']
        rows.append(dict(id=old['id'],sha256=a['sha256'],group=old['group'],profile=old['profile'],noFocus=old['noFocus'],
            arm=arm,model=model,reference=old['reference'],unrestricted=old['outcome'],outcome=outcome,
            usedSupplemental=allowed,reason=reason,gain=old['reference'] not in SUCCESS and outcome in SUCCESS,
            loss=old['reference'] in SUCCESS and outcome not in SUCCESS,
            newWrong=old['reference'] not in WRONG and outcome in WRONG,
            lostUnrestrictedGain=old['gain'] and outcome not in SUCCESS,
            preventedNewWrong=old['newWrong'] and outcome not in WRONG))
    return dict(version='proposal-agreement-v1',rows=rows,modelAccepted=False,policy='unique-primary-top-agrees-iou-0.5',
        models={k:primary['inputs'][k] for k in ('baseline','candidate')},threshold=.85,
        limitation='Post-hoc development correction. Agreement is not independent evidence. HCF retains the primary decisions.')


def context():
    spec=q.load(OUT.parents[2]/'spec.json');deps=q.dependency_inputs(spec,OUT.parents[4])
    q.require(deps==q.load(OUT/'dependencies.json'),'agreement_dependencies')
    plan=q.load(checked(spec['agreementPlan']))
    q.require(plan['version']=='proposal-agreement-plan-v1','agreement_plan')
    return spec,deps,plan


def receipt():
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=p.name,sha256=q.digest(p)) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='artifact-receipt.json']))


def gate():
    _,deps,_=context();q.require(len(deps)==1,'agreement_gate_dependencies')
    source=q.load(checked(deps[0]['outputs'][0]))
    q.require(source['version']=='bounded-selection-followup-v1' and source['branch']=='supplemental' and source['modelAccepted'] is False,'agreement_gate_source')
    counts=source['standard']['baseline']
    outcome='supported' if counts['gains']>0 and counts['newWrong']>0 else 'contradicted'
    if counts['noFocus']==0 or counts['groups']<3:outcome='inconclusive'
    q.save(OUT/'gate.json',dict(version='research-condition-v1',outcome=outcome,
        reason='Test spatial agreement only after the retained-model fallback gains selections but adds wrong selections.',evidence=[deps[0]['result']]))
    q.save(OUT/'preservation.json',source['preservation']);receipt()


def run():
    spec,_,_=context()
    ref=next(s['from'] for s in spec['stage'] if s['to']=='bundle.json')
    source=checked(ref);q.require(q.digest(source)==q.digest(OUT/'bundle.json'),'agreement_stage')
    bundle=q.load(source)
    q.require(set(bundle)=={'version','baseline','supplemental'} and bundle['version']=='supplemental-proposals-v1','agreement_bundle')
    result=evaluate(supplemental.load(bundle['baseline']),supplemental.load(bundle['supplemental']))
    q.save(OUT/'benchmark_summary.json',result);receipt()


def summarize(reports, membership, preservation):
    rows=[];seen=set();models=None
    for report in reports:
        q.require(report['version']=='proposal-agreement-v1' and report['modelAccepted'] is False,'agreement_report')
        if models is None:models=report['models']
        q.require(models==report['models'],'agreement_models')
        for r in report['rows']:
            key=(r['id'],r['profile'],r['arm'],r['model']);q.require(key not in seen,'agreement_duplicate');seen.add(key);rows.append(r)
    actual=sorted({(r['id'],r['sha256'],r['group'],r['profile']) for r in rows})
    q.require(actual==[tuple(x) for x in membership],'agreement_membership')
    q.require(len(rows)==len(actual)*4,'agreement_missing_arms')
    slices={}
    for profile in ('standard','hcf'):
        for model in ('baseline','candidate'):
            s=[r for r in rows if r['profile']==profile and r['model']==model and r['arm']=='detector']
            slices[profile+'/'+model]=dict(frames=len(s),groups=len({r['group'] for r in s}),
                noFocus=sum(r['noFocus'] for r in s),outcomes=dict(Counter(r['outcome'] for r in s)),
                **{k:sum(r[k] for r in s) for k in ('gain','loss','newWrong','lostUnrestrictedGain','preventedNewWrong')})
    standard=slices['standard/baseline']
    outcome='contradicted' if standard['loss'] or standard['newWrong'] else ('supported' if standard['gain']>0 and standard['groups']>=3 and standard['noFocus']>0 else 'inconclusive')
    return dict(version='proposal-agreement-decision-v1',outcome=outcome,slices=slices,rows=rows,preservation=preservation,
        modelAccepted=False,terminal=True,nextAction='If supported, require new independent development groups before runtime review. Otherwise reject or diagnose without threshold sweeps.')


def finish():
    _,deps,plan=context()
    result=summarize([q.load(checked(d['outputs'][0])) for d in deps[1:]],plan['membership'],q.load(checked(deps[0]['outputs'][1])))
    q.save(OUT/'decision.json',result)
    (OUT/'report.md').write_text('# Spatial agreement correction\n\nOutcome: '+result['outcome']+'\n\n'+str(result['slices'])+'\n\n'+result['nextAction']+'\n')
    receipt()


def compile_request(source,destination,queue=q.QUEUE):
    """Bind a finite request to existing cached bundles and a completed-or-pending decision."""
    from experiment_templates import pin
    from model_decision_batch434 import retain
    request=q.load(source)
    q.require(set(request)=={'version','id','decision','bundles'} and request['version']=='proposal-agreement-request-v1','agreement_request')
    q.require(q.ID.fullmatch(request['id']) and q.ID.fullmatch(request['decision']),'agreement_ids')
    q.require(1<=len(request['bundles'])<=8,'agreement_bundles')
    parent=q.load(queue/'jobs'/request['decision']/'spec.json')
    q.require(parent['adapter']['steps']==['bounded_selection444.finish'] and parent['selectionBranch']=='supplemental','agreement_parent')
    membership=[]
    for ref in request['bundles']:
        bundle=q.load(checked(ref));report=supplemental.load(bundle['baseline'])
        membership.extend((r['id'],r['sha256'],r['group'],r['profile']) for r in report['rows'])
    q.require(len(membership)==len(set(membership)) and len({x[0] for x in membership})==len(membership),'agreement_duplicate_membership')
    destination.mkdir(parents=True,exist_ok=True)
    plan=destination/'plan.json';retain(plan,dict(version='proposal-agreement-plan-v1',membership=sorted(membership),request=pin(source)))
    def dep(s,outputs):return dict(job=s['id'],specSHA256=q.text_digest(s),outputs=outputs)
    def make(suffix,step,deps):
        return dict(version='research-spec-v2',id=request['id']+'-'+suffix,task=request['id'],owner='Maximum-mini-NUIAK',
            authority='diagnostic',kind='screen',jobKind='artifact',question='Does fixed spatial agreement remove unsafe supplemental selections while retaining useful Standard gains?',
            hypothesis='Agreement between the primary top-score box and supplemental selected box can reject conflicting locations.',
            controlledComparison='Keep frames, models, thresholds, and original scores fixed. Change only the fallback agreement requirement.',
            decisionRule='Require Standard gains without lost retained successes or new wrong selections. Keep HCF unchanged.',
            nextActionByOutcome=dict(supported='Require independent groups before runtime qualification.',contradicted='Reject this policy and preserve failures.',inconclusive='Record missing gains or support. Do not sweep thresholds.'),
            inputs=[pin(plan),pin(q.MODULES/'proposal_agreement445.py')],agreementPlan=pin(plan),dependencies=deps,
            evidence=dict(reads=[q.relative(plan)],artifactReceipt='artifact-receipt.json'),
            adapter=dict(type='python-callable',steps=['proposal_agreement445.'+step],outputAttributes=['proposal_agreement445.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    gate_spec=make('gate','gate',[dep(parent,['decision.json'])]);specs=[gate_spec];comparisons=[]
    def condition(spec,outputs):
        spec['dependencies'].insert(0,dep(gate_spec,outputs))
        spec['conditions']=[dict(job=gate_spec['id'],output='gate.json',outcome='supported')]
    for index,ref in enumerate(request['bundles'],1):
        spec=make(f'compare-{index:02}','run',[]);condition(spec,['gate.json'])
        spec['inputs'].append(ref);spec['stage']=[dict(to='bundle.json',**{'from':ref})]
        spec['evidence']['reads'].append(ref['path']);comparisons.append(spec);specs.append(spec)
    summary=make('decision','finish',[dep(s,['benchmark_summary.json']) for s in comparisons])
    condition(summary,['gate.json','preservation.json']);specs.append(summary)
    jobs=[]
    for spec in specs:
        q.validate(spec);path=destination/(spec['id']+'.json');retain(path,spec)
        jobs.append(dict(job=spec['id'],specSHA256=q.text_digest(spec),spec=pin(path)))
    manifest=dict(version='model-decision-compiled-v1',plan=pin(plan),existing=[dict(job=parent['id'],specSHA256=q.text_digest(parent))],
                  jobs=jobs,executionStarted=False,modelAccepted=False)
    retain(destination/'compiled.json',manifest);return manifest
