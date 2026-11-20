"""Verify and project system sheets and row accessory controls on the two bounded iOS list recipes."""
from pathlib import Path
from collections import Counter
import argparse
import cv2
import numpy as np
from PIL import Image
import research_queue as q
from detector_training419 import prepare,TRAIN_ONLY_VERSION
from framework_projection604 import tvos_classes
from milestone_readback604 import decode_batch
from qpacket_import604 import _iou_edge
from template_inputs398 import pin
from verify_ios_native_forms607 import attachments,pixel_hash


def verify(folder,out):
    pairs=attachments(folder)
    assert set(pairs)=={f'{role}-{fw}-{scale}-{stage}' for role in ('dev','train') for fw in ('SwiftUI','UIKit')
                        for scale in (2,3) for stage in ('initial','presented','dismissed')}
    hist=q.load(q.ROOT/'reports/work/REPAIR478/ios-toggles-membership-v2.json')['exclusion']
    inv=q.ROOT/hist['path'];assert q.digest(inv)==hist['sha256']
    inventory=q.load(inv);assert inventory['integrityPassed'] and not inventory['errors']
    used={r['pixelSHA256'] for r in inventory['members']}
    used.update(pixel_hash(p['.png']) for k,p in pairs.items() if k.startswith('dev-'))
    report={};accepted=[];native={};names=tvos_classes()
    membership=dict(version=TRAIN_ONLY_VERSION,trainingAdmitted=True,calibrationPolicy='none-fixed-last-training-diagnostics',names=names)
    for key,p in sorted(pairs.items()):
        role,fw,scale,stage=key.split('-');s=int(scale);png=p['.png'];doc=q.load(p['.json'])
        assert doc['sha']==q.digest(png) and (doc['framework'],doc['scale'],doc['stage'],doc['training'])==(fw,s,stage,role=='train')
        with Image.open(png) as image:rgb=np.asarray(image.convert('RGB'));w,h=image.size
        objs={r['id']:r for r in doc['rows']};assert len(objs)==len(doc['rows'])
        assert set(objs)==({f'{k}{i}' for k in ('a','r') for i in range(6)}|({'sheet'} if stage=='presented' else set()))
        controls=[];unresolved=[];sheet=objs.get('sheet');surface_error=None
        if sheet:
            # Locate the central opaque white sheet by component in its interior.
            mask=(np.min(rgb,axis=2)>=249).astype('uint8')
            _,labels,stats,_=cv2.connectedComponentsWithStats(mask)
            l,t,r,b=sheet['edges'];n=labels[(t+b)//2,(l+r)//2];assert n>0
            surface_error=float(_iou_edge(stats[n][:4],[l,t,r-l,b-t])[1])
            if surface_error>2:unresolved.append('sheet_pixel_edge')
        for i in range(6):
            row=objs['r'+str(i)];acc=objs['a'+str(i)]
            l,t,r,b=row['edges'];al,at,ar,ab=acc['edges']
            assert row['role']=='cell' and acc['role']=='button' and l<=al<ar<=r and t<=at<ab<=b
            assert ar-al==ab-at==44*s
        for i,o in objs.items():
            l,t,r,b=o['edges'];assert 0<=l<r<=w and 0<=t<b<=h
            if sheet and i!='sheet':
                L,T,R,B=sheet['edges']
                if max(l,L)<min(r,R) and max(t,T)<min(b,B):
                    if not (L<=l and T<=t and r<=R and b<=B):unresolved.append(i)
                    continue
            controls.append(dict(id=i,**{'class':o['role']},bounds=[l,t,r-l,b-t]))
        row=dict(id=key,group=f'{role}-{fw}-accessory-list',role='train',trainingEligible=True,labelsComplete=True,
                 controls=controls,image=pin(png),width=w,height=h)
        # Partial sheet underlays cannot be represented by one visible rectangle.
        # Exercise a diagnostic tensor for the sheet alone, preserving the full-frame withholding.
        diag=dict(row,controls=[c for c in controls if c['id']=='sheet']) if unresolved else row
        ds,_=prepare(dict(membership,rows=[diag]),out/'loader'/key)
        boxes=decode_batch(ds,names)[key]['boxes'];err=[]
        for c in diag['controls']:
            m=min((x for x in boxes if x['cls']==c['class']),key=lambda x:_iou_edge(x['box_src_px'],c['bounds'])[1])
            err.append(_iou_edge(m['box_src_px'],c['bounds'])[1]);boxes.remove(m)
        assert not boxes and max(err)<1
        sig=pixel_hash(png)
        if role=='train' and stage=='initial' and not unresolved and sig not in used:accepted.append(row);used.add(sig)
        report[key]=dict(pixelSHA=sig,decoded=len(err),edgePx=max(err),sheetPixelEdge=surface_error,unresolved=unresolved,
                         candidateCounts=dict(Counter(c['class'] for c in controls)),admitted=any(r['id']==key for r in accepted))
        native[key]=doc
    for k,v in native.items():
        if k.endswith('-dismissed'):
            assert v['rows']==native[k.replace('-dismissed','-initial')]['rows']
        if '-2-' in k:
            other=native[k.replace('-2-','-3-')]
            for a,b in zip(v['rows'],other['rows']):
                assert a['id']==b['id'] and max(abs(t/2-u/3) for t,u in zip(a['edges'],b['edges']))<=1
    q.save(out/'readback.json',report);q.save(out/'membership.json',dict(membership,rows=accepted,exclusion=hist))
    print(len(report),len(accepted),Counter(c['class'] for r in accepted for c in r['controls']))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    verify(a.folder.resolve(),a.out.resolve())
