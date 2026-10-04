"""Analytic paired-image transforms shared by diagnostics and opt-in training."""
from PIL import Image
import math
import human_annotation_review as h

CONDITIONS=('baseline','reverse','left','right','up','down')
DEFAULT_POLICY='paired-translation-4pct-v1'
BROAD_POLICY='paired-translation-25x15pct-v1'
COMPRESSED_POLICY='paired-halfwidth-25x15pct-v1'
POLICIES=(DEFAULT_POLICY,BROAD_POLICY,COMPRESSED_POLICY)


def transform(images, boxes, condition,policy=DEFAULT_POLICY):
    h.require(condition in CONDITIONS,'unknown_transform')
    h.require(policy in POLICIES,'unknown_augmentation_policy')
    size=images[0].size
    h.require(len(images)==len(boxes)==2 and all(im.size==size for im in images),'image_dimensions')
    if policy!=DEFAULT_POLICY:
        h.require(condition!='reverse','unsupported_policy_condition')
        if condition=='baseline':return translate(images,boxes,0,0)
        valid,_=translate(images,boxes,0,0)
        h.require(valid is not None,'invalid_source_boxes')
        dx=round(size[0]*.25)*({'left':-1,'right':1}.get(condition,0))
        dy=round(size[1]*.15)*({'up':-1,'down':1}.get(condition,0))
        if policy==BROAD_POLICY:return translate(images,boxes,dx,dy)
        width=max(1,round(size[0]*.5));scale=width/size[0];offset=(size[0]-width)//2+dx
        truth=[[x*scale+offset,y+dy,w*scale,height] for x,y,w,height in boxes]
        if any(x<0 or y<0 or x+w>size[0] or y+height>size[1] for x,y,w,height in truth):return None,None
        result=[]
        for image in images:
            out=Image.new('RGB',size)
            out.paste(image.resize((width,size[1]),Image.Resampling.BILINEAR),(offset,dy));result.append(out)
        return result,truth
    if condition=='reverse':return list(reversed(images)),list(reversed(boxes))
    dx=round(size[0]*.04)*({'left':-1,'right':1}.get(condition,0))
    dy=round(size[1]*.04)*({'up':-1,'down':1}.get(condition,0))
    return translate(images,boxes,dx,dy)


def translate(images,boxes,dx,dy):
    h.require(type(dx)is int and type(dy)is int,'translation_integer_pixels')
    h.require(len(images)==len(boxes)==2 and images[0].size==images[1].size,'image_dimensions')
    h.require(all(len(b)==4 and all(type(v) in (int,float) and math.isfinite(v) for v in b) for b in boxes),'translation_boxes')
    size=images[0].size
    truth=[[x+dx,y+dy,w,h] for x,y,w,h in boxes]
    if any(x<0 or y<0 or w<=0 or h<=0 or x+w>size[0] or y+h>size[1] for x,y,w,h in truth):
        return None,None
    if dx==dy==0:return images,truth
    shifted=[]
    for im in images:
        out=Image.new('RGB',size);out.paste(im,(dx,dy));shifted.append(out)
    return shifted,truth
