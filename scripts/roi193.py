"""Prepare source-bound YOLO ROI inputs, not training or production inference."""
import collections
import copy
import hashlib
import math
import shutil
import time
from pathlib import Path
from PIL import Image
import yaml
import roi192 as r
import crossover189 as c

h,p,e=r.h,r.p,r.e
OUT=h.ROOT/'reports/work/IOS-ROI-193/artifacts/attempt02'
JITTER=((0,0),(-.1,-.1),(-.1,.1),(.1,-.1),(.1,.1))


def window(width,height,box,jitter=(0,0)):
    r.window(width,height,box)  # Validate source bounds/aspect before integer conversion.
    side=math.floor(width/2+.5)
    h.require(side>0 and side<=height and len(jitter)==2 and all(math.isfinite(x) for x in jitter),'window_geometry')
    x=min(max(math.floor((box[0]+box[2]-side)/2+jitter[0]*side+.5),0),width-side)
    y=min(max(math.floor((box[1]+box[3]-side)/2+jitter[1]*side+.5),0),height-side)
    return [x,y,x+side,y+side]


def labels(image,roi):
    result=[];audit=[];side=roi[2]-roi[0]
    for index,line in enumerate(image.label_path.read_text().splitlines()):
        if not line.strip():continue
        cid,cx,cy,w,ht=map(float,line.split())
        box=[(cx-w/2)*image.width,(cy-ht/2)*image.height,(cx+w/2)*image.width,(cy+ht/2)*image.height]
        a,b=max(box[0],roi[0]),max(box[1],roi[1]);u,v=min(box[2],roi[2]),min(box[3],roi[3])
        area=max(0,u-a)*max(0,v-b);fraction=area/((box[2]-box[0])*(box[3]-box[1]))
        disposition='outside' if area==0 else 'excluded_sliver' if min(u-a,v-b)<2 else 'retained' if math.isclose(fraction,1,rel_tol=1e-8) else 'clipped'
        if disposition in ('retained','clipped'):
            result.append(f'{int(cid)} {(a+u-2*roi[0])/(2*side):.9f} {(b+v-2*roi[1])/(2*side):.9f} {(u-a)/side:.9f} {(v-b)/side:.9f}')
        audit.append(dict(index=index,classID=int(cid),disposition=disposition,visibleFraction=fraction))
    return '\n'.join(result)+('\n' if result else ''),audit


def proposals(row,cid):
    h.require(row['status'] in ('ok','empty'),'failed_inference')
    return [(i,d) for i,d in enumerate(row['detections']) if d['classID']==cid and d['score']>=.25]


def restore(box,roi):
    side=roi[2]-roi[0]
    h.require(len(box)==4 and all(math.isfinite(x) for x in box) and
              0<=box[0]<box[2]<=side and 0<=box[1]<box[3]<=side,'crop_box')
    return [box[0]+roi[0],box[1]+roi[1],box[2]+roi[0],box[3]+roi[1]]


def refine(base,crop_results,cid):
    """Geometry-only deployment rule; crop_results contain no ground truth."""
    result=copy.deepcopy(base);tentative={}
    selected=dict(proposals(base,cid))
    h.require(set(crop_results)==set(selected),'proposal_completeness')
    for index,item in crop_results.items():
        h.require(item.get('status') in ('ok','empty'),'failed_crop_inference')
        h.require(item['window']==window(base['width'],base['height'],selected[index]['xyxyPixels']),'window_binding')
        donors=[]
        for d in item['detections']:
            h.require(math.isfinite(d['score']) and 0<=d['score']<=1,'crop_score')
            if d['classID']==cid and d['score']>=.25:
                box=restore(d['xyxyPixels'],item['window'])
                if e.iou_xyxy(box,selected[index]['xyxyPixels'])>=.25:donors.append(box)
        if len(donors)==1:tentative[index]=donors[0]
    for i,box in tentative.items():
        # Two independent crop passes must not refine distinct proposals to the same object.
        if any(i!=j and e.iou_xyxy(box,other)>=.5 for j,other in tentative.items()):continue
        result['detections'][i]['xyxyPixels']=box
    return result


