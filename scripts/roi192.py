"""Training-only ROI feasibility; never creates pixels, labels or model outputs."""
import collections
import math
import statistics
from PIL import Image
import fit175 as f
h,p,e=f.h,f.p,f.e
OUT=h.ROOT/'reports/work/IOS-ROI-192/artifacts'


def window(width,height,box):
    h.require(all(math.isfinite(x) for x in [width,height,*box]) and width>0 and height>0,'dimensions')
    x1,y1,x2,y2=box
    h.require(0<=x1<x2<=width and 0<=y1<y2<=height,'box')
    side=width/2
    h.require(side<=height,'unsupported_aspect_ratio')
    left=min(max((x1+x2-side)/2,0),width-side)
    top=min(max((y1+y2-side)/2,0),height-side)
    return [left,top,left+side,top+side]


def support(box,width,height,roi):
    w,ht=box[2]-box[0],box[3]-box[1]
    return {name:dict(width=w*scale,height=ht*scale,stride8Height=ht*scale/8)
            for name,scale in [('full640',640/max(width,height)),('full1280',1280/max(width,height)),('roi640',640/(roi[2]-roi[0]))]}


def intersect(a,b):
    return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))


def run():
    h.require(not OUT.exists(),'output_collision')
    protocol=f.inputs(); metadata=protocol['metadata']
    request=e.load_request(f.OUT/'input.json',41)
    membership=p.sealed(h.checked(h.ROOT,f.d.inputs()['membership']))
    roles={r['id']:r['split'] for r in membership['rows']}
    h.require(len(request.images)==216 and all(roles[im.image_id]=='train' for im in request.images),'training_only')
    cid=e.load_names().index('pageControl');rows=[]
    for im in request.images:
        with Image.open(im.image_path) as image:h.require(image.size==(im.width,im.height),'dimensions_changed')
        boxes=f.d.prior.truth(im,cid);h.require(len(boxes)==1,'page_support');box=list(boxes[0])
        roi=window(im.width,im.height,box);clipped=0;contained=0
        for line in im.label_path.read_text().splitlines():
            if not line.strip():continue
            _,cx,cy,w,ht=map(float,line.split());other=[(cx-w/2)*im.width,(cy-ht/2)*im.height,(cx+w/2)*im.width,(cy+ht/2)*im.height]
            area=(other[2]-other[0])*(other[3]-other[1]);overlap=intersect(roi,other)
            if overlap>0:
                if math.isclose(overlap,area,rel_tol=1e-8):contained+=1
                else:clipped+=1
        rows.append(dict(id=im.image_id,image=h.ref(im.image_path),label=h.ref(im.label_path),metadata=metadata[im.image_id],
            window=roi,target=box,targetContained=math.isclose(intersect(roi,box),(box[2]-box[0])*(box[3]-box[1]),rel_tol=1e-8),
            support=support(box,im.width,im.height,roi),incidentalClipped=clipped,containedAnnotations=contained))
    summary={}
    for mode in ('full640','full1280','roi640'):
        values=[r['support'][mode]['height'] for r in rows]
        summary[mode]=dict(minHeight=min(values),medianHeight=statistics.median(values),maxHeight=max(values),
                           below8Pixels=sum(v<8 for v in values),below4Pixels=sum(v<4 for v in values))
    OUT.mkdir(parents=True)
    h.write(OUT/'feasibility.json',dict(rows=rows,summary=summary,source=h.ref(__file__),protocol=h.ref(f.OUT/'protocol.json'),
        targetContained=sum(r['targetContained'] for r in rows),framesWithClippedAnnotations=sum(r['incidentalClipped']>0 for r in rows),
        placement=dict(collections.Counter(r['metadata']['placement'] for r in rows)),
        interpretation='Training-truth-centered representation upper bound only; not inference localization or glyph-pixel measurement.',
        trainingEligible=False,trainingLaunched=False,imagesGenerated=False,productionEligible=False),sealed=True)
    h.require(sum(x.stat().st_size for x in OUT.iterdir())<8*1024**2,'output_budget')
    print(summary,flush=True)


if __name__=='__main__':run()
