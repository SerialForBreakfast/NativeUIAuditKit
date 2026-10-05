"""Explicit terminal-candidate evaluation; reuse established export and AP paths."""
import argparse
import csv
import math
import statistics
from pathlib import Path
import shared_transfer
import ios_repair165 as r
import eval_run013 as e
from train_ios_model import full_frame_finetune_kwargs
h=r.h


def page_geometry(document,request,cid):
    """Oracle geometry diagnostic; AP and operational matching remain authoritative."""
    indexed={row['imageID']:row for row in document['results']}
    reports={}
    for name,threshold in [('export',0.0),('operational',.25)]:
        rows=[]
        for image in request.images:
            labels=[list(map(float,line.split())) for line in image.label_path.read_text().splitlines() if line.strip()]
            h.require(len(labels)==1 and labels[0][0]==cid,'page_single_target_required')
            _,cx,cy,w,ht=labels[0]
            h.require(w>0 and ht>0,'page_target_geometry')
            g=((cx-w/2)*image.width,(cy-ht/2)*image.height,
               (cx+w/2)*image.width,(cy+ht/2)*image.height)
            candidates=[d for d in indexed[image.image_id]['detections'] if d['classID']==cid and d['score']>=threshold]
            row=dict(imageID=image.image_id,candidateCount=len(candidates),geometry=None)
            if candidates:
                d=max(candidates,key=lambda d:(e.iou_xyxy(g,d['xyxyPixels']),d['score'],tuple(d['xyxyPixels'])))
                b=d['xyxyPixels'];bx=(b[0]+b[2])/2;by=(b[1]+b[3])/2
                row['geometry']=dict(iou=e.iou_xyxy(g,b),score=d['score'],
                    widthRatio=(b[2]-b[0])/(g[2]-g[0]),heightRatio=(b[3]-b[1])/(g[3]-g[1]),
                    centerErrorXPixels=bx-cx*image.width,centerErrorYPixels=by-cy*image.height,
                    centerInside=g[0]<=bx<=g[2] and g[1]<=by<=g[3])
            rows.append(row)
        present=[row['geometry'] for row in rows if row['geometry'] is not None]
        reports[name]=dict(imageCount=len(rows),withCandidates=len(present),missingCandidates=len(rows)-len(present),
            medianWidthRatio=statistics.median(v['widthRatio'] for v in present) if present else None,
            medianHeightRatio=statistics.median(v['heightRatio'] for v in present) if present else None,
            centerInside=sum(v['centerInside'] for v in present),cases=rows)
    return dict(selection='best-IoU oracle diagnostic, not model-selected output',populations=reports)


def terminal_contract(arm,launch,checkpoint,args,rows):
    expected=h.ROOT/'NativeUITrainer/yolo_runs'/('repair165-'+arm)/'weights/last.pt'
    h.require(checkpoint.resolve()==expected.resolve(),'wrong_arm_or_checkpoint')
    config=dict(full_frame_finetune_kwargs(),epochs=5,imgsz=640,batch=8,workers=0,
        device='mps',resume=False,optimizer='AdamW',cos_lr=True,seed=42,
        name='repair165-'+arm,data=str(h.ROOT/launch['configs'][arm]['path']),
        model=launch['initializer']['path'])
    h.require(all(k in args and args[k]==v and
        (type(args[k]) is bool if type(v) is bool else True) for k,v in config.items()),'training_settings_mismatch')
    h.require(len(rows)==5 and [str(row.get('epoch')) for row in rows]==['1','2','3','4','5'],'epoch_accounting')
    required={'time','train/box_loss','train/cls_loss','train/dfl_loss','val/box_loss','val/cls_loss','val/dfl_loss',
              'metrics/mAP50(B)','metrics/mAP50-95(B)'}
    h.require(all(required<=row.keys() and all(math.isfinite(float(value)) for value in row.values()) for row in rows),'nonfinite_epoch_evidence')


def ready(arm):
    h.require(arm in ('r016-prior','r017-repaired'),'arm')
    launch=h.read(r.ART/'launch-corrected.json')
    h.require(launch['seal']==h.digest({k:v for k,v in launch.items() if k!='seal'}),'launch_seal')
    receipt=h.read(r.ART/(arm+'-completion.json'))
    h.require(receipt['seal']==h.digest({k:v for k,v in receipt.items() if k!='seal'}) and receipt['exitCode']==0,'incomplete_training')
    checkpoint=h.checked(h.ROOT,receipt['checkpoint'],256*1024**2)
    root=checkpoint.parent.parent
    args=shared_transfer.document(root/'args.yaml')
    h.require((root/'results.csv').stat().st_size<128*1024,'epoch_report_size')
    with (root/'results.csv').open() as handle:rows=list(csv.DictReader(handle))
    terminal_contract(arm,launch,checkpoint,args,rows)
    refs=[h.checked(h.ROOT,v,256*1024**2) for v in launch['evaluation']]
    return checkpoint,refs


def infer(arm):
    checkpoint,refs=ready(arm)
    for name,manifest in [('combined',refs[0]),('page',refs[3])]:
        output=r.ART/(arm+'-'+name+'-predictions.json')
        h.require(not output.exists(),'prediction_collision')
        e.export_predictions(manifest,checkpoint,output,'mps')


def report(arm):
    checkpoint,refs=ready(arm);names=e.load_names();candidate=h.read(r.ART/(arm+'-combined-predictions.json'),256*1024**2)
    baseline=h.read(refs[5],256*1024**2);scores={}
    for i,pop in enumerate(('combined','withheld','addon')):
        request=e.load_request(refs[i],len(names))
        pair={}
        for label,doc,sha in [('candidate',candidate,h.sha(checkpoint)),('run013',baseline,r.WEIGHT_SHA)]:
            subset=e.subset(doc,request) if pop!='combined' else doc
            e.validated_artifact(subset,request,sha);pair[label]=e.score(subset,request,names)
        scores[pop]=pair
    page_request=e.load_request(refs[3],len(names));page={};geometry={}
    for label,path,sha in [('candidate',r.ART/(arm+'-page-predictions.json'),h.sha(checkpoint)),('run013',refs[4],r.WEIGHT_SHA)]:
        doc=h.read(path,256*1024**2);e.validated_artifact(doc,page_request,sha)
        full=e.score(doc,page_request,names)
        page[label]=next(v for v in full['perClass'] if v['class']=='pageControl')
        geometry[label]=page_geometry(doc,page_request,names.index('pageControl'))
    output=r.ART/(arm+'-evaluation.json');h.require(not output.exists(),'report_collision')
    h.write(output,dict(arm=arm,checkpoint=h.ref(checkpoint),populations=scores,pageDevelopment=page,pageGeometry=geometry,
        evaluatorSources=[h.ref(__file__)]+[h.ref(h.ROOT/p) for p in e.CODE],
        independentEvaluation=False,productionEligible=False),sealed=True)
    print('evaluated',arm,'complete2400retained/96page development; no DS-G8 claim')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['infer','report']);p.add_argument('arm',choices=['r016-prior','r017-repaired']);a=p.parse_args()
    globals()[a.mode](a.arm)
