"""Assess style-specific bounds on retained probes; never rewrite annotations."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
from native_page150_audit import ink_bounds
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'reports/work/IOS-NATIVE-PAGE-150/artifacts'


def proposal(row,width,public_size):
    if type(row['prominent']) is not bool or row['scale'] not in (2,3):raise ValueError('style_or_scale')
    if not row['prominent']:return row['frame']
    w,h=public_size
    if w<=0 or h<=0 or w>width:raise ValueError('bounds')
    # Exactly matches the retained test controller's explicit placement.
    return [(width-w)/2,151,w,h]


def run():
    doc=json.loads((BASE/'alpha-capture/receipt.json').read_text())
    intrinsic=json.loads((BASE/'geometry-audit.json').read_text());sizes={}
    for row in intrinsic['rows']:
        sizes.setdefault(row['pages'],[]).append(row['publicSize'])
    for n,values in sizes.items():
        if not all(np.allclose(v,values[0],atol=1e-9,rtol=0) for v in values):raise ValueError('inconsistent_public_size')
    if len(doc['rows'])!=72 or len({r['id'] for r in doc['rows']})!=72:raise ValueError('membership')
    results=[]
    for row in doc['rows']:
        p=BASE/'alpha-capture'/(row['id']+'.png')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('image_hash')
        with Image.open(p) as im:
            actual=np.array(ink_bounds(np.array(im.convert('RGB')),row['dark']))/row['scale']
            proposed=np.array(proposal(row,im.width/row['scale'],sizes[row['pages']][0]))
        error=float(np.max(np.abs(np.r_[actual[:2],actual[:2]+actual[2:]]-np.r_[proposed[:2],proposed[:2]+proposed[2:]])))
        results.append(dict(id=row['id'],prominent=row['prominent'],scale=row['scale'],proposed=proposed.tolist(),edgeError=error,passed=error<=1))
    out=BASE/'style154-assessment.json'
    report=dict(version='page-style154-v1',rows=results,passed=sum(r['passed'] for r in results),count=72,
        productionQualified=False,limits='Prominent public size reused from same-runtime prior probes and explicit test-controller placement; scale2 public-size equivalence remains inferred. Flat backgrounds only. Automatic interactive, minimal, other counts, dynamic type and real template compositing untested.',
        sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [BASE/'alpha-capture/receipt.json',BASE/'geometry-audit.json',Path(__file__)]})
    with out.open('x') as f:json.dump(report,f,indent=2)
    print(report['passed'],'/',report['count'],'max edge error',max(r['edgeError'] for r in results))


if __name__=='__main__':run()
