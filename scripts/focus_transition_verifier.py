"""Opt-in, offline translation-aware focus diagnostic. Never sends controls."""
import argparse
import base64
import io
import math
import time

import cv2
import numpy as np
from PIL import Image
import human_annotation_review as h
import focus_paired_growth as paired
import focus_runtime as native

VERSION='focus-transition-diagnostic-v1'
POLICY=dict(templateFraction=.7,maxBodyWidth=256,searchX=.25,searchYHeights=3,
            searchYViewport=.1,minCorrelation=.55,minPeakGap=.08,minTexture=.01,
            reciprocal=.15,illumination=.04)


def unavailable(reason,**fields):
    return dict(status='unavailable',reason=reason,**fields)


def footprint(bounds,size):
    x,y,w,ht=bounds;W,H=size
    return [max(0,.16*w-x),max(0,.16*ht-y),max(0,x+1.16*w-W),max(0,y+1.16*ht-H)]


def common_support(before,after,size):
    """Trim equal context from both translated windows; never fit each state."""
    h.require(before[2:]==after[2:],'window_scale_changed')
    w,ht=before[2:]
    cuts=[max(a,b) for a,b in zip(footprint(before,size),footprint(after,size))]
    if any(c>margin+1e-7 for c,margin in zip(cuts,[.16*w,.16*ht,.16*w,.16*ht])):
        return None
    left,top,right,bottom=cuts
    cw=(1.32*w-left-right)/1.32;ch=(1.32*ht-top-bottom)/1.32
    windows=[[x-.16*w+left+.16*cw,y-.16*ht+top+.16*ch,cw,ch] for x,y,_,_ in (before,after)]
    sizes=[]
    for b in windows:
        l,t,r,bt=footprint(b,size)
        sizes.append([math.floor(1.32*b[2]-l-r+.5),math.floor(1.32*b[3]-t-bt+.5)])
    return windows if sizes[0]==sizes[1] and min(sizes[0])>0 else None


