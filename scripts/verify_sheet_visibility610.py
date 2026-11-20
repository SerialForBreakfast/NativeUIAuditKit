"""Qualify original native frames. White and black calibration images never enter the dataset."""
from pathlib import Path
import argparse
from collections import Counter
import numpy as np
from PIL import Image
import research_queue as q
from detector_training419 import prepare,TRAIN_ONLY_VERSION
from framework_projection604 import tvos_classes
from milestone_readback604 import decode_batch
from template_inputs398 import pin
from qpacket_import604 import _iou_edge
from ios_sheet_visibility610 import visible_body,footprint
from verify_ios_native_forms607 import attachments,pixel_hash


def pixels(p):
    with Image.open(p) as im:return np.asarray(im.convert('RGB'))


def run(folder,out):
    files=attachments(folder);names=tvos_classes()
    hist=q.load(q.ROOT/'reports/work/REPAIR478/ios-toggles-membership-v2.json')['exclusion']
    inv=q.ROOT/hist['path'];assert q.digest(inv)==hist['sha256']
    data=q.load(inv);assert data['integrityPassed'] and not data['errors']
    reserved={r['pixelSHA256'] for r in data['members']}
    for p in (q.ROOT/'reports/work/IOS609/final-frames').glob('*.png'):reserved.add(pixel_hash(p))
    reserved.update(pixel_hash(v['.png']) for k,v in files.items() if k.startswith('dev-') or k.endswith(('-white','-black')))
    base=dict(version=TRAIN_ONLY_VERSION,trainingAdmitted=True,calibrationPolicy='none-fixed-last-training-diagnostics',names=names)
    report={};accepted=[];observed={}
    for key,p in sorted(files.items()):
        if '.json' not in p:continue
        role,fw,ss,stage=key.split('-');s=int(ss);doc=q.load(p['.json']);png=p['.png'];rgb=pixels(png);h,w=rgb.shape[:2]
        assert q.digest(png)==doc['sha'] and (fw,s,stage,role=='train')==(doc['framework'],doc['scale'],doc['stage'],doc['training'])
        objects={r['id']:r for r in doc['rows']}
        assert len(objects)==len(doc['rows']) and set(objects)=={f'{k}{i}' for k in ('a','r') for i in range(6)}|({'sheet'} if stage=='presented' else set())
        for i in range(6):
            row=objects[f'r{i}'];a=objects[f'a{i}'];assert (row['role'],a['role'])==('cell','button')
            l,t,r,b=row['edges'];x,y,R,B=a['edges'];assert l<=x<R<=r and t<=y<B<=b and R-x==B-y==44*s
        masks=[np.zeros((h,w),dtype=bool)]
        if stage=='presented':
            assert objects['sheet']['role']=='dialog'
            white,black=[pixels(files[key+'-'+v]['.png']) for v in ('white','black')]
            masks=[footprint(white,black,level) for level in (128,96,160)]
            x,y=np.where(masks[0])[1],np.where(masks[0])[0]
            painted=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
            assert max(abs(a-b) for a,b in zip(painted,objects['sheet']['edges']))<=2
            # Check the clean original at the center of the surface and outside its bounds.
            l,t,r,b=objects['sheet']['edges'];assert rgb[(t+b)//2,(l+r)//2].min()>=249
            outside=np.ones((h,w),dtype=bool);outside[t:b,l:r]=False
            assert np.mean(np.max(np.abs(rgb.astype('int16')-black.astype('int16')),axis=2)[outside]>24)<0.01
        controls=[];decisions={}
        for i,o in objects.items():
            if i=='sheet':
                l,t,r,b=painted;v=dict(disposition='visible',bounds=[l,t,r-l,b-t])
            else:
                v=visible_body(o['edges'],masks[0])
                for alternative in masks[1:]:
                    v2=visible_body(o['edges'],alternative)
                    assert v2['disposition']==v['disposition']
                    if 'bounds' in v:assert _iou_edge(v2['bounds'],v['bounds'])[1]<=1
            decisions[i]=v
            if 'bounds' in v:controls.append(dict(id=i,bounds=v['bounds'],**{'class':o['role']}))
        row=dict(id=key,group=f'{role}-{fw}-sheet610',role='train',trainingEligible=True,labelsComplete=True,image=pin(png),controls=controls,width=w,height=h)
        ds,_=prepare(dict(base,rows=[row]),out/'loader'/key)
        boxes=decode_batch(ds,names)[key]['boxes'];errors=[]
        for c in controls:
            item=min((b for b in boxes if b['cls']==c['class']),key=lambda b:_iou_edge(c['bounds'],b['box_src_px'])[1])
            errors.append(_iou_edge(c['bounds'],item['box_src_px'])[1]);boxes.remove(item)
        assert not boxes and max(errors)<1
        sig=pixel_hash(png);admit=(role=='train' and stage=='presented' and sig not in reserved
               and all(v['disposition']!='fragmented_context' for v in decisions.values()))
        if admit:accepted.append(row);reserved.add(sig)
        observed[key]=objects
        report[key]=dict(decisions=decisions,edgePx=max(errors),decoded=len(controls),admitted=admit,sha256=doc['sha'])
    assert len(report)==24
    for key,objs in observed.items():
        if key.endswith('dismissed'):assert objs==observed[key.replace('dismissed','initial')]
        if '-2-' in key:
            other=report[key.replace('-2-','-3-')]['decisions']
            for i,v in report[key]['decisions'].items():
                assert other[i]['disposition']==v['disposition']
                if 'bounds' in v:assert _iou_edge([a/2 for a in v['bounds']],[b/3 for b in other[i]['bounds']])[1]<=1
    q.save(out/'readback.json',report);q.save(out/'membership.json',dict(base,rows=accepted,exclusion=hist,taxonomyPolicy='ios-sheet-visible-connected-v1'))
    print(Counter(c['class'] for r in accepted for c in r['controls']))
    print(Counter(o['disposition'] for k,r in report.items() if k.endswith('presented') for o in r['decisions'].values()))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    run(a.folder.resolve(),a.output.resolve())
