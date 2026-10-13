"""Measure lossless storage and input transformations on retained captures."""
import time
from PIL import Image
import numpy as np
import research_queue as q
from research_campaign340 import pin
OUT = None


def transform(image, half=False):
    image=image.convert('RGB')
    return image.resize((image.width//2,image.height//2),Image.Resampling.LANCZOS) if half else image


def run():
    c=q.load(OUT/'config.json')
    for ref in c['inputs']:
        q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'input_changed')
    if c['mode']=='storage':
        rows=[]
        for i,ref in enumerate(c['images']):
            path=q.ROOT/ref['path'];destination=OUT/f'encoded-{i}.png';start=time.monotonic()
            with Image.open(path) as original:
                original.load();original.save(destination,format='PNG',compress_level=c['level'])
                encode=time.monotonic()-start;start=time.monotonic()
                with Image.open(destination) as decoded:
                    decoded.load()
                    q.require(original.mode==decoded.mode and original.size==decoded.size and original.tobytes()==decoded.tobytes(),'pixel_parity')
                decode=time.monotonic()-start
            rows.append(dict(source=ref,output=pin(destination),sourceBytes=path.stat().st_size,
                outputBytes=destination.stat().st_size,encodeSeconds=encode,decodeSeconds=decode,pixelParity=True))
        result=dict(rows=rows,level=c['level'],decision='Compare size and time before changing storage. Preserve originals.',
            limitation='A small retained sample does not establish a corpus compression bound.')
    else:
        import compare351,report_additive341 as report
        from diagnostics343 import counts
        report.a.t.set_num_threads(2)
        path=q.ROOT/c['capture']['path'];doc=q.load(path);frames=compare351.validate_capture(doc,path.parent)
        model=report.a.e.load_candidate(q.ROOT/c['model']['path']);variants={};baseline=None
        for name,half,jpeg in [('original',False,False),('half-png',True,False),('half-jpeg95',True,True),('full-jpeg95',False,True)]:
            refs={};start=time.monotonic()
            for i,(ident,frame) in enumerate(frames.items()):
                source=path.parent/frame['path']
                if name=='original':refs[ident]=pin(source);continue
                target=OUT/(f'{name}-{i}'+('.jpg' if jpeg else '.png'))
                with Image.open(source) as image:
                    image=transform(image,half)
                    image.save(target,format='JPEG' if jpeg else 'PNG',**({'quality':95,'subsampling':2} if jpeg else {}))
                refs[ident]=pin(target)
            rows=[dict(id=p['case']+'-'+p['condition'],changed=int(p['changed']),condition=p['condition'],
                group=doc['group'],role='development',images=[refs[p[k]] for k in ('before','after')]) for p in doc['pairs']]
            timing=dict(preprocessingSeconds=0.,inferenceSeconds=0.,examples=0)
            scores=report.score_rows(model,rows,False,timing)
            if baseline is None:baseline=scores
            variants[name]=dict(rows=rows,probabilities=scores.tolist(),counts=counts(rows,scores,baseline),
                timing=timing,totalSeconds=time.monotonic()-start)
        result=dict(variants=variants,model=c['model'],independentGroups=1,
            limitation='JPEG 4:2:0 is a controlled distortion, not a qualified HDMI model. Existing Fixture labels remain development-only.')
    q.save(OUT/'summary.json',dict(**result,modelAccepted=False,trainingEligible=False,originalsChanged=False))
