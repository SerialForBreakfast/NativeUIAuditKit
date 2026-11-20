"""Bounded campaign reporting with a persistent LangGraph review state.

The existing queue owns execution. This module has no dispatch or promotion action.
"""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import sqlite3
import time
from typing import TypedDict

import research_queue as q
from template_inputs398 import checked, pin

VERSION = 'campaign-event585-v1'
TRACKS = {'iOS detection', 'tvOS focus'}
DB_LIMIT = 32_000_000


class State(TypedDict, total=False):
    event: dict
    observed: bool
    report: dict
    reviewRequired: bool


def read_event(ref):
    """Verify complete selected terminal receipts. Do not infer other job completion."""
    path = checked(ref)
    q.require(path.stat().st_size <= 1_000_000, 'event_size')
    event = q.load(path)
    fields = {'version', 'campaignID', 'track', 'manifest', 'jobs', 'prerequisites', 'scope'}
    q.require(set(event) == fields and event['version'] == VERSION, 'event_contract')
    q.require(q.ID.fullmatch(event['campaignID']) and event['track'] in TRACKS, 'event_identity')
    manifest = q.load(checked(event['manifest']))
    q.require(manifest['version'] == 'model-decision-compiled-v1', 'event_manifest_version')
    members = {r['job']: r for r in manifest['jobs']}
    q.require(0 < len(event['jobs']) <= 10 and len({r['job'] for r in event['jobs']}) == len(event['jobs']), 'event_jobs')
    q.require(isinstance(event['scope'], str) and event['scope'], 'event_scope')
    q.require(isinstance(event['prerequisites'], list) and len(event['prerequisites']) <= 10
              and all(isinstance(x, str) and x for x in event['prerequisites']), 'event_prerequisites')
    for row in event['jobs']:
        q.require(set(row) == {'job', 'specSHA256', 'result', 'outputs'}, 'event_job_fields')
        q.require(row['job'] in members and members[row['job']]['specSHA256'] == row['specSHA256'], 'event_membership')
        entry = members[row['job']]
        spec = q.load(checked(entry['spec']))
        q.require(q.text_digest(spec) == row['specSHA256'] and spec['id'] == row['job'], 'event_spec_changed')
        result_path = checked(row['result'])
        result = q.load(result_path)
        q.require(result.get('status') == 'complete' and result['job'] == row['job']
                  and result['specSHA256'] == row['specSHA256'], 'event_execution_incomplete')
        q.require(0 < len(row['outputs']) <= 10, 'event_outputs')
        names = set()
        for output in row['outputs']:
            p = checked(output)
            q.require(p.parent == result_path.parent/'out' and p.name not in names, 'event_output_location')
            names.add(p.name)
            q.require(any(x['path'] == p.name and x['sha256'] == output['sha256']
                          and x['bytes'] == p.stat().st_size for x in result['outputs']), 'event_output_receipt')
            q.require(p.suffix == '.json' and p.stat().st_size <= 2_000_000, 'event_output_budget')
            doc = q.load(p)
            q.require(isinstance(doc, dict) and doc.get('modelAccepted') is False, 'event_model_acceptance')
    return event


def observe(event):
    return dict(event=event, observed=True)


def report_for(event):
    blocked = bool(event['prerequisites'])
    return dict(version='campaign-review585-v1', campaignID=event['campaignID'], track=event['track'],
        manifest=event['manifest'], scope=event['scope'], terminalEvidenceComplete=True,
        terminalJobs=[dict(job=r['job'], specSHA256=r['specSHA256'], result=r['result'], outputs=r['outputs'])
                      for r in event['jobs']],
        state='waiting_for_prerequisite' if blocked else 'waiting_for_Joe_evidence_review',
        prerequisites=event['prerequisites'], resultsProvisional=True, modelAccepted=False,
        metricClaimsAccepted=False, reviewRequired=True,
        executionOwner='existing-detached-runner', scientificJobsDispatched=0,
        limitation='Selected terminal evidence only. No new model evaluation, accepted metric, or promotion.')


def baseline(event):
    """The same report logic without LangGraph. Queue automation remains the control."""
    return report_for(observe(event)['event'])


def build_graph(saver, stop_after_observe=False):
    from langgraph.graph import StateGraph, START, END
    from langgraph.types import interrupt

    def observe_node(state):
        return observe(state['event'])

    def report_node(state):
        return dict(report=report_for(state['event']), reviewRequired=True)

    def review_node(state):
        interrupt(dict(campaignID=state['event']['campaignID'], state=state['report']['state'],
                       requiredReviewer='Joe', resultsProvisional=True, modelAccepted=False))
        # The trial has no approval or promotion handler. Real review stays in chat.
        raise ValueError('approval_is_outside_this_trial')

    graph = StateGraph(State)
    graph.add_node('observe', observe_node)
    graph.add_node('report', report_node)
    graph.add_node('review', review_node)
    graph.add_edge(START, 'observe')
    graph.add_edge('observe', 'report')
    graph.add_edge('report', 'review')
    graph.add_edge('review', END)
    return graph.compile(checkpointer=saver, interrupt_after=['observe'] if stop_after_observe else None)


