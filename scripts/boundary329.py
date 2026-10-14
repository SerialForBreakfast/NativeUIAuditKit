"""Measure native boundaries before training an added image feature."""
import argparse
from collections import Counter
from pathlib import Path
import time
import numpy as np
from PIL import Image
import regions313 as r
from detail307 import source_window

b=r.b; t=r.t; OUT=b.ROOT/'reports/work/FOCUS-329'


def scenes_for(row):
    """Match observed scenes to exact image hashes."""
    ids=row['observedIDs']; scenes=[]
    b.require(len(ids)==2 and len(row['metadata'])==2,'endpoint_count')
    for n,(image,meta) in enumerate(zip(row['images'],row['metadata'])):
        doc=b.read(b.checked(meta))
        matches=[doc[key] for prefix,key in [('unfocused','baseline_scene'),('focused','focused_scene')]
                 if doc.get(prefix+'_sha256')==image['sha256'] and key in doc]
        if not matches:return None,'missing_scene'
        b.require(all(v==matches[0] for v in matches),'conflicting_scene')
        b.require(matches[0].get('focused_element_id')==ids[n],'focus_identity')
        scenes.append(matches[0])
    return scenes,None


def bodies(row,scenes):
    selected=[]; clipping=[]
    # Use every measured body. Focus changes cannot change the mask population.
    populations=[]
    for scene in scenes:
        populations.append({v['element_id'] for v in scene.get('elements',[])
            if v.get('rendered_body_geometry',{}).get('availability')=='measured'})
    if populations[0]!=populations[1]:return None,[],'body_population_changed'
    if not populations[0]:return None,[],'missing_body'
    for focus in sorted(populations[0]):
        boxes=[]
        for scene in scenes:
            elements=[v for v in scene.get('elements',[]) if v.get('element_id')==focus]
            if len(elements)!=1:return None,[],'missing_element'
            g=elements[0].get('rendered_body_geometry',{})
            if g.get('availability')!='measured' or g.get('coordinate_space')!='image_top_left_pixels':
                return None,[],'missing_body'
            box=g.get('visible_pixel_bounds')
            b.require(box is not None and len(box)==4 and np.isfinite(box).all() and min(box[2:])>0,'invalid_body')
            boxes.append(box); clipping.append(g.get('clipping','not_reported'))
        selected.append(boxes)
    return selected,clipping,None


def fill(mask,box):
    x,y,w,h=box; height,width=mask.shape
    x0=max(0,min(width,int(np.ceil(x))));y0=max(0,min(height,int(np.ceil(y))))
    x1=max(0,min(width,int(np.floor(x+w))));y1=max(0,min(height,int(np.floor(y+h))))
    if x1>x0 and y1>y0:mask[y0:y1,x0:x1]=True


def masks(shape,paired,band=35):
    inner=np.zeros(shape,bool); boundary=np.zeros(shape,bool)
    for first,second in paired:
        x=max(first[0],second[0]);y=max(first[1],second[1])
        right=min(first[0]+first[2],second[0]+second[2]);bottom=min(first[1]+first[3],second[1]+second[3])
        fill(inner,(x,y,max(0,right-x),max(0,bottom-y)))
        x=min(first[0],second[0])-band;y=min(first[1],second[1])-band
        right=max(first[0]+first[2],second[0]+second[2])+band
        bottom=max(first[1]+first[3],second[1]+second[3])+band
        fill(boundary,(x,y,right-x,bottom-y))
    boundary &= ~inner
    return inner,boundary


def measure(delta,inner,band,proposal):
    total=float(delta.sum(dtype=np.float64));edge=float(delta[band].sum(dtype=np.float64))
    inside=float(delta[inner].mean()) if inner.any() else None
    outside=float(delta[band].mean()) if band.any() else None
    return dict(totalChange=total,interiorMean=inside,boundaryMean=outside,
        boundaryFraction=edge/total if total else None,
        boundaryToInterior=outside/(outside+inside) if outside is not None and inside is not None and outside+inside else None,
        proposalBoundaryCoverage=float(delta[band&proposal].sum(dtype=np.float64))/edge if edge else None,
        proposalBoundaryPurity=float(delta[band&proposal].sum(dtype=np.float64))/float(delta[proposal].sum(dtype=np.float64)) if delta[proposal].sum() else None)


