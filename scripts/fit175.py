"""Bounded in-sample learning diagnostic using existing training/evaluation paths."""
import argparse
import collections
import csv
import math
import os
import shutil
import subprocess
import sys
import time
import yaml
import diagnostic174 as d
h=d.h;e=d.e;p=d.p
OUT=h.ROOT/'reports/work/IOS-FIT-175/artifacts'
RUN=h.ROOT/'NativeUITrainer/yolo_runs/fit175-r020'


def select(metadata):
    groups=collections.defaultdict(dict)
    for key,row in sorted(metadata.items()):
        group=(row['group'],row['tint']);place=row['placement']
        h.require(place in ('leading','center','trailing') and place not in groups[group],'duplicate_or_unknown_placement')
        groups[group][place]=key
    ids=sorted(v for group in groups.values() if len(group)==3 for v in group.values())
    h.require(len(ids)==216 and collections.Counter(metadata[k]['placement'] for k in ids)==dict(leading=72,center=72,trailing=72),'balanced_membership')
    return ids


def prepare():
    h.require(not OUT.exists() and not RUN.exists(),'output_collision')
    prior=d.inputs();ids=select(prior['metadata']);request=e.load_request(d.OUT/'input.json',41)
    indexed={im.image_id:im for im in request.images};h.require(set(ids)<=set(indexed),'missing_training_member')
    membership=p.sealed(h.checked(h.ROOT,prior['membership']))
    roles={r['id']:r['split'] for r in membership['rows']};h.require(all(roles[k]=='train' for k in ids),'role_change')
    OUT.mkdir(parents=True);root=OUT/'dataset';(root/'train/images').mkdir(parents=True);(root/'train/labels').mkdir()
    entries=[]
    for key in ids:
        im=indexed[key];(root/'train/images'/(key+'.png')).symlink_to(im.image_path)
        (root/'train/labels'/(key+'.txt')).symlink_to(im.label_path)
        entries.append(dict(imageID=key,imagePath='dataset/train/images/'+key+'.png',labelPath='dataset/train/labels/'+key+'.txt',
            imageSHA256=h.sha(im.image_path),labelSHA256=h.sha(im.label_path)))
    config=dict(path=str(root),train='train/images',val='train/images',names=e.load_names())
    with (root/'dataset.yaml').open('x') as f:yaml.safe_dump(config,f)
    h.write(OUT/'input.json',dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='fit175-in-sample-only',images=entries))
    h.write(OUT/'protocol.json',dict(input=h.ref(OUT/'input.json'),config=h.ref(root/'dataset.yaml'),
        initializer=prior['checkpoints']['019'],prior=h.ref(d.OUT/'protocol.json'),metadata={k:prior['metadata'][k] for k in ids},
        sources=[h.ref(__file__),h.ref(h.ROOT/'scripts/train_ios_model.py')],epochs=20,budgetBytes=2*1024**3,
        role='train and in-sample monitor only; not independent validation',selection='fixed-last',
        independentEvaluation=False,productionEligible=False),sealed=True)
    print('Prepared216members,72per placement; val is explicitly training-fit monitoring',flush=True)


def inputs():
    doc=p.sealed(OUT/'protocol.json')
    for ref in doc['sources']+[doc[k] for k in ('input','config','initializer','prior')]:h.checked(h.ROOT,ref,256*1024**2)
    e.load_request(OUT/'input.json',41)
    return doc


def execute():
    doc=inputs();h.require(not RUN.exists() and not (OUT/'execution.json').exists(),'launch_collision')
    h.require(shutil.disk_usage(h.ROOT).free>8*1024**3,'space')
    os.environ.update(YOLO_OFFLINE='true',YOLO_AUTOINSTALL='false',PYTHONDONTWRITEBYTECODE='1')
    import torch
    h.require(torch.backends.mps.is_available(),'mps_unavailable')
    command=[sys.executable,str(h.ROOT/'scripts/train_ios_model.py'),'--dataset',str(OUT/'dataset'),
        '--initial-weights',str(h.checked(h.ROOT,doc['initializer'],256*1024**2)),
        '--epochs','20','--batch','8','--imgsz','640','--workers','0','--name',RUN.name,'--full-frame-finetune','--timing']
    start=time.monotonic()
    with (OUT/'training.log').open('x') as log:
        child=subprocess.Popen(command,cwd=h.ROOT,env=os.environ.copy(),stdout=log,stderr=subprocess.STDOUT)
        h.write(OUT/'execution.json',dict(pid=child.pid,command=command,protocol=h.ref(OUT/'protocol.json')))
        print('Run020 PID',child.pid,flush=True);code=child.wait()
    result=dict(exitCode=code,seconds=time.monotonic()-start,log=h.ref(OUT/'training.log'))
    if code==0:result['checkpoint']=h.ref(RUN/'weights/last.pt')
    h.write(OUT/'completion.json',result,sealed=True);h.require(code==0,'training_failed_preserved')
    h.require(sum(f.stat().st_size for f in RUN.rglob('*') if f.is_file())<doc['budgetBytes'],'budget')
    print('Run020 terminal',code,flush=True)


