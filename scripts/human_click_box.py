"""Experimental bounded flat-panel proposal. No labels, models, or file writes."""
from collections import deque
import math
import numpy as np
from PIL import Image, ImageFilter


def suggest(image, point):
    """Return top-left two-corner pixels or None. Deliberately abstain on weak cues."""
    width, height = image.size
    if width <= 0 or height <= 0 or width*height > 80000000:
        return None
    x, y = point
    if not all(math.isfinite(v) for v in (x,y)) or not (0 <= x < width and 0 <= y < height):
        return None
    scale = min(1., 640/max(width,height))
    w, h = max(1,round(width*scale)), max(1,round(height*scale))
    rgb = np.asarray(image.convert('RGB').resize((w,h)).filter(ImageFilter.MedianFilter(3)), dtype=np.int16)
    sx, sy = min(w-1,int(x*w/width)), min(h-1,int(y*h/height))
    distance = np.max(np.abs(rgb-rgb[sy,sx]),axis=2)
    candidates = []
    for threshold in (14,28,42):
        mask = distance <= threshold
        seen = np.zeros((h,w),dtype=bool)
        queue = deque([(sx,sy)]); points=[]
        while queue and len(points) <= 80000:
            px,py=queue.popleft()
            if px<0 or py<0 or px>=w or py>=h or seen[py,px] or not mask[py,px]:
                continue
            seen[py,px]=True; points.append((px,py))
            queue.extend(((px-1,py),(px+1,py),(px,py-1),(px,py+1)))
        if not points or len(points)>80000:
            continue
        coords=np.asarray(points); left,top=coords.min(axis=0); right,bottom=coords.max(axis=0)+1
        bw,bh=right-left,bottom-top; area=int(bw*bh)
        fill=len(points)/area
        if bw<12 or bh<8 or area>w*h*.30 or bw>w*.9 or fill<.72:
            continue
        # Require a visible contrast boundary on every side. Border-clipped controls
        # and large background regions need manual annotation in this prototype.
        if left==0 or top==0 or right==w or bottom==h:
            continue
        contrasts=[np.median(np.max(np.abs(rgb[top:bottom,left]-rgb[top:bottom,left-1]),axis=1)),
                   np.median(np.max(np.abs(rgb[top:bottom,right-1]-rgb[top:bottom,right]),axis=1)),
                   np.median(np.max(np.abs(rgb[top,left:right]-rgb[top-1,left:right]),axis=1)),
                   np.median(np.max(np.abs(rgb[bottom-1,left:right]-rgb[bottom,left:right]),axis=1))]
        if min(contrasts)<5:
            continue
        candidates.append((fill*float(min(contrasts)),[[float(left*width/w),float(top*height/h)],
                                                     [float(right*width/w),float(bottom*height/h)]]))
    return max(candidates,key=lambda pair:pair[0])[1] if candidates else None