def save_crop(image,roi,directory,key):
    directory.mkdir(parents=True,exist_ok=True)
    image_path=directory/(key+'.png');label_path=directory/(key+'.txt')
    h.require(not image_path.exists() and not label_path.exists(),'crop_collision')
    label,audit=labels(image,roi)
    with Image.open(image.image_path) as original:
        h.require(original.size==(image.width,image.height),'image_dimensions')
        crop=original.convert('RGB').crop(roi)
        pixels=hashlib.sha256(crop.tobytes()).hexdigest()
        crop.save(image_path)
    with label_path.open('x') as stream:stream.write(label)
    with Image.open(image_path) as saved:
        h.require(saved.size==(roi[2]-roi[0],roi[3]-roi[1]) and hashlib.sha256(saved.tobytes()).hexdigest()==pixels,'crop_pixels')
    return dict(imageID=key,imagePath=str(image_path.relative_to(OUT)),labelPath=str(label_path.relative_to(OUT)),
                imageSHA256=h.sha(image_path),labelSHA256=h.sha(label_path)),dict(dispositions=audit,pixelSHA256=pixels)


def signature(image,roi):
    label,_=labels(image,roi)
    with Image.open(image.image_path) as original:
        digest=hashlib.sha256(original.convert('RGB').crop(roi).tobytes()).hexdigest()
    return digest,tuple(sorted(label.splitlines()))


def duplicate(seen,digest,label):
    if digest not in seen:return None
    h.require(seen[digest]['labels']==label,'identical_pixels_conflicting_labels')
    return seen[digest]['id']


