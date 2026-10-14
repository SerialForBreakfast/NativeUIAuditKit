"""Measure actual focus positions in original and replacement training frames."""
import argparse
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image
import transition270 as base

OUT=base.ROOT/'reports/work/TRANSITION-290/coverage.json'


def cell(box, size):
    values=np.asarray(box,dtype=float)
    base.require(values.shape==(4,) and np.isfinite(values).all() and min(values[2:])>0,'visible_bounds')
    width,height=size
    x,y,w,h=values
    base.require(width>0 and height>0 and x>=-1e-6 and y>=-1e-6
                 and x+w<=width+1e-6 and y+h<=height+1e-6,'outside_image')
    return (min(2,int(3*(x+w/2)/width)),min(2,int(3*(y+h/2)/height)))


def run():
    base.require(not OUT.exists(),'output_collision')
    base.worker.read_package(base.PACKAGE)
    membership=base.read(base.PACKAGE/'membership.json')
    prior=base.read(base.ROOT/'reports/work/TRANSITION-266/preflight.json')
    replacement=base.read(base.checked(prior['replacements']))
    admission=base.read(base.checked(prior['admission']))
    base.require(admission['approved'] and not admission['protectedEndpointOverlap'],'admission')
    replacements={r['nativeIndex']:r for r in replacement['rows']}
    weights=np.load(base.checked(base.read(base.ROOT/'reports/work/TRANSITION-266/DTM074/registration.json')['weights']))
    verified={}
    def checked(ref):
        key=(ref['path'],ref['sha256'])
        if key not in verified:verified[key]=base.checked(ref)
        return verified[key]
    @lru_cache(maxsize=256)
    def metadata(path):return base.read(path)
    @lru_cache(maxsize=256)
    def size(path):
        with Image.open(path) as image:return image.size
    summaries={};records=[]
    for variant in ('original','shifted'):
        buckets=defaultdict(lambda:dict(entries=0,images=set(),groups=set(),weight=0.))
        for position,index in enumerate(membership['selected']):
            original=membership['rows'][index]
            row=replacements.get(index,original) if variant=='shifted' else original
            base.require(row['role']==original['role']=='train' and row['changed']==original['changed'],'training_role')
            condition=('content_changed' if row['changed'] else 'content_unchanged') if 'content_contrast' in row['conditions'] else (
                'focus_changed' if row['changed'] else 'other_unchanged')
            for image,annotation in zip(row['images'],row['metadata']):
                shape=size(checked(image));doc=metadata(checked(annotation))
                matches=[doc[scene] for prefix,scene in [('unfocused','baseline_scene'),('focused','focused_scene')]
                         if doc[prefix+'_sha256']==image['sha256']]
                base.require(bool(matches),'frame_binding')
                scene=matches[0]
                elements=[e for e in scene['elements'] if e['element_id']==scene['focused_element_id']]
                base.require(len(elements)==1,'observed_focus')
                box=elements[0]['rendered_body_geometry']['visible_pixel_bounds']
                location=cell(box,shape)
                key=(condition,*location)
                bucket=buckets[key];bucket['entries']+=1
                bucket['images'].add(image['sha256']);bucket['groups'].add(row['group'])
                bucket['weight']+=float(weights[len(membership['replayLabels'])+position])/2
                records.append(dict(variant=variant,id=row['id'],imageSHA256=image['sha256'],
                    group=row['group'],condition=condition,cell=list(location),visibleBounds=box,dimensions=shape))
        summaries[variant]=[dict(condition=k[0],cell=list(k[1:]),endpointEntries=v['entries'],
            uniqueImages=len(v['images']),groups=sorted(v['groups']),forwardWeight=v['weight'])
            for k,v in sorted(buckets.items())]
    base.write(OUT,dict(version='coverage290-v1',summaries=summaries,records=records,
        membership=base.ref(base.PACKAGE/'membership.json'),replacements=prior['replacements'],
        admission=prior['admission'],runner=base.ref(Path(__file__)),verifiedFiles=len(verified),
        cells='Zero-based x,y on a 3 by 3 grid. Use visible focus-body centers.',
        limitations=['Endpoint counts are correlated, not independent trials.',
                     'Coverage does not establish accuracy.', 'Replay rows are outside this native-position audit.'],
        dataRolesChanged=False))
    print({k:len(v) for k,v in summaries.items()},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args();run()
