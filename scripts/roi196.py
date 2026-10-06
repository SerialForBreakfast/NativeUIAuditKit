"""Qualified coverage extension using the existing ROI cropper and evaluator."""
import argparse
import collections
import hashlib
import importlib.metadata
import math
import os
import shutil
import time
from pathlib import Path
from PIL import Image
import yaml
import roi195 as audit
import roi194 as runner

h,p,e=runner.h,runner.p,runner.e
r=runner.r
OUT=h.ROOT/'reports/work/IOS-ROI-196/artifacts/attempt02'
RUN=h.ROOT/'NativeUITrainer/yolo_runs/roi196-r026'


def ancestry(row,annotation,reserved):
    h.require(row['split']=='train','source_role')
    recipe=annotation.get('generatorProfile',{})
    family=recipe.get('templateFamily')
    # Source annotations, rather than file-name prefixes, establish renderer family.
    h.require(family in ('KitchenSink','UIKitControls','MediaCardGrid','ProgressActivity'),'unknown_ancestry')
    h.require(family not in reserved,'reserved_family')
    h.require(family==row['sourceFamily'] and isinstance(recipe.get('seed'),int),'source_identity')
    return dict(family=family,seed=recipe.get('seed'),group=row.get('group',Path(row['id']).stem))


def configure():
    runner.OUT=OUT/'candidate';runner.RUN=RUN


def prepare():
    h.require(not OUT.exists() and not RUN.exists(),'output_collision')
    h.require(shutil.disk_usage(h.ROOT).free>8*1024**3,'space')
    proposal=p.sealed(audit.OUT/'coverage-proposal.json');old=p.sealed(r.OUT/'proposal.json')
    members=p.sealed(h.checked(h.ROOT,proposal['sourceMembership']))['rows'];byid={v['id']:v for v in members}
    selected=proposal['rows'];h.require(len(selected)==96,'source_count')
    native=h.ROOT/'reports/work/IOS-NATIVE-PAGE-150/artifacts'
    catalog=h.read(native/'compose155-catalog.json');receipt=h.read(native/'compose155-capture/receipt.json')
    native_audit=h.read(native/'compose155-audit/report.json')
    freeze=h.read(native/'page156-freeze.json')
    h.require(native_audit['catalogSHA256']==h.sha(native/'compose155-catalog.json') and
              native_audit['receiptSHA256']==h.sha(native/'compose155-capture/receipt.json') and
              freeze['auditSHA256']==h.sha(native/'compose155-audit/report.json'),'native_ancestry_changed')
    h.require(catalog['role']=='development' and {v['id'] for v in catalog['rows']}=={v['id'] for v in receipt['rows']},'native_reservation')
    reserved={v['family'] for v in catalog['rows']};ancestries=[];entries=[]
    eval_pixels={v['decodedSHA256'] for v in native_audit['rows']}
    eval_groups={v.get('group',Path(v['id']).stem) for v in members if v['split']!='train'}
    for row in selected:
        original=byid[row['id']]
        h.require(all(row[k]==v for k,v in original.items()),'membership_changed')
        annotation=h.read(h.checked(h.ROOT,row['annotation']));info=ancestry(row,annotation,reserved)
        h.require(info['group'] not in eval_groups,'group_overlap');ancestries.append(dict(id=row['id'],**info))
        image=h.checked(h.ROOT,row['image']);label=h.checked(h.ROOT,row['label'])
        with Image.open(image) as im:
            digest=hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
        h.require(digest not in eval_pixels,'native_pixel_overlap')
        entries.append(dict(imageID=row['id'],imagePath=str(image),labelPath=str(label),imageSHA256=row['image']['sha256'],labelSHA256=row['label']['sha256']))
    OUT.mkdir(parents=True)
    source_dir=OUT/'sources';source_dir.mkdir()
    for index,entry in enumerate(entries):
        for field,suffix in (('imagePath','.png'),('labelPath','.txt')):
            link=source_dir/(str(index)+suffix);link.symlink_to(entry[field]);entry[field]=str(link.relative_to(OUT))
    h.write(OUT/'sources.json',dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='roi196-additional-training-only',images=entries))
    req=e.load_request(OUT/'sources.json',41);cid=e.load_names().index('pageControl')
    old_req=e.load_request(h.checked(h.ROOT,old['membership']),41)
    train=[];lineage=list(old['rows']);aliases=list(old['duplicateAliases']);seen={}
    images=OUT/'dataset/train/images';labels=OUT/'dataset/train/labels';images.mkdir(parents=True);labels.mkdir(parents=True)
    for im in old_req.images:
        with Image.open(im.image_path) as source:digest=hashlib.sha256(source.convert('RGB').tobytes()).hexdigest()
        canonical=tuple(sorted(im.label_path.read_text().splitlines()))
        h.require(r.duplicate(seen,digest,canonical) is None,'old_duplicate');seen[digest]=dict(id=im.image_id,labels=canonical)
        for source,dest in ((im.image_path,images/(im.image_id+'.png')),(im.label_path,labels/(im.image_id+'.txt'))):dest.symlink_to(source)
        train.append(dict(imageID=im.image_id,imagePath=str((images/(im.image_id+'.png')).relative_to(OUT)),labelPath=str((labels/(im.image_id+'.txt')).relative_to(OUT)),imageSHA256=im.image_sha256,labelSHA256=im.label_sha256))
    eval_crop_pixels={v['pixelSHA256'] for kind,plan in old['evaluation'].items() if kind!='fit' for item in plan['records'] for v in item['proposals']}
    new_count=0
    for index,im in enumerate(req.images):
        truths=r.c.g.r.f.d.prior.truth(im,cid);h.require(len(truths)==1,'page_source_count');windows=set()
        for variant,shift in enumerate(r.JITTER):
            roi=r.window(im.width,im.height,truths[0],shift)
            if tuple(roi) in windows:continue
            windows.add(tuple(roi));key=f'additional-{index:04d}-{variant}';digest,canonical=r.signature(im,roi)
            h.require(digest not in eval_crop_pixels,'evaluation_crop_overlap')
            previous=r.duplicate(seen,digest,canonical)
            if previous is not None:
                aliases.append(dict(id=key,canonical=previous,parent=im.image_id,group=ancestries[index]['group'],window=roi));continue
            # Existing crop writer makes paths relative to its output root; restore even on failure.
            saved_root=r.OUT
            try:
                r.OUT=OUT;entry,detail=r.save_crop(im,roi,images,key)
            finally:r.OUT=saved_root
            dest=labels/(key+'.txt');(OUT/entry['labelPath']).rename(dest);entry['labelPath']=str(dest.relative_to(OUT))
            h.require(all(v['disposition']=='retained' for v in detail['dispositions'] if v['classID']==cid),'clipped_page')
            train.append(entry);seen[digest]=dict(id=key,labels=canonical);new_count+=1
            lineage.append(dict(id=key,parent=im.image_id,group=ancestries[index]['group'],window=roi,**detail))
    h.write(OUT/'train-input.json',dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='roi196-training-only',images=train))
    e.load_request(OUT/'train-input.json',41)
    with (OUT/'dataset/dataset.yaml').open('x') as stream:
        yaml.safe_dump(dict(path=str(OUT/'dataset'),train='train/images',val='train/images',names=e.load_names()),stream)
    args=dict(old['args'],data=str(OUT/'dataset/dataset.yaml'),name=RUN.name,project=str(RUN.parent),exist_ok=False)
    doc=dict(old,membership=h.ref(OUT/'train-input.json'),rows=lineage,duplicateAliases=aliases,args=args,
        sources=old['sources']+[h.ref(__file__),h.ref(audit.OUT/'coverage-proposal.json'),h.ref(OUT/'dataset/dataset.yaml'),
            h.ref(native/'compose155-catalog.json'),h.ref(native/'compose155-audit/report.json'),h.ref(native/'page156-freeze.json'),h.ref(OUT/'sources.json')],
        ancestry=ancestries,additionalCrops=new_count,originalCrops=len(old_req.images),runID='026')
    doc.pop('seal',None);h.write(OUT/'proposal.json',doc,sealed=True)
    import ultralytics.engine.trainer as trainer
    configure();runner.OUT.mkdir()
    batches=math.ceil(len(train)/8)
    h.write(OUT/'verification.json',dict(proposal=h.ref(OUT/'proposal.json'),count=len(train),nativeReservedFamilies=sorted(reserved),trainingOnly=True),sealed=True)
    h.write(runner.OUT/'protocol.json',dict(proposal=h.ref(OUT/'proposal.json'),verification=h.ref(OUT/'verification.json'),
        sources=[h.ref(__file__),h.ref(runner.__file__),h.ref(r.__file__),h.ref(e.__file__)],trainer=h.ref(trainer.__file__),
        packages={k:importlib.metadata.version(k) for k in ('torch','ultralytics','numpy','Pillow')},args=args,
        batches=batches,budgetBytes=2*1024**3,schedule=r.c.g.r.schedule(batches,10,.25),productionEligible=False),sealed=True)
    print('prepared',len(train),'crops;',new_count,'additional;',batches,'batches',flush=True)


