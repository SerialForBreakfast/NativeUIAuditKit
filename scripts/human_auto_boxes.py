"""Bounded raster rectangle proposals; no semantic labels, model or focus claims."""
import numpy as np
from PIL import Image, ImageFilter


def overlap(a, b):
    """Containment overlap suppresses repeated/nested proposals inside existing boxes."""
    (x,y),(r,t)=a; (u,v),(s,z)=b
    intersection=max(0,min(r,s)-max(x,u))*max(0,min(t,z)-max(y,v))
    return intersection/max(1,min((r-x)*(t-y),(s-u)*(z-v)))


def regions(mask):
    """Four-connected run-length components: linear overlap walk, bounded raster."""
    parents=[]; runs=[]; previous=[]
    def root(i):
        while parents[i]!=i:
            parents[i]=parents[parents[i]]; i=parents[i]
        return i
    for y,row in enumerate(mask):
        changes=np.flatnonzero(np.diff(np.pad(row.astype(np.int8),(1,1))))
        current=[]; j=0
        for left,right in zip(changes[::2],changes[1::2]):
            left,right=int(left),int(right)
            i=len(parents); parents.append(i)
            while j<len(previous) and previous[j][1]<=left: j+=1
            k=j
            while k<len(previous) and previous[k][0]<right:
                parents[root(previous[k][2])]=root(i); k+=1
            current.append((left,right,i)); runs.append((left,right,y,i))
        previous=current
    boxes={}
    for left,right,y,i in runs:
        key=root(i)
        if key not in boxes: boxes[key]=[left,y,right,y+1,0]
        b=boxes[key]; b[0]=min(b[0],left); b[1]=min(b[1],y)
        b[2]=max(b[2],right); b[3]=max(b[3],y+1); b[4]+=right-left
    return boxes.values()


def outlined_rectangles(dx, dy, w, h):
    """Pair long horizontal boundaries, then verify both vertical sides.

    Unlike connected contours this can tolerate artwork touching a card edge.
    This is still geometry, not evidence that the region is interactive.
    """
    lines=[]
    for y,row in enumerate(dy>=8):
        # Close at most four-pixel gaps along the horizontal boundary only.
        padded=np.pad(row,(2,2))
        dilated=np.logical_or.reduce([padded[i:i+w] for i in range(5)])
        padded=np.pad(dilated,(2,2))
        closed=np.logical_and.reduce([padded[i:i+w] for i in range(5)])
        changes=np.flatnonzero(np.diff(np.pad(closed.astype(np.int8),(1,1))))
        for l,r in zip(changes[::2],changes[1::2]):
            if r-l<32: continue
            if any(abs(y-yy)<=2 and abs(l-ll)<=3 and abs(r-rr)<=3 for ll,rr,yy in lines[-30:]): continue
            lines.append((int(l),int(r),y))
    lines=sorted(sorted(lines,key=lambda p:-(p[1]-p[0]))[:300],key=lambda p:p[2])
    result=[]
    for i,(l,r,t) in enumerate(lines):
        for ll,rr,b in lines[i+1:]:
            if b-t<16 or abs(l-ll)>8 or abs(r-rr)>8 or (b-t)*(r-l)>w*h*.30: continue
            middle=slice(t+3,b-2)
            lefts=range(max(1,min(l,ll)-8),min(w-2,max(l,ll)+4))
            rights=range(max(1,min(r,rr)-4),min(w-2,max(r,rr)+8))
            if not lefts or not rights: continue
            def strength(x): return float(np.mean(np.max(dx[middle,max(0,x-1):x+2],axis=1)>=8))
            left=max(lefts,key=strength); right=max(rights,key=strength)
            if min(strength(left),strength(right))<.75: continue
            if left<=1 or right>=w-2 or t<=1 or b>=h-2: continue
            result.append([left,t,right+1,b+1])
    return result


