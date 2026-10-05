"""One pinned replay candidate using resident YOLO and existing prediction/scoring contracts."""
import argparse
import collections
import csv
import math
import os
import shutil
import time
from pathlib import Path
import yaml
import fit175 as f
h,e,p=f.h,f.e,f.p
OUT=h.ROOT/'reports/work/IOS-REPLAY-179/attempt02/artifacts'
RUN=h.ROOT/'NativeUITrainer/yolo_runs/replay179-r021'
PROPOSAL=h.ROOT/'reports/work/IOS-FIT-176/artifacts/replay-proposal.json'


def schedule(nb,epochs,warmup):
    nw=round(warmup*nb);last=-1;steps=[]
    for i in range(nb*epochs):
        acc=max(1,round(1+7*i/nw)) if i<nw else 8
        if i-last>=acc:steps.append(i);last=i
    return dict(batches=nb*epochs,warmupBatches=nw,optimizerAt=steps)


def choose(doc,membership,metadata):
    indexed={r['id']:r for r in membership}
    ids=doc['fitIDs']+[r['id'] for r in doc['replayRows']]
    h.require(len(ids)==432 and len(set(ids))==432,'membership_count')
    h.require(set(doc['fitIDs'])==set(metadata),'fit_membership')
    rows=[indexed[i] for i in ids]
    h.require(all(r['split']=='train' for r in rows),'role_change')
    h.require(all(indexed[r['id']]==r for r in doc['replayRows']),'changed_replay')
    evaluation=[r for r in membership if r['split']!='train']
    h.require(len({r['pixelSHA256'] for r in rows})==432 and not
        ({r['pixelSHA256'] for r in rows}&{r['pixelSHA256'] for r in evaluation}),'pixel_leak')
    eval_ids={Path(r['id']).stem for r in evaluation}
    # Added placement rows explicitly record original training parent; base rows
    # retain original image identity/family from the sealed admitted membership.
    parents={Path(r['id']).stem for r in membership if r['split']=='train'}
    for r in rows:
        parent=r.get('group',Path(r['id']).stem)
        h.require(parent in parents and parent not in eval_ids,'ancestry_leak')
    return rows


def prepare():
    h.require(not OUT.exists() and not RUN.exists(),'output_collision')
    doc=p.sealed(PROPOSAL);old=f.inputs();prior=f.d.inputs()
    membership=p.sealed(h.checked(h.ROOT,doc['membership']))
    rows=choose(doc,membership['rows'],old['metadata'])
    paths=[]
    for r in rows:paths.append((r,h.checked(h.ROOT,r['image']),h.checked(h.ROOT,r['label'])))
    control=schedule(27,20,.5);treatment=schedule(54,10,.25)
    h.require(control==treatment,'schedule_events_differ')
    OUT.mkdir(parents=True);root=OUT/'dataset'
    for kind in ('images','labels'):(root/'train'/kind).mkdir(parents=True)
    counts=collections.Counter();entries=[]
    for r,image,label in paths:
        key=r['id'].replace('/','__')
        (root/'train/images'/(key+'.png')).symlink_to(image)
        (root/'train/labels'/(key+'.txt')).symlink_to(label)
        counts.update(set(int(l.split()[0]) for l in label.read_text().splitlines() if l.strip()))
        entries.append(dict(imageID=r['id'],imagePath='dataset/train/images/'+key+'.png',
            labelPath='dataset/train/labels/'+key+'.txt',imageSHA256=h.sha(image),labelSHA256=h.sha(label)))
    h.write(OUT/'input.json',dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='replay179-training-only',images=entries))
    e.load_request(OUT/'input.json',41)
    h.require(all(counts[e.load_names().index(c)]>=16 for c,n in doc['omittedFitTrainSupport'].items() if n),'coverage')
    cfg=dict(path=str(root),train='train/images',val='train/images',names=e.load_names())
    with (root/'dataset.yaml').open('x') as stream:yaml.safe_dump(cfg,stream)
    args=yaml.safe_load((f.RUN/'args.yaml').read_text())
    args.pop('save_dir',None)
    args.update(data=str(root/'dataset.yaml'),epochs=10,warmup_epochs=.25,name=RUN.name,
                project=str(RUN.parent),exist_ok=False)
    import ultralytics.engine.trainer as trainer
    h.write(OUT/'protocol.json',dict(proposal=h.ref(PROPOSAL),fitProtocol=h.ref(f.OUT/'protocol.json'),
        membership=doc['membership'],rows=rows,input=h.ref(OUT/'input.json'),config=h.ref(root/'dataset.yaml'),initializer=old['initializer'],
        args=args,schedule=treatment,epochScheduleIdentical=False,metadata=old['metadata'],
        sources=[h.ref(__file__),h.ref(f.__file__),h.ref(e.__file__),h.ref(h.ROOT/'scripts/train_ios_model.py')],
        trainerSHA256=h.sha(Path(trainer.__file__)),prior=prior['evaluation'],budgetBytes=2*1024**3,
        monitorRole='in-sample only; no final/independent evaluation',productionEligible=False),sealed=True)
    print('Prepared432; schedule',treatment,flush=True)


def inputs():
    doc=p.sealed(OUT/'protocol.json')
    for r in doc['sources']+[doc[k] for k in ('proposal','fitProtocol','membership','input','config','initializer','prior')]:h.checked(h.ROOT,r,256*1024**2)
    e.load_request(OUT/'input.json',41)
    for r in doc['rows']:
        for k in ('image','label'):h.checked(h.ROOT,r[k])
    import ultralytics.engine.trainer as trainer
    h.require(h.sha(Path(trainer.__file__))==doc['trainerSHA256'],'trainer_changed')
    return doc


