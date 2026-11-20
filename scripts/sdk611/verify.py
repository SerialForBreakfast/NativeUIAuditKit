"""Select observed motion and settled states; measure underlying row and accessory edge contrast."""
from pathlib import Path
import sys,json,math
from collections import Counter
import numpy as np
from inspect_frames import anchored_frames,rgb
import research_queue as q
from detector_training419 import prepare,TRAIN_ONLY_VERSION
from framework_projection604 import tvos_classes
from milestone_readback604 import decode_batch
from template_inputs398 import pin
from qpacket_import604 import _iou_edge
from verify_ios_native_forms607 import pixel_hash

def states(frames):
    initial=[f for f in frames if f['phase']=='initial' and f['surface'] is None]
    done=[f for f in frames if f['phase']=='closing' and f['surface'] is None and f['native'] is None]
    steady=[f for f in frames if 6<=f['relative']<=8.7 and f['phase']=='opening' and f['surface'] and f['nativeRange']
            and max(f['nativeRange'])-min(f['nativeRange'])<.5]
    if len(steady)<2 or not initial or not done:raise ValueError('incomplete_episode')
    settled=steady[len(steady)//2];top=settled['surface'][1]
    assert max(abs(t['surface'][1]-top) for t in steady)<=2
    picks={'initial':initial[-1],'settled':settled,'restored':done[-1]}
    for name,phase in [('arriving','opening'),('departing','closing')]:
        moving=[f for f in frames if f['phase']==phase and f['surface'] and f['surface'][1]>top+8
                and len(f['nativeRange'])>=2 and max(f['nativeRange'])-min(f['nativeRange'])>2]
        if moving:picks[name]=min(moving,key=lambda f:f['surface'][1])
    return picks

def strength(a,b,acc):
    """Median expected edge contrast in green-channel units, measured at native coordinates."""
    x,y,w,h=b;rad=2 if a.shape[1]<900 else 3
    band=lambda yy,xx: float(np.median(a[yy,xx,1]))
    x0=x+round(w*.57);x1=x+round(w*.70)
    if acc:
        yy=slice(y+round(.22*h),y+round(.78*h))
        return min(band(yy,slice(x+rad,x+3*rad))-band(yy,slice(x-3*rad,x-rad)),
                   band(yy,slice(x+w-3*rad,x+w-rad))-band(yy,slice(x+w+rad,x+w+3*rad)))
    xx=slice(x0,x1)
    return min(abs(band(slice(k+rad,k+3*rad),xx)-band(slice(k-3*rad,k-rad),xx)) for k in (y,y+h))

def body_visible(a,b,accessory):
    x,y,w,h=b;rad=2 if a.shape[1]<900 else 3
    if accessory:
        # Verify all four edges. Quarter-width samples avoid the central icon.
        xx=slice(x+w//4-2,x+w//4+2)
        side=strength(a,b,True)
        top=np.median(a[y+rad:y+3*rad,xx,1])-np.median(a[y-3*rad:y-rad,xx,1])
        bottom=np.median(a[y+h-3*rad:y+h-rad,xx,1])-np.median(a[y+h+rad:y+h+3*rad,xx,1])
        return min(side,top,bottom)>=12
    # These native rows span the viewport. Their measured vertical edges must
    # remain visible up to both viewport margins, outside the caption and icon.
    return (x==0 and x+w==a.shape[1] and strength(a,b,False)>=12)


def verify(root,offset=False,matched=False):
    out=root/('matched-final' if matched else 'offset-final' if offset else 'final');out.mkdir(exist_ok=False)
    cfg=dict(names=tvos_classes(),version=TRAIN_ONLY_VERSION,trainingAdmitted=True,calibrationPolicy='none-fixed-last-training-diagnostics')
    hist=q.load(q.ROOT/'reports/work/REPAIR478/ios-toggles-membership-v2.json')['exclusion']
    inv=q.ROOT/hist['path'];assert q.digest(inv)==hist['sha256']
    inventory=q.load(inv);assert inventory['integrityPassed'] and not inventory['errors']
    used={m['pixelSHA256'] for m in inventory['members']};admitted=[];report={};coverage=[]
    if matched:
        for scan in (root/'final/readback.json',root/'offset-final/readback.json'):
            for entry in q.load(scan).values():
                used.add(pixel_hash(q.ROOT/entry['frame']['path']))
    for scale in (2,3):
        base=root/(('matched-' if matched else 'offset-' if offset else 'episodes-')+str(scale))
        for fw in ('UIKit','SwiftUI'):
            for mode,role in ([('opaque','training'),('translucent','training')] if offset else [('opaque','development'),('translucent','development'),('translucent','training')]):
                folder=base/f'{fw}-{mode}-{role}';frames=anchored_frames(folder)
                try:picks=states(frames)
                except ValueError as e:
                    coverage.append([folder.name,scale,str(e)]);continue
                ref=rgb(folder/picks['initial']['png'])
                for stage,f in picks.items():
                    key=f'{fw}-{mode}-{role}-{scale}-{stage}';png=folder/f['png'];a=rgb(png);H,W=a.shape[:2]
                    surface=f['surface'];verdict={};ctrl=[];uncertain=[]
                    for ident,edges in sorted(f['geometry'].items()):
                        l,t,r,b=[round(v*scale) for v in edges];bounds=[l,t,r-l,b-t]
                        assert 0<=l<r<=W and 0<t<b<H
                        contact='exposed'
                        if surface:
                            sx,sy,sw,sh=surface
                            if sy<b and sy+sh>t and min(r,sx+sw)>max(l,sx):
                                contact='behind' if sy<=t and b<=sy+sh and sx<=l and r<=sx+sw else 'crossing'
                        c=strength(a,bounds,ident.startswith('a'));orig=strength(ref,bounds,ident.startswith('a'))
                        visible=body_visible(a,bounds,ident.startswith('a')) and body_visible(ref,bounds,ident.startswith('a'))
                        verdict[ident]=dict(relation=contact,edgeContrast=round(c,1),initialContrast=round(orig,1),
                                              edgeEvidence='resolved' if visible else 'unresolved')
                        if visible:ctrl.append(dict(id=ident,bounds=bounds,**{'class':'button' if ident.startswith('a') else 'cell'}))
                        else:uncertain.append(ident)
                    if surface:ctrl.append(dict(id='sheet',bounds=surface,**{'class':'dialog'}))
                    row=dict(id=key,group=fw+'-'+role+'-'+mode,role='train',trainingEligible=True,labelsComplete=True,
                             controls=ctrl,image=pin(png),width=W,height=H)
                    ds,_=prepare(dict(cfg,rows=[row]),out/'loader'/key);pool=decode_batch(ds,cfg['names'])[key]['boxes'];errors=[]
                    for c in ctrl:
                        match=min((b for b in pool if b['cls']==c['class']),key=lambda b:_iou_edge(c['bounds'],b['box_src_px'])[1])
                        errors.append(_iou_edge(c['bounds'],match['box_src_px'])[1]);pool.remove(match)
                    assert not pool and max(errors)<1
                    digest=pixel_hash(png)
                    # Independent agreement of the settled surface envelope with the presentation layer.
                    surfaceErr=None
                    if f['native'] and surface:
                        l,t,r,b=f['native'];v=[l*scale,t*scale,(r-l)*scale,(b-t)*scale]
                        surfaceErr=round(_iou_edge(surface,v)[1],2)
                    eligible=(mode=='translucent' and role=='training' and stage=='settled' and not uncertain and
                              surfaceErr is not None and surfaceErr<=2 and digest not in used)
                    if eligible and matched:
                        opaque=report[f'{fw}-opaque-training-{scale}-settled']['observations']
                        # An actually covered edge must lose support in the matched opaque control.
                        eligible=any(o['relation']=='behind' and o['edgeEvidence']=='resolved' and
                                     opaque[i]['edgeEvidence']=='unresolved' for i,o in verdict.items())
                    if eligible:admitted.append(row);used.add(digest)
                    if role=='development' or mode=='opaque':used.add(digest)
                    report[key]=dict(frame=pin(png),bracketSeconds=f['end']-f['start'],surface=surface,
                        surfaceNativeErrorPx=surfaceErr,nativeRangePt=f['nativeRange'],observations=verdict,
                        uncertain=uncertain,admitted=eligible,decoded=len(errors),maxLoaderEdgePx=max(errors))
    q.save(out/'readback.json',report);q.save(out/'membership.json',dict(cfg,rows=admitted,exclusion=hist,trainingAdmitted=bool(admitted)))
    q.save(out/'coverage.json',coverage)
    print('states',len(report),'eligible',[(r['id'],len(r['controls'])) for r in admitted],'gaps',coverage)
if __name__=='__main__':verify(Path(sys.argv[1]).resolve(), any(v in sys.argv for v in ('--matched','--offset')), '--matched' in sys.argv)
