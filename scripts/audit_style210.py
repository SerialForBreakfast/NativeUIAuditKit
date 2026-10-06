"""Read-only audit of a completed native-style210 capture; no automatic admission."""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
from PIL import Image
import numpy as np
from page_style210 import validate


def audit(root,catalog_path):
    raw=catalog_path.read_bytes();catalog=validate(json.loads(raw))
    receipt=json.loads((root/'receipt.json').read_text())
    if receipt['catalogSHA256']!=hashlib.sha256(raw).hexdigest() or receipt['target']!=catalog['target']:
        raise ValueError('receipt_identity')
    if [r['id'] for r in receipt['rows']] != [r['id'] for r in catalog['members']]:raise ValueError('membership')
    pixels=collections.defaultdict(list);heights=collections.defaultdict(list);files=[]
    for recipe,evidence in zip(catalog['members'],receipt['rows']):
        key=recipe['id'];ann=json.loads((root/(key+'.json')).read_text())
        if json.loads((root/(key+'-evidence.json')).read_text())!=evidence:raise ValueError('evidence_alias')
        if evidence['group']!=recipe['group'] or evidence['interaction'] is not recipe['interaction'] or evidence['requestedBackgroundStyle']!=recipe['backgroundStyle']:
            raise ValueError('resolved_config')
        # UIKit BackgroundStyle automatic=0, prominent=1; actual raster geometry is separately measured.
        if evidence['resolvedBackgroundStyle'] != (1 if recipe['backgroundStyle']=='prominent' else 0):raise ValueError('native_style')
        dimensions=[];rasters=[]
        for suffix,field in [('.png','sha256'),('-hidden.png','hiddenSHA256')]:
            path=root/(key+suffix)
            if path.resolve()!=path or path.is_symlink():raise ValueError('path_boundary')
            b=path.read_bytes()
            if hashlib.sha256(b).hexdigest()!=evidence[field]:raise ValueError('image_hash')
            with Image.open(path) as image:
                image.load();dimensions.append(image.size);rasters.append(np.asarray(image.convert('RGB'),dtype=np.int16))
                if suffix=='.png':pixels[hashlib.sha256(str(image.size).encode()+image.convert('RGB').tobytes()).hexdigest()].append(dict(id=key,group=recipe['group']))
        if dimensions[0]!=dimensions[1]:raise ValueError('dimension_pair')
        page=[e for e in ann['elements'] if e['elementType']=='pageControl']
        if len(page)!=1:raise ValueError('page_membership')
        # Independent full-frame visible/hidden comparison; never generates labels.
        ys,xs=np.where(np.max(np.abs(rasters[0]-rasters[1]),axis=2)>4)
        if not len(xs):raise ValueError('empty_native_difference')
        measured=[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]
        pb=page[0]['boundsPixels'];expected=[pb['x'],pb['y'],pb['x']+pb['width'],pb['y']+pb['height']]
        if max(abs(a-b) for a,b in zip(measured,expected))>1:raise ValueError('native_difference_geometry')
        p=page[0]['boundsPoints'];body=evidence['body']
        if any(abs(p[k]-v)>1e-6 for k,v in zip(('x','y','width','height'),body)):raise ValueError('body_annotation')
        w,h=dimensions[0]
        for element in ann['elements']:
            b=element['boundsPixels'];x,y,bw,bh=[b[k] for k in ('x','y','width','height')]
            if not all(math.isfinite(v) for v in (x,y,bw,bh)) or min(x,y)<0 or min(bw,bh)<=0 or x+bw>w or y+bh>h:raise ValueError('geometry')
        heights[recipe['backgroundStyle']+':'+str(recipe['interaction'])].append(page[0]['boundsPixels']['height'])
        for suffix in ('.png','-hidden.png','.json','-evidence.json'):
            path=root/(key+suffix);b=path.read_bytes();files.append(dict(path=path.name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
    duplicates=[v for v in pixels.values() if len(v)>1]
    return dict(expected=144,accounted=len(receipt['rows']),uniquePixels=len(pixels),duplicateSets=duplicates,
        crossGroupDuplicates=[v for v in duplicates if len({r['group'] for r in v})>1],
        measuredHeightPixels={k:dict(min=min(v),max=max(v),count=len(v)) for k,v in heights.items()},
        files=files,trainingEligible=False,remaining=['visual_review','ancestry_review','duplicate_disposition'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--catalog',type=Path,required=True)
    a=p.parse_args();print(json.dumps(audit(a.root.absolute(),a.catalog),indent=2))