def train():
    h.require(not RUN.exists() and not (OUT/'completion.json').exists(),'output_collision')
    doc=inputs();h.require(shutil.disk_usage(h.ROOT).free>8*1024**3,'space')
    import torch
    from ultralytics import YOLO
    h.require(torch.backends.mps.is_available(),'mps_unavailable')
    model=YOLO(str(h.checked(h.ROOT,doc['initializer'],256*1024**2)))
    observed=[]
    def started(t):
        h.require(len(t.train_loader)==54 and t.args.epochs==10 and t.args.nbs==64,'loader_schedule')
        original=t.optimizer_step
        def step():
            observed.append(t.epoch*54+t.batch_i);return original()
        t.optimizer_step=step
    # batch_i is supplied by our callback; no resident trainer edits.
    index=[-1]
    def batch(t):index[0]+=1;t.batch_i=index[0]%54
    model.add_callback('on_train_start',started);model.add_callback('on_train_batch_start',batch)
    def mirror(t):
        if Path(t.last).exists():shutil.copy2(t.last,Path(t.last).with_name('last.prev.pt'))
    model.add_callback('on_model_save',mirror)
    started_at=time.monotonic();h.write(OUT/'execution.json',dict(pid=os.getpid(),protocol=h.ref(OUT/'protocol.json')))
    try:
        model.train(**doc['args'])
        h.require(observed==doc['schedule']['optimizerAt'],'optimizer_event_mismatch')
        h.require(sum(x.stat().st_size for x in RUN.rglob('*') if x.is_file())<doc['budgetBytes'],'budget')
        h.write(OUT/'completion.json',dict(exitCode=0,seconds=time.monotonic()-started_at,
            optimizerAt=observed,checkpoint=h.ref(RUN/'weights/last.pt')),sealed=True)
    except Exception as error:
        h.write(OUT/'completion.json',dict(exitCode=1,error=str(error),seconds=time.monotonic()-started_at,optimizerAt=observed),sealed=True);raise


def ready():
    doc=inputs();end=p.sealed(OUT/'completion.json');h.require(end['exitCode']==0,'run_failed')
    with (RUN/'results.csv').open() as stream:rows=list(csv.DictReader(stream))
    h.require([str(r['epoch']) for r in rows]==[str(i) for i in range(1,11)] and all(math.isfinite(float(v)) for r in rows for v in r.values()),'terminal_epochs')
    actual=yaml.safe_load((RUN/'args.yaml').read_text())
    h.require(all(actual.get(k)==v for k,v in doc['args'].items()),'settings_changed')
    checkpoint=h.checked(h.ROOT,end['checkpoint'],256*1024**2)
    h.require(checkpoint==RUN/'weights/last.pt','checkpoint_selection')
    return checkpoint


def infer():
    cp=ready();prior=f.d.inputs()
    for name,path in [('fit',f.OUT/'input.json'),('page',h.checked(h.ROOT,prior['evaluationManifests'][3])),('combined',h.checked(h.ROOT,prior['evaluationManifests'][0]))]:
        e.export_predictions(path,cp,OUT/(name+'-predictions.json'),'mps',discard_degenerate=True)


def assess(results,strata,reference):
    retained=results['combined'];old=reference['results']['combined']['019']
    classes={r['class']:r for r in retained['perClass']}
    previous={r['class']:r for r in old['perClass']}
    page=next(r for r in results['page']['perClass'] if r['class']=='pageControl')
    gates={s:strata[s].get('operating-hit',0)/72>=.9 for s in ('leading','center','trailing')}
    gates.update(pageTP=page['tp']>=59,pageFP=page['fp']<=4,
        retainedAP=retained['metrics']['map50']+1e-6>=old['metrics']['map50'])
    for name in ('sheet','scrollIndicator'):
        gates[name+'AP']=classes[name]['ap50']+1e-6>=previous[name]['ap50']
    for name in ('sheet','cancelAction','mapView'):
        gates[name+'TP']=classes[name]['tp']>=previous[name]['tp']
        gates[name+'FP']=classes[name]['fp']<=previous[name]['fp']
    return dict(gates=gates,developmentSuccess=all(gates.values()),
        perClassAPDelta={k:None if v['ap50'] is None or previous[k]['ap50'] is None else
            v['ap50']-previous[k]['ap50'] for k,v in classes.items()},productionEligible=False)


def report():
    cp=ready();doc=inputs();prior=f.d.inputs();results={};strata={}
    h.require(not (OUT/'evaluation.json').exists(),'output_collision')
    for name,path in [('fit',f.OUT/'input.json'),('page',h.checked(h.ROOT,prior['evaluationManifests'][3])),('combined',h.checked(h.ROOT,prior['evaluationManifests'][0]))]:
        req=e.load_request(path,41);a=h.read(OUT/(name+'-predictions.json'),256*1024**2)
        e.validated_artifact(a,req,h.sha(cp),expected_settings=f.d.completed.SETTINGS)
        results[name]=e.score(a,req,e.load_names())
        if name=='fit':
            cases=f.d.pages(req,a,e.load_names().index('pageControl'),doc['metadata'])
            strata={s:dict(collections.Counter(r['disposition'] for r in cases if r['metadata']['placement']==s)) for s in ('leading','center','trailing')}
    reference=p.sealed(f.OUT/'evaluation.json')
    h.write(OUT/'evaluation.json',dict(results=results,strata=strata,assessment=assess(results,strata,reference),fitCases=cases,checkpoint=h.ref(cp),
        protocol=h.ref(OUT/'protocol.json'),reference=h.ref(f.OUT/'evaluation.json'),productionEligible=False),sealed=True)
    print('Matched evaluation complete; no promotion',flush=True)


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['prepare','train','infer','report']);args=a.parse_args();globals()[args.mode]()
