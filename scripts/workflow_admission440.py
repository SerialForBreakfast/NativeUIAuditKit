"""Check a compiled campaign before publication. Never approve or dispatch work."""
import argparse
import collections
import json
import shutil
import tempfile
import time
from pathlib import Path

import research_queue as q
import research_approval as approval
from experiment_templates import checked


def inspect(manifest, queue=q.QUEUE, profile_sources=False):
    q.require(queue.is_dir(), 'admission_queue_missing')
    q.require(manifest.get('version')=='model-decision-compiled-v1', 'admission_manifest_version')
    checked(manifest['plan'])
    entries=manifest['jobs']
    q.require(isinstance(entries,list) and 0<len(entries)<=128,'admission_job_limit')
    ids=[r['job'] for r in entries]
    q.require(len(set(ids))==len(ids) and all(q.ID.fullmatch(i) for i in ids),'admission_job_ids')
    start=time.monotonic(); timings=collections.defaultdict(float)
    def measured(name, operation):
        before=time.monotonic()
        try:return operation()
        finally:timings[name]+=time.monotonic()-before
    store=measured('approvalReadSeconds',lambda:approval.load(queue))
    revoked={e.get('job') for e in store['events'] if e.get('action')=='revoke'}
    specs={}; rows=[]; errors=[]
    def problem(row, code, action):
        row['blockers'].append(dict(requirement=str(code)[:500],owner=row['owner'],action=action))
    for ref in manifest['existing']:
        try:
            q.require(q.ID.fullmatch(ref['job']), 'admission_parent_id')
            parent=q.load(queue/'jobs'/ref['job']/'spec.json')
            q.require(q.text_digest(parent)==ref['specSHA256'],'campaign_existing_changed:'+ref['job'])
            specs[ref['job']]=parent
        except (ValueError,OSError,KeyError,TypeError) as error:errors.append(str(error)[:500])
    free=shutil.disk_usage(queue).free
    for entry in entries:
        ident=entry['job'];row=dict(job=ident,owner='Maximum-mini-NUIAK',blockers=[],waits=[],alreadyRegistered=False)
        rows.append(row)
        try:
            spec=measured('specificationReadSeconds',lambda:q.load(checked(entry['spec'])))
            row['owner']=spec.get('owner','Maximum-mini-NUIAK')
            q.require(spec['id']==ident and q.text_digest(spec)==entry['specSHA256'],'campaign_spec_changed')
            measured('validationSeconds',lambda:q.validate(spec))
            measured('inputHashSeconds',lambda:q.verify_pins(spec))
            measured('trainingPrerequisiteSeconds',lambda:q.check_training(spec,queue))
            q.require(ident not in revoked,'campaign_revoked')
            q.require(not spec.get('requirements'),'approval_requirements_unresolved')
            needed=max(spec['limits']['maxOutputBytes'],spec.get('training',{}).get('storageBudgetBytes',0))+q.STORAGE_MARGIN
            q.require(free>=needed,'approval_storage_insufficient')
            current=queue/'jobs'/ident/'spec.json'
            if current.exists():
                q.require(q.load(current)==spec,'campaign_registration_conflict')
                row['alreadyRegistered']=True
            if spec['authority']=='capture':
                problem(row,'capture_ownership_not_checked','Use the qualified capture admission path. This command does not contact a target.')
            if profile_sources:
                pins=measured('sourceClosureSeconds',lambda:approval.code_pins(spec,q.MODULES))
                row['sourceFiles']=len(pins)
            specs[ident]=spec
        except (ValueError,OSError,KeyError,TypeError) as error:
            problem(row,error,'Repair this requirement before publication. Preserve existing attempts and specifications.')
    # Validate the complete dependency closure, including dependencies not listed as reused roots.
    visited=set()
    def visit(ident, trail):
        q.require(ident not in trail,'dependency_cycle:'+ident)
        q.require(len(trail)<64,'dependency_depth')
        if ident in visited:return
        spec=specs[ident]
        for dep in spec.get('dependencies',[]):
            parent=dep['job'];q.require(q.ID.fullmatch(parent),'admission_parent_id')
            if parent not in specs:
                q.require(len(specs)<512,'admission_graph_limit')
                specs[parent]=q.load(queue/'jobs'/parent/'spec.json')
            q.require(q.text_digest(specs[parent])==dep['specSHA256'],'dependency_spec_changed:'+parent)
            visit(parent,trail|{ident})
        visited.add(ident)
    for row in rows:
        if row['blockers'] or row['job'] not in specs:continue
        spec=specs[row['job']]
        try:measured('dependencyGraphSeconds',lambda:visit(row['job'],set()))
        except (ValueError,OSError,KeyError,TypeError) as error:
            problem(row,error,'Repair the dependency identity or producer requirement before publication.')
            continue
        for dep in spec.get('dependencies',[]):
            if dep['job'] in ids and not (queue/'jobs'/dep['job']/'spec.json').exists():
                row['waits'].append('producer_not_published:'+dep['job']);continue
            try:
                # Inspect one dependency and its corresponding conditions without changing it.
                subset=dict(dependencies=[dep],conditions=[c for c in spec.get('conditions',[]) if c['job']==dep['job']])
                measured('dependencyEvidenceSeconds',lambda:q.dependency_inputs(subset,queue))
            except (ValueError,OSError,KeyError,TypeError) as error:
                reason=str(error)[:500]
                attempts=q.attempts_of(queue/'jobs'/dep['job'])
                last=attempts[-1]/'result.json' if attempts else None
                failure=q.load(last).get('status') if last and last.is_file() else None
                if reason.startswith('dependency_incomplete:') and failure in ('failed','cancelled','interrupted','timeout','exhausted'):
                    problem(row,'producer_requires_review:'+dep['job']+':'+failure,
                            'Review the failed producer. Use an explicit successor; do not retry it automatically.')
                elif reason.startswith('condition_not_met:') and reason.split(':')[2]=='inconclusive':
                    problem(row,reason,'Review missing evidence before selecting or approving another branch.')
                elif reason.startswith(('dependency_incomplete:','condition_not_met:')):row['waits'].append(reason)
                else:problem(row,reason,'Verify the producer outputs or publish an explicit corrected successor.')
    for row in rows:
        row['state']='blocked' if row['blockers'] else 'waiting' if row['waits'] else 'preflight-passed'
        if not row['blockers'] and row['waits'] and all(w.startswith('condition_not_met:') for w in row['waits']):
            row['state']='branch-not-selected'
    return dict(version='workflow-admission-review-v1',canRegister=not errors and not any(r['blockers'] for r in rows),
        executionChanged=False,approvalGranted=False,modelAccepted=False,rows=rows,errors=errors,
        counts=dict(collections.Counter(r['state'] for r in rows)),timings=dict(timings,totalSeconds=time.monotonic()-start),
        approvalStoreBytes=approval.path(queue).stat().st_size if approval.path(queue).exists() else 0,
        limitation='Preflight is a snapshot, not authority or a resource reservation. Approval and dispatch recheck current state.')


