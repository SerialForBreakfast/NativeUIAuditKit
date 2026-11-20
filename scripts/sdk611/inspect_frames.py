"""Locate a tinted surface in actual compositor pixels and join to display-link timing."""
import cv2
import numpy as np
from PIL import Image

def rgb(path):
    with Image.open(path) as im:return np.asarray(im.convert('RGB'))

def sheet_pixels(array):
    r,g,b=np.moveaxis(array.astype('int16'),2,0)
    mask=((r-g>27)&(r-b>20)).astype('uint8')
    _,_,stats,_=cv2.connectedComponentsWithStats(mask)
    candidates=[v for v in stats[1:] if v[2]>array.shape[1]*.55 and v[4]>array.shape[1]*5]
    if not candidates:return None
    return [int(v) for v in max(candidates,key=lambda v:v[4])[:4]]

def closest(trace,t):
    return min(trace,key=lambda r:abs(r['t']-t))

def anchored_frames(folder):
    import json
    frames=json.loads((folder/'frames.json').read_text());trace=json.loads((folder/'trace.json').read_text())
    assert trace and frames
    selected=[]
    for f in frames:
        mid=(f['start']+f['end'])/2
        if mid<trace[0]['t'] or mid>trace[-1]['t']:continue
        obs=closest(trace,mid)
        window=[s for s in trace if f['start']-.05<=s['t']<=f['end']+.05]
        if not window or len(obs['geometry'])!=16:continue
        surface=sheet_pixels(rgb(folder/f['png']))
        selected.append(dict(**f,phase=obs['phase'],relative=mid-trace[0]['t'],surface=surface,
                             native=obs.get('surface'),scale=obs['scale'],geometry=obs['geometry'],
                             nativeRange=[s['surface'][1] for s in window if 'surface' in s]))
    return selected
