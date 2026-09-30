"""Offline Run audit and benchmark specification; no Torch import or execution."""
import argparse
import csv
import hashlib
import io
import json
import statistics
import re
from pathlib import Path
import yaml
from focus_dataset_contract import ROOT, local


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def configuration(args):
    requested={k:args.get(k) for k in ('model','resume','imgsz','batch','workers','amp','rect','mosaic','optimizer',
        'nbs','weight_decay','warmup_epochs','patience','save_period','cache','epochs','device')}
    batch=args.get('batch');nbs=args.get('nbs')
    accumulate=max(round(nbs/batch),1) if type(batch) is int and batch>0 and type(nbs) is int else None
    return dict(requested=requested,initialization='resume' if args.get('resume') else 'fresh_from_saved_model_argument',
        sourceDerived=dict(workers=0 if args.get('device') in ('mps','cpu') else args.get('workers'),
            amp=False if args.get('device') in ('mps','cpu') else None,
            mosaic=0. if args.get('rect') else args.get('mosaic'),
            steadyAccumulation=accumulate,steadyEffectiveBatch=batch*accumulate if accumulate else None,
            warmup='accumulation interpolates from 1 to nbs/batch',
            stoppingFitness='mAP50-95 in inspected installed source',
            checkpoint='last and best; save_period controls extra epoch snapshots; last.prev mirrors current last after save'),
        runtimeConfirmed=dict(batchTensorShapes=None,effectiveAMP=None,workers=None,stageTiming=None),
        caveat='Source-derived values describe inspected installation; not a recovered historical runtime trace.')


def epoch_times(text):
    rows=list(csv.DictReader(io.StringIO(text)))
    if not rows:raise ValueError('empty_results')
    try:
        epochs=[int(r['epoch']) for r in rows]; times=[float(r['time']) for r in rows]
        import math
        if epochs!=list(range(1,len(rows)+1)) or any(not math.isfinite(t) or t<=0 for t in times):
            raise ValueError('invalid_results')
        durations=[times[0]]+[b-a for a,b in zip(times,times[1:])]
        if min(durations)<=0:raise ValueError('invalid_times')
        best=max(rows,key=lambda r:float(r['metrics/mAP50-95(B)']))
    except (KeyError,TypeError) as e:raise ValueError('truncated_results') from e
    return dict(epochs=len(rows),csvElapsedSeconds=times[-1],medianEpochSeconds=statistics.median(durations),
        firstEpochSeconds=durations[0],bestRecordedFitnessEpoch=int(best['epoch']),
        stageCosts=dict(dataLoading=None,forwardBackward=None,validation=None,ohem=None,checkpoint=None),
        interpretation='CSV elapsed includes overhead; cannot attribute it to GPU compute or infer CUDA speedup.')


def log_evidence(path):
    if path is None or not path.is_file(): return dict(status='unavailable',workers=None,lines=[])
    # Bounded text snapshot; do not mistake absence in a truncated tail for absence in the run.
    with path.open('rb') as f:
        first=f.read(65536);f.seek(max(0,path.stat().st_size-65536));last=f.read(65536)
    text=re.sub(r'\x1b\[[0-9;]*m','',(first+b'\n'+last).decode(errors='replace'))
    workers=re.findall(r'Using (\d+) dataloader workers',text)
    lines=[line for line in text.splitlines() if any(s in line for s in ('dataloader workers','epochs completed in','EarlyStopping:'))]
    return dict(status='bounded_snapshot',workers=int(workers[-1]) if workers else None,
        lines=lines,snapshotSHA256=hashlib.sha256(first+b'\n'+last).hexdigest(),bytesOnDisk=path.stat().st_size)


