"""Pinned retained-data replay for translation-only focus diagnostics; no training."""
import argparse
import base64
from collections import Counter,defaultdict
from functools import lru_cache
import json
import os
import subprocess
import sys
import time

from PIL import Image,ImageDraw
import numpy as np
import human_annotation_review as h
import focus_paired_growth as paired
import focus_transition_verifier as verifier
import focus_runtime as native

PREVIOUS=h.ROOT/'reports/work/FOCUS-PAIRED-11/artifacts'


def run(output,common=False):
    out=h.fresh(output);out.mkdir(parents=True)
    inventory_path=PREVIOUS/'inventory/inventory.json'
    inv=paired.read_inventory(inventory_path)
    old=h.read(PREVIOUS/'audit/audit.json',limit=16*1024**2)
    original_render=h.read(PREVIOUS/'rendered/receipt.json')
    h.require(original_render['runtime']==native.identity(),'changed_crop_runtime')
    h.require(old['inventory']==h.ref(inventory_path),'old_inventory_mismatch')
    started=time.monotonic();runtime=native.identity()
    protocol=dict(version='focus-alignment-experiment-v1',inventory=h.ref(inventory_path),
        baseline=h.ref(PREVIOUS/'audit/audit.json'),policy=verifier.POLICY,runtime=runtime,
        code=h.ref(h.ROOT/'scripts/focus_transition_verifier.py'),opencv=verifier.cv2.__version__,
        modelTraining=False,releaseEligible=False,commonSupport=common)
    h.write(out/'protocol.json',protocol)
    paths={};tracks={};items={};times=[]
    @lru_cache(maxsize=12)
    def image(refpath):
        with Image.open(paths[refpath]) as im:return im.convert('RGB')
    for c in inv['cases']:
        if time.monotonic()-started>1800:raise ValueError('experiment_deadline')
        ga,gb=[inv['geometry'][c[k]] for k in ('before','after')]
        for g in (ga,gb):
            ref=g['original']
            if ref['path'] not in paths:paths[ref['path']]=h.checked(h.ROOT,ref)
        start=time.monotonic()
        tracking=verifier.track(image(ga['original']['path']),image(gb['original']['path']),c['anchor'],common=common)
        times.append(time.monotonic()-start);tracks[c['id']]=tracking
        if tracking['status']=='matched':
            for geom,b in [(ga,tracking.get('beforeCropBounds',c['anchor'])),(gb,tracking.get('afterCropBounds',tracking['afterBounds']))]:
                key=paired.crop_key(geom,b)
                if key not in original_render['crops']:
                    items[key]=dict(id=key,path=str(paths[geom['original']['path']]),sha256=geom['original']['sha256'],bounds=b)
        if len(tracks)%250==0:print('tracked',len(tracks),'/',len(inv['cases']),flush=True)
    h.write(out/'tracking.json',dict(tracks=tracks,seconds=sum(times),statuses=dict(Counter(r['status'] for r in tracks.values()))))
    image.cache_clear();croprefs=dict(original_render['crops']);crop_start=time.monotonic()
    cropdir=out/'crops';cropdir.mkdir()
    for batch in native.bounded_batches(list(items.values())):
        h.require(time.monotonic()-started<1800,'experiment_deadline')
        for r in native.invoke(batch)['results']:
            dest=cropdir/(r['id']+'.png')
            with dest.open('xb') as f:f.write(base64.b64decode(r['png'],validate=True))
            croprefs[r['id']]=h.ref(dest)
    h.require(native.identity()==runtime and h.ref(h.ROOT/'scripts/focus_transition_verifier.py')==protocol['code'],'runtime_or_code_changed')
    h.write(out/'render.json',dict(runtime=runtime,crops=croprefs,newCrops=len(items),seconds=time.monotonic()-crop_start))
    @lru_cache(maxsize=64)
    def crop(key):
        with Image.open(h.checked(h.ROOT,croprefs[key])) as im:return im.convert('RGB')
    rows=[];summary=defaultdict(Counter);audit=[]
    for oldrow in old['decisions']:
        c=dict(oldrow);c['arms']=dict(oldrow['arms']);tr=tracks[c['id']];c['tracking']=tr
        if tr['status']=='identical':raw=gated='unchanged'
        elif tr['status']!='matched':raw=gated='unavailable'
        else:
            ga,gb=[inv['geometry'][c[k]] for k in ('before','after')]
            prediction=verifier.compare_crops(crop(paired.crop_key(ga,tr.get('beforeCropBounds',c['anchor']))),crop(paired.crop_key(gb,tr.get('afterCropBounds',tr['afterBounds']))),clipped=c['clipped'])
            c['alignedMeasurement']=prediction;raw=prediction['rawCombined'];gated=prediction['decision']
            # After geometry is used only after all image decisions, to audit translation.
            a,b=ga['bounds'],gb['bounds'];truthdx=b[0]+b[2]/2-a[0]-a[2]/2;truthdy=b[1]+b[3]/2-a[1]-a[3]/2
            audit.append(dict(case=c['id'],lane=c['lane'],dx=tr['dx'],dy=tr['dy'],
                              truthCenterDelta=[truthdx,truthdy],centerError=float(np.hypot(tr['dx']-truthdx,tr['dy']-truthdy))))
        c['arms'].update(alignedRaw=raw,alignedGated=gated);rows.append(c)
        for arm,pred in c['arms'].items():
            result='abstained' if pred in ('unknown','unavailable') else 'correct' if pred==c['truth'] else 'wrong'
            key='/'.join((c['lane'],'identical' if c['kind'].startswith('identical') else 'contrast',c['truth'],arm))
            summary[key][result]+=1
    baseline=h.read(h.ROOT/'NativeUITrainer/focus_ring_runs/fdr021-reviewed-contrast/experiment-result.json',limit=32*1024**2)
    selected=next(s for s in baseline['history'] if s['update']==baseline['selectedUpdate'])
    frames=paired.frame_analysis(rows,inv,selected['validation']['real']['metrics']['completeFrameSelection']['frames'])
    h.write(out/'result.json',dict(protocol=h.ref(out/'protocol.json'),decisions=rows,summary=dict(summary),
        frameComparisons=frames,translationAudit=audit,elapsedSeconds=time.monotonic()-started,
        trackingSeconds=sum(times),trackingP50=float(np.median(times)),trackingP95=float(np.quantile(times,.95)),
        reasons=dict(Counter(r.get('reason',r['status']) for r in tracks.values())),
        releaseEligible=False,genuineActionAccuracy=None))
    # Reusable direct CLI requests and visual evidence for the known scroll and a Home arrival.
    choices=[]
    for lane,term in [('retention-contrast','Accessibility Shortcut'),('real-development-contrast','home')]:
        choice=next(c for c in rows if c['lane']==lane and c['kind']=='forward' and c['truth']=='arrival' and term in ' '.join(c['group']))
        choices.append(choice)
    cli=[]
    for i,c in enumerate(choices):
        ga,gb=[inv['geometry'][c[k]] for k in ('before','after')]
        request=dict(version=1,before=ga['original'],after=gb['original'],beforeBounds=c['anchor'],
            context=dict(sameScene=True,settled=True,fresh=True,identityVerified=True))
        req=out/f'request-{i}.json';h.write(req,request)
        dest=out/f'verify-{i}.json'
        command=[sys.executable,str(h.ROOT/'scripts/focus_transition_verifier.py'),'--request',str(req),'--output',str(dest),'--enable-experimental']
        if common:command.append('--common-support')
        p=subprocess.run(command,cwd=h.ROOT,env=os.environ.copy(),capture_output=True,text=True,timeout=120)
        h.require(p.returncode==0,'actual_verify_cli_failed')
        actual=h.read(dest);h.require(actual['decision']==c['arms']['alignedGated'],'verify_replay_differs')
        cli.append(dict(request=h.ref(req),result=h.ref(dest),exitCode=p.returncode))
        panel=Image.new('RGB',(1024,600),'#222222');draw=ImageDraw.Draw(panel)
        for j,g in enumerate((ga,gb)):
            with Image.open(h.checked(h.ROOT,g['original'])) as im:
                im.thumbnail((512,288));panel.paste(im,(j*512,0))
        for j,(g,b) in enumerate([(ga,c['anchor']),(gb,c['anchor'])]):
            panel.paste(crop(paired.crop_key(g,b)),(j*256,320))
        if c['tracking']['status']=='matched':panel.paste(crop(paired.crop_key(gb,c['tracking'].get('afterCropBounds',c['tracking']['afterBounds']))),(512,320))
        draw.text((5,300),'Before crop | unaligned after | aligned after; '+c['arms']['alignedGated'],fill='white')
        panel.save(out/f'example-{i}.png')
    h.write(out/'cli.json',dict(cases=cli))
    print('tracking',dict(Counter(r['status'] for r in tracks.values())),flush=True)
    for arm in ('fdr021','combined-clipping-followup','alignedRaw','alignedGated'):
        print(arm,dict(Counter(r['outcomes'][arm] for r in frames if r['eligible'])))
    print('seconds',time.monotonic()-started,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    p.add_argument('--common-support',action='store_true')
    args=p.parse_args();run(args.output,args.common_support)
