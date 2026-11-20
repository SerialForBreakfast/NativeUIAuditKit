"""Check independent black/white interventions and read clean labels through YOLODataset."""
from material_verify import inspect_case, rgb, prepare, decode_batch, tvos_classes, pin, _iou_edge, TRAIN_ONLY_VERSION, q
import numpy as np
from pathlib import Path
import json

base=q.ROOT/'reports/work/PAR613'
out=base/'verification-final'
out.mkdir(exist_ok=True)
cfg=dict(names=tvos_classes(),version=TRAIN_ONLY_VERSION,trainingAdmitted=True,calibrationPolicy='none-fixed-last-training-diagnostics')
results={}
for fw in ('UIKit','SwiftUI'):
    for alpha in (30,55,100):
        prefix=f'{fw}-system-{alpha}'
        folder=base/(prefix+'-clean-base')
        geometry,old,controls,sheet,surface,_=inspect_case(folder)
        clean=[rgb(folder/f'settled{i}.png').astype('int16') for i in (1,2)]
        evidence={}
        for target in ('r6','a6','r7','a7'):
            l,t,r,b=[round(a*3) for a in geometry[target]]
            h,w=clean[0].shape[:2]
            bbox=[l,t,r-l,b-t]
            repeat=[]
            for seq,img in enumerate(clean,1):
                differences=[]
                probes=[]
                for ink in ('white','black'):
                    path=base/(prefix+'-'+target+'-'+ink)
                    tr=q.load(path/'trace.json')[-1]
                    assert tr['geometry']==geometry and max(abs(a*3-b) for a,b in zip(tr['surface'],(surface[0],surface[1],surface[0]+surface[2],surface[1]+surface[3])))<1
                    probes.append(rgb(path/f'settled{seq}.png').astype('int16'))
                # A full-width strip contains the sheet and both rows. Exclude unrelated system chrome.
                y0=min(round(geometry['r6'][1]*3),round(surface[1]))-100
                y1=round(geometry['r7'][3]*3)+100
                for x1,x2 in [(probes[0],probes[1]),(img,probes[0]),(img,probes[1])]:
                    d=np.abs(x1[y0:y1]-x2[y0:y1]).max(2)
                    cuts=[]
                    for cut in (12,24):
                        ys,xs=np.where(d>=cut)
                        if not len(xs):
                            cuts.append(None)
                            continue
                        measured=[int(xs.min()),int(ys.min()+y0),int(np.ptp(xs)+1),int(np.ptp(ys)+1)]
                        iou,edge=_iou_edge(measured,bbox)
                        cuts.append(dict(box=measured,iou=round(iou,5),edge=edge))
                    differences.append(cuts)
                # Check the unchanged screenshot at 3 positions per interior edge; viewport sides clip rows.
                strength=[]
                for vertical,edge in [(True,l),(True,r),(False,t),(False,b)]:
                    if vertical and edge in (0,w):continue
                    v=[]
                    for frac in (.25,.5,.75):
                        scan=img[round(t+(b-t)*frac)] if vertical else img[:,round(l+(r-l)*frac)]
                        left=np.median(scan[edge-4:edge-1],axis=0)
                        right=np.median(scan[edge+1:edge+4],axis=0)
                        v.append(int(np.max(abs(left-right))))
                    strength.append(v)
                repeat.append(dict(footprints=differences,cleanEdges=strength))
            certified=all(all(c and c['edge']<=1.78 and c['iou']>=.9722 for pair in v['footprints'] for c in pair)
                          and all(min(edge)>=12 for edge in v['cleanEdges']) for v in repeat)
            if certified and not any(o['id']==target for o in controls):
                controls.append(dict(id=target,bounds=bbox,**{'class':'button' if target.startswith('a') else 'cell'}))
            evidence[target]=dict(previousEdgePass=all(old[target]),referencePass=certified,repeat=repeat)
        row=dict(id=prefix,group=f'{fw}-ios611-training-list',role='train',trainingEligible=True,labelsComplete=True,
                 image=pin(folder/'settled2.png'),width=w,height=h,controls=controls)
        ds,_=prepare(dict(cfg,rows=[row]),out/'diagnostic-loader'/prefix)
        read=decode_batch(ds,cfg['names'])[prefix]['boxes']
        errors={}
        for o in controls:
            best=min((p for p in read if p['cls']==o['class']),key=lambda p:_iou_edge(p['box_src_px'],o['bounds'])[1])
            errors[o['id']]=_iou_edge(best['box_src_px'],o['bounds'])[1]
            read.remove(best)
        assert not read and max(errors.values())<1
        missing=sorted(set(geometry)-set(errors))
        results[prefix]=dict(missing=missing,edges=evidence,decoded=errors,surfaceVerified=sheet,image=row['image'],
                             complete=not missing and sheet,role='opaque-control' if alpha==100 else 'matched-development')
        print(prefix,missing,len(errors),flush=True)
q.save(out/'readback.json',results)