def run():
    h.require(not OUT.exists(),'output_collision');start=time.monotonic()
    h.require(shutil.disk_usage(h.ROOT).free>=4*1024**3,'insufficient_space')
    feasibility=p.sealed(r.OUT/'feasibility.json');h.checked(h.ROOT,feasibility['source'])
    parent=c.inputs();metadata={x['id']:x for x in feasibility['rows']};cid=e.load_names().index('pageControl')
    requests={k:e.load_request(h.checked(h.ROOT,v),41) for k,v in parent['manifests'].items()}
    membership=p.sealed(h.checked(h.ROOT,r.f.d.inputs()['membership']))
    roles={x['id']:x['split'] for x in membership['rows']}
    h.require(set(metadata)=={im.image_id for im in requests['fit'].images} and all(roles[k]=='train' for k in metadata),'training_membership')
    training_hashes={h.sha(im.image_path) for im in requests['fit'].images}
    h.require(all(h.sha(im.image_path) not in training_hashes for kind,req in requests.items() if kind!='fit' for im in req.images),'source_split_overlap')
    original={};sources=[]
    for kind,req in requests.items():
        path=h.checked(h.ROOT,parent['reused']['022'][kind],256*1024**2)
        original[kind]=e.validated_artifact(h.read(path,256*1024**2),req,parent['checkpoints']['022']['sha256'],expected_settings=c.SETTINGS)
        sources.append(h.ref(path))
    OUT.mkdir(parents=True);train=[];lineage=[];seen={};eval_plan={};aliases=[]
    for index,im in enumerate(requests['fit'].images):
        frozen=metadata[im.image_id];h.checked(h.ROOT,frozen['image']);h.checked(h.ROOT,frozen['label']);windows=set()
        for variant,shift in enumerate(JITTER):
            roi=window(im.width,im.height,frozen['target'],shift)
            if tuple(roi) in windows:continue
            windows.add(tuple(roi));key=f'train-{index:04d}-{variant}'
            digest,canonical=signature(im,roi)
            previous=duplicate(seen,digest,canonical)
            if previous is not None:
                aliases.append(dict(id=key,canonical=previous,parent=im.image_id,group=frozen['metadata']['group'],window=roi))
                continue
            entry,audit=save_crop(im,roi,OUT/'dataset/train/images',key)
            # Ultralytics derives labels by replacing the images path segment.
            target=OUT/'dataset/train/labels'/(key+'.txt');target.parent.mkdir(parents=True,exist_ok=True)
            (OUT/entry['labelPath']).rename(target);entry['labelPath']=str(target.relative_to(OUT))
            h.require(all(a['disposition']=='retained' for a in audit['dispositions'] if a['classID']==cid),'clipped_training_target')
            seen[audit['pixelSHA256']]=dict(id=key,labels=canonical)
            train.append(entry);lineage.append(dict(id=key,parent=im.image_id,group=frozen['metadata']['group'],window=roi,**audit))
    h.write(OUT/'train-input.json',dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='roi193-training-only',images=train))
    e.load_request(OUT/'train-input.json',41)
    for kind,req in requests.items():
        by_id={x['imageID']:x for x in original[kind]['results']};entries=[];records=[]
        for image_index,im in enumerate(req.images):
            windows=[]
            for prediction_index,d in proposals(by_id[im.image_id],cid):
                roi=window(im.width,im.height,d['xyxyPixels']);key=f'{kind}-{image_index:04d}-{prediction_index}'
                entry,audit=save_crop(im,roi,OUT/'evaluation'/kind,key)
                h.require(kind=='fit' or audit['pixelSHA256'] not in seen,'train_evaluation_pixel_overlap')
                entries.append(entry);windows.append(dict(id=key,proposalIndex=prediction_index,window=roi,pixelSHA256=audit['pixelSHA256']))
            records.append(dict(imageID=im.image_id,proposals=windows))
        h.write(OUT/(kind+'-input.json'),dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='roi193-'+kind,images=entries))
        if entries:e.load_request(OUT/(kind+'-input.json'),41)
        eval_plan[kind]=dict(records=records,manifest=h.ref(OUT/(kind+'-input.json')),croppedImages=len(entries),noProposal=sum(not x['proposals'] for x in records))
    cfg=dict(path=str(OUT/'dataset'),train='train/images',val='train/images',names=e.load_names())
    with (OUT/'dataset/dataset.yaml').open('x') as stream:yaml.safe_dump(cfg,stream)
    control=p.sealed(c.g.CONTROL/'protocol.json')
    args=dict(control['args'],data=str(OUT/'dataset/dataset.yaml'),model=str(h.checked(h.ROOT,parent['checkpoints']['022'],256*1024**2)),
              name='roi193-candidate-pending',project=str(h.ROOT/'NativeUITrainer/yolo_runs'))
    h.require(sum(x.stat().st_size for x in OUT.rglob('*') if x.is_file())<=2*1024**3-8*1024**2,'dataset_budget')
    h.write(OUT/'proposal.json',dict(version='roi193-prepared-v1',sources=sources+[h.ref(__file__),h.ref(r.__file__),h.ref(r.OUT/'feasibility.json'),h.ref(OUT/'dataset/dataset.yaml')],
        membership=h.ref(OUT/'train-input.json'),rows=lineage,duplicateAliases=aliases,evaluation=eval_plan,args=args,initializer=parent['checkpoints']['022'],
        monitorRole='training fit only; validation paths intentionally in-sample',outputBudgetBytes=2*1024**3,
        trainAdmission='derived from existing216train sources only; clipped visible-box convention',
        configurationReady=True,remainingLaunchRequirements=['record candidate run before launch','review crop boundary evidence and integrated verification'],runID=None,trainingLaunched=False,productionEligible=False,seconds=time.monotonic()-start),sealed=True)
    h.require(sum(x.stat().st_size for x in OUT.rglob('*') if x.is_file())<=2*1024**3,'dataset_budget')
    print('Prepared',len(train),'training crops;', {k:(v['croppedImages'],v['noProposal']) for k,v in eval_plan.items()},flush=True)


if __name__=='__main__':run()
