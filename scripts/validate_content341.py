"""Validate content-only pairs and score the frozen control."""
from collections import Counter
import time
import numpy as np
from PIL import Image, ImageDraw
import additive341 as a


def main():
    start=time.monotonic();a.t.set_num_threads(2)
    doc=a.b.read(a.OUT/'negatives.json');source=a.b.read(a.b.checked(doc['source']))
    sources={r['id']:r for r in source['rows']['independent']}
    protected={r['group'] for r in a.b.read(a.b.PACKAGE/'membership.json')['rows'] if r['role']!='train'}
    net=a.e.load_candidate(a.e.OUT/'run/last.pt');records=[];decoded={};samples=[]
    for i,row in enumerate(doc['rows']):
        original=sources[row['matchedMovementID']]
        a.b.require(row['role']=='train' and row['group']==original['group'] and row['group'] not in protected,'ancestry')
        a.b.require(row['images'][0]==original['images'][0] and row['changed']==0,'original_identity')
        a.b.require(row['endpoints']==[original['endpoints'][0]]*2,'unchanged_focus_and_geometry')
        images=[a.r.s.image(v['path'],v['sha256']) for v in row['images']]
        a.b.require(all(im.size==(1920,1080) for im in images),'dimensions')
        first,second=[np.asarray(im) for im in images]
        for x,y,w,h in original['patchBounds']:
            if row['method']=='background-panel':
                a.b.require(np.array_equal(first[y:y+h,x:x+w],second[y:y+h,x:x+w]),'control_effect_changed')
        actual=a.magnitude(first,second)
        error=abs(actual-row['targetMagnitude'])/max(actual,row['targetMagnitude'])
        a.b.require(actual==row['actualMagnitude'] and error<=.1,'magnitude_match')
        pair=tuple(a.b.sha(v.tobytes()) for v in (first,second))
        a.b.require(pair[0]!=pair[1],'unchanged_pixels')
        a.b.require(decoded.setdefault(pair,row['changed'])==row['changed'],'conflicting_labels')
        x=np.stack([a.r.s.encoded(*images,(192,128))[0]])
        detail,_=a.r.prepare(x,[row],2)
        p=float(a.b.worker.score(net,np.concatenate((x,detail),1))[0])
        records.append(dict(id=row['id'],group=row['group'],label=0,probability=p,
            decision=0 if p<=.15 else 1 if p>=.85 else None,relativeError=error,method=row['method']))
        if i in (0,64,128):samples.append((row,images))
    sheet=Image.new('RGB',(960,600));draw=ImageDraw.Draw(sheet)
    for i,(row,images) in enumerate(samples):
        for j,im in enumerate(images):sheet.paste(im.resize((480,270)),(j*480,i*200))
        draw.rectangle((0,i*200,960,i*200+24),fill='black')
        draw.text((4,i*200+4),row['id'],fill='white')
    sheet.save(a.OUT/'content-review.png')
    a.b.write(a.OUT/'negative-validation.json',dict(passed=True,rows=records,
        corpus=a.b.ref(a.OUT/'negatives.json'),model=a.b.ref(a.e.OUT/'run/last.pt'),
        uniquePairs=len(decoded),groups=len({r['group'] for r in records}),
        counts=dict(Counter('abstain' if r['decision'] is None else 'correct' if r['decision']==0 else 'false_change' for r in records)),
        seconds=time.monotonic()-start,trainingOnly=True,nativeQualified=False,
        limitation='All matches change a background panel. This does not cover equal-magnitude changes inside controls.'))
    print('Validated',len(records),'pairs',flush=True)


if __name__=='__main__':main()
