"""Approved reviewed-pair replay and fixed Home sensitivity diagnostics."""
import argparse
import os
import time
import numpy as np
from PIL import Image
import human_annotation_review as h
import native_focus_transfer as t
import native_focus_spike as n
import focus_runtime as runtime
from prepare_real_focus_references import intersections
from real_reference_challenge import REVIEW, SEAL, summarize

INVENTORY=h.ROOT/'reports/work/REAL-REFERENCE-CHALLENGE-31/grouped-review/inventory.json'
INVENTORY_SHA='152534b5535dc83b645e303954b9cd2d9dcca07c0cc34a612762de3a61168b09'
APPROVED=(0,1,2,3,4,7)


def diagnostic_window(bounds,size):
    """Expose production clamping for offline diagnostics, not live qualification."""
    try:
        window=t.geometry(bounds,size)
        return window,window,False
    except ValueError as error:
        if str(error)!='reference_context_clipped':raise
    x,y,w,v=bounds;W,H=size;requested=[x-.2*w,y-.2*v,1.4*w,1.4*v]
    left=max(0,requested[0]);top=max(0,requested[1])
    actual=[left,top,min(W,requested[0]+requested[2])-left,min(H,requested[1]+requested[3])-top]
    return requested,actual,True


def masks(reference,targets,neighbors):
    """Same source-space union for both states; preserve every target body."""
    x,y,w,v=reference;xs=x-.2*w+(np.arange(256)+.5)*1.4*w/256
    ys=y-.2*v+(np.arange(256)+.5)*1.4*v/256
    def union(boxes):
        mask=np.zeros((256,256),dtype=bool)
        for bx,by,bw,bh in boxes:
            h.require(bw>0 and bh>0,'invalid_mask_box')
            mask |= (ys[:,None]>=by)&(ys[:,None]<by+bh)&(xs[None,:]>=bx)&(xs[None,:]<bx+bw)
        return mask
    body=union(targets)
    return dict(neighbor=union(neighbors)&~body,target=body)


def apply_mask(image,mask):
    h.require(image.size==(256,256) and mask.shape==(256,256) and mask.dtype==bool,'invalid_mask')
    pixels=np.array(image.convert('RGB'),copy=True);pixels[mask]=128
    return Image.fromarray(pixels)


def luminance(image):
    # Fixed Rec.709 coefficients on display-encoded RGB; not physical luminance.
    return float(np.asarray(image.convert('RGB'),dtype=np.float64).mean(axis=(0,1)) @ np.array([.2126,.7152,.0722]))


def load_pairs():
    h.require(h.sha(INVENTORY)==INVENTORY_SHA,'unapproved_inventory')
    inv=h.sealed(INVENTORY,'real-reference-inventory-v1')
    for ref in inv['inputs'].values():t.checked(ref)
    frames={f['sha256']:f for group in inv['groups'].values() for f in group}
    pairs=[]
    for index in APPROVED:
        p=inv['selected'][index];fs=[frames[p[k]] for k in ('referenceImage','focusedImage')]
        cs=[next(c for c in f['controls'] if c['id']==p[key]) for f,key in zip(fs,('referenceControl','focusedControl'))]
        h.require([c['state'] for c in cs]==['unfocused','focused'],'reviewed_state_changed')
        pairs.append(dict(id=f'review-{index+1}',screen=p['screen'],frames=fs,targets=cs,home=False))
    review=h.sealed(REVIEW,'real-reference-review-v1');h.require(review['seal']==SEAL,'home_review_changed')
    for p in review['pairs']:
        fs=[frames[f['image']['sha256']] for f in p['frames']]
        cs=[f['target'] for f in p['frames']]
        h.require(all(c in f['controls'] for f,c in zip(fs,cs)),'home_truth_changed')
        pairs.append(dict(id=p['id'],screen='home',frames=fs,targets=cs,home=True))
    return pairs


