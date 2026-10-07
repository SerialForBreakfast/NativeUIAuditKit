"""Compare bounded border and shadow formulas on retained native images."""
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, shift, binary_dilation

import measure_native_focus253 as m


def rectangle(shape,box):
    box=np.asarray(box,float)
    if box.shape!=(4,) or not np.isfinite(box).all() or min(box[2:])<=0:
        raise ValueError('invalid_box')
    y,x=np.indices(shape,dtype=float)
    return (x>=box[0])&(x<box[0]+box[2])&(y>=box[1])&(y<box[1]+box[3])


def rounded(shape,box,radius):
    rectangle(shape,box)
    if not np.isfinite(radius) or radius<0 or radius>min(box[2:])/2:raise ValueError('invalid_radius')
    y,x=np.indices(shape,dtype=float)
    center=np.asarray(box[:2])+np.asarray(box[2:])/2
    qx=np.abs(x-center[0])-(box[2]/2-radius)
    qy=np.abs(y-center[1])-(box[3]/2-radius)
    distance=np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-radius
    return np.clip(.5-distance,0,1)


def shadow_field(alpha,sigma,offset):
    if not np.isfinite([sigma,offset]).all() or sigma<=0 or offset<0:raise ValueError('invalid_shadow')
    return shift(gaussian_filter(alpha,sigma,mode='constant',truncate=3),[offset,0],order=1,mode='constant')


def strength(samples):
    numerator=sum(float(np.sum(x*y)) for x,y in samples)
    denominator=sum(float(np.sum(x*x)) for x,_ in samples)
    return float(np.clip(numerator/denominator,0,.8)) if denominator else 0.


def composite(before,body,alpha,shadow,opacity):
    if not 0<=opacity<=.8:raise ValueError('invalid_opacity')
    darkened=before*(1-opacity*shadow[...,None])
    return np.clip(body*alpha[...,None]+darkened*(1-alpha[...,None]),0,1)


def size_scale(box,increase):
    if not np.isfinite(increase) or increase<0 or min(box[2:])<=0:raise ValueError('invalid_growth')
    return 1+increase/max(box[2:])


