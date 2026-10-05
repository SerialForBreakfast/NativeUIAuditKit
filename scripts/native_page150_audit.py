"""Measure isolated native probe ink, not production annotation or inferred labels."""
import hashlib
import json
import argparse
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'reports/work/IOS-NATIVE-PAGE-150/artifacts/native-capture'


def ink_bounds(rgb,dark):
    if rgb.ndim!=3 or rgb.shape[2]!=3 or rgb.dtype!=np.uint8:raise ValueError('rgb_image')
    background=0 if dark else 255
    mask=np.max(np.abs(rgb.astype(np.int16)-background),axis=2)>4
    ys,xs=np.where(mask)
    if not len(xs):raise ValueError('empty_render')
    return [int(xs.min()),int(ys.min()),int(xs.max()+1-xs.min()),int(ys.max()+1-ys.min())]


def audit():
    receipt=json.loads((BASE/'receipt.json').read_text())
    expected={f'native-{w}-{n}-{s}-{theme}' for w in (375,430) for n in (3,5,7)
              for s in (0,n//2,n-1) for theme in ('light','dark')}
    rows=receipt['rows']
    if receipt['count']!=36 or len(rows)!=36 or {r['id'] for r in rows}!=expected:raise ValueError('membership')
    reports=[]
    for row in rows:
        path=BASE/(row['id']+'.png');ann=json.loads(path.with_suffix('.json').read_text())
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        if sha!=row['sha256'] or sha!=ann['imageSHA256']:raise ValueError('image_hash')
        with Image.open(path) as im:
            if im.size!=(row['width']*3,540):raise ValueError('dimensions')
            ink=ink_bounds(np.array(im.convert('RGB')),row['theme']=='dark')
        x,y,w,h=row['frame'];ix,iy,iw,ih=[v/3 for v in ink]
        if not (x-1<=ix and y-1<=iy and ix+iw<=x+w+1 and iy+ih<=y+h+1):raise ValueError('ink_outside_frame')
        reports.append(dict(row,inkPixelBounds=ink,inkPointBounds=[ix,iy,iw,ih],
            frameToInkWidthRatio=w/iw,frameToInkHeightRatio=h/ih))
    result=dict(version='native-page150-ink-audit-v1',count=len(reports),rows=reports,
        hashVerification=True,allInkContained=True,
        qualifiedAsTightVisualBounds=all(r['frameToInkWidthRatio']<1.1 and r['frameToInkHeightRatio']<1.1 for r in reports),
        limits='Threshold4 background difference on isolated flat-background probes only; not a production cropper or ground-truth annotation algorithm.')
    out=BASE.parent/'geometry-audit.json'
    with out.open('x') as f:json.dump(result,f,indent=2)
    print({k:v for k,v in result.items() if k!='rows'})
    print(sorted({(r['pages'],tuple(r['publicSize']),tuple(r['inkPointBounds'][2:])) for r in reports}))


def audit_alpha():
    root=BASE.parent/'alpha-capture';doc=json.loads((root/'receipt.json').read_text())
    rows=doc['rows'];expected={f'alpha-{m}-{n}-{s}-{d}-{p}' for m in ('false','true')
        for n in (3,5,7) for s in (0,n//2,n-1) for d in ('false','true') for p in ('false','true')}
    if doc['version']!='native-page150-alpha-v1' or len(rows)!=72 or {r['id'] for r in rows}!=expected:raise ValueError('alpha_membership')
    results=[]
    for row in rows:
        image=root/(row['id']+'.png')
        if hashlib.sha256(image.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('alpha_image_hash')
        with Image.open(image) as im:
            if im.size not in ((750,1334),(1179,2556)):raise ValueError('alpha_dimensions')
            ink=np.asarray(ink_bounds(np.array(im.convert('RGB')),row['dark']),float)/row['scale']
        measured=np.asarray(row['frame'],float)
        error=float(np.abs(np.r_[ink[:2],ink[:2]+ink[2:]]-np.r_[measured[:2],measured[:2]+measured[2:]]).max())
        results.append(dict(row,inkPointBounds=ink.tolist(),maximumEdgeErrorPoints=error,passed=error<=1))
    report=dict(version='native-page150-alpha-audit-v1',count=72,passed=all(r['passed'] for r in results),rows=results,
        limits='Qualification of flat-background native controls only; real template compositing remains required before corpus admission.')
    with (BASE.parent/'alpha-audit.json').open('x') as f:json.dump(report,f,indent=2)
    print('alpha passed',report['passed'],'max edge error',max(r['maximumEdgeErrorPoints'] for r in results))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--alpha',action='store_true');args=p.parse_args()
    audit_alpha() if args.alpha else audit()
