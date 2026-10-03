"""Reconstruct experiment geometry and replay scoring independently from raw predictions."""
import argparse
import hashlib
import json
from pathlib import Path
import human_annotation_review as h
from focus_priorities46 import square_content, place, measure, summarize
from focus_alignment46 import aligned
from train_fullscreen_focus import source_image


def run(root,output):
    import numpy as np
    from PIL import Image,ImageDraw
    root=h.local(root);output=h.fresh(output);output.mkdir(parents=True)
    protocol=h.read(root/'run/protocol.json');frames={f['id']:f for f in protocol['frames']}
    cache={};sets={};verified=0
    for folder,count in [('run',240),('alignment',60)]:
        rows=[];keys=set()
        for i in range(count):
            r=h.read(root/folder/f'{i:03d}.json');f=frames[r['id']]
            key=(r['id'],r['arm']);h.require(key not in keys,'duplicate_result');keys.add(key)
            if f['id'] not in cache:
                path,size,pixel=source_image(f['image']);h.require(pixel==f['pixelSHA256'],'pixel_binding')
                with Image.open(path) as image:rgb=np.array(image.convert('RGB'))
                cache[f['id']]=square_content(rgb)
            content,scales=cache[f['id']]
            variant=r['arm'].split('-',1)[1]
            if variant.startswith('rect'):controls=f['controls']
            elif variant.startswith('aligned'):
                image,controls,y=aligned(content,scales,f['controls'],int(variant[len('aligned'):]))
            else:image,controls,y=place(content,scales,f['controls'],variant)
            if not variant.startswith('rect'):
                h.require(r['offset']==y and r['contentSHA256']==hashlib.sha256(content.tobytes()).hexdigest(),'content_or_offset')
                np.testing.assert_array_equal(image[y:y+content.shape[0]],content)
            h.require(controls==r['controls'] and measure(f,controls,r['predictions'])==r['measure'],'geometry_or_scoring')
            verified+=1;rows.append(r)
        h.require(summarize(rows)==h.read(root/folder/'summary.json')['groups'],'summary')
        sets[folder]=rows
    # Check ordinary640 predictions against earlier independent retained calls.
    previous=h.ROOT/'reports/work/REFERENCE-BENCHMARK-45/benchmark'
    reference=h.read(previous/'protocol.json')['frames']
    # The benchmark deduplicated decoded pixels; a reviewed alias can have a
    # different PNG encoding. Bind through its retained alias, not encoded bytes.
    old_ref={alias:(f,h.read(previous/f'{i:03d}.json')['candidate'])
             for i,f in enumerate(reference) for alias in f['aliases']}
    old_native={r['id']:r for r in (json.loads(line) for line in
        (h.ROOT/'reports/work/FULLSCREEN-EXPERIMENT-41/confidence-diagnosis/one-progress.jsonl').read_text().splitlines())}
    matched=0
    for row in sets['run']:
        if row['arm']!='one-rect640':continue
        f=frames[row['id']]
        if f['family']=='native26':
            old=old_native[f['id']];pred=[dict(box=b,score=s) for b,s in zip(old['boxes'],old['scores'])]
        else:
            earlier,pred=old_ref[f['id']]
            # Historical import hashes and source_image use different dimension
            # prefixes. Recompute through one decoder before comparing aliases.
            _,_,earlier_pixel=source_image(earlier['image'])
            h.require(earlier_pixel==f['pixelSHA256'],'baseline_pixel_binding')
        prior=measure(f,f['controls'],pred)
        h.require(prior['localized']==row['measure']['localized'] and prior['selection']==row['measure']['selection'],'independent_baseline_decision')
        h.require(abs(prior['bestFocusScore']-row['measure']['bestFocusScore'])<1e-5,'independent_baseline_score')
        matched+=1
    # One explanatory image, chosen by membership order rather than best improvement.
    f=next(f for f in protocol['frames'] if f['family']=='native26');content,scales=cache[f['id']]
    preview=Image.new('RGB',(1600,370),'white');draw=ImageDraw.Draw(preview)
    arms=['one-top','one-aligned-128','one-center','one-aligned128','one-bottom']
    for j,arm in enumerate(arms):
        r=next(r for rows in sets.values() for r in rows if r['id']==f['id'] and r['arm']==arm)
        image=np.full((640,640,3),114,dtype=np.uint8);y=r['offset'];image[y:y+content.shape[0]]=content
        panel=Image.fromarray(image);pen=ImageDraw.Draw(panel)
        for c in r['controls']:
            if c['state']=='focused':
                x,y,w,v=c['bounds'];pen.rectangle([x,y,x+w,y+v],outline='lime',width=3)
        for p in r['predictions']:
            if p['score']>=.25:pen.rectangle(p['box'],outline='red',width=2)
        preview.paste(panel.resize((320,320)),(j*320,35))
        draw.text((j*320+5,5),f"padding {r['offset']} | score {r['measure']['bestFocusScore']:.3f}",fill='black')
    draw.text((5,355),'Green: known focused body. Red: predictions >=0.25. Identical content at all five offsets.',fill='black')
    preview.save(output/'alignment-example.png')
    h.write(output/'audit.json',dict(rowsReconstructed=verified,independentBaselineMatches=matched,
        inputFrames=len(cache),models={k:h.ref(h.checked(h.ROOT,v)) for k,v in protocol['models'].items()},
        figureSource=f['id'],pixelContentPreserved=True,geometryAndScoringReplayed=True))
    print(f'{verified} rows reconstructed; {matched} independent baseline matches.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.root,a.output)
