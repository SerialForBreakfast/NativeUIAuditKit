"""Measure paired OS-profile pixels. Do not infer focus or accept models."""
from pathlib import Path
import time
import numpy as np
from PIL import Image
import research_queue as q
from template_adapters395 import document, resolve_inputs
OUT=None


def run():
    start=time.monotonic()
    try:
        cfg=q.load(OUT.parents[2]/'spec.json')['template'];inputs=resolve_inputs(cfg,OUT)
        artifact=document(inputs['capture']);path=Path(artifact['path'])
        q.require(path.resolve()==path and path.is_relative_to('/Volumes/training-drive/data/NUIAK/HCF371'), 'capture_scope')
        q.require(q.digest(path)==artifact['sha256'], 'capture_changed')
        capture=q.load(path);q.require(capture['complete'] and capture['cleanup'], 'capture_incomplete')
        pairs={}
        for row in capture['frames']:
            key=(row['case'],row['focus'],row['repeat']);group=pairs.setdefault(key,{})
            q.require(row['profile'] not in group, 'duplicate_profile');group[row['profile']]=row
        reports=[]
        for key,pair in sorted(pairs.items()):
            q.require(set(pair)=={'standard','hcf'}, 'missing_profile')
            images=[]
            for profile in ('standard','hcf'):
                row=pair[profile];image=q.local_path(path.parent,row['path'])
                q.require(q.digest(image)==row['sha256'], 'image_changed')
                with Image.open(image) as opened:images.append(np.asarray(opened.convert('RGB'),dtype=np.int16))
            a,b=images;q.require(a.shape==b.shape, 'image_shape')
            delta=np.abs(a-b)
            reports.append(dict(case=key[0],focus=key[1],repeat=key[2],pixels=a.shape[0]*a.shape[1],
                changedPixels=int(np.count_nonzero(delta.max(axis=2))),meanAbsoluteChannelDifference=float(delta.mean()),
                standardNearWhitePixels=int(np.count_nonzero(a.min(axis=2)>=230)),
                hcfNearWhitePixels=int(np.count_nonzero(b.min(axis=2)>=230))))
        q.save(OUT/'report.json',dict(rows=reports,modelAccepted=False,
            limitation='Pixel differences are not focus labels. Native animation, highlights, and setting effects require separate interpretation.'))
        q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='report.json',sha256=q.digest(OUT/'report.json'))]))
        q.save(OUT/'template-result.json',dict(execution='complete',modelAccepted=False,seconds=time.monotonic()-start))
    except Exception as error:
        q.save(OUT/'template-result.json',dict(execution='failed',modelAccepted=False,code=str(error)[:500]));raise
