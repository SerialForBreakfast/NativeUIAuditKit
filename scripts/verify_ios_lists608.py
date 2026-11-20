"""Compare native row observations, independent PNG landmarks and decoded labels."""
import argparse, copy
from collections import defaultdict
from pathlib import Path
import numpy as np
from PIL import Image
import research_queue as q
from detector_training419 import prepare, TRAIN_ONLY_VERSION
from framework_projection604 import tvos_classes
from ios_list_projection608 import project
from milestone_readback604 import decode_batch
from qpacket_import604 import _iou_edge
from template_inputs398 import pin
from verify_ios_native_forms607 import attachments, pixel_hash


def verify(folder, out):
    pairs=attachments(folder)
    expected={f'{role}-{fw}-{s}-{stage}' for role in ('train','cal') for fw in ('UIKit','SwiftUI')
              for s in (2,3) for stage in ('initial','scroll','covered','restored')}
    q.require(set(pairs)==expected,'row_missing_capture')
    report={}; eligible=[]; results={}
    hist=q.load(q.ROOT/'reports/work/REPAIR478/ios-toggles-membership-v2.json')['exclusion']
    inv=q.ROOT/hist['path'];assert q.digest(inv)==hist['sha256']
    baseline=q.load(inv);assert baseline['integrityPassed'] and not baseline['errors']
    reserved={r['pixelSHA256'] for r in baseline['members']}
    reserved.update(pixel_hash(p['.png']) for key,p in pairs.items() if key.startswith('cal-'))
    for key,p in sorted(pairs.items()):
        role,framework,scale,stage=key.split('-');s=int(scale);train=role=='train'
        doc=q.load(p['.json']);png=p['.png'];ct,owners=project(doc,png)
        assert (doc['framework'],doc['scale'],doc['stage'],doc['training'])==(framework,s,stage,train)
        # Independent recipe key: viewport, scroll stops and row order in original points.
        x,y,w,h,rh,offset,cover=(14,32,292,215,61,27,96) if train else (20,40,280,200,52,19,89)
        shift=0 if stage=='initial' else offset
        assert doc['offset']==shift and doc['viewport']==[s*x,s*y,s*(x+w),s*(y+h)]
        first=y+(cover if stage=='covered' else 0)
        expected_boxes={}
        with Image.open(png) as im: pixels=np.array(im.convert('RGB'),dtype=int)
        for i in range(12):
            top=max(first,y+i*rh-shift);bottom=min(y+h,y+(i+1)*rh-shift)
            if bottom<=top: continue
            expected_boxes[f'row-{i}']=[s*x,s*top,s*w,s*(bottom-top)]
        assert {c['id']:c['bounds'] for c in ct}==expected_boxes,(key,ct,expected_boxes)
        tests=[]
        for change,reason in [('owner','row_owner'),('duplicate','row_duplicate'),('scene','row_image_binding')]:
            bad=copy.deepcopy(doc)
            if change=='owner': bad['rows'][0]['captionOwner']=-1
            if change=='duplicate': bad['rows'].append(bad['rows'][0])
            if change=='scene': bad['sha256']='0'*64
            try: project(bad,png)
            except ValueError as err:
                assert str(err)==reason
                tests.append(change)
            else: raise AssertionError(change)
        if stage=='covered':
            bad=copy.deepcopy(doc);bad['stage']='scroll';bad['overlay']=[]
            stale,_=project(bad,png)
            assert {c['id']:c['bounds'] for c in stale}!=expected_boxes
            tests.append('opaque_cover_omitted')
        if stage=='scroll':
            bad=copy.deepcopy(doc)
            for row_obs in bad['rows']:
                for field in ('edges','caption'):
                    for edge in (1,3): row_obs[field][edge]+=shift*s
            stale,_=project(bad,png)
            assert {c['id']:c['bounds'] for c in stale}!=expected_boxes
            tests.append('stale_scroll_geometry')
        # Scan source pixels independently at the row interiors. Find each full painted span.
        # For the grayscale training layouts use connected components to separate repeated colors.
        import cv2
        for c in ct:
            idx=int(c['id'][4:])
            # The PNG carries a display profile. Sample its interior color using the
            # independent recipe key, then find the entire component on the full PNG.
            l,t,width,height=expected_boxes[c['id']]
            color=pixels[t+height//2,l+3*width//4]
            mask=(np.max(abs(pixels-color),axis=2)<=2).astype('uint8')
            _,_,stats,_=cv2.connectedComponentsWithStats(mask)
            b=c['bounds']; candidates=[v[:4].tolist() for v in stats[1:] if v[4]>50]
            assert candidates and min(_iou_edge(v,b)[1] for v in candidates)<=1,(key,idx,b,candidates)
        row=dict(id=key,group=f'{role}-{framework}',role='train',trainingEligible=True,labelsComplete=True,image=pin(png),
                 width=pixels.shape[1],height=pixels.shape[0],controls=ct)
        names=tvos_classes()
        membership=dict(version=TRAIN_ONLY_VERSION,trainingAdmitted=True,calibrationPolicy='none-fixed-last-training-diagnostics',names=names)
        ds,_=prepare(dict(membership,rows=[row]),out/'loader'/key)
        pool=decode_batch(ds,names)[key]['boxes'];errors=[]
        for c in ct:
            best=min((v for v in pool if v['cls']=='cell'),key=lambda v:_iou_edge(v['box_src_px'],c['bounds'])[1])
            errors.append(_iou_edge(best['box_src_px'],c['bounds'])[1]);pool.remove(best)
        assert not pool and max(errors)<=1
        signature=pixel_hash(png)
        add=train and stage!='restored' and signature not in reserved
        if add: eligible.append(row);reserved.add(signature)
        results[key]=(signature,expected_boxes)
        report[key]=dict(labels=len(ct),maxEdgePx=max(errors),ownership=owners,rejectedMutations=tests,eligible=add,sidecar=pin(p['.json']))
    for key,(pixels,boxes) in results.items():
        if key.endswith('-restored'):
            prior=results[key.replace('-restored','-scroll')]
            assert boxes==prior[1]
            report[key]['identicalRestoredPixels']=pixels==prior[0]
    q.save(out/'readback.json',report);q.save(out/'membership.json',dict(membership,rows=eligible,exclusion=hist))
    print(len(report),len(eligible),sum(len(r['controls']) for r in eligible))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    verify(a.folder.resolve(),a.out.resolve())