def summary(report):
    lines=['# Campaign admission review','',f"Can register: {report['canRegister']}.",
           'Registration does not approve or start execution.','']
    for error in report['errors']:lines.append('Campaign requirement: '+error)
    for row in report['rows']:
        lines.extend([f"## {row['job']}",'',f"State: {row['state']}. Owner: {row['owner']}."])
        for item in row['blockers']:lines.append(item['requirement']+'. '+item['action'])
        for wait in row['waits']:lines.append('Wait: '+wait)
        lines.append('')
    return '\n'.join(lines)


def profile_store(queue, destination, repetitions=3):
    """Measure a local disposable copy. Never lock or write the live approval store."""
    q.require(type(repetitions) is int and 1<=repetitions<=3,'profile_repetitions')
    destination=q.local_path(q.ROOT,q.relative(destination.resolve()))
    destination.mkdir(parents=True,exist_ok=True)
    source=approval.path(queue)
    size=source.stat().st_size
    q.require(size<=256*1024*1024,'profile_store_limit')
    q.require(shutil.disk_usage(destination).free>=size*3+q.STORAGE_MARGIN,'profile_storage_insufficient')
    samples=[]
    with tempfile.TemporaryDirectory(dir=destination,prefix='approval-profile-') as directory:
        folder=Path(directory)
        for index in range(repetitions):
            sample={};start=time.monotonic();raw=source.read_bytes();sample['readSeconds']=time.monotonic()-start
            start=time.monotonic();doc=json.loads(raw);sample['parseSeconds']=time.monotonic()-start
            q.require(doc.get('version')==approval.VERSION,'profile_store_version')
            start=time.monotonic();serialized=json.dumps(doc,indent=2,sort_keys=True)
            sample['serializeSeconds']=time.monotonic()-start
            sample.update(sourceBytes=len(raw),serializedBytes=len(serialized.encode()),jobs=len(doc['jobs']),events=len(doc['events']))
            start=time.monotonic()
            with q.host_lock(folder/'profile.lock'):
                sample['uncontendedLockSeconds']=time.monotonic()-start
                start=time.monotonic();q.save(folder/'copy.json',doc,replace=True)
                sample['atomicSaveSeconds']=time.monotonic()-start
            samples.append(sample)
    return dict(version='workflow-admission-profile-v1',samples=samples,executionChanged=False,
        liveLockContention='not measured',temporaryCopyRemoved=True,
        limitation='Warm-cache samples on this host only. Atomic save includes serialization. No live approval is added or changed.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path);parser.add_argument('--profile-sources',action='store_true')
    parser.add_argument('--text',action='store_true')
    parser.add_argument('--profile-store',type=Path,help='Measure a disposable approval copy in this project directory.')
    args=parser.parse_args()
    source=q.local_path(q.ROOT,q.relative(args.manifest.resolve()))
    report=inspect(q.load(source),profile_sources=args.profile_sources)
    if args.profile_store:report['storeProfile']=profile_store(q.QUEUE,args.profile_store)
    print(summary(report) if args.text else json.dumps(report,indent=2))
    return 0 if report['canRegister'] else 2


if __name__=='__main__':raise SystemExit(main())
