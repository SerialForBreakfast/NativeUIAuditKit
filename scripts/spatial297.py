"""Measure region proposals and fixed score interventions on retained inputs."""
import argparse
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image
import condition291 as c
import transition244 as geometry

base=c.base
OUT=base.ROOT/'reports/work/TRANSITION-297'


def region_mask(boxes):
    mask=np.zeros((128,192),bool)
    for box in boxes:
        base.require(len(box)==4 and np.isfinite(box).all() and min(box[2:])>0,'invalid_box')
        mask |= geometry.rect(box,(1,1,0,0),mask.shape,1)
    return mask


def control_mask(mask, seed):
    rng=np.random.default_rng(seed)
    moved=np.roll(mask,(int(rng.integers(1,128)),int(rng.integers(1,192))),axis=(0,1))
    base.require(moved.sum()==mask.sum(),'control_area')
    return moved


def intervene(value, mask, keep):
    result=value.copy()
    removed=~mask if keep else mask
    result[3:,removed]=result[:3,removed]
    return result


def run():
    base.require(not OUT.exists(),'output_collision')
    base.torch.set_num_threads(2)
    manifest=base.worker.read_package(base.PACKAGE)
    membership=base.read(base.PACKAGE/'membership.json')
    native=np.load(base.PACKAGE/'native.npy',mmap_mode='r',allow_pickle=False)
    models={};cached={};pins={}
    for name,folder in [('DTM083','TRANSITION-291'),('DTM085','TRANSITION-292')]:
        path=base.ROOT/f'reports/work/{folder}/{name}'
        result=base.read(path/'result.json')
        models[name]=c.model.load_candidate(base.checked(result['model']))
        cached[name]=base.read(path/'evaluation.json')
        pins[name]=dict(model=result['model'],evaluation=base.ref(path/'evaluation.json'))
    # Freeze all native IDs. Extra disturbance inputs lack bound per-frame focus geometry.
    OUT.mkdir(); (OUT/'frames').mkdir()
    base.write(OUT/'registration.json',dict(version='spatial297-v1',runner=base.ref(Path(__file__)),
        models=pins,package=base.ref(base.PACKAGE/'manifest.json'),membership=base.ref(base.PACKAGE/'membership.json'),
        selectedIDs=[r['id'] for r in membership['rows']],noiseThreshold=24,regionExpansion=1.2,
        controlSeed=42,threads=2,outputCapBytes=128*1024**2,training=False,
        accuracyOnInterventions=False,rolesChanged=False,
        disturbanceScope='Proposal-only diagnostics on left8, center8, global8; no fabricated focus regions.'))
    values=[]; masks=[]; rows=[]; pairs=[]; exclusions=[]; checked=set()
    def verify(ref):
        key=(ref['path'],ref['sha256'])
        if key not in checked: base.checked(ref); checked.add(key)
        return base.storage.resolve_input(base.ROOT/ref['path'])
    for i,row in enumerate(membership['rows']):
        try:
            value=np.array(native[i]); base.require(base.sha(value.tobytes())==row['tensorSHA256'],'tensor_identity')
            mask=np.zeros((128,192),bool)
            for frame,metadata in zip(row['images'],row['metadata']):
                doc=base.read(verify(metadata)); path=verify(frame)
                scenes=[doc[s] for e,s in [('unfocused','baseline_scene'),('focused','focused_scene')]
                        if doc[e+'_sha256']==frame['sha256']]
                base.require(bool(scenes),'missing_scene')
                base.require(all(s['focused_element_id']==scenes[0]['focused_element_id'] for s in scenes),'conflicting_scene')
                scene=scenes[0]
                base.require(scene['is_settled'],'unsettled_scene')
                element=next(e for e in scene['elements'] if e['element_id']==scene['focused_element_id'])
                box=element['rendered_body_geometry']['visible_pixel_bounds']
                with Image.open(path) as image: width,height=image.size
                scale=min(192/width,128/height); nw,nh=round(width*scale),round(height*scale)
                mask |= geometry.rect(box,(nw/width,nh/height,(192-nw)//2,(128-nh)//2),mask.shape,1.2)
            base.require(mask.any(),'empty_focus_region')
        except (ValueError,KeyError,StopIteration) as error:
            exclusions.append(dict(id=row['id'],reason=str(error))); continue
        values.append(value);masks.append(mask);rows.append(dict(row,index=i,set='native.npy'))
    for name in ('left8.npy','center8.npy','global8.npy'):
        array=np.load(base.PACKAGE/name,mmap_mode='r',allow_pickle=False)
        for i,value in enumerate(array):
            values.append(np.array(value));masks.append(None)
            rows.append(dict(id=f'{name}:{i}',index=i,set=name,role='development-diagnostic',changed=0,conditions=[name]))
    for i,value in enumerate(values):
        refs=[]
        for j in (0,3):
            path=OUT/'frames'/f'{i}-{j}.png'
            pixels=np.rint(value[j:j+3].transpose(1,2,0)*255).clip(0,255).astype(np.uint8)
            Image.fromarray(pixels).save(path)
            refs.append(dict(path=str(path),sha256=base.worker.digest(path)))
        pairs.append(dict(id=str(i),previous=refs[0],current=refs[1]))
    tool=base.ROOT/'.build/debug/TransitionTool'
    request=dict(version=1,root=str(OUT),noiseThreshold=24,localizeOnly=True,pairs=pairs)
    base.write(OUT/'proposal-request.json',request)
    with (OUT/'proposal-request.json').open('rb') as source, (OUT/'proposals.json').open('xb') as target, (OUT/'tool.log').open('xb') as log:
        subprocess.run([str(tool)],stdin=source,stdout=target,stderr=log,check=True,timeout=300)
    proposals=base.read(OUT/'proposals.json')['results']
    base.require([r['id'] for r in proposals]==[p['id'] for p in pairs],'proposal_order')
    records=[]
    # Score small batches. Never keep all transformed tensors in memory.
    for start in range(0,len(values),16):
        chunk=values[start:start+16]; original=np.stack(chunk)
        normal={name:base.worker.score(net,original) for name,net in models.items()}
        prepared=[]; interventions=[]
        for offset,value in enumerate(chunk):
            index=start+offset; row=rows[index]; oracle=masks[index]
            proposed=region_mask(proposals[index]['regions'])
            selections={'proposal':proposed}
            if oracle is not None:selections.update(observed=oracle,control=control_mask(oracle,42+row['index']))
            detail={}
            for key,mask in selections.items():
                detail[key]=dict(area=int(mask.sum()),observedOverlap=None if oracle is None else int((mask&oracle).sum()))
                for keep in (True,False):
                    interventions.append(intervene(value,mask,keep))
                    prepared.append((offset,key,'keep' if keep else 'remove'))
            records.append(dict(id=row['id'],set=row['set'],role=row['role'],group=row.get('group'),
                changed=row['changed'],conditions=row['conditions'],regions=detail,models={}))
        for name,net in models.items():
            predictions=base.worker.score(net,np.stack(interventions))
            for offset,row in enumerate(rows[start:start+16]):
                expected=cached[name]['conditions'][row['set']]['probabilities'][row['index']]
                base.require(abs(float(normal[name][offset])-expected)<=1e-6,'cache_parity')
                records[start+offset]['models'][name]=dict(original=expected,interventions={})
            for (offset,key,mode),probability in zip(prepared,predictions):
                records[start+offset]['models'][name]['interventions'][f'{key}_{mode}']=float(probability)
        print('Scored',min(start+16,len(values)),'of',len(values),flush=True)
    base.write(OUT/'result.json',dict(version='spatial297-v1',rows=records,exclusions=exclusions,
        tool=base.ref(tool),localizer=base.ref(base.ROOT/'Sources/NativeUIAuditKit/Perception/ChangeRegionLocalizer.swift'),
        modifiedInputAccuracy=False,productionEligible=False,training=False))
    size=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    base.require(size<128*1024**2,'output_budget')
    base.write(OUT/'completion.json',dict(scored=len(records),excluded=len(exclusions),outputBytes=size))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args();run()