def gradient(image,scale):
    a=np.asarray(image.convert('RGB'),dtype=np.float32)/255
    y=a@np.array([.2126,.7152,.0722],dtype=np.float32)
    if scale<1:y=cv2.resize(y,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
    dx=cv2.Sobel(y,cv2.CV_32F,1,0,ksize=3);dy=cv2.Sobel(y,cv2.CV_32F,0,1,ksize=3)
    return cv2.magnitude(dx,dy)


def locate(a,b,bounds,scale):
    x,y,w,ht=[v*scale for v in bounds];H,W=a.shape
    tw=max(3,int(w*.7));th=max(3,int(ht*.7))
    left=int(round(x+(w-tw)/2));top=int(round(y+(ht-th)/2))
    if left<0 or top<0 or left+tw>W or top+th>H:return unavailable('template_outside')
    template=a[top:top+th,left:left+tw]
    texture=float(template.std())
    if texture<POLICY['minTexture']:return unavailable('low_texture',texture=texture)
    rx=max(2,int(math.ceil(w*.25)));ry=max(2,int(math.ceil(max(3*ht,.1*H))))
    lx=max(0,left-rx);ty=max(0,top-ry)
    right=min(W,left+tw+rx);bottom=min(H,top+th+ry)
    scores=cv2.matchTemplate(b[ty:bottom,lx:right],template,cv2.TM_CCOEFF_NORMED)
    scores=np.nan_to_num(scores,nan=-1,posinf=-1,neginf=-1)
    _,best,_,(px,py)=cv2.minMaxLoc(scores)
    alternate=scores.copy();radius=max(2,int(math.ceil(.3*ht)))
    alternate[max(0,py-radius):py+radius+1,max(0,px-radius):px+radius+1]=-1
    gap=float(best-alternate.max())
    if best<POLICY['minCorrelation'] or gap<POLICY['minPeakGap']:
        return unavailable('ambiguous_texture',correlation=best,peakGap=gap)
    return dict(status='matched',dx=(px+lx-left)/scale,dy=(py+ty-top)/scale,
                correlation=best,peakGap=gap,texture=texture)


def track(before,after,bounds,*,common=False):
    paired.box(bounds);x,y,w,ht=bounds;W,H=before.size
    h.require(W*H<=40_000_000,'image_pixel_limit')
    if before.size!=after.size:return unavailable('viewport_changed')
    if x+w>W or y+ht>H:return unavailable('body_outside')
    if np.array_equal(np.asarray(before),np.asarray(after)):
        return dict(status='identical',dx=0.,dy=0.,afterBounds=list(bounds))
    scale=min(1.,256/w);a=gradient(before,scale);b=gradient(after,scale)
    forward=locate(a,b,bounds,scale)
    if forward['status']!='matched':return forward
    translated=[x+forward['dx'],y+forward['dy'],w,ht]
    if translated[0]<0 or translated[1]<0 or translated[0]+w>W or translated[1]+ht>H:
        return unavailable('translated_body_outside',forward=forward)
    backward=locate(b,a,translated,scale)
    if backward['status']!='matched':return unavailable('reciprocal_unavailable',forward=forward,backward=backward)
    error=math.hypot(forward['dx']+backward['dx'],forward['dy']+backward['dy'])*scale
    if error>max(2,.15*ht*scale):return unavailable('reciprocal_mismatch',forward=forward,backward=backward)
    if max(abs(p-q) for p,q in zip(footprint(bounds,before.size),footprint(translated,after.size)))>1:
        if common:
            windows=common_support(bounds,translated,before.size)
            if windows is not None:
                return dict(forward,afterBounds=translated,reciprocalError=error,
                            beforeCropBounds=windows[0],afterCropBounds=windows[1],commonSupport=True)
        return unavailable('clipping_footprint_changed',forward=forward)
    return dict(forward,afterBounds=translated,reciprocalError=error)


def compare_crops(before,after,clipped=False):
    raw=paired.predict(before,after,settled=True,matched=True,stable_context=True,fresh=True)
    growth=raw['growth'] if not clipped else 'unavailable'
    signals={s for s in (growth,raw['brightness']) if s not in ('unknown','unavailable')}
    combined=next(iter(signals)) if len(signals)==1 else 'unknown'
    delta=(np.asarray(after.convert('RGB'),dtype=float)-np.asarray(before.convert('RGB'),dtype=float))@np.array([.2126,.7152,.0722])/255
    border=np.ones((256,256),dtype=bool);border[24:-24,24:-24]=False
    illumination=float(np.median(delta[border]));warning=abs(illumination)>.04
    return dict(rawCombined=combined,decision='unknown' if warning else combined,
                illuminationWarning=warning,borderLumaDelta=illumination,
                growth=growth,brightness=raw['brightness'],measurement=raw)


def verify(request,enabled,*,common=False):
    result=dict(version=VERSION,diagnosticOnly=True,releaseEligible=False,controlIssued=False)
    if not enabled:return dict(result,status='disabled',decision='unavailable')
    h.require(type(request.get('version')) is int and request['version']==1,'request_version')
    h.require(set(request)=={'version','before','after','beforeBounds','context'},'request_fields')
    flags=request.get('context',{})
    h.require(isinstance(flags,dict) and set(flags)=={'sameScene','settled','fresh','identityVerified'},'context_fields')
    for name in ('sameScene','settled','fresh','identityVerified'):
        h.require(type(flags.get(name)) is bool,'context_boolean_required')
    if not all(flags.values()):return dict(result,status='unavailable',decision='unavailable',reason='context_not_verified')
    bounds=request['beforeBounds'];paired.box(bounds)
    refs=[request[k] for k in ('before','after')];paths=[h.checked(h.ROOT,r) for r in refs]
    ims=[]
    for path in paths:
        with Image.open(path) as im:
            h.require(im.width*im.height<=40_000_000,'image_pixel_limit');ims.append(im.convert('RGB'))
    start=time.monotonic();tracking=track(*ims,bounds,common=common)
    result.update(tracking=tracking,inputs=refs,policy=POLICY,commonSupportEnabled=common)
    if tracking['status']=='identical':return dict(result,status='available',decision='unchanged',elapsedSeconds=time.monotonic()-start)
    if tracking['status']!='matched':return dict(result,status='unavailable',decision='unavailable',elapsedSeconds=time.monotonic()-start)
    identity=native.identity()
    windows=[tracking.get('beforeCropBounds',bounds),tracking.get('afterCropBounds',tracking['afterBounds'])]
    items=[dict(id=str(i),path=str(path),sha256=ref['sha256'],bounds=b) for i,(path,ref,b) in enumerate(zip(paths,refs,windows))]
    crops=[Image.open(io.BytesIO(base64.b64decode(r['png'],validate=True))).convert('RGB') for r in native.invoke(items)['results']]
    h.require(native.identity()==identity,'runtime_changed')
    decision=compare_crops(*crops,clipped=any(footprint(bounds,ims[0].size)))
    return dict(result,status='available',**decision,runtime=identity,elapsedSeconds=time.monotonic()-start)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--request',required=True);p.add_argument('--output',required=True)
    p.add_argument('--enable-experimental',action='store_true')
    p.add_argument('--common-support',action='store_true',help='Also enable isolated equal-context clipping correction')
    a=p.parse_args();out=h.fresh(a.output)
    result=verify(h.read(h.local(a.request)),a.enable_experimental,common=a.common_support)
    h.write(out,result);print(result['status'],result['decision'])


if __name__=='__main__':main()
