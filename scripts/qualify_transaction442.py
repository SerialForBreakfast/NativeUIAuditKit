"""Measure admission on a disposable snapshot. Never mutate the source queue."""
import argparse
import json
import shutil
import statistics
import time
from pathlib import Path

import research_queue as q
import research_approval as approval
import workflow_transaction441 as transaction
from test_workflow_transaction441 import TransactionTests


def measure(source, output, repetitions=3):
    q.require(1 <= repetitions <= 3, 'qualification_repetitions')
    q.require(output.resolve().is_relative_to(q.ROOT.resolve()), 'qualification_output_outside_project')
    original = approval.path(source).read_bytes()
    q.require(len(original) <= 256_000_000, 'qualification_store_limit')
    q.require(shutil.disk_usage(q.ROOT).free > 4*len(original)+q.STORAGE_MARGIN, 'qualification_storage')
    snapshot = json.loads(original)
    q.require(snapshot['version'] == approval.VERSION, 'approval_version')
    fixture = TransactionTests()
    fixture.setUp()
    samples=[]
    try:
        entries=fixture.entries(10)
        q.require(not set(e['job'] for e in entries) & set(snapshot['jobs']), 'qualification_identity_collision')
        q.require(not any(e.get('job') in {r['job'] for r in entries} for e in snapshot['events']), 'qualification_history_collision')
        for count in (5,10):
            for repeat in range(repetitions):
                # Alternate order to reduce systematic warm-cache ordering effects.
                modes=('individual','transaction') if repeat % 2 == 0 else ('transaction','individual')
                for mode in modes:
                    q.save(approval.path(fixture.queue),snapshot,replace=True)
                    started=time.monotonic()
                    if mode=='individual':
                        for row in entries[:count]:
                            approval.approve(fixture.queue,row['job'],row['approver'],row['reason'],fixture.modules)
                        lock_seconds=None
                    else:
                        result=transaction.qualify(fixture.queue,entries[:count],fixture.modules)
                        lock_seconds=result['lockSeconds']
                    seconds=time.monotonic()-started
                    doc=approval.load(fixture.queue)
                    q.require(doc['events'][:len(snapshot['events'])]==snapshot['events'],'qualification_history_changed')
                    q.require(all(doc['jobs'][k]==v for k,v in snapshot['jobs'].items()),'qualification_existing_changed')
                    q.require(len(doc['events'])==len(snapshot['events'])+count,'qualification_duplicate_events')
                    for row in entries[:count]:
                        spec=q.load(fixture.queue/'jobs'/row['job']/'spec.json')
                        q.require(approval.is_approved(fixture.queue,spec,doc=doc),'qualification_approval_invalid')
                    sample=dict(jobs=count,repeat=repeat,mode=mode,seconds=seconds,lockSeconds=lock_seconds,
                                storeWrites=count if mode=='individual' else 1)
                    samples.append(sample)
                    print(json.dumps(sample),flush=True)
        summary=[]
        for count in (5,10):
            medians={mode:statistics.median(s['seconds'] for s in samples if s['jobs']==count and s['mode']==mode)
                     for mode in ('individual','transaction')}
            summary.append(dict(jobs=count,medianSeconds=medians,speedup=medians['individual']/medians['transaction']))
        import hashlib
        report=dict(version='transaction-qualification-v1',sourceBytes=len(original),
                    sourceSnapshotSHA256=hashlib.sha256(original).hexdigest(),samples=samples,summary=summary,
                    sourceWritten=False,executionStarted=False,
                    limits=['One host; warm-cache samples.', 'Individual lock duration is not instrumented.',
                            'Snapshot contents are preserved. Concurrent live changes are not overwritten.'])
        output.parent.mkdir(parents=True,exist_ok=True)
        q.save(output,report)
        return report
    finally:
        fixture.doCleanups()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=q.QUEUE)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--repetitions',type=int,default=3)
    args=parser.parse_args()
    measure(args.source,args.output,args.repetitions)
