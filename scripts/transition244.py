"""Matched resolution and region diagnostics on retained native frames."""
import argparse
from collections import Counter
import math
import time

import numpy as np
from PIL import Image
import transition242 as p
import transition243 as c

h=p.h
OUT=h.ROOT/'reports/work/TRANSITION-244/artifacts'
SIZES=((192,128),(384,256))
NAMES=('whole','region','border')


def boxes(scene):
    """Use nominal artwork bounds without focus state or presentation scale."""
    result={}
    for e in scene['elements']:
        if e.get('is_hidden') or not e.get('is_accessibility_element'):continue
        box=e.get('artwork_geometry',{}).get('pixel_bounds',e.get('pixel_bounds'))
        if box is None:continue
        p.review.require(len(box)==4 and np.isfinite(box).all() and box[2]>0 and box[3]>0,'invalid_box')
        identity=e['element_id']
        p.review.require(identity not in result,'duplicate_element')
        result[identity]=box
    p.review.require(result,'missing_regions')
    return result


def common_boxes(a,b):
    p.review.require(a.keys()==b.keys(),'candidate_membership_changed')
    p.review.require(all(np.allclose(a[k],b[k],rtol=0,atol=1e-6) for k in a),'nominal_geometry_changed')
    return [a[k] for k in sorted(a)]


def rect(box, transform, shape, scale):
    sx,sy,px,py=transform; height,width=shape
    x,y,w,z=box;cx=x+w/2;cy=y+z/2
    x0=max(0,math.floor((cx-w*scale/2)*sx+px));x1=min(width,math.ceil((cx+w*scale/2)*sx+px))
    y0=max(0,math.floor((cy-z*scale/2)*sy+py));y1=min(height,math.ceil((cy+z*scale/2)*sy+py))
    mask=np.zeros(shape,dtype=bool)
    if x1>x0 and y1>y0:mask[y0:y1,x0:x1]=True
    return mask


def scores(a,b,regions,transform):
    delta=np.abs(a-b).mean(axis=0)
    regional=[];border=[];widths=[]
    for box in regions:
        outer=rect(box,transform,delta.shape,1.2)
        inner=rect(box,transform,delta.shape,.8)
        ring=outer & ~inner
        nominal=rect(box,transform,delta.shape,1)
        p.review.require(inner.any() and ring.any() and nominal.any(),'region_too_small')
        regional.append(float(delta[nominal].mean()))
        border.append(float(delta[ring].mean()-delta[inner].mean()))
        widths.append(min(box[2]*transform[0],box[3]*transform[1]))
    return dict(whole=float(delta.mean()),region=max(regional),border=max(border),
                identical=bool(np.array_equal(a,b)),minimumControlWidth=min(widths))


def choose_threshold(values,labels):
    values=np.asarray(values,dtype=float);labels=np.asarray(labels)
    p.review.require(values.ndim==1 and labels.shape==values.shape and np.isfinite(values).all()
                     and set(labels.tolist())=={0,1},'threshold_support')
    unique=np.unique(values)
    thresholds=np.concatenate([[np.nextafter(unique[0],-np.inf)],unique,[np.nextafter(unique[-1],np.inf)]])
    ranked=[]
    for threshold in thresholds:
        pred=values>threshold
        error=.5*(np.mean(pred[labels==0])+np.mean(~pred[labels==1]))
        ranked.append((float(error),float(threshold)))
    error,threshold=min(ranked)
    return dict(threshold=threshold,trainingBalancedError=error,rule='changed_if_greater',selection='training_only')


def counts(values,labels,threshold):
    values=np.asarray(values);labels=np.asarray(labels);pred=values>threshold
    return dict(count=len(labels),changed=int((labels==1).sum()),unchanged=int((labels==0).sum()),
                correct=int((pred==labels).sum()),falseChange=int(((pred==1)&(labels==0)).sum()),
                missedChange=int(((pred==0)&(labels==1)).sum()),abstentions=0)


