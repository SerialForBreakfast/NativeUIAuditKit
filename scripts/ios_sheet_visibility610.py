"""Project the visible, connected control bodies in the bounded native sheet recipes."""
import cv2
import numpy as np


def visible_body(edges, cover):
    l,t,r,b=edges
    h,w=cover.shape
    if not (0<=l<r<=w and 0<=t<b<=h):
        raise ValueError("invalid_source_box")
    remaining=(~cover[t:b,l:r]).astype('uint8')
    n=int(remaining.sum())
    fraction=n/remaining.size
    if n==0:
        return dict(disposition='fully_hidden',visibleFraction=0)
    if n==remaining.size:
        return dict(disposition='visible',bounds=[l,t,r-l,b-t],visibleFraction=1)
    count,_,stats,_=cv2.connectedComponentsWithStats(remaining,connectivity=4)
    fragments=[[l+int(x),t+int(y),int(width),int(height)] for x,y,width,height,_ in stats[1:]]
    if count>2:
        return dict(disposition='fragmented_context',visibleFraction=fraction,fragments=fragments)
    return dict(disposition='partial',visibleFraction=fraction,bounds=fragments[0])


def footprint(white,black,level=128):
    if white.shape!=black.shape or white.ndim!=3:
        raise ValueError("calibration_shape")
    delta=white.astype('int16')-black.astype('int16')
    return np.min(delta,axis=2)>=level
