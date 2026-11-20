"""Connect bounded LangGraph report jobs to the existing detached runner."""
import json
import os
from pathlib import Path
import subprocess
import time

import research_queue as q
from template_inputs398 import checked, pin
from langgraph_campaign585 import read_event

OUT = None


def receipt(names):
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=name, sha256=q.digest(OUT/name)) for name in names]))


def run():
    spec = q.load(OUT.parents[2]/'spec.json')
    config = q.load(checked(spec['campaignConfig']))
    q.require(set(config) == {'version','campaignID','track','manifest','jobs','scope'}
              and config['version'] == 'langgraph-campaign585-v1', 'campaign_contract')
    deps = {r['job']:r for r in q.dependency_inputs(spec, OUT.parents[4])}
    q.require(set(deps) == {r['job'] for r in config['jobs']}, 'campaign_dependencies')
    jobs = []
    for row in config['jobs']:
        dep = deps[row['job']]
        parent = OUT.parents[4]/'jobs'/row['job']
        matches = [a/'result.json' for a in q.attempts_of(parent)
                   if (a/'result.json').is_file() and q.load(a/'result.json').get('status') == 'complete'
                   and q.text_digest(q.load(parent/'spec.json')) == dep['specSHA256']]
        q.require(len(matches) == 1, 'campaign_result_ambiguous')
        jobs.append(dict(job=row['job'], specSHA256=dep['specSHA256'], result=pin(matches[0]), outputs=dep['outputs']))
    event = dict(version='campaign-event585-v1', campaignID=config['campaignID'], track=config['track'],
                 manifest=config['manifest'], scope=config['scope'], jobs=jobs, prerequisites=[])
    q.save(OUT/'event.json', event)
    read_event(pin(OUT/'event.json'))  # Parent read tracing covers the actual consumed evidence.
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', LANGSMITH_TRACING='false', LANGCHAIN_TRACING_V2='false',
               TMPDIR=str(q.ROOT/'.build/langgraph585/tmp'))
    for key in ('LANGSMITH_API_KEY','LANGCHAIN_API_KEY'):env.pop(key, None)
    state_folder = OUT.parents[4]/'controller-state585'
    state_folder.mkdir(exist_ok=True)
    state = state_folder/'state.sqlite'
    command = [str(q.ROOT/'.venv-langgraph585/bin/python'), '-B', str(q.ROOT/'scripts/langgraph_campaign585.py'),
        '--event', str(OUT/'event.json'), '--database', str(state), '--output', str(OUT/'benchmark_summary.json'),
        '--lock', str(q.ROOT/'scripts/requirements-langgraph585.lock')]
    started = time.monotonic()
    result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=300)
    (OUT/'controller.stdout').write_text(result.stdout)
    (OUT/'controller.stderr').write_text(result.stderr)
    q.require(result.returncode == 0, 'controller_process_failed')
    report = q.load(OUT/'benchmark_summary.json')
    q.require(report['equivalentReports'] is True and report['modelAccepted'] is False
              and report['langgraph']['interruptedForReview'] is True, 'controller_report_invalid')
    q.save(OUT/'runtime-receipt.json', dict(version='langgraph-runtime585-v1',
        campaign=config['campaignID'], wallSeconds=time.monotonic()-started, database=dict(path=q.relative(state),observedSHA256=q.digest(state),mutable=True),
        databaseBytes=state.stat().st_size, runnerPID=os.getppid(), scientificExecutionChanged=False,
        resultsProvisional=True, modelAccepted=False))
    receipt(['event.json','benchmark_summary.json','runtime-receipt.json','controller.stdout','controller.stderr'])


def compare():
    spec = q.load(OUT.parents[2]/'spec.json')
    deps = q.dependency_inputs(spec, OUT.parents[4])
    reports = [q.load(checked(d['outputs'][0])) for d in deps]
    q.require(len(reports) == 2 and {r['baseline']['report']['track'] for r in reports} == {'iOS detection','tvOS focus'}, 'trial_tracks')
    q.require(all(r['equivalentReports'] and r['langgraph']['interruptedForReview']
                  and r['modelAccepted'] is False for r in reports), 'trial_gate')
    threads = [r['langgraph']['threadID'] for r in reports]
    q.require(len(set(threads)) == 2, 'trial_campaign_isolation')
    software = q.load(checked(spec['softwareMeasurements']))
    q.require(software.get('version') == 'langgraph-software-measurements585-v1', 'software_measurements_version')
    m = software['measurements']
    q.require(m['processRecovery']['injectedTerminationReturnCode'] == 86
              and m['processRecovery']['resumedReturnCode'] == 0
              and m['processRecovery']['reportsAgree'] is True
              and m['blockedCampaign']['distinctThreads'] is True
              and m['actualQueueCaller']['complete'] == 2, 'software_measurements_gate')
    result = dict(version='langgraph-comparison585-v1', campaigns=[r['baseline']['report']['campaignID'] for r in reports],
        equivalentReports=2, independentPendingReviews=2, separateThreads=True,
        controllerSeconds=[dict(campaign=r['baseline']['report']['campaignID'], control=r['baseline']['wallSeconds'],
                               langgraph=r['langgraph']['wallSeconds']) for r in reports],
        routineRecoveryInterventions=dict(control=0, langgraph=0, reductionEstablished=False),
        historicalManualMinutes=None, softwareOnlyRecovery=m, modelAccepted=False, metricClaimsAccepted=False, resultsProvisional=True,
        decision='Retain the bounded prototype. Routine manual-work reduction is not established.',
        limitation='The existing runner already handles dependency release. Two report runs do not establish overnight throughput or model improvement.')
    q.save(OUT/'benchmark_summary.json', result)
    (OUT/'report.md').write_text('# LangGraph trial comparison\n\nBoth campaign reports agree with the control.\nBoth reach separate durable review states.\nRoutine recovery interventions are 0 for both controls.\nNo reduction is established. Model results remain provisional.\n')
    receipt(['benchmark_summary.json','report.md'])