def detect(image, existing=(), limit=40):
    """Return deterministic two-corner rectangles in original top-left pixels."""
    width,height=image.size
    if width<=0 or height<=0 or width*height>80_000_000 or limit<=0:
        return []
    scale=min(1.,640/max(width,height))
    w,h=max(1,round(width*scale)),max(1,round(height*scale))
    rgb=np.asarray(image.convert('RGB').resize((w,h)).filter(ImageFilter.MedianFilter(3)),dtype=np.int16)
    edge=np.zeros((h,w),dtype=np.int16)
    dx=np.max(np.abs(np.diff(rgb,axis=1)),axis=2)
    dy=np.max(np.abs(np.diff(rgb,axis=0)),axis=2)
    edge[:,1:]=np.maximum(edge[:,1:],dx); edge[:,:-1]=np.maximum(edge[:,:-1],dx)
    edge[1:]=np.maximum(edge[1:],dy); edge[:-1]=np.maximum(edge[:-1],dy)
    proposals=[]
    for l,t,r,b in outlined_rectangles(dx,dy,w,h):
        points=[[l*width/w,t*height/h],[r*width/w,b*height/h]]
        if not any(overlap(points,box)>=.80 for box in existing):
            proposals.append((50.,(r-l)*(b-t),points))
    # Closed high-contrast outlines can enclose textured artwork rather than a
    # flat interior. Require sustained evidence along all four rectangle sides.
    outline=np.asarray(Image.fromarray((edge>=12).astype(np.uint8)*255).filter(ImageFilter.MaxFilter(3)))>0
    for left,top,right,bottom,_ in regions(outline):
        l,t,r,b=left+1,top+1,right-1,bottom-1
        bw,bh=r-l,b-t; area=bw*bh
        if bw<24 or bh<14 or area>w*h*.30 or bw>w*.96 or l<=1 or t<=1 or r>=w-1 or b>=h-1:
            continue
        border=[np.mean(np.max(edge[t:b,max(0,l-2):l+3],axis=1)>=12),
                np.mean(np.max(edge[t:b,r-3:min(w,r+2)],axis=1)>=12),
                np.mean(np.max(edge[max(0,t-2):t+3,l:r],axis=0)>=12),
                np.mean(np.max(edge[b-3:min(h,b+2),l:r],axis=0)>=12)]
        if min(border)<.75: continue
        points=[[l*width/w,t*height/h],[r*width/w,b*height/h]]
        if not any(overlap(points,box)>=.80 for box in existing):
            proposals.append((float(min(border))*40,area,points))
    for threshold in (10,24):
        for left,top,right,bottom,count in regions(edge<=threshold):
            bw,bh=right-left,bottom-top; area=bw*bh
            if bw<12 or bh<8 or area>w*h*.30 or bw>w*.96 or count/area<.68:
                continue
            # Interior components omit their sharp boundary pixels; restore one
            # pixel per side. Clipped controls and connected background abstain.
            l,t,r,b=left-1,top-1,right+1,bottom+1
            if l<=0 or t<=0 or r>=w or b>=h: continue
            contrast=[np.median(np.max(np.abs(rgb[t:b,l]-rgb[t:b,l-1]),axis=1)),
                      np.median(np.max(np.abs(rgb[t:b,r-1]-rgb[t:b,r]),axis=1)),
                      np.median(np.max(np.abs(rgb[t,l:r]-rgb[t-1,l:r]),axis=1)),
                      np.median(np.max(np.abs(rgb[b-1,l:r]-rgb[b,l:r]),axis=1))]
            if min(contrast)<5: continue
            points=[[l*width/w,t*height/h],[r*width/w,b*height/h]]
            if any(overlap(points,box)>=.80 for box in existing): continue
            proposals.append((float(min(contrast))*count/area,area,points))
    accepted=[]
    for _,_,points in sorted(proposals,key=lambda p:(-p[1],-p[0],p[2])):
        if not any(overlap(points,box)>=.80 for box in accepted):
            accepted.append(points)
        if len(accepted)>=min(40,limit): break
    return sorted(accepted,key=lambda p:(p[0][1],p[0][0]))
