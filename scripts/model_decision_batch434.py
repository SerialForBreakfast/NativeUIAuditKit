"""Compile a train/score/compare/follow-up graph using resident template jobs."""
import argparse
from pathlib import Path
import research_queue as q
import research_approval as approval
import experiment_batch402 as batches
import hcf_templates395 as templates
from experiment_templates import checked, pin


def retain(path, value):
    if path.exists():q.require(q.load(path)==value,'decision_immutable_conflict:'+path.name)
    else:q.save(path,value)


def compile_plan(plan_path, destination, queue=q.QUEUE):
    plan=q.load(plan_path)
    q.require(set(plan)=={'version','id','question','controlledComparison','executionBatch','training','pairs'},'decision_plan_fields')
    q.require(plan['version']=='model-decision-batch-v1' and q.ID.fullmatch(plan['id']),'decision_plan_version')
    q.require(all(isinstance(plan[k],str) and len(plan[k].strip())>=12 for k in ('question','controlledComparison')),'decision_plan_text')
    pairs=plan['pairs']
    q.require(isinstance(pairs,list) and 1<=len(pairs)<=32,'decision_pair_limit')
    q.require(all(set(p)=={'id','baseline','candidate'} and q.ID.fullmatch(p['id']) for p in pairs),'decision_pair_fields')
    q.require(len({p['id'] for p in pairs})==len(pairs),'decision_duplicate_pair')
    q.require(len({p['candidate'] for p in pairs})==len(pairs),'decision_duplicate_candidate')
    execution={}
    if plan['executionBatch'] is not None:
        batch=q.load(checked(plan['executionBatch']))
        execution={d['id']:templates.build(d) for d in batches.compile_batch(batch,queue)}
        q.require(all(s['template']['id'] in ('T05','T06','T37','T63') for s in execution.values()),'decision_execution_template')
        preparations={ident for ident,spec in execution.items() if spec['template']['id']=='T05'}
        q.require(set(execution)<={plan['training']}|{p['candidate'] for p in pairs}|preparations,'decision_unrelated_execution')
    def lookup(ident):
        q.require(isinstance(ident,str) and q.ID.fullmatch(ident),'decision_job_identity')
        spec=execution.get(ident) or q.load(queue/'jobs'/ident/'spec.json')
        return spec
    training=lookup(plan['training'])
    q.require(training['template']['id']=='T06' and training['authority']=='training' and
              training['training']['epochs']==30,'decision_training_contract')
    preparations={ident for ident,spec in execution.items() if spec['template']['id']=='T05'}
    if preparations:
        q.require(len(preparations)==1,'decision_preparation_count')
        ident=next(iter(preparations))
        q.require(any(d['job']==ident and d['specSHA256']==q.text_digest(execution[ident]) and
                      d['outputs']==['crops.json'] for d in training['dependencies']), 'decision_preparation_dependency')
        membership=q.load(checked(training['template']['inputs']['membership']))
        q.require(membership.get('version')=='crop-membership-plan-v1','decision_frozen_membership_required')
        rows=membership.get('rows',[])
        fields={'id','role','profile','group','label'}
        q.require(bool(rows) and all(set(r)==fields and r['role'] in ('train','development') and
            r['profile'] in ('standard','hcf') and type(r['label']) is int and r['label'] in (0,1) and
            all(isinstance(r[k],str) and r[k] for k in ('id','group')) for r in rows),'decision_membership_rows')
        q.require(len({r['id'] for r in rows})==len(rows),'decision_membership_duplicate')
        groups={}
        for row in rows:
            q.require(groups.setdefault(row['group'],row['role'])==row['role'],'decision_membership_leak')
        q.require({r['role'] for r in rows}=={'train','development'},'decision_membership_roles')
    sources={training['id']:training}
    resolved_cache={}
    def canonical(ref,spec):
        if 'path' in ref:
            checked(ref)
            return ref
        q.require(set(ref)=={'job','output'},'decision_input_reference')
        dependencies=[d for d in spec.get('dependencies',[]) if d['job']==ref['job']]
        q.require(len(dependencies)==1 and ref['output'] in dependencies[0]['outputs'],'decision_input_dependency')
        key=q.text_digest(dependencies[0])
        if key not in resolved_cache:
            resolved_cache[key]=q.dependency_inputs(dict(dependencies=dependencies),queue)[0]
        dep=resolved_cache[key]
        index=dependencies[0]['outputs'].index(ref['output'])
        return dep['outputs'][index]
    prepared=[]
    for pair in pairs:
        left,right=(lookup(pair[k]) for k in ('baseline','candidate'))
        q.require(left['template']['id']==right['template']['id'] in ('T37','T63'),'decision_score_template')
        q.require(left['template']['parameters']==right['template']['parameters'],'decision_score_parameters')
        a,b=left['template']['inputs'],right['template']['inputs']
        q.require(set(a)==set(b) and all(a[k]==b[k] or canonical(a[k],left)==canonical(b[k],right)
                  for k in a if k!='model'),'decision_unmatched_inputs')
        q.require(b['model']==dict(job=training['id'],output='final.pt'),'decision_score_model')
        q.require(any(d['job']==training['id'] and d['specSHA256']==q.text_digest(training) and
                      'final.pt' in d['outputs'] for d in right['dependencies']),'decision_training_dependency')
        sources.update({left['id']:left,right['id']:right})
        prepared.append((pair,left,right))
    # Readiness validation precedes writes. Pending dependencies remain legitimate.
    destination.mkdir(parents=True,exist_ok=True)
    generated={}
    def dep(spec,outputs):return dict(job=spec['id'],specSHA256=q.text_digest(spec),outputs=outputs)
    def make(ident,kind,config,dependencies):
        path=destination/(ident+'-config.json');retain(path,dict(kind=kind,**config))
        spec=dict(version='research-spec-v2',id=ident,task=plan['id'],owner='Maximum-mini-NUIAK',kind='screen',
            jobKind='artifact',authority='diagnostic',question=plan['question'],hypothesis=plan['question'],
            controlledComparison=plan['controlledComparison'],
            decisionRule='Protect every retained success. Require Standard proposal-selection gains. Missing evidence cannot support acceptance.',
            nextActionByOutcome=dict(supported='Prepare independent qualification without automatic model promotion.',
                contradicted='Report lost successes and keep the retained model.',inconclusive='Report coverage gaps before another correction.'),
            decisionConfig=pin(path),inputs=[pin(path),pin(q.MODULES/'model_decision434.py')],dependencies=dependencies,
            evidence=dict(reads=[q.relative(path)],artifactReceipt='artifact-receipt.json'),
            adapter=dict(type='python-callable',steps=['model_decision434.'+('comparison' if kind=='pair' else kind)],
                         outputAttributes=['model_decision434.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        q.validate(spec);generated[ident]=spec;return spec
    leaf=[]
    for start in range(0,len(prepared),4):
        configs=[];dependencies={}
        for pair,left,right in prepared[start:start+4]:
            output='selection.json' if left['template']['id']=='T37' else 'benchmark_summary.json'
            configs.append(dict(pair=pair['id'],baseline=left['id'],candidate=right['id'],output=output,template=left['template']['id']))
            for source in (left,right):dependencies[source['id']]=dep(source,[output])
        leaf.append(make(f"{plan['id']}-compare-{start//4+1:02}",'pair',dict(pairs=configs),list(dependencies.values())))
    merges=[]
    for start in range(0,len(leaf),8):
        merges.append(make(f"{plan['id']}-merge-{start//8+1:02}",'merge',{},[dep(s,['comparison.json']) for s in leaf[start:start+8]]))
    final=make(plan['id']+'-decision','decision',dict(question=plan['question'],training=training['id'],pairs=[p['id'] for p in pairs]),
        [dep(s,['comparison.json']) for s in merges]+[dep(training,['fit.json','final.pt'])])
    make(plan['id']+'-followup','followup',{},[dep(final,['decision.json'])])
    all_specs={**execution,**generated}
    for ident,spec in all_specs.items():
        current=queue/'jobs'/ident/'spec.json'
        if current.exists():q.require(q.load(current)==spec,'decision_existing_conflict:'+ident)
    for ident,spec in all_specs.items():retain(destination/(ident+'-spec.json'),spec)
    manifest=dict(version='model-decision-compiled-v1',plan=pin(plan_path),
        existing=[dict(job=s['id'],specSHA256=q.text_digest(s)) for s in sources.values() if s['id'] not in execution],
        jobs=[dict(job=s['id'],specSHA256=q.text_digest(s),spec=pin(destination/(s['id']+'-spec.json'))) for s in all_specs.values()],
        executionStarted=False,modelAccepted=False)
    retain(destination/'compiled.json',manifest)
    return manifest


def register(manifest, queue=q.QUEUE, approve=False):
    specs=[q.load(checked(row['spec'])) for row in manifest['jobs']]
    # Check every existing dependency again. Do not replace or reapprove reused jobs.
    for ref in manifest['existing']:
        q.require(q.text_digest(q.load(queue/'jobs'/ref['job']/'spec.json'))==ref['specSHA256'],'decision_existing_changed')
    records=approval.load(queue)
    ids={s['id'] for s in specs}
    q.require(not any(e.get('action')=='revoke' and e.get('job') in ids for e in records['events']),'decision_revoked')
    for row,spec in zip(manifest['jobs'],specs):
        q.require(q.text_digest(spec)==row['specSHA256'],'decision_spec_changed')
        q.submit(checked(row['spec']),queue)
    if approve:
        for spec in specs:
            approval.approve(queue,spec['id'],'agent:Maximum-mini-NUIAK',
                'Maintainer-approved matched Standard decision batch. Preserve previous successes and shipped models.')
    return dict(jobs=len(specs),approved=approve,executionStarted=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan',type=Path);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--register',action='store_true');parser.add_argument('--approve-new',action='store_true')
    args=parser.parse_args()
    q.require(not args.approve_new or args.register,'decision_register_required')
    # Restrict authored paths to this repository, including USB metadata paths.
    plan=q.local_path(q.ROOT,q.relative(args.plan.resolve()))
    output=q.local_path(q.ROOT,q.relative(args.output.resolve()))
    manifest=compile_plan(plan,output)
    print(register(manifest,approve=args.approve_new) if args.register else dict(jobs=len(manifest['jobs']),executionStarted=False))
