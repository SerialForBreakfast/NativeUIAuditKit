"""Prepare fixed campaign jobs through existing admission tools. Never execute jobs."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time

import research_queue as q
import research_approval as approval
from template_inputs398 import checked, pin
from langgraph_campaign585 import read_event as verify_source
from campaign_state586 import VERSION, transition, read_event


def field(doc, path):
    q.require(isinstance(path,list) and 1<=len(path)<=8 and all(isinstance(k,str) and k for k in path),'preparation_field')
    for key in path:
        q.require(isinstance(doc,dict) and key in doc,'preparation_field_missing:'+key)
        doc=doc[key]
    return doc


def same_value(actual, expected):
    """Do not treat numeric zero or one as observed Boolean evidence."""
    return type(actual) is type(expected) and actual == expected


def compile_recipe(ref, destination, queue):
    """Compile existing template descriptions. Preserve every retained specification."""
    import copy
    from experiment_batch402 import compile_batch
    import hcf_templates395 as templates
    from model_decision_batch434 import retain
    recipe=q.load(checked(ref))
    q.require(set(recipe)=={'version','batch','artifacts','conditions','budget'} and recipe['version']=='campaign-preparation-recipe586-v1','preparation_recipe')
    q.require(isinstance(recipe['artifacts'],list) and len(recipe['artifacts'])<=10 and isinstance(recipe['conditions'],list),'preparation_recipe_jobs')
    destination=q.local_path(q.ROOT,q.relative(destination))
    saved=destination/'compiled.json'
    if saved.exists():
        # Reuse the immutable, conditioned output. Recompilation would compare an unconditioned draft with a submitted job.
        if recipe['batch'] is not None:checked(recipe['batch'])
        for ref_item in recipe['artifacts']:checked(ref_item)
        stored=q.load(saved)
        q.require(stored['plan']==ref,'preparation_recipe_changed')
        for row in stored['jobs']:
            spec=q.load(checked(row['spec']))
            q.require(spec['id']==row['job'] and q.text_digest(spec)==row['specSHA256'],'preparation_spec_drift')
            q.validate(spec);q.verify_pins(spec)
        return stored
    specs=[]
    if recipe['batch'] is not None:
        specs=[templates.build(d) for d in compile_batch(q.load(checked(recipe['batch'])),queue)]
        for spec in specs:
            q.require(not spec.get('conditions'),'preparation_nested_condition')
            for condition in recipe['conditions']:
                q.require(set(condition)=={'job','specSHA256','output','outcome'},'preparation_recipe_condition')
                dep=next((d for d in spec['dependencies'] if d['job']==condition['job']),None)
                q.require(dep is not None and dep['specSHA256']==condition['specSHA256'] and condition['output'] in dep['outputs'],'preparation_condition_dependency')
            if recipe['conditions']:
                spec['conditions']=[{k:r[k] for k in ('job','output','outcome')} for r in recipe['conditions']]
    known={}
    for spec in specs:
        for dep in spec.get('dependencies',[]):
            if dep['job'] in known:dep['specSHA256']=q.text_digest(known[dep['job']])
        known[spec['id']]=spec
    for item in recipe['artifacts']:
        spec=copy.deepcopy(q.load(checked(item)))
        for dep in spec.get('dependencies',[]):
            if dep['job'] in known:dep['specSHA256']=q.text_digest(known[dep['job']])
        q.require(spec['id'] not in known,'preparation_recipe_collision')
        known[spec['id']]=spec;specs.append(spec)
    budget=recipe['budget']
    q.require(set(budget)=={'maxJobs','maxSeconds','maxOutputBytes'} and all(type(v) is int and v>0 for v in budget.values()),'preparation_recipe_budget')
    q.require(0<len(specs)<=min(10,budget['maxJobs']) and sum(s['limits']['timeoutSeconds'] for s in specs)<=budget['maxSeconds'] and
              sum(s['limits']['maxOutputBytes'] for s in specs)<=budget['maxOutputBytes'],'preparation_recipe_budget_exceeded')
    destination=q.local_path(q.ROOT,q.relative(destination))
    destination.mkdir(parents=True,exist_ok=True);entries=[];existing={}
    for spec in specs:
        q.validate(spec);q.verify_pins(spec)
        path=destination/(spec['id']+'.json');retain(path,spec)
        entries.append(dict(job=spec['id'],spec=pin(path),specSHA256=q.text_digest(spec)))
        for dep in spec.get('dependencies',[]):
            if dep['job'] not in known:existing[dep['job']]=dict(job=dep['job'],specSHA256=dep['specSHA256'])
    manifest=dict(version='model-decision-compiled-v1',plan=ref,jobs=entries,existing=list(existing.values()),executionStarted=False,modelAccepted=False)
    retain(destination/'compiled.json',manifest)
    return manifest


def request(ref, queue=q.QUEUE, destination=None):
    c=q.load(checked(ref))
    base={'version','id','track','scope','source','selection','requirements'}
    q.require((set(c)==base|{'manifest'} and c['version']=='campaign-preparation586-v1') or
              (set(c)==base|{'recipe'} and c['version']=='campaign-preparation586-v2'), 'preparation_request_fields')
    q.require(q.ID.fullmatch(c['id']) and c['track'] in ('iOS detection','tvOS focus') and isinstance(c['scope'],str) and c['scope'], 'preparation_request_identity')
    source=verify_source(c['source'])
    q.require(source['track']==c['track'],'preparation_source_track')
    selector=c['selection'];q.require(set(selector)=={'evidence','field','equals'},'preparation_selection')
    source_refs=[r for j in source['jobs'] for r in j['outputs']]
    q.require(selector['evidence'] in source_refs,'preparation_selection_source')
    selected=same_value(field(q.load(checked(selector['evidence'])),selector['field']),selector['equals'])
    q.require(isinstance(c['requirements'],list) and len(c['requirements'])<=16,'preparation_requirements')
    requirements=[]
    for r in c['requirements']:
        q.require(set(r)=={'id','owner','requirement','resumeWhen','appliesTo','evidence','field','equals'},'preparation_requirement_fields')
        satisfied=same_value(field(q.load(checked(r['evidence'])),r['field']),r['equals'])
        requirements.append({**{k:r[k] for k in ('id','owner','requirement','resumeWhen','appliesTo')},'satisfied':satisfied})
    if 'recipe' in c:
        q.require(destination is not None,'preparation_destination_required')
        manifest=compile_recipe(c['recipe'],destination,queue)
    else:manifest=q.load(checked(c['manifest']))
    q.require(manifest.get('version')=='model-decision-compiled-v1' and 0<len(manifest['jobs'])<=10,'preparation_manifest')
    checked(manifest['plan']);ids=[]
    for row in manifest['jobs']:
        spec=q.load(checked(row['spec']));q.validate(spec);q.verify_pins(spec)
        q.require(spec['id']==row['job'] and q.text_digest(spec)==row['specSHA256'],'preparation_spec_drift')
        q.require(spec['authority']=='diagnostic' and spec['jobKind']=='artifact' and
                  spec['limits']['timeoutSeconds']<=800 and spec['limits']['maxOutputBytes']<=100_000_000 and
                  spec['limits']['maxAttempts']==1,'preparation_diagnostic_scope')
        ids.append(spec['id'])
    q.require(len(ids)==len(set(ids)),'preparation_duplicate_jobs')
    return c,manifest,selected,requirements


def snapshot(manifest,queue):
    rows=[];store=approval.load(queue)
    revoked={e.get('job') for e in store['events'] if e.get('action')=='revoke'}
    for entry in manifest['jobs']:
        ident=entry['job'];p=queue/'jobs'/ident/'spec.json'
        q.require(ident not in revoked,'preparation_revoked:'+ident)
        if not p.exists():rows.append(dict(job=ident,state='unregistered',approved=False));continue
        spec=q.load(p)
        q.require(q.text_digest(spec)==entry['specSHA256'],'preparation_registration_conflict:'+ident)
        state,attempts=q.state(p.parent)
        if state=='complete':
            complete=[a for a in attempts if (a/'result.json').is_file() and q.load(a/'result.json').get('status')=='complete']
            q.require(len(complete)==1 and q.outputs_intact(complete[0],q.load(complete[0]/'result.json')),'preparation_output_drift')
        rows.append(dict(job=ident,state=state,approved=approval.is_approved(queue,spec,store)))
    return rows


def advance(config, folder, queue=q.QUEUE, admit=False):
    start=time.monotonic();c=q.load(checked(config))
    q.require(q.ID.fullmatch(c['id']),'preparation_request_identity')
    folder=q.local_path(q.ROOT,q.relative(folder));folder.mkdir(parents=True,exist_ok=True)
    # Separate per-campaign locks allow one blocked campaign to leave another campaign usable.
    state_dir=q.local_path(q.ROOT,q.relative(folder/c['id']));state_dir.mkdir(exist_ok=True)
    with q.host_lock(state_dir/'preparation.lock',wait=30):
        c,manifest,selected,requirements=request(config,queue,state_dir/'prepared')
        journal_path=state_dir/'journal.json'
        journal=q.load(journal_path) if journal_path.exists() else dict(campaign=config,events=[],invocations=[])
        q.require(journal['campaign']==config,'preparation_config_changed')
        q.require(len(journal['invocations'])<256 and len(journal['events'])<=128,'preparation_history_budget')
        rows=snapshot(manifest,queue)
        control_start=time.monotonic()
        report=transition(dict(selection=selected,requirements=requirements,jobs=rows))
        control_seconds=time.monotonic()-control_start
        # Finish an existing, immutable event after an uncertain controller return.
        latest=q.load(checked(journal['events'][-1])) if journal['events'] else None
        same=bool(latest and all(latest[k]==v for k,v in dict(selection=selected,requirements=requirements,jobs=rows).items()))
        event_ref=journal['events'][-1] if same else None
        if not same:
            event=dict(version=VERSION,campaign=config,sequence=len(journal['events'])+1,
                previous=q.text_digest(latest) if latest else None,observedAt=time.time(),selection=selected,requirements=requirements,jobs=rows)
            event_path=state_dir/('event-%03d.json'%event['sequence']);q.save(event_path,event)
            event_ref=pin(event_path);journal['events'].append(event_ref)
            q.save(journal_path,journal,replace=True)
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',LANGSMITH_TRACING='false',LANGCHAIN_TRACING_V2='false',TMPDIR=str(q.ROOT/'.build/langgraph585/tmp'))
        for key in ('LANGSMITH_API_KEY','LANGCHAIN_API_KEY'):env.pop(key,None)
        output=state_dir/('controller-%03d.json'%len(journal['events']))
        # A controller output is a verified observation. Repeat event processing after a lost response is safe.
        command=[str(q.ROOT/'.venv-langgraph585/bin/python'),'-B',str(q.MODULES/'campaign_state586.py'),
            '--event',str(checked(event_ref)),'--database',str(folder/'state.sqlite'),'--output',str(output)]
        if output.exists():
            # Keep observations immutable. A duplicate goes to a distinct invocation receipt.
            call=1
            while (state_dir/('controller-%03d-call-%03d.json'%(len(journal['events']),call))).exists():
                call+=1
                q.require(call<=256,'preparation_receipt_budget')
            output=state_dir/('controller-%03d-call-%03d.json'%(len(journal['events']),call))
            command[-1]=str(output)
        process=subprocess.run(command,env=env,capture_output=True,text=True,timeout=120)
        q.require(process.returncode==0,'preparation_controller_failed:'+process.stderr[-1000:])
        actual=q.load(output);q.require(actual['report']==report,'preparation_report_disagreement')
        admitted=[]
        if admit and report['state']=='ready_for_admission':
            from workflow_campaign439 import admit as admit_existing
            needed=[r['job'] for r in rows if r['state'] in ('unregistered','pending','blocked') and not r['approved']]
            q.require(needed,'preparation_admission_empty')
            # Existing APIs validate the full graph and preserve unchanged submitted specifications.
            admit_existing(manifest,queue,approved=needed)
            admitted=needed
        invocation=dict(observedAt=time.time(),wallSeconds=time.monotonic()-start,event=event_ref,
            state=report['state'],admitted=admitted,queueAfter=snapshot(manifest,queue),controller=pin(output),
            executionStarted=False,resultsProvisional=True,modelAccepted=False,
            controlTransitionSeconds=control_seconds,controllerSeconds=actual.get('wallSeconds'),reportsAgree=True,
            manualPreparationMinutes=None,operatorMinutesSaved=None,
            limitation='Actual command and preparation timings only. No historical manual-work baseline.')
        journal['invocations'].append(invocation);q.save(journal_path,journal,replace=True)
        return invocation


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('campaign',type=Path);p.add_argument('--state',type=Path,required=True);p.add_argument('--admit',action='store_true')
    a=p.parse_args();result=advance(pin(a.campaign),a.state,admit=a.admit)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
