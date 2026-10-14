"""Measure retained rule errors, proposal recall, and visible boundary support."""
from collections import Counter
from pathlib import Path
import research_queue as q
from score_hcf_pilot import iou

OUT=None


def inputs():
    docs={};refs=[]
    for dep in q.load(OUT/'dependencies.json'):
        for ref in dep['outputs']:
            path=q.local_path(q.ROOT,ref['path'])
            q.require(q.digest(path)==ref['sha256'],'input_changed')
            docs[(dep['job'],path.name)]=q.load(path);refs.append(ref)
    rules=docs[('hcf371r4-60-rules','comparison.json')]
    frames=docs[('hcf371r4-40-catalog','admission.json')]['rows']+docs[('hcf371-00-retained','admission.json')]['rows']
    frames={r['id']:r for r in frames if r['role'] in ('development','retained')}
    q.require(len({r['id'] for r in rules['rows']})==len(rules['rows']),'duplicate_prediction')
    for row in rules['rows']:
        frame=frames[row['id']]
        q.require(all(frame[k]==row[k] for k in ('sha256','group','role','profile')),'identity_mismatch')
    return rules,frames,refs


def overlap(a,b):
    return iou(dict(zip(('x','y','width','height'),a)),dict(zip(('x','y','width','height'),b)))


def proposal_rows(rules,frames):
    rows=[]
    for row in rules['rows']:
        f=frames[row['id']]; boxes=row['prediction']['candidates']
        matched=[overlap(b,f['boxes'][f['focus']]) for b in boxes]
        rows.append(dict(id=row['id'],sha256=row['sha256'],group=row['group'],profile=row['profile'],
            candidates=len(boxes),bestFocusIoU=max(matched,default=0),proposalHit=any(v>=.5 for v in matched),
            selectedOutcome=row['outcome']))
    return rows


def proposals():
    rules,frames,refs=inputs();rows=proposal_rows(rules,frames)
    q.save(OUT/'proposals.json',dict(version='hcf-rule-proposals-v1',rows=rows,frames=len(rows),
        hits=sum(r['proposalHit'] for r in rows),groups=len({r['group'] for r in rows}),
        method='bright-closed-stroke-v1',modelAccepted=False,
        limitation='This measures existing rule proposals, not the YOLO proposals discarded by the earlier evaluator.'))
    q.save(OUT/'sources.json',refs)


def wrong_selections():
    rules,frames,refs=inputs();rows=[]
    for row in rules['rows']:
        if row['outcome']!='wrong':continue
        f=frames[row['id']];pred=row['prediction']['box']
        matches={key:overlap(pred,value) for key,value in f['boxes'].items()}
        nonfocus=max((value for key,value in matches.items() if key!=f['focus']),default=0)
        rows.append(dict(id=row['id'],sha256=row['sha256'],group=row['group'],profile=row['profile'],
            focus=f['focus'],prediction=pred,controlIoU=matches,
            category='unfocused-control' if nonfocus>=.5 else 'unmatched-outline'))
    q.save(OUT/'wrong-selections.json',dict(version='hcf-rule-wrong-v1',rows=rows,
        counts=dict(Counter(r['category'] for r in rows)),modelAccepted=False,
        limitation='Overlap classifies geometry. It does not identify the artwork or prove the visible cause.'))
    q.save(OUT/'sources.json',refs)


def boundary(image,box):
    """Measure the fixed bright-mask support near body edges, not an annotated outline."""
    import numpy as np
    rgb=np.asarray(image.convert('RGB'));height,width=rgb.shape[:2]
    x,y,w,h=box;x0=max(0,round(x));y0=max(0,round(y));x1=min(width,round(x+w));y1=min(height,round(y+h))
    if x1-x0<8 or y1-y0<8:return dict(available=False,reason='body_too_small_or_clipped')
    patch=rgb[y0:y1,x0:x1].astype(float)
    mask=(patch.min(axis=2)>=220)&((patch.max(axis=2)-patch.min(axis=2))<=30)
    band=min(16,(x1-x0)//4,(y1-y0)//4)
    strips=[mask[:band,:],mask[-band:,:],mask[:,:band],mask[:,-band:]]
    supports=[float(s.any(axis=0 if i<2 else 1).mean()) for i,s in enumerate(strips)]
    luma=patch.mean(axis=2);edge=np.concatenate([luma[:band,:].ravel(),luma[-band:,:].ravel(),luma[:,:band].ravel(),luma[:,-band:].ravel()])
    inner=luma[band:-band,band:-band]
    return dict(available=True,bandPixels=band,sideBrightSupport=supports,minimumSideSupport=min(supports),
        edgeMean=float(edge.mean()),interiorMean=float(inner.mean()),edgeMinusInterior=float(edge.mean()-inner.mean()))


def contrast():
    from PIL import Image
    rules,frames,refs=inputs();rows=[]
    for row in rules['rows']:
        f=frames[row['id']];path=Path(f['path'])
        q.require(q.digest(path)==f['sha256'],'image_changed')
        with Image.open(path) as image:measurement=boundary(image,f['boxes'][f['focus']])
        rows.append(dict(id=row['id'],sha256=row['sha256'],group=row['group'],profile=row['profile'],
            outcome=row['outcome'],measurement=measurement))
    q.save(OUT/'boundary.json',dict(version='hcf-body-boundary-v1',rows=rows,modelAccepted=False,
        threshold=dict(minChannel=220,maxChannelSpread=30,bodyBandPixels=16),
        limitation='Body-edge support is a diagnostic proxy. True stroke contrast and closure require separate outline labels. No rule threshold is changed.'))
    q.save(OUT/'sources.json',refs)