def edge_features(details):
    """Measure image gradients without reading labels or body boxes."""
    b.require(details.ndim==4 and details.shape[1:]==(12,128,192),'detail_shape')
    b.require(bool(t.isfinite(details).all()),'nonfinite_detail')
    features=[]
    for j in (0,6):
        x=details[:,j:j+6];before=x[:,:3];after=x[:,3:]
        # Gradient magnitudes keep edges separate from signed brightness change.
        gx=(after[:,:,:,1:]-after[:,:,:,:-1]).abs()-(before[:,:,:,1:]-before[:,:,:,:-1]).abs()
        gy=(after[:,:,1:,:]-after[:,:,:-1,:]).abs()-(before[:,:,1:,:]-before[:,:,:-1,:]).abs()
        delta=(after-before).abs().mean((1,2,3))
        edge=(gx.abs().mean((1,2,3))+gy.abs().mean((1,2,3)))/2
        features.append(t.stack((delta,edge,edge/(delta+1e-6)),1))
    return t.stack(features).mean(0)


def auc(values,labels):
    positive=np.array([v for v,l in zip(values,labels) if l==1],float)
    negative=np.array([v for v,l in zip(values,labels) if l==0],float)
    if not len(positive) or not len(negative):return None
    return float(((positive[:,None]>negative).sum()+.5*(positive[:,None]==negative).sum())/(len(positive)*len(negative)))


def summary(rows):
    measured=[v for v in rows if v['status']=='measured'];result={}
    for name,subset in [('all',measured),('content_contrast',[v for v in measured if 'content_contrast' in v['conditions']]),
                        ('nonzero',[v for v in measured if v['totalChange']>0])]:
        metrics={}
        for key in ('boundaryMean','interiorMean','boundaryFraction','boundaryToInterior','imageEdge','imageEdgeRatio'):
            valid=[v for v in subset if v[key] is not None]
            metrics[key]=dict(rows=len(valid),auc=auc([v[key] for v in valid],[v['changed'] for v in valid]),
                byLabel={str(label):dict(rows=len(z),median=float(np.median(z)) if z else None,
                    minimum=min(z) if z else None,maximum=max(z) if z else None)
                    for label in (0,1) for z in [[v[key] for v in valid if v['changed']==label]]})
        result[name]=dict(rows=len(subset),groups=len({v['group'] for v in subset}),metrics=metrics)
    return result


def run():
    b.require(not (OUT/'audit.json').exists(),'output_collision');t.set_num_threads(2);start=time.monotonic()
    membership=b.read(b.PACKAGE/'membership.json');values=np.load(b.PACKAGE/'native.npy',allow_pickle=False,mmap_mode='r')
    b.write(OUT/'registration.json',dict(version='boundary329-audit-v2',runner=b.ref(Path(__file__)),
        membership=b.ref(b.PACKAGE/'membership.json'),encoded=b.ref(b.PACKAGE/'native.npy'),
        geometryHelper=b.ref(Path(r.s.__file__)),proposals=b.ref(Path(r.__file__)),
        role='train',bandPixels=35,bodySelection='All measured controls, with identical ID populations in both frames.',rows=sum(v['role']=='train' for v in membership['rows']),
        trainingStarted=False,productionEligible=False,diagnosticOnly=True))
    records=[]
    for i,row in enumerate(membership['rows']):
        if row['role']!='train':continue
        record={k:row[k] for k in ('id','group','role','changed','conditions')};record['index']=i
        scenes,error=scenes_for(row)
        paired,clipping,error=bodies(row,scenes) if not error else (None,[],error)
        if error:records.append(dict(record,status=error));continue
        frames=[]
        for pin in row['images']:
            with Image.open(b.checked(pin)) as image:frames.append(image.convert('RGB'))
        b.require(frames[0].size==frames[1].size,'image_size')
        b.require(np.array_equal(r.s.encoded(*frames,(192,128))[0],values[i]),'encoding_parity')
        delta=np.abs(np.asarray(frames[1],dtype=np.float32)/255-np.asarray(frames[0],dtype=np.float32)/255).mean(2)
        inner,band=masks(delta.shape,paired)
        proposal=np.zeros(delta.shape,bool);windows=r.windows(t.from_numpy(np.array(values[i:i+1])))[0]
        for x,y in windows:
            x0,y0,x1,y1=source_window((x,y,x+32,y+32),frames[0].size)
            fill(proposal,(x0,y0,x1-x0,y1-y0))
        details,_=r.prepare(np.array(values[i:i+1]),[row],2)
        with t.inference_mode():feature=edge_features(t.from_numpy(details))[0].tolist()
        records.append(dict(record,status='measured',clipping=clipping,pairedBodies=paired,windows=windows,
            **measure(delta,inner,band,proposal),imageAbsolute=feature[0],imageEdge=feature[1],imageEdgeRatio=feature[2]))
        if len(records)%50==0:print('Measured',len(records),flush=True)
    b.write(OUT/'audit.json',dict(registration=b.ref(OUT/'registration.json'),rows=records,summary=summary(records),
        statusCounts=dict(Counter(v['status'] for v in records)),seconds=time.monotonic()-start,
        limitation='Training-only, correlated native-derived pairs. Known boxes are diagnostic inputs, not deployable inputs.'))
    print(summary(records),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args();run()