def train():
    configure();doc,proposal=runner.inputs()
    h.require(not RUN.exists() and not (runner.OUT/'completion.json').exists(),'output_collision')
    h.require(shutil.disk_usage(h.ROOT).free>8*1024**3,'space')
    import torch
    from ultralytics import YOLO
    h.require(torch.backends.mps.is_available(),'mps_unavailable')
    model=YOLO(str(h.checked(h.ROOT,proposal['initializer'],256*1024**2)));events=[];batch_index=[-1]
    def started(t):
        h.require(len(t.train_loader)==doc['batches'] and t.args.nbs==64,'schedule')
        step=t.optimizer_step
        def counted():events.append(batch_index[0]);return step()
        t.optimizer_step=counted
    def batch(t):batch_index[0]+=1
    def budget(t):h.require(sum(v.stat().st_size for root in (RUN,OUT) for v in root.rglob('*') if v.is_file() and not v.is_symlink())<=doc['budgetBytes'],'budget')
    model.add_callback('on_train_start',started);model.add_callback('on_train_batch_start',batch);model.add_callback('on_model_save',budget)
    start=time.monotonic();h.write(runner.OUT/'execution.json',dict(pid=os.getpid(),protocol=h.ref(runner.OUT/'protocol.json')))
    try:
        model.train(**doc['args']);h.require(events==doc['schedule']['optimizerAt'],'optimizer_schedule_mismatch');budget(None)
        h.write(runner.OUT/'completion.json',dict(exitCode=0,seconds=time.monotonic()-start,optimizerAt=events,checkpoint=h.ref(RUN/'weights/last.pt')),sealed=True)
    except Exception as exc:
        h.write(runner.OUT/'completion.json',dict(exitCode=1,error=str(exc),seconds=time.monotonic()-start,optimizerAt=events),sealed=True);raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','train','infer','report']);mode=parser.parse_args().mode
    if mode in ('prepare','train'):globals()[mode]()
    else:configure();getattr(runner,mode)()
