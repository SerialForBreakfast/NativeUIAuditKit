"""Matched fixed-device settled material audit. Reuse IOS611's >=12 control-edge criterion."""
import numpy as np
import json
from pathlib import Path
from collections import Counter
from material_capture import conditions
from verify import strength
from inspect_frames import sheet_pixels
from verify import (rgb,body_visible,prepare,decode_batch,tvos_classes,pixel_hash,pin,_iou_edge,
                    TRAIN_ONLY_VERSION,q)


def surface_edges(image,native):
    """Locate each boundary on 3 interior scanlines within ±8 px of the native proposal."""
    x,y,w,h=native
    found=[]
    for vertical,edge in [(True,x),(False,y),(True,x+w),(False,y+h)]:
        offsets=[]
        for fraction in (.35,.5,.65):
            scan=(image[round(y+h*fraction)] if vertical else image[:,round(x+w*fraction)]).astype(int)
            start=round(edge)-8
            jumps=np.abs(np.diff(scan[start:start+17],axis=0)).max(axis=1)
            if jumps.max()<12:return None
            offsets.append(start+1+int(np.argmax(jumps)))
        if max(offsets)-min(offsets)>2:return None
        found.append(int(np.median(offsets)))
    l,t,r,b=found
    return [l,t,r-l,b-t]


def inspect_case(folder):
    trace=q.load(folder/'trace.json')
    stable=[v for v in trace if v.get('surface') and v['phase']=='opening']
    assert stable and trace[-1]['scale']==3 and len(trace[-1]['geometry'])==16
    last=stable[-1];near=[v for v in stable if v['t']>=last['t']-.25]
    assert len(near)>=3 and np.ptp([v['surface'][1] for v in near])<.5
    geometry=last['geometry'];initial=rgb(folder/'initial.png');render=[rgb(folder/f'settled{i}.png') for i in (1,2)]
    verdict={};boxes=[]
    for i,(l,t,r,b) in sorted(geometry.items()):
        l,t,r,b=[int(round(z*3)) for z in (l,t,r,b)];box=[l,t,r-l,b-t]
        # Warm-launch screenshot may precede a populated app. Verify baseline independently below.
        scores=[bool(body_visible(a,box,i.startswith('a'))) for a in render]
        verdict[i]=scores
        if all(scores):boxes.append(dict(id=i,bounds=box,**{'class':'cell' if i[0]=='r' else 'button'}))
    times=q.load(folder/'times.json')
    assert times['settled1'][0]>=last['t'] and times['settled2'][1]-trace[0]['t']<7.5
    l,t,r,b=last['surface'];native=[3*l,3*t,3*(r-l),3*(b-t)]
    surfaces=[surface_edges(a,native) for a in render]
    surfaceOK=all(v and _iou_edge(v,native)[1]<=2 for v in surfaces)
    if surfaceOK:boxes.append(dict(id='sheet',bounds=surfaces[-1],**{'class':'dialog'}))
    return geometry,verdict,boxes,surfaceOK,native,surfaces


def run():
    base=q.ROOT/'reports/work/IOS612';out=base/'verification';out.mkdir()
    hist=q.load(q.ROOT/'reports/work/REPAIR478/ios-toggles-membership-v2.json')['exclusion'];assert q.digest(q.ROOT/hist['path'])==hist['sha256']
    inventory=q.load(q.ROOT/hist['path']);assert inventory['integrityPassed'] and not inventory['errors']
    used={r['pixelSHA256'] for r in inventory['members']}
    previous=q.ROOT/'reports/work/IOS611/matched-final/readback.json'
    used.update(pixel_hash(q.ROOT/r['frame']['path']) for r in q.load(previous).values())
    cfg=dict(names=tvos_classes(),version=TRAIN_ONLY_VERSION,trainingAdmitted=True,calibrationPolicy='none-fixed-last-training-diagnostics')
    results={};admitted=[];layouts={}
    for m,a in conditions+[('system',35),('system',40),('system',45),('system',50),('clear',30),('thin',30),('thick',30)]:
        for fw in ('UIKit','SwiftUI'):
            name=f'{fw}-{m}-{a}';folder=base/name
            geom,verdict,ctrl,surfaceOK,native,surfaces=inspect_case(folder)
            assert layouts.setdefault(fw,geom)==geom
            ref=q.load(previous)[f'{fw}-translucent-training-3-initial']
            assert all(o['edgeEvidence']=='resolved' for o in ref['observations'].values())
            # Require identical control bounds to those in the original IOS611 layout.
            original=base.parent/'IOS611/matched-3'/f'{fw}-translucent-training'/'trace.json'
            originalGeom=next(v['geometry'] for v in q.load(original) if len(v['geometry'])==16)
            assert geom==originalGeom
            img=folder/'settled2.png';H,W=rgb(img).shape[:2]
            assert (W,H)==(1206,2622)
            row=dict(id=name,group=f'{fw}-ios611-training-list',role='train',trainingEligible=True,labelsComplete=True,image=pin(img),controls=ctrl,width=W,height=H)
            errors=[]
            if ctrl:
                ds,_=prepare(dict(cfg,rows=[row]),out/'loader'/name);pool=decode_batch(ds,cfg['names'])[name]['boxes']
                for c in ctrl:
                    best=min((v for v in pool if v['cls']==c['class']),key=lambda v:_iou_edge(c['bounds'],v['box_src_px'])[1])
                    errors.append(_iou_edge(c['bounds'],best['box_src_px'])[1]);pool.remove(best)
                assert not pool and max(errors)<1
            sig=pixel_hash(img);eligible=surfaceOK and len(ctrl)==17 and sig not in used and a!=100
            if eligible:admitted.append(row);used.add(sig)
            results[name]=dict(geometry=geom,edges=verdict,unresolved=[i for i,v in verdict.items() if not all(v)],surfaceVerified=surfaceOK,
                               nativeSurface=native,painted=surfaces,decoded=len(ctrl),eligible=eligible,frame=pin(img),maxEdgePx=max(errors,default=None))
    q.save(out/'readback.json',results);q.save(out/'membership.json',dict(cfg,rows=admitted,trainingAdmitted=bool(admitted),exclusion=hist))
    for k,v in results.items():print(k,v['decoded'],v['unresolved'],v['surfaceVerified'],v['eligible'])
if __name__=='__main__':run()
