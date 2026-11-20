"""Persist campaign preparation events. Queue execution and acceptance stay external."""
import argparse
import json
from pathlib import Path
import time
from typing import TypedDict

import research_queue as q
from template_inputs398 import checked, pin
from langgraph_campaign585 import safe_database, database_bytes, runtime_identity

VERSION = 'campaign-preparation-event586-v1'


def read_event(ref):
    p = checked(ref)
    q.require(p.stat().st_size <= 1_000_000, 'preparation_event_size')
    e = q.load(p)
    q.require(set(e) == {'version','campaign','sequence','previous','observedAt','selection','requirements','jobs'}, 'preparation_event_fields')
    q.require(e['version'] == VERSION and type(e['sequence']) is int and 1 <= e['sequence'] <= 128, 'preparation_event_version')
    c = q.load(checked(e['campaign']))
    q.require(c['version'] in ('campaign-preparation586-v1','campaign-preparation586-v2') and q.ID.fullmatch(c['id']), 'preparation_campaign')
    q.require(type(e['observedAt']) in (int,float) and e['observedAt'] > 0 and type(e['selection']) is bool, 'preparation_observation')
    q.require(e['previous'] is None or isinstance(e['previous'], str) and q.HASH.fullmatch(e['previous']), 'preparation_previous')
    q.require(isinstance(e['requirements'],list) and len(e['requirements']) <= 16, 'preparation_requirements')
    for r in e['requirements']:
        q.require(set(r) == {'id','owner','requirement','resumeWhen','appliesTo','satisfied'} and
                  r['appliesTo'] in ('jobs','training') and type(r['satisfied']) is bool and
                  all(isinstance(r[k],str) and r[k] for k in ('id','owner','requirement','resumeWhen')), 'preparation_requirement')
    q.require(isinstance(e['jobs'],list) and 0 < len(e['jobs']) <= 10 and len({r['job'] for r in e['jobs']}) == len(e['jobs']), 'preparation_jobs')
    for r in e['jobs']:
        q.require(set(r) == {'job','state','approved'} and q.ID.fullmatch(r['job']) and
                  r['state'] in ('unregistered','pending','complete','blocked','failed','cancelled','timeout','exhausted','running','interrupted','invalid')
                  and type(r['approved']) is bool, 'preparation_job')
    return e


def transition(event):
    jobs = event['jobs']
    missing = [r for r in event['requirements'] if not r['satisfied']]
    if not event['selection']:
        status = 'branch_not_selected'
    elif any(r['appliesTo'] == 'jobs' for r in missing):
        status = 'waiting_for_prerequisite'
    elif any(r['state'] in ('failed','cancelled','timeout','exhausted','interrupted','invalid') for r in jobs):
        status = 'execution_needs_review'
    elif all(r['state'] == 'complete' for r in jobs):
        status = 'waiting_for_training_evidence' if missing else 'waiting_for_Joe_evidence_review'
    elif any(r['state'] == 'unregistered' or r['state'] in ('pending','blocked') and not r['approved'] for r in jobs):
        status = 'ready_for_admission'
    else:
        status = 'waiting_for_runner'
    return dict(version='campaign-preparation-state586-v1',state=status, jobs=jobs,
        missingRequirements=missing, selection=event['selection'], resultsProvisional=True,
        modelAccepted=False, metricClaimsAccepted=False, scientificAcceptance='not_established',
        executionOwner='existing-detached-runner')


class State(TypedDict, total=False):
    event: dict
    report: dict
    history: list


def build(saver):
    from langgraph.graph import StateGraph, START, END
    def decide(s):
        e=s['event']
        row=dict(sequence=e['sequence'],eventSHA256=q.text_digest(e),observedAt=e['observedAt'])
        return dict(report=transition(e),history=s.get('history',[])+[row])
    graph=StateGraph(State);graph.add_node('decide',decide)
    graph.add_edge(START,'decide');graph.add_edge('decide',END)
    return graph.compile(checkpointer=saver)


def advance(event_ref, database):
    e=read_event(event_ref);c=q.load(checked(e['campaign']))
    from langgraph.checkpoint.sqlite import SqliteSaver
    thread=c['id']+':'+e['campaign']['sha256'];db=safe_database(database)
    with q.host_lock(Path(str(db)+'.advance.lock'),wait=30):
        with SqliteSaver.from_conn_string(str(db)) as saver:
            graph=build(saver);cfg={'configurable':{'thread_id':thread}}
            prior=graph.get_state(cfg);h=prior.values.get('history',[])
            duplicate=bool(h and h[-1]['eventSHA256']==q.text_digest(e))
            if not duplicate:
                q.require(e['sequence']==len(h)+1 and e['previous']==(h[-1]['eventSHA256'] if h else None), 'stale_preparation_event')
                graph.invoke({'event':e},cfg,durability='sync')
            current=graph.get_state(cfg)
            q.require(current.values['report']==transition(e),'preparation_control_disagreement')
            result=dict(report=current.values['report'],threadID=thread,history=current.values['history'],
                        duplicateEvent=duplicate,checkpointCount=sum(1 for _ in graph.get_state_history(cfg)))
    q.require(database_bytes(db)<=32_000_000,'database_budget')
    return dict(result,databaseBytes=database_bytes(db),modelAccepted=False)


def main():
    import os
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--event',required=True,type=Path);p.add_argument('--database',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--crash-after-checkpoint',action='store_true');a=p.parse_args()
    q.require(os.environ.get('LANGSMITH_TRACING')=='false' and os.environ.get('LANGCHAIN_TRACING_V2')=='false','remote_tracing_must_be_disabled')
    runtime_identity(q.MODULES/'requirements-langgraph585.lock')
    start=time.monotonic();r=advance(pin(a.event),a.database)
    if a.crash_after_checkpoint:os._exit(86)
    r['wallSeconds']=time.monotonic()-start
    out=q.local_path(q.ROOT,q.relative(a.output));q.save(out,r)
    print(json.dumps(dict(threadID=r['threadID'],state=r['report']['state'],duplicate=r['duplicateEvent'])))


if __name__=='__main__':main()