def database_bytes(path):
    files = [Path(str(path)+suffix) for suffix in ('', '-wal', '-shm')]
    q.require(not any(p.is_symlink() for p in files), 'database_sidecar_boundary')
    return sum(p.stat().st_size for p in files if p.exists())


def safe_database(path):
    path = Path(path).absolute()
    q.require(path == path.resolve() and path.is_relative_to(q.ROOT)
              and path.parent.is_dir(), 'database_boundary')
    q.require(database_bytes(path) <= DB_LIMIT, 'database_budget')
    return path


def advance(event_ref, database, *, stop_after_observe=False):
    start = time.perf_counter()
    from langgraph.checkpoint.sqlite import SqliteSaver
    event = read_event(event_ref)  # Recheck sources even when a checkpoint already exists.
    db = safe_database(database)
    thread = event['campaignID'] + ':' + event_ref['sha256']
    config = {'configurable': {'thread_id': thread}}
    with SqliteSaver.from_conn_string(str(db)) as saver:
        graph = build_graph(saver, stop_after_observe)
        prior = graph.get_state(config)
        if prior.values:
            q.require(prior.values['event'] == event, 'checkpoint_event_changed')
        pending_review = any(t.interrupts for t in prior.tasks)
        if not pending_review:
            graph.invoke(None if prior.values else {'event': event}, config, durability='sync')
        current = graph.get_state(config)
        interrupted = any(t.interrupts for t in current.tasks)
        report = current.values.get('report')
        q.require(stop_after_observe or interrupted and report is not None, 'review_state_missing')
        checkpoints = sum(1 for _ in graph.get_state_history(config))
    q.require(database_bytes(db) <= DB_LIMIT, 'database_budget')
    return dict(report=report, threadID=thread, checkpointCount=checkpoints,
                reusedPendingReview=pending_review, interruptedForReview=interrupted,
                nextNodes=list(current.next), databaseBytes=database_bytes(db),
                wallSeconds=time.perf_counter()-start, modelAccepted=False)


def runtime_identity(lock):
    import re
    packages = {}
    for line in Path(lock).read_text().splitlines():
        if not line or line.startswith('#'): continue
        m = re.fullmatch(r'([^= ]+)==([^ ]+) --hash=sha256:[0-9a-f]{64}', line)
        q.require(m is not None, 'dependency_lock_format')
        name, version = m.groups()
        q.require(importlib.metadata.version(name) == version, 'dependency_version_changed:'+name)
        packages[name] = version
    return dict(python=os.sys.version.split()[0], packages=packages, lock=pin(Path(lock)))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--event', type=Path, required=True)
    p.add_argument('--database', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--lock', type=Path, required=True)
    p.add_argument('--crash-after-checkpoint', action='store_true')
    args = p.parse_args()
    q.require(os.environ.get('LANGSMITH_TRACING') == 'false'
              and os.environ.get('LANGCHAIN_TRACING_V2') == 'false', 'remote_tracing_must_be_disabled')
    identity = runtime_identity(args.lock)
    ref = pin(args.event)
    started = time.perf_counter();event = read_event(ref);control = baseline(event)
    control_seconds = time.perf_counter()-started
    candidate = advance(ref, args.database, stop_after_observe=args.crash_after_checkpoint)
    if args.crash_after_checkpoint:
        os._exit(86)  # The database closes after a synchronous checkpoint.
    q.require(control == candidate['report'], 'control_report_disagreement')
    value = dict(version='langgraph-trial585-v1', event=ref, runtime=identity,
        baseline=dict(report=control, wallSeconds=control_seconds, operatorInvocations=1,
                      recoveryInterventions=0, automaticQueueDependenciesAlreadySupported=True),
        langgraph=candidate, equivalentReports=True, resultsProvisional=True,
        modelAccepted=False, metricClaimsAccepted=False,
        manualWork=dict(controlRecoveryInterventions=0, langgraphRecoveryInterventions=0,
            reductionEstablished=False, historicalOperatorMinutes=None,
            limitation='Successful report generation only. No manual action is invented for each existing queue node.'))
    out = Path(args.output).absolute()
    q.require(out == out.resolve() and out.is_relative_to(q.ROOT), 'output_boundary')
    q.save(out, value)
    print(json.dumps(dict(equivalentReports=True, state=candidate['report']['state'], databaseBytes=candidate['databaseBytes'])))


if __name__ == '__main__': main()
