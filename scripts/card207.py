"""Fixed development-only card proposals; reuse the existing ROI/export/scoring path."""
import argparse
import copy
from dataclasses import replace
import shutil
import time
import roi193 as r

h,p,e=r.h,r.p,r.e
SOURCE=h.ROOT/'reports/work/IOS-ASSET-200/artifacts/campaign-evaluation01'
OUT=h.ROOT/'reports/work/IOS-ASSET-200/artifacts/card207-01'
CHECKPOINT=h.ROOT/'NativeUITrainer/yolo_runs/replay184-r022/weights/last.pt'
MODEL='d40ad18f8d7dea266082de153a3cf078845cf2c53bd277735d79aa4d226f8e6d'


def select(row,cid):
    """No labels: group identical integer windows, retaining all parent proposals."""
    windows={}
    for _,d in r.proposals(row,cid):
        box=d['xyxyPixels'];roi=tuple(r.window(row['width'],row['height'],box))
        windows.setdefault(roi,[]).append(box)
    return [dict(window=list(k),parents=v) for k,v in windows.items()]


def merge(row,plans,crops,cid):
    candidates=copy.deepcopy([d for d in row['detections'] if d['classID']==cid])
    for plan in plans:
        crop=crops[plan['id']];roi=plan['window']
        h.require(crop['status'] in ('ok','empty'),'failed_crop')
        h.require((crop['width'],crop['height'])==(roi[2]-roi[0],roi[3]-roi[1]),'crop_dimensions')
        for d in crop['detections']:
            if d['classID']!=cid or d['score']<.25:continue
            box=r.restore(d['xyxyPixels'],roi);cx=(box[0]+box[2])/2;cy=(box[1]+box[3])/2
            if any(b[0]<=cx<=b[2] and b[1]<=cy<=b[3] and e.iou_xyxy(box,b)>=.25 for b in plan['parents']):
                candidates.append(dict(d,xyxyPixels=box))
    retained=[]
    for d in sorted(candidates,key=lambda x:-x['score']):
        if d['score']<.25 or not any(v['score']>=.25 and e.iou_xyxy(d['xyxyPixels'],v['xyxyPixels'])>=.5 for v in retained):
            retained.append(d)
    result=copy.deepcopy(row)
    result['detections']=[d for d in result['detections'] if d['classID']!=cid]+retained
    result['status']='ok' if result['detections'] else 'empty'
    return result


def original():
    proto=h.read(SOURCE/'protocol.json');req=e.load_request(SOURCE/'manifest.json',41)
    h.require(h.sha(SOURCE/'manifest.json')==proto['manifestSHA256'] and proto['checkpointSHA256']==MODEL,'source_identity')
    h.require(len(req.images)==96,'membership')
    data=e.validated_artifact(h.read(SOURCE/'predictions.json',32*1024**2),req,MODEL,expected_settings=proto['settings'])
    return proto,req,data


def prepare():
    h.require(not OUT.exists(),'output_collision');proto,req,data=original()
    h.require(h.sha(CHECKPOINT)==MODEL and shutil.disk_usage(h.ROOT).free>3*1024**3,'model_or_space')
    cid=e.load_names().index('collectionItem');by={v['imageID']:v for v in data['results']}
    plans=[dict(imageID=im.image_id,proposals=select(by[im.image_id],cid)) for im in req.images]
    h.require(0<sum(len(v['proposals']) for v in plans)<=512,'proposal_budget')
    refs=[h.ref(SOURCE/x) for x in ('protocol.json','manifest.json','predictions.json')]
    refs += [h.ref(__file__),h.ref(r.__file__),h.ref(e.__file__),h.ref(CHECKPOINT)]
    OUT.mkdir(parents=True);entries=[];old=r.OUT;r.OUT=OUT
    try:
        for index,(im,plan) in enumerate(zip(req.images,plans)):
            for j,item in enumerate(plan['proposals']):
                key=f'card-{index:03d}-{j:03d}';entry,audit=r.save_crop(im,item['window'],OUT/'crops',key)
                item.update(id=key,audit=audit);entries.append(entry)
    finally:r.OUT=old
    h.write(OUT/'input.json',dict(formatVersion=e.INPUT_FORMAT_VERSION,corpusID='card207-development',images=entries))
    e.load_request(OUT/'input.json',41)
    h.require(sum(x.stat().st_size for x in OUT.rglob('*') if x.is_file())<1024**3,'output_budget')
    h.write(OUT/'protocol.json',dict(sources=refs,settings=proto['settings'],manifest=h.ref(OUT/'input.json'),
        plans=plans,checkpointSHA256=MODEL,role='development_only',training=False,modelQualified=False),sealed=True)
    print('prepared',len(entries),'crops',len(plans),'frames',flush=True)


def protocol():
    d=p.sealed(OUT/'protocol.json')
    for ref in d['sources']+[d['manifest']]:h.checked(h.ROOT,ref,256*1024**2)
    return d


def infer():
    d=protocol();h.require(not (OUT/'predictions.json').exists(),'output_collision');start=time.monotonic()
    e.export_predictions(OUT/'input.json',CHECKPOINT,OUT/'predictions.json','mps',imgsz=640,discard_degenerate=True)
    h.write(OUT/'timing.json',dict(seconds=time.monotonic()-start,device='mps',newFullFramePass=False),sealed=True)


def report():
    d=protocol();h.require(not (OUT/'report.json').exists(),'output_collision');start=time.monotonic()
    _,req,base=original();cr=e.load_request(OUT/'input.json',41)
    crops=e.validated_artifact(h.read(OUT/'predictions.json',64*1024**2),cr,MODEL,expected_settings=d['settings'])
    lookup={v['imageID']:v for v in crops['results']};plans={v['imageID']:v for v in d['plans']}
    h.require(set(plans)=={im.image_id for im in req.images} and set(lookup)=={x['id'] for v in d['plans'] for x in v['proposals']},'completeness')
    names=e.load_names();cid=names.index('imageView');parent=names.index('collectionItem');out=[]
    for row in base['results']:
        expected=select(row,parent);actual=plans[row['imageID']]['proposals']
        h.require(expected==[{k:v[k] for k in ('window','parents')} for v in actual],'proposal_binding')
        out.append(merge(row,actual,lookup,cid))
    results={}
    for layout in ('grid','detail'):
        for condition in ('procedural','low','busy'):
            images=tuple(im for im in req.images if im.image_id.startswith(layout+'-') and im.image_id.endswith('-'+condition))
            ids={im.image_id for im in images};subset=replace(req,images=images)
            old=e.score(dict(results=[x for x in base['results'] if x['imageID'] in ids]),subset,names)
            new=e.score(dict(results=[x for x in out if x['imageID'] in ids]),subset,names)
            h.require(all(a==b for i,(a,b) in enumerate(zip(old['perClass'],new['perClass'])) if i!=cid),'non_target_drift')
            results[layout+'/'+condition]=dict(baseline=old,candidate=new)
    h.write(OUT/'report.json',dict(groups=results,crops=len(cr.images),source=h.ref(OUT/'protocol.json'),
        predictions=h.ref(OUT/'predictions.json'),seconds=time.monotonic()-start,modelQualified=False,
        scope='Development crop-context diagnostic; custom composite metrics, not a promoted decoder.'),sealed=True)
    for group,value in results.items():
        print(group,{arm:{k:value[arm]['perClass'][cid][k] for k in ('tp','fp','fn','ap50')} for arm in ('baseline','candidate')},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('prepare','infer','report'))
    globals()[parser.parse_args().mode]()
