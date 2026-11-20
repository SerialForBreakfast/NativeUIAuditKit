"""Project the two native row recipes with a rectangular viewport and opaque top cover."""
from PIL import Image
import research_queue as q


def intersect(a, b):
    return [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]


def area(b):
    return max(0,b[2]-b[0])*max(0,b[3]-b[1])


def project(doc, png):
    q.require(q.digest(png)==doc['sha256'], 'row_image_binding')
    with Image.open(png) as im:
        size=im.size
    scale=doc['scale']
    q.require(scale in (2,3) and size==(320*scale,320*scale), 'row_scale')
    viewport=doc['viewport']
    cover=doc['overlay']
    q.require(doc['stage'] in ('initial','scroll','covered','restored') and
              bool(cover)==(doc['stage']=='covered'), 'row_presentation')
    visible=viewport.copy()
    if cover:
        q.require(cover[:3]==viewport[:3] and viewport[1]<cover[3]<viewport[3], 'unsupported_cover')
        visible[1]=cover[3]
    objects=doc['rows']
    q.require(len({r['id'] for r in objects})==len(objects),'row_duplicate')
    primitive={'UIKit':'UITableViewCell','SwiftUI':'List.Row'}.get(doc['framework'])
    q.require(primitive is not None,'row_framework')
    controls=[]; ownership=[]
    for r in objects:
        q.require(r['primitive']==primitive and r['captionOwner']==r['id'],'row_owner')
        body=r['edges']
        q.require(area(body)>0 and intersect(body,r['caption'])==r['caption'],'caption_bounds')
        clipped=intersect(body,visible)
        caption = intersect(r['caption'], visible)
        ownership.append(dict(id=r['id'],caption='owned_metadata',targetVisible=bool(area(clipped)),
                              captionVisibleEdges=caption if area(caption) else None,
                              visibleRowEdges=clipped if area(clipped) else None))
        if area(clipped):
            l,t,rr,b=clipped
            controls.append(dict(id=f"row-{r['id']}",bounds=[l,t,rr-l,b-t], **{'class':'cell'}))
    return controls,ownership