def execute(output,scorer_factory=t.Scorer):
    started=time.monotonic();pairs=load_pairs();identity=runtime.identity()
    out=h.fresh(output);out.mkdir(parents=True)
    h.write(out/'authorization.json',dict(inventory=h.ref(INVENTORY),indices=[i+1 for i in APPROVED],
        statement='Maintainer confirmed matching control identities and correct states, then assigned next tranche.',
        role='development diagnostic only',pid=os.getpid(),maximumInputs=24,maximumSeconds=300))
    images=[];rows=[]
    for p in pairs:
        sizes=[h.image(h.ROOT,f['image']) for f in p['frames']]
        h.require(sizes[0]==sizes[1],'pair_size_changed')
        ref=p['targets'][0]['bounds'];requested,window,clipped=diagnostic_window(ref,sizes[0])
        overlaps=[intersections(window,f['controls'],c['id']) for f,c in zip(p['frames'],p['targets'])]
        crops=[t.crop(dict(id=p['id'],path=str(t.checked(f['image'])),sha256=f['image']['sha256'],
                           bounds=n.common_window(ref)),h.ROOT) for f in p['frames']]
        variants={'original':crops};mask_fractions={}
        if p['home']:
            targets=[c['bounds'] for c in p['targets']]
            neighbors=[c['bounds'] for f,target in zip(p['frames'],p['targets']) for c in f['controls'] if c['id']!=target['id']]
            for kind,mask in masks(ref,targets,neighbors).items():
                variants[kind]=[apply_mask(im,mask) for im in crops];mask_fractions[kind]=float(mask.mean())
        row=dict(id=p['id'],screen=p['screen'],referenceBounds=ref,window=window,
                 requestedWindow=requested,clippedContext=clipped,
                 retainedWindowFraction=window[2]*window[3]/(requested[2]*requested[3]),
                 frames=[dict(image=f['image'],target=c) for f,c in zip(p['frames'],p['targets'])],
                 neighborOverlaps=overlaps,cleanContext=not any(overlaps),
                 bodyContainment=[n.overlap(window,c['bounds'])/(c['bounds'][2]*c['bounds'][3]) for c in p['targets']],
                 maskFractions=mask_fractions,variants={})
        for kind,ims in variants.items():
            indices=[];refs=[]
            for label,im in enumerate(ims):
                path=out/f"{p['id']}-{kind}-{label}.png";im.save(path)
                refs.append(h.ref(path));indices.append(len(images));images.append(im)
            brightness=[luminance(im) for im in ims]
            row['variants'][kind]=dict(indices=indices,crops=refs,meanLuminance=brightness,
                                       brighterWhenFocused=brightness[1]>brightness[0])
        rows.append(row)
    h.require(len(images)==24 and runtime.identity()==identity,'input_or_runtime_changed')
    scorer=scorer_factory();values=scorer.score(images)
    h.require(len(values)==24 and time.monotonic()-started<300,'score_count_or_budget')
    for row in rows:
        for variant in row['variants'].values():
            variant.update(summarize([values[i] for i in variant['indices']]))
    previous=h.sealed(h.ROOT/'reports/work/REAL-REFERENCE-CHALLENGE-31/scored/result.json','real-reference-challenge-v1')
    h.require(scorer.identity==previous['model'],'model_changed')
    parity=max(abs(row['variants']['original'][key]-old[key]) for row,old in zip(rows[-2:],previous['pairs'])
               for key in ('unfocusedScore','focusedScore'))
    h.require(parity<1e-5,'home_baseline_parity')
    result=dict(version='real-transfer-diagnosis-v1',**h.FLAGS,pid=os.getpid(),seconds=time.monotonic()-started,
                implementation=h.ref(__file__),inventory=h.ref(INVENTORY),model=scorer.identity,runtime=identity,
                homeMaximumScoreDifference=parity,rows=rows,
                caveat='Small related development sample; native profile unverified; masking is sensitivity evidence, not causal isolation.')
    h.write(out/'result.json',result,sealed=True)
    lines=['# Real transfer diagnosis32','',result['caveat'],'',
           '| Pair | Variant | Unfocused / focused score | Correct at0.85 | Advisory correct/wrong/uncertain | Focused brighter? |',
           '| --- | --- | --- | --- | --- | --- |']
    for row in rows:
        for name,v in row['variants'].items():
            lines.append(f"| {row['id']} ({row['screen']}) | {name} | {v['unfocusedScore']:.5f} / {v['focusedScore']:.5f} | {v['correctAt085']}/2 | {v['advisoryCorrect']}/{v['advisoryWrong']}/{v['advisoryUncertain']} | {v['brighterWhenFocused']} |")
    (out/'result.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines),flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    execute(p.parse_args().output)