def run(run_dir,dataset,site,output,log=None):
    run_dir,dataset,site,output=map(local,(run_dir,dataset,site,output))
    if output.exists():raise ValueError('output_collision')
    args_path=run_dir/'args.yaml';csv_path=run_dir/'results.csv'
    args=yaml.safe_load(args_path.read_text())
    if not isinstance(args,dict):raise ValueError('invalid_args')
    ds=yaml.safe_load((dataset/'dataset.yaml').read_text())
    if Path(args['data']).resolve()!=(dataset/'dataset.yaml').resolve():raise ValueError('wrong_dataset')
    sources=[ROOT/'scripts/train_ios_model.py',ROOT/'scripts/ohem_callback.py',
        site/'ultralytics/engine/trainer.py',site/'ultralytics/data/dataset.py',site/'ultralytics/utils/checks.py',
        site/'ultralytics/utils/metrics.py',site/'ultralytics/data/base.py']
    pins=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in [args_path,csv_path,dataset/'dataset.yaml',*sources]]
    # Fail closed when inspected dependency semantics no longer support the deductions.
    for path,snippet in ((sources[2],'self.args.workers = 0'),(sources[3],'hyp.mosaic if self.augment and not self.rect else 0.0'),
            (sources[4],'if device.type in {"cpu", "mps"}'),(sources[5],'w = [0.0, 0.0, 0.0, 1.0]')):
        if snippet not in path.read_text():raise ValueError('source_semantics_need_review')
    counts={};support={};members=[]
    for split in ('train','val','test'):
        images=sorted((dataset/split/'images').glob('*'))
        images=[p for p in images if p.suffix.lower() in ('.png','.jpg','.jpeg')]
        counts[split]=len(images);classes=set()
        for image in images:
            label=dataset/split/'labels'/(image.stem+'.txt')
            if not image.is_file() or not label.is_file():raise ValueError('missing_corpus_member')
            for line in label.read_text().splitlines():
                fields=line.split()
                if len(fields)!=5:raise ValueError('invalid_label')
                c=int(fields[0])
                if not 0<=c<ds['nc']:raise ValueError('invalid_class')
                classes.add(c)
        support[split]=sorted(classes)
        if split=='train':
            selected=sorted(images,key=lambda p:hashlib.sha256(p.name.encode()).hexdigest())[:512]
            for p in selected:
                label=dataset/split/'labels'/(p.stem+'.txt')
                members.append(dict(image=dict(path=str(p.relative_to(ROOT)),sha256=sha(p)),
                    label=dict(path=str(label.relative_to(ROOT)),sha256=sha(label)),split='train'))
    if len(members)!=512:raise ValueError('insufficient_training_subset')
    versions={}
    for name in ('torch','ultralytics'):
        paths=sorted(site.glob(name+'-*.dist-info/METADATA'))
        versions[name]=next((line[9:] for line in paths[0].read_text().splitlines() if line.startswith('Version: ')),None) if len(paths)==1 else None
    report=dict(version='training-efficiency-audit-v1',configuration=configuration(args),
        measurements=epoch_times(csv_path.read_text()),sources=pins,installedVersions=versions,
        counts=counts,classSupport=support,modelLoaded=False,
        findings=[dict(id='batch-loss-proxy',severity='interpretation',evidence='ohem_callback.on_train_batch_end',
            detail='detach().cpu() scalar shared across all images in batch; not individual losses. Synchronization cost not timed.'),
            dict(id='rect-replacement',severity='repaired_pending_measurement',evidence='compatible_oversample',
            detail='Current callback restricts replacements to equal original rectangular output shapes and reports unfulfilled requests. Historical run used unrestricted replacement; impact unmeasured.'),
            dict(id='cache-reset',severity='cost_unknown',evidence='sync_dataset_lists',detail='All decoded image cache entries invalidated each epoch.'),
            dict(id='checkpoint-mirror',severity='recovery',evidence='_backup_last_pt',detail='last.prev is a post-save mirror, not the previous epoch or an atomic backup guarantee.'),
            dict(id='local-backend',severity='scope',evidence='train_ios_model.main',detail='MPS only; user excludes unavailable CUDA hardware. No backend migration proposed.')])
    report['logEvidence']=log_evidence(local(log) if log else None)
    report['configuration']['runtimeConfirmed']['workers']=report['logEvidence']['workers']
    spec=dict(version='training-benchmark-plan-v1',executionAuthorized=False,membership=members,
        savedRequestedConfiguration=args,sourceDerivedConfiguration=report['configuration']['sourceDerived'],
        arms=[dict(device='mps',batch=b,workers=0,amp=False,rect=True,seed=42,
            steadyAccumulation=max(round(64/b),1),steadyEffectiveBatch=64) for b in (8,16)],
        sameInitialization=dict(path=args['model'],sha256=sha(Path(args['model'])) if Path(args['model']).is_file() else None),
        repetitions=2,warmupBatches=10,timedExamplesPerRepetition=512,maxWallSeconds=1800,
        stages=['cold_load','data_wait','forward_backward_optimizer','validation','ohem','checkpoint','unattributed'],
        synchronization='Synchronize backend at timing boundaries, not every step; retain raw repetition timings.',
        memory='Reserve OS/other-task headroom; stop before budget exhaustion, nonfinite loss, or unstable backend. No forced OOM.',
        correctnessGate='Use repaired shape-compatible OHEM and record fulfilled replacements; no silent no-OHEM substitution.',
        sourcePins=pins,launchCommand=None,
        blockers=['separate local compute authorization','bounded benchmark harness with explicit synchronization; --timing provides host-wall diagnostics only'],
        adoption='MPS only. No speedup claim before repeated local measurements. Batch changes affect warmup and OHEM batch-loss proxies, so quality equivalence is not assumed.')
    for pin in pins:
        if sha(ROOT/pin['path'])!=pin['sha256']:raise ValueError('source_changed_during_audit')
    output.mkdir(parents=True)
    for name,doc in [('audit',report),('benchmark',spec)]:
        (output/(name+'.json')).write_text(json.dumps(doc,indent=2,allow_nan=False))
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('run-dir','dataset','site','output'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--log',type=Path)
    a=p.parse_args();print(json.dumps(run(a.run_dir,a.dataset,a.site,a.output,a.log)['measurements']))
