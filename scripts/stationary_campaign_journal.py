"""Offline append-only campaign accounting and incremental strict intake; no device API."""
import argparse
import ast
import json
import os
import re
from pathlib import Path
import human_annotation_review as h
import intake_stationary_transition as intake
from focus_corrected_transition_audit import stationary_condition

VERSION='stationary-campaign-journal-v1'


def validator_pins():
    """Follow repository-local imports, including lazily imported validators."""
    pending=['intake_stationary_transition'];seen={}
    while pending:
        name=pending.pop();path=h.ROOT/'scripts'/(name+'.py')
        if name in seen or not path.is_file():continue
        seen[name]=h.ref(path)
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node,ast.Import):pending.extend(v.name.split('.')[0] for v in node.names)
            elif isinstance(node,ast.ImportFrom) and node.module:pending.append(node.module.split('.')[0])
    from importlib.metadata import version
    return dict(code=[seen[k] for k in sorted(seen)],pillow=version('pillow'))


def initialize(plan_path,bindings_path,output):
    plan=h.read(h.local(plan_path));bindings=h.read(h.local(bindings_path))
    h.require(plan.get('version')=='stationary-session-campaign-v1','campaign_version')
    cases=plan['cases'];ids=[c['id'] for c in cases]
    h.require(ids and len(ids)==len(set(ids)) and set(bindings['cases'])==set(ids),'campaign_membership')
    flat=[v for b in plan['batches'] for v in b['caseIDs']]
    h.require(sorted(flat)==sorted(ids),'batch_accounting')
    runtime=bindings['runtime']
    h.require(set(runtime)=={'simulatorID','fixtureRunID','buildSHA256'} and
        all(isinstance(v,str) and v for v in runtime.values()) and runtime['simulatorID']!='booted' and
        re.fullmatch('[a-f0-9]{64}',runtime['buildSHA256']),'runtime_binding')
    for case in cases:
        bound=h.read(h.checked(h.ROOT,bindings['cases'][case['id']]))
        h.require(bound['case_id']==case['id'] and stationary_condition(bound['transition']['condition'])==case['condition'],'case_binding')
        recipe=bound['recipe'];pack=(recipe.get('appearance') or {}).get('referencePack') or {}
        if 'referenceScreen' in case:
            h.require(pack.get('screen')==case['referenceScreen'] and
                all(pack.get(k)==case[k] for k in ('seed','variant','artworkStyle')) and
                recipe.get('theme')==case['theme'],'planned_visual_coverage_mismatch')
        h.require(case['partition']=='development','campaign_role')
    out=h.fresh(output);out.mkdir(parents=True)
    h.write(out/'manifest.json',dict(version=VERSION,**h.FLAGS,plan=h.ref(h.local(plan_path)),
        bindings=h.ref(h.local(bindings_path)),validatorPins=validator_pins(),executionAuthorized=False),sealed=True)
    return snapshot(out)


def snapshot(root):
    root=h.local(root);doc=h.sealed(root/'manifest.json',VERSION)
    h.require(doc['validatorPins']==validator_pins(),'intake_validator_changed')
    plan=h.read(h.checked(h.ROOT,doc['plan']));bindings=h.read(h.checked(h.ROOT,doc['bindings']))
    for ref in bindings['cases'].values():h.checked(h.ROOT,ref)
    states={c['id']:dict(state='planned',attempts=[]) for c in plan['cases']}
    previous=h.ref(root/'manifest.json')['sha256'];events=sorted(root.glob('event-*.json'))
    for i,path in enumerate(events):
        h.require(path.name==f'event-{i:06}.json' and i<10000,'journal_sequence')
        event=h.sealed(path,'stationary-campaign-event-v1')
        h.require(event['previous']==previous and event['revision']==i and event['caseID'] in states,'journal_chain')
        row=states[event['caseID']];state=event['state']
        allowed={'planned':{'running'},'running':{'completed-unvalidated','interrupted'},
            'completed-unvalidated':{'accepted','rejected'},'interrupted':{'planned'},'rejected':{'planned'}}
        h.require(state in allowed.get(row['state'],set()),'journal_transition')
        for ref in event.get('evidence',[]):h.checked(h.ROOT,ref)
        if state=='running':
            h.require(event['destination'] not in [a for r in states.values() for a in r['attempts']], 'attempt_collision')
            row['attempts'].append(event['destination'])
        row.update(state=state,last=event)
        previous=h.ref(path)['sha256']
    return dict(root=root,plan=plan,bindings=bindings,states=states,revision=len(events),head=previous)


