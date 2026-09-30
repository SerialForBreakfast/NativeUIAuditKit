"""Bounded four-trial diagnostic comparison; reuses the existing MPS supervisor."""
import argparse
import json
import math
import statistics
import time
from pathlib import Path
import mps_training_diagnostic as d

ORDER=[8,16,16,8]


def matching(plans):
    if len(plans)!=2: raise ValueError('requires_two_plans')
    for key in ('members','weights','taxonomy','sources','versions','limits'):
        if plans[0][key]!=plans[1][key]: raise ValueError('unmatched_'+key)
    a,b=[dict(p['settings']) for p in plans]
    if (a.pop('batch'),b.pop('batch'))!=(8,16) or a!=b: raise ValueError('unmatched_settings')


def prepare(spec,dataset,output):
    output=d.local(output)
    if output.exists(): raise ValueError('output_collision')
    output.mkdir(parents=True)
    records=[]
    for batch in (8,16):
        record=d.prepare(spec,dataset,output/f'frozen-b{batch}',batch=batch)
        records.append(record)
    plans=[d.load_plan(d.ROOT/r['path'],r['sha256']) for r in records];matching(plans)
    bundle=dict(schema='mps-batch-comparison-v1',plans=records,order=ORDER,
                max_seconds=1800,source=d.pin(Path(__file__)),quality_eligible=False)
    d.write(output/'comparison-plan.json',bundle)
    return d.pin(output/'comparison-plan.json')


def trial_metrics(folder,batch):
    receipt=json.loads((folder/'receipt.json').read_text())
    if receipt.get('outcome')!='completed' or receipt.get('returncode')!=0:
        raise ValueError('incomplete_trial')
    paths=list((folder/'runs/diagnostic-only').glob('host-timing-*.jsonl'))
    if len(paths)!=1: raise ValueError('missing_or_ambiguous_timing')
    rows=[json.loads(line) for line in paths[0].read_text().splitlines()]
    meta=rows[0]
    if any(meta.get(k)!=v for k,v in dict(kind='metadata',device='mps',workers=0,batch_size=batch,rect=True,amp=False).items()):
        raise ValueError('runtime_mismatch')
    epochs=[r for r in rows if r['kind']=='epoch']
    if [r['epoch'] for r in epochs]!=[0,1] or rows[-1].get('outcome')!='completed':
        raise ValueError('incomplete_epochs')
    for epoch in epochs:
        if epoch['intervals']['batch_interval']['calls']!=512//batch:
            raise ValueError('incomplete_batches')
        if any(v['errors'] for v in epoch['intervals'].values()): raise ValueError('timing_errors')
    stages=epochs[0]['intervals']
    training=stages['batch_interval']['seconds']+stages['inter_batch_gap']['seconds']
    if not math.isfinite(training) or training<=0: raise ValueError('invalid_timing')
    return dict(batch=batch,epoch1_training_seconds=training,epoch1_images_per_second=512/training,
                epoch_seconds=[e['intervals']['epoch_total']['seconds'] for e in epochs],
                epoch1_optimizer_steps=stages['optimizer_step']['calls'],
                trial_seconds=receipt['elapsed_seconds'],
                min_available_gib=min(s['available_bytes'] for s in receipt['resource_samples'])/2**30,
                ohem=[e.get('ohem_replacements') for e in epochs],
                receipt=d.pin(folder/'receipt.json'),timing=d.pin(paths[0]))


def summarize(trials):
    if [t['batch'] for t in trials]!=ORDER: raise ValueError('incomplete_comparison')
    groups={}
    for batch in (8,16):
        values=[t['epoch1_training_seconds'] for t in trials if t['batch']==batch]
        groups[str(batch)]=dict(median_seconds=statistics.median(values),range_seconds=[min(values),max(values)],
                               median_images_per_second=512/statistics.median(values))
    return dict(groups=groups,batch16_speed_ratio=groups['8']['median_seconds']/groups['16']['median_seconds'],
                caveat='Two early-epoch repeats per batch; padding, warmup/optimizer and host conditions differ. Not pure GPU speed or quality equivalence.')


def execute(bundle_path,expected):
    bundle_path=d.local(bundle_path)
    if d.digest(bundle_path)!=expected: raise ValueError('changed_bundle')
    bundle=json.loads(bundle_path.read_text());output=bundle_path.parent
    if (bundle.get('schema')!='mps-batch-comparison-v1' or bundle.get('order')!=ORDER
            or bundle.get('max_seconds')!=1800 or bundle.get('quality_eligible') is not False):
        raise ValueError('invalid_bundle')
    d.verified(bundle['source'])
    records=bundle['plans']
    plans=[d.load_plan(d.ROOT/r['path'],r['sha256']) for r in records];matching(plans)
    folders=[output/f'trial-{i+1:02d}-b{batch}' for i,batch in enumerate(ORDER)]
    if (output/'comparison-result.json').exists() or any(p.exists() for p in folders):
        raise ValueError('execution_collision')
    started=time.monotonic();deadline=started+1800;trials=[];dispositions=[];outcome='completed'
    try:
        for batch,folder in zip(ORDER,folders):
            if time.monotonic()>=deadline:
                outcome='aggregate_deadline_exceeded';break
            record=records[0 if batch==8 else 1]
            print(json.dumps(dict(event='trial_start',batch=batch,output=str(folder))),flush=True)
            result=d.execute(d.ROOT/record['path'],record['sha256'],folder,deadline=deadline)
            dispositions.append(dict(batch=batch,**result))
            print(json.dumps(dict(event='trial_end',**dispositions[-1])),flush=True)
            if result['outcome']!='completed': outcome=result['outcome'];break
            trials.append(trial_metrics(folder,batch))
        summary=summarize(trials) if len(trials)==4 else None
    except Exception as error:
        outcome='failed';summary=None
        dispositions.append(dict(error=type(error).__name__,detail=str(error)))
    result=dict(schema='mps-batch-comparison-result-v1',outcome=outcome,
                elapsed_seconds=time.monotonic()-started,bundle_sha256=expected,
                trials=trials,dispositions=dispositions,summary=summary,quality_eligible=False)
    d.write(output/'comparison-result.json',result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='mode',required=True)
    q=sub.add_parser('prepare')
    for name in ('spec','dataset','output'):q.add_argument('--'+name,required=True)
    q=sub.add_parser('execute');q.add_argument('--bundle',required=True);q.add_argument('--sha256',required=True)
    a=p.parse_args()
    result=prepare(a.spec,a.dataset,a.output) if a.mode=='prepare' else execute(a.bundle,a.sha256)
    print(json.dumps(result),flush=True)