def check_terminal(args,rows):
    expected=dict(p.control.full_frame_finetune_kwargs(),epochs=20,imgsz=640,batch=8,workers=0,device='mps',
        resume=False,seed=42,optimizer='AdamW',cos_lr=True,name=RUN.name,data=str(OUT/'dataset/dataset.yaml'))
    h.require(all(args.get(k)==v for k,v in expected.items()),'settings_changed')
    h.require(len(rows)==20 and [str(r['epoch']) for r in rows]==[str(i) for i in range(1,21)],'epoch_count')
    h.require(all(math.isfinite(float(v)) for r in rows for v in r.values()),'nonfinite_epochs')


def ready():
    doc=inputs();receipt=p.sealed(OUT/'completion.json');h.require(receipt['exitCode']==0,'not_completed')
    checkpoint=h.checked(h.ROOT,receipt['checkpoint'],256*1024**2)
    h.require(checkpoint==(RUN/'weights/last.pt'),'checkpoint_selection')
    with (RUN/'results.csv').open() as f:rows=list(csv.DictReader(f))
    args=yaml.safe_load((RUN/'args.yaml').read_text());check_terminal(args,rows)
    h.require(args['model']==str(h.checked(h.ROOT,doc['initializer'],256*1024**2)),'initializer_changed')
    return checkpoint


def infer():
    checkpoint=ready();prior=d.inputs()
    manifests=[OUT/'input.json']+[h.checked(h.ROOT,prior['evaluationManifests'][i]) for i in (3,0)]
    for name,path in zip(('fit','page','combined'),manifests):
        e.export_predictions(path,checkpoint,OUT/(name+'-predictions.json'),'mps',discard_degenerate=True)
    print('Exported216fit/96probe/2400retained images',flush=True)


def report():
    checkpoint=ready();prior=d.inputs();doc=inputs();names=e.load_names();results={}
    h.require(not (OUT/'evaluation.json').exists(),'report_collision')
    manifests=[OUT/'input.json']+[h.checked(h.ROOT,prior['evaluationManifests'][i]) for i in (3,0)]
    paths=[d.OUT/'019-predictions.json',d.completed.OUT/'page-predictions.json',d.completed.OUT/'combined-predictions.json']
    fitcases={}
    for name,path,oldpath in zip(('fit','page','combined'),manifests,paths):
        request=e.load_request(path,41);results[name]={}
        for arm,pred,sha in [('019',oldpath,doc['initializer']['sha256']),('020',OUT/(name+'-predictions.json'),h.sha(checkpoint))]:
            artifact=h.read(pred,256*1024**2)
            if name=='fit' and arm=='019':artifact=e.subset(artifact,request)
            e.validated_artifact(artifact,request,sha,expected_settings=d.completed.SETTINGS)
            results[name][arm]=e.score(artifact,request,names)
            if name=='fit':fitcases[arm]=d.pages(request,artifact,names.index('pageControl'),doc['metadata'])
    strata={arm:{place:dict(collections.Counter(r['disposition'] for r in cases if r['metadata']['placement']==place))
        for place in ('leading','center','trailing')} for arm,cases in fitcases.items()}
    success=all(v.get('operating-hit',0)/72>=.9 for v in strata['020'].values())
    h.write(OUT/'evaluation.json',dict(results=results,fitCases=fitcases,strata=strata,trainingFitSuccess=success,
        protocol=h.ref(OUT/'protocol.json'),checkpoint=h.ref(checkpoint),
        sources=[h.ref(__file__),h.ref(d.__file__),h.ref(e.__file__)],
        independentEvaluation=False,productionEligible=False),sealed=True)
    print('Training-fit success:',success,'not independent evaluation or promotion',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','execute','infer','report']);args=parser.parse_args();globals()[args.mode]()