def append(view,case,state,**fields):
    current=snapshot(view['root'])
    h.require(current['head']==view['head'],'journal_conflict')
    h.require(view['revision']<10000,'journal_limit')
    h.require(case in view['states'],'unknown_case')
    if state=='running':
        h.require(fields['destination'] not in [a for r in view['states'].values() for a in r['attempts']], 'attempt_collision')
    event=dict(version='stationary-campaign-event-v1',**h.FLAGS,revision=view['revision'],previous=view['head'],
        caseID=case,state=state,**fields)
    event['seal']=h.digest(event)
    path=h.fresh(view['root']/f"event-{view['revision']:06}.json")
    # Exclusive creation arbitrates concurrent writers without replacing their evidence.
    with path.open('x') as stream:
        json.dump(event,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    return snapshot(view['root'])


def record(root,case,action,receipt_path,expected_head,destination=None):
    view=snapshot(root);h.require(view['head']==expected_head,'journal_conflict')
    h.require(case in view['states'],'unknown_case');old=view['states'][case]['state']
    receipt=h.read(h.local(receipt_path));ref=h.ref(h.local(receipt_path))
    h.require(receipt.get('runtime')==view['bindings']['runtime'] and receipt.get('caseID')==case,'runtime_or_case_mismatch')
    h.require(receipt.get('authorityReference') and receipt.get('observedAtUTC'),'missing_operation_context')
    if action=='start':
        h.require(old=='planned' and receipt.get('ready') is True,'start_not_ready')
        dest=h.fresh(destination);dest=str(dest.relative_to(h.ROOT))
        return append(view,case,'running',destination=dest,evidence=[ref])
    if action=='complete':
        h.require(old=='running' and receipt.get('cleanupVerified') is True and receipt.get('responsive') is True,'completion_unverified')
        h.require(receipt.get('destination')==view['states'][case]['attempts'][-1],'completion_destination')
        return append(view,case,'completed-unvalidated',evidence=[ref])
    if action=='interrupt':
        h.require(old=='running' and receipt.get('reason'),'interrupt_reason')
        return append(view,case,'interrupted',evidence=[ref])
    h.require(action=='reconcile' and old in ('interrupted','rejected') and
        receipt.get('cleanupVerified') is True and receipt.get('retryAuthorized') is True,'reconciliation_required')
    return append(view,case,'planned',evidence=[ref])


def ingest(root,case,evidence_path,expected_head):
    view=snapshot(root);h.require(view['head']==expected_head,'journal_conflict')
    h.require(case in view['states'],'unknown_case');row=view['states'][case]
    if row['state']=='accepted':return view  # snapshot revalidates every stored source hash
    h.require(row['state']=='completed-unvalidated','case_not_completed')
    raw_path=h.local(evidence_path);raw=h.read(raw_path);runtime=view['bindings']['runtime']
    output_root=h.local(h.ROOT/row['attempts'][-1])
    h.require(raw_path.is_relative_to(output_root),'evidence_outside_attempt')
    h.require(raw.get('simulator_id')==runtime['simulatorID'] and raw.get('run_id')==runtime['fixtureRunID'],'observed_runtime_mismatch')
    case_path=h.checked(h.ROOT,view['bindings']['cases'][case])
    # The existing consumer requires case and raw evidence under one bounded root.
    common=h.ROOT
    report=h.fresh(view['root']/f"intake-{view['revision']:06}.json")
    try:
        result=intake.run(common,str(case_path.relative_to(common)),str(raw_path.relative_to(common)),report)
    except (ValueError,KeyError,OSError) as error:
        return append(view,case,'rejected',reason=str(error),evidence=[h.ref(case_path),h.ref(raw_path)])
    h.require(result['caseID']==case,'intake_case_mismatch')
    return append(view,case,'accepted',evidence=[h.ref(report),*result['inputs']])


def summary(view):
    states={k:v['state'] for k,v in view['states'].items()}
    return dict(head=view['head'],revision=view['revision'],states=states,
        missing=[k for k,v in states.items() if v=='planned'],
        needsReconciliation=[k for k,v in states.items() if v in ('running','interrupted','rejected')],
        allInspectionAccepted=all(v=='accepted' for v in states.values()),
        trainingEligible=False,executionAuthorized=False)


def freeze(root,output):
    """Full final hash/pixel audit, separate from inexpensive incremental reuse."""
    from focus_transition_learning import decoded_hash
    view=snapshot(root);h.require(summary(view)['allInspectionAccepted'],'campaign_incomplete')
    records=[];pixels={}
    for case in view['plan']['cases']:
        event=view['states'][case['id']]['last'];report=h.read(h.checked(h.ROOT,event['evidence'][0]))
        hashes=[]
        for ref in report['inputs']:
            if ref['path'].endswith('.png'):
                digest=decoded_hash(ref);hashes.append(digest);pixels.setdefault(digest,[]).append(case['id'])
        h.require(len(hashes)==2,'capture_accounting')
        records.append(dict(caseID=case['id'],partition='development',
            group=case.get('journeyGroup','fixture-procedural-renderer-v1'),
            intake=event['evidence'][0],decodedPixelHashes=hashes))
    result=dict(version='stationary-campaign-corpus-v1',**h.FLAGS,journalHead=view['head'],
        plan=view['plan'],records=records,duplicateContentGroups=[sorted(set(v)) for v in pixels.values() if len(v)>1],
        limitation='Inspection corpus only. Duplicate focus/no-op frames are reported, not dropped; no training admission or final evaluation.')
    h.write(h.fresh(output),result,sealed=True);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['init','status','start','complete','interrupt','reconcile','intake','freeze'])
    for key in ('root','plan','bindings','case','receipt','destination','evidence','expected-head','output'):p.add_argument('--'+key)
    a=p.parse_args()
    if a.action=='freeze':
        result=freeze(a.root,a.output);print(json.dumps(dict(records=len(result['records']),trainingEligible=False)));raise SystemExit(0)
    if a.action=='init':v=initialize(a.plan,a.bindings,a.root)
    elif a.action=='status':v=snapshot(a.root)
    elif a.action=='intake':v=ingest(a.root,a.case,a.evidence,a.expected_head)
    else:v=record(a.root,a.case,a.action,a.receipt,a.expected_head,a.destination)
    print(json.dumps(summary(v),sort_keys=True))