def run(artwork=False,geometry_mode='fixed'):
    if geometry_mode not in ('fixed','longest','observed') or (geometry_mode!='fixed' and not artwork):raise ValueError('geometry_mode')
    out=m.OUT/(('edges-r3-artwork'+('-'+geometry_mode if geometry_mode!='fixed' else '')) if artwork else 'edges-r3')
    if out.exists():raise ValueError('output_collision')
    start=time.monotonic();source=m.OUT/'formula-r2/result.json';prior=json.loads(source.read_text())
    member=m.ROOT/'reports/work/TRANSITION-249/artifacts/package/membership.json'
    if hashlib.sha256(member.read_bytes()).hexdigest()!=prior['membershipSHA256']:raise ValueError('changed_membership')
    all_rows=json.loads(member.read_text())['rows']
    if artwork:
        rows=sorted([r for r in all_rows if r['group'] in ('234:recipe-00','234:recipe-03') and r['changed'] and 'original_capture' in r['conditions']],key=lambda r:(r['group'],r['id']))
        if len(rows)!=8 or any(r['role']!='train' for r in rows):raise ValueError('artwork_membership')
        frozen=json.loads((m.OUT/'edges-r3/result.json').read_text())
    else:rows=m.formula_members(all_rows)
    geometry=np.asarray(prior['geometry']);params=prior['selectedParameters'];increase=None
    if geometry_mode=='longest':
        fit_rows=[r for r in all_rows if r['group']=='233:recipe-00' and r['changed'] and 'original_capture' in r['conditions']]
        if len(fit_rows)!=4 or any(r['role']!='train' for r in fit_rows):raise ValueError('growth_fit_membership')
        differences=[]
        for row in fit_rows:
            *_,regions=m.prepare(row,regions=True)
            differences.append(max(regions['after'][2:])-max(regions['before'][2:]))
        increase=float(np.median(differences))
    prepared=[]
    for row in rows:
        (before,after),center,interior,observed,regions=m.prepare(row,regions=True)
        current=geometry.copy()
        if geometry_mode=='longest':current[:4]=[size_scale(regions['before'],increase)]*2+[0,0]
        if geometry_mode=='observed':current[:4]=[observed['scaleX'],observed['scaleY'],*observed['centerShift']]
        x,y=m.coordinates(interior.shape,center)
        raw=m.warp(before,[*current[:4],1,0],center)
        body=m.highlight(raw,x,y,params)
        a=regions['before'];fitted=np.r_[center+current[2:4]-a[2:]*current[:2]/2,a[2:]*current[:2]]
        visible=rectangle(interior.shape,regions['visible'])
        nominal=rectangle(interior.shape,regions['after'])
        border=visible&~interior
        # Exclude the old body. The surrounding frame is a reference, not a clean plate.
        exterior=binary_dilation(nominal,iterations=48)&~binary_dilation(nominal,iterations=3)&~rectangle(interior.shape,a)
        if min(border.sum(),exterior.sum())<100:raise ValueError('insufficient_region_support')
        prepared.append(dict(row=row,before=before,after=after,body=body,box=fitted,visible=visible,
            interior=interior,border=border,exterior=exterior,observed=observed,regions=regions,geometry=current[:4].tolist()))
    out.mkdir()
    fitting=[p for p in prepared if p['row']['group']=='233:recipe-00']
    radius_trials=[]
    for radius in ([] if artwork else [0,8,16,24,32]):
        errors=[]
        for p in fitting:
            alpha=rounded(p['interior'].shape,p['box'],radius)*p['visible']
            predicted=composite(p['before'],p['body'],alpha,np.zeros_like(alpha),0)
            mask=p['border'][::4,::4]
            errors.append(m.metrics(predicted[::4,::4],p['after'][::4,::4],mask)['meanAbsolute255'])
        radius_trials.append(dict(radius=radius,fitMAE=float(np.mean(errors))))
    radius=frozen['selectedRadius'] if artwork else min(radius_trials,key=lambda r:r['fitMAE'])['radius']
    trials=[]
    for sigma in ([] if artwork else [6,12,24,48]):
        for offset in [0,8,16,32]:
            samples=[]
            for p in fitting:
                alpha=rounded(p['interior'].shape,p['box'],radius)*p['visible']
                field=shadow_field(alpha[::4,::4],sigma/4,offset/4)
                mask=p['exterior'][::4,::4];before=p['before'][::4,::4];after=p['after'][::4,::4]
                samples.append(((before*field[...,None])[mask],(before-after)[mask]))
            opacity=strength(samples)
            error=float(np.mean([np.mean(abs(y-opacity*x))*255 for x,y in samples]))
            trials.append(dict(sigma=sigma,offset=offset,opacity=opacity,fitMAE=error))
    chosen=frozen['selectedShadow'] if artwork else min(trials,key=lambda r:r['fitMAE']);results=[]
    for index,p in enumerate(prepared):
        alpha=rounded(p['interior'].shape,p['box'],radius)*p['visible']
        field=shadow_field(alpha,chosen['sigma'],chosen['offset'])
        predicted=composite(p['before'],p['body'],alpha,field,chosen['opacity'])
        no_shadow=composite(p['before'],p['body'],alpha,field,0)
        scores={region:{name:m.metrics(image,p['after'],p[region]) for name,image in
            [('unchanged',p['before']),('bodyOnly',no_shadow),('bodyAndShadow',predicted)]}
            for region in ['interior','border','exterior']}
        unaffected=(alpha==0)&(field==0)
        results.append(dict(id=p['row']['id'],group=p['row']['group'],sourceImages=p['row']['images'],sourceMetadata=p['row']['metadata'],
            scores=scores,clipping=p['regions']['clipping'],geometry=p['geometry'],observedGeometry=p['observed'],
            support={r:int(p[r].sum()) for r in ['interior','border','exterior']},
            unchangedOutsideSupport=bool(np.array_equal(predicted[unaffected],p['before'][unaffected])),
            outsideSupportPixels=int(unaffected.sum()),
            exactRepeat=bool(np.array_equal(predicted,composite(p['before'],p['body'],alpha,field,chosen['opacity'])))))
        if index%4==0:
            panel=np.concatenate([p['before'],p['after'],predicted,np.minimum(abs(predicted-p['after'])*4,1)],axis=1)
            Image.fromarray(np.rint(panel*255).astype('uint8')).save(out/(p['row']['group'].replace(':','-')+'.png'))
    summary={group:{region:{name:float(np.mean([r['scores'][region][name]['meanAbsolute255'] for r in results if r['group']==group]))
        for name in ['unchanged','bodyOnly','bodyAndShadow']} for region in ['interior','border','exterior']}
        for group in sorted({r['group'] for r in results})}
    report=dict(version=1,seconds=time.monotonic()-start,sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),
        geometryMode=geometry_mode,longestDimensionIncrease=increase,usesCheckGeometryForRendering=geometry_mode=='observed',
        parametersFrozen=artwork,frozenParametersSHA256=hashlib.sha256((m.OUT/'edges-r3/result.json').read_bytes()).hexdigest() if artwork else None,
        membershipSHA256=prior['membershipSHA256'],scriptSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        sharedScriptSHA256=hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest(),
        radiusTrials=radius_trials,shadowTrials=trials,selectedRadius=radius,selectedShadow=chosen,results=results,summary=summary,
        trainingEligible=False,scope='Rounded-body approximation and incremental darkening. No clean background or native alpha silhouette. All groups retain training role.')
    (out/'result.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(seconds=report['seconds'],radius=radius,shadow=chosen,summary=summary),indent=2))


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--artwork-check',action='store_true')
    parser.add_argument('--geometry',choices=['fixed','longest','observed'],default='fixed')
    args=parser.parse_args();run(args.artwork_check,args.geometry)