def run():
    p.review.require(not OUT.exists(),'output_collision')
    start=time.monotonic()
    old,oldrows,x=p.load_inputs()
    new=h.read(c.OUT/'inputs.json')
    p.review.require(new['seal']==h.digest({k:v for k,v in new.items() if k!='seal'}),'input_seal')
    admission=h.read(c.OUT/'admission.json')
    p.review.require(admission['approved'] and admission['inputs']==h.ref(c.OUT/'inputs.json'),'admission')
    nx=np.load(h.checked(h.ROOT,new['tensor'],512*1024**2),allow_pickle=False)
    rows=oldrows+new['rows'];p.check_roles(rows)
    p.review.require(len(x)==len(oldrows) and len(nx)==len(new['rows']),'tensor_membership')
    encoded_by_hash={}
    for row,value in zip(rows,list(x)+list(nx)):
        p.review.require(p.sha(value.tobytes())==row['tensorSHA256'],'cached_row_changed')
        for ref,v in zip(row['images'],(value[:3],value[3:])):
            encoded_by_hash[ref['sha256']]=p.sha(v.tobytes())
    del x,nx
    images={};metadata={};observations={}
    for row in rows:
        for image_ref,meta_ref in zip(row['images'],row['metadata']):
            path=h.checked(h.ROOT,image_ref)
            key=image_ref['sha256']
            if key not in images:
                with Image.open(path) as im:
                    rgb=im.convert('RGB')
                    images[key]={size:p.encoded(rgb,rgb,size) for size in SIZES}
                p.review.require(p.sha(images[key][SIZES[0]][0][:3].tobytes())==encoded_by_hash[key],'encoder_parity')
            mk=meta_ref['sha256']
            if mk not in metadata:
                mp=h.checked(h.ROOT,meta_ref);m=h.read(mp)
                p.review.pair(mp.parent,mp.name,expected_version=m['schema_version']);metadata[mk]=m
            m=metadata[mk]
            matches=[m[scene] for endpoint,scene in [('unfocused','baseline_scene'),('focused','focused_scene')]
                     if m[endpoint+'_sha256']==key]
            p.review.require(matches,'missing_scene_for_image')
            for scene in matches:
                p.label(scene,scene)
                state=(scene['focused_element_id'],boxes(scene))
                if key in observations:
                    p.review.require(observations[key][0]==state[0],'image_focus_conflict')
                    common_boxes(observations[key][1],state[1])
                observations[key]=state
    results=[];excluded=[]
    for row in rows:
        ka,kb=[r['sha256'] for r in row['images']]
        sa,sb=observations[ka],observations[kb]
        p.review.require(int(sa[0]!=sb[0])==row['changed'],'label_changed')
        try:regions=common_boxes(sa[1],sb[1])
        except ValueError as error:
            excluded.append(dict(id=row['id'],role=row['role'],source=row['source'],reason=str(error)))
            continue
        for size in SIZES:
            a,transform=images[ka][size];b,tb=images[kb][size]
            p.review.require(transform==tb,'frame_geometry_changed')
            results.append(dict(id=row['id'],role=row['role'],source=row['source'],group=row['group'],
                    changed=row['changed'],conditions=row['conditions'],size=list(size),
                    **scores(a[:3],b[:3],regions,transform)))
    del images
    comparisons=[]
    for size in SIZES:
        subset=[r for r in results if r['size']==list(size)]
        train=[r for r in subset if r['role']=='train']
        for name in NAMES:
            chosen=choose_threshold([r[name] for r in train],[r['changed'] for r in train])
            groups={role:[r for r in subset if r['role']==role] for role in ('train','reserved','development')}
            groups.update({cond:[r for r in subset if cond in r['conditions']]
                           for cond in ('original_capture','identity','content_contrast','artwork_contrast')})
            groups['artwork_unchanged']=[r for r in groups['artwork_contrast'] if not r['changed']]
            comparisons.append(dict(size=list(size),score=name,**chosen,
                regions='none' if name=='whole' else 'native_nominal_all_controls_oracle',
                groups={k:counts([r[name] for r in group],[r['changed'] for r in group],chosen['threshold'])
                        for k,group in groups.items()}))
    OUT.mkdir(parents=True)
    report=dict(version='transition244-v1',source=h.ref(__file__),encoder=h.ref(h.ROOT/'scripts/diagnose_signal95.py'),
        inputs=[h.ref(p.OUT/'inputs.json'),h.ref(c.OUT/'inputs.json')],results=results,comparisons=comparisons,
        rows=len(rows),scoredRows=len(results)//len(SIZES),excluded=excluded,
        uniqueImages=len(encoded_by_hash),parity192=True,seconds=time.monotonic()-start,
        roleCounts=dict(Counter(r['role'] for r in rows)),independentEvaluation=False,productionEligible=False,
        limitation='Native nominal regions are privileged. Forced decisions differ from abstaining model decisions.')
    h.write(OUT/'result.json',report,sealed=True)
    for r in comparisons:print(r,flush=True)
    print('seconds',report['seconds'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.parse_args();run()
