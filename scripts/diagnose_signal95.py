"""Multi-resolution signal diagnosis; ground-truth windows never enter prediction."""
import argparse
from collections import Counter
import math
import time
import numpy as np
from PIL import Image
import focus_direct_transition as d

SIZES=((96,64),(192,128),(384,256))


def source_coverage(rows,sources):
    counts=Counter()
    for row in rows:
        matches=[name for name,ref in sources.items() if row['id'].startswith(ref['sha256']+':')]
        d.h.require(len(matches)==1,'signal_source_identity')
        counts[matches[0],row['split'],row['changed']]+=1
    return [dict(source=source,split=split,changed=changed,pairs=count)
            for (source,split,changed),count in sorted(counts.items())]


def encoded(before,after,size):
    d.h.require(size in SIZES and before.size==after.size,'signal_size')
    W,H=size;w,h=before.size;s=min(W/w,H/h)
    rw,rh=max(1,round(w*s)),max(1,round(h*s));px,py=(W-rw)//2,(H-rh)//2
    images=[]
    for image in (before,after):
        canvas=Image.new('RGB',size)
        canvas.paste(image.resize((rw,rh),Image.Resampling.BILINEAR),(px,py))
        images.append(np.asarray(canvas,dtype=np.float32).transpose(2,0,1)/255)
    return np.concatenate(images), (rw/w,rh/h,px,py)


def metrics(x,boxes,original_size,transform):
    difference=np.abs(x[3:]-x[:3]);H,W=difference.shape[1:]
    sx,sy,px,py=transform;mask=np.zeros((H,W),dtype=bool)
    for box in boxes:
        d.target_box(box,original_size)
        left,top,w,h=box
        x0,y0=max(0,math.floor(left*sx+px)),max(0,math.floor(top*sy+py))
        x1,y1=min(W,math.ceil((left+w)*sx+px)),min(H,math.ceil((top+h)*sy+py))
        mask[y0:y1,x0:x1]=True
    d.h.require(mask.any(),'signal_empty_region')
    return dict(meanAbsolute=float(difference.mean()),maximum=float(difference.max()),
        nonzeroPixelFraction=float(np.any(difference>0,axis=0).mean()),
        identical=bool(np.array_equal(x[:3],x[3:])),
        truthRegionMean=float(difference[:,mask].mean()),truthRegionPixels=int(mask.sum()),
        truthRegionUse='diagnostic_only_not_prediction')


def run(output):
    h=d.h;start=time.monotonic();out=h.fresh(output)
    protocol_path=h.ROOT/'reports/work/CONTEXT-93/ready/protocol.json';p=h.read(protocol_path)
    h.require(p['protocolSHA256']==h.digest({k:v for k,v in p.items() if k!='protocolSHA256'}),'signal_protocol')
    corpus=h.read(h.checked(h.ROOT,p['corpus']))
    rows=d.admitted(corpus,h.read(h.checked(h.ROOT,p['admission'])))
    old=np.load(h.checked(h.ROOT,p['x']),allow_pickle=False)
    h.require(p['rowIDs']==[r['id'] for r in rows] and old.shape==(73,6,64,96),'signal_membership')
    results=[]
    for i,row in enumerate(rows):
        before,after=[d.pixels(ref) for ref in row['images']]
        for size in SIZES:
            x,transform=encoded(before,after,size)
            if size==SIZES[0]:h.require(np.array_equal(x,old[i]),'signal_base_encoding_changed')
            results.append(dict(id=row['id'],split=row['split'],changed=row['changed'],size=list(size),
                **metrics(x,row['boxes'],before.size,transform)))
    summaries=[]
    for size in SIZES:
        for split in ('train','development'):
            for changed in (False,True):
                values=[r for r in results if r['size']==list(size) and r['split']==split and r['changed']==changed]
                summaries.append(dict(size=list(size),split=split,changed=changed,pairs=len(values),
                    identical=sum(r['identical'] for r in values),
                    medianMeanAbsolute=float(np.median([r['meanAbsolute'] for r in values])) if values else None))
    out.mkdir(parents=True)
    report=dict(version='transition-resolution-diagnostic-v1',**h.FLAGS,
        protocol=h.ref(protocol_path),implementation=h.ref(__file__),baseEncodingParity=True,
        results=results,summaries=summaries,sourceCoverage=source_coverage(rows,corpus['sources']),
        elapsedSeconds=time.monotonic()-start,
        trainingLaunched=False,thresholdSelected=False,
        limitation='Exposed train/development signal measurements, not detector accuracy or resolution qualification.')
    h.write(out/'diagnostic.json',report,sealed=True)
    print(summaries);print('seconds',report['elapsedSeconds'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True)
    run(parser.parse_args().output)
