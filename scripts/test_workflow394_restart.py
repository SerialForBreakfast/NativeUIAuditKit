"""Stop an isolated caller after preparation. Resume without repeating preparation."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

import experiment_templates as t
import research_approval as approval
import research_queue as q
import workflow394 as workflow


def child(folder,dvc=False):
    if dvc:
        workspace=folder/'pipeline'
        workflow.command([str(q.ROOT/'.venv-workflow394/bin/dvc'),'repro','prepare'],workspace,
                         workflow.environment(folder),'prepare-only')
        q.save(folder/'ready.json',dict(prepared=True))
        while True: time.sleep(.1)
    queue=folder/'queue'
    ident='workflow394-restart-prepare'
    result=q.run(queue,max_jobs=1,lock=queue/'test.lock',job_ids=[ident])
    q.require(result==[(ident,'complete')],'prepare_failed')
    q.save(folder/'ready.json',dict(prepared=True))
    # The test owner stops this caller. No queue worker runs during this wait.
    while True: time.sleep(.1)


def run(root):
    folder=root/'process-restart-v2';folder.mkdir(exist_ok=False)
    config=dict(q.load(root/'queue-v2/jobs/workflow394-d0/spec.json')['templateConfig'],id='workflow394-restart')
    queue=folder/'queue'
    for row in t.register(config,queue):
        approval.approve(queue,row['job'],'test','Isolated caller restart after completed preparation.')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(q.MODULES))
    with (folder/'child.log').open('w') as log:
        process=subprocess.Popen([sys.executable,__file__,'--child',str(folder)],cwd=q.ROOT,env=env,stdout=log,stderr=log)
        try:
            deadline=time.monotonic()+30
            while not (folder/'ready.json').exists():
                q.require(process.poll() is None,'caller_exited_before_preparation')
                q.require(time.monotonic()<deadline,'preparation_timeout')
                time.sleep(.05)
        finally:
            process.terminate()
            process.wait(timeout=10)
    prepared=queue/'jobs/workflow394-restart-prepare/attempts/1/out/tensors.npy'
    before=(q.digest(prepared),prepared.stat().st_mtime_ns)
    result=[]
    for step in ('prepare','score','report'):
        result.extend(q.run(queue,max_jobs=1,lock=queue/'test.lock',job_ids=[config['id']+'-'+step]))
    q.require(result==[(config['id']+'-score','complete'),(config['id']+'-report','complete')],'restart_failed')
    q.require(before==(q.digest(prepared),prepared.stat().st_mtime_ns),'preparation_repeated')
    report=q.load(queue/'jobs/workflow394-restart-report/attempts/1/out/report.json')
    reference=q.load(root/'queue-v2/jobs/workflow394-q0-report/attempts/1/out/report.json')
    q.require(report==reference,'restart_report_changed')
    q.save(root/'process-restart.json',dict(version=1,callerStopped=True,preparationReused=True,
        reportMatches=True,modelAccepted=False,limitation='Caller stops at a completed stage boundary, not during training.'))


def run_dvc(root):
    folder=root/'dvc-process-restart';folder.mkdir(exist_ok=False)
    workspace=folder/'pipeline';workspace.mkdir()
    reference=root/'queue-v2/jobs/workflow394-d0/attempts/1/out/pipeline'
    config=q.load(reference/'config.json')
    q.save(workspace/'config.json',config)
    stages=q.load(reference/'dvc.yaml')
    for name,stage in stages['stages'].items():
        stage['cmd']=shlex.join([str(q.ROOT/'.venv-yolo/bin/python'),str(q.MODULES/'experiment_steps393.py'),
                                name,str(workspace/'config.json'),str(workspace)])
    env=workflow.environment(folder)
    dvc=str(q.ROOT/'.venv-workflow394/bin/dvc')
    workflow.command([dvc,'init','--no-scm'],workspace,env,'init')
    workflow.command([dvc,'config','core.analytics','false'],workspace,env,'analytics')
    q.save(workspace/'dvc.yaml',stages)
    with (folder/'child.log').open('w') as log:
        process=subprocess.Popen([sys.executable,__file__,'--child','--dvc',str(folder)],cwd=q.ROOT,env=env,stdout=log,stderr=log)
        try:
            deadline=time.monotonic()+30
            while not (folder/'ready.json').exists():
                q.require(process.poll() is None,'dvc_caller_exited')
                q.require(time.monotonic()<deadline,'dvc_preparation_timeout')
                time.sleep(.05)
        finally:
            process.terminate();process.wait(timeout=10)
    prepared=workspace/'prepare/tensors.npy'
    before=(q.digest(prepared),prepared.stat().st_mtime_ns)
    q.require(not (workspace/'score/predictions.json').exists(),'score_ran_before_restart')
    workflow.command([dvc,'repro'],workspace,env,'resume')
    q.require(before==(q.digest(prepared),prepared.stat().st_mtime_ns),'dvc_preparation_repeated')
    q.require(q.load(workspace/'report/report.json')==q.load(reference/'report/report.json'),'dvc_restart_report_changed')
    q.save(root/'dvc-process-restart.json',dict(callerStopped=True,preparationReused=True,reportMatches=True,modelAccepted=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path)
    parser.add_argument('--child',action='store_true')
    parser.add_argument('--dvc',action='store_true')
    args=parser.parse_args()
    if args.child: child(args.folder.absolute(),args.dvc)
    elif args.dvc: run_dvc(args.folder.absolute())
    else: run(args.folder.absolute())
