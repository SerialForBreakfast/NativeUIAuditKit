"""Measure detector-centered regions without using focus labels as inputs."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
import numpy as np
import boundary329 as a

b=a.b; r=a.r; t=a.t; OUT=b.ROOT/'reports/work/FOCUS-330'
BINARY=b.ROOT/'.build/debug/nativeui-audit'


def boxes(payload):
    b.require(payload.get('status') in ('success','degraded'),'scan_failed')
    b.require(payload['configuration']==dict(minConfidence=.25,ocr=False,platform='tvOS',strict=False),'scan_settings')
    w,h=payload['width'],payload['height']; result=[]
    for item in payload['runtime']['result']['elements']:
        if item['confidenceSource']!='pixelModel' or item['confidence']<.25:continue
        rect=item['boundingBoxPixels'];x,y,width,height=[rect[k] for k in ('x','y','width','height')]
        b.require(np.isfinite([x,y,width,height]).all() and min(width,height)>0,'invalid_box')
        x0,y0=max(0,x),max(0,y);x1,y1=min(w,x+width),min(h,y+height)
        if x1<=x0 or y1<=y0:continue
        result.append([x0,y0,x1-x0,y1-y0])
    return result


def collect():
    b.require(not (OUT/'detections.json').exists(),'output_collision')
    membership=b.read(b.PACKAGE/'membership.json'); pins={}
    for row in membership['rows']:
        if row['role']=='train':
            for pin in row['images']:b.checked(pin);pins.setdefault(pin['sha256'],pin)
    items=sorted(pins.items()); binary=b.ref(BINARY); results={};identity=None;start=time.monotonic()
    b.write(OUT/'detector-registration.json',dict(binary=binary,membership=b.ref(b.PACKAGE/'membership.json'),
        images=[p for _,p in items],confidence=.25,ocr=False,role='train',timeoutSeconds=120,
        purpose='Control proposals only. Ignore all predicted focus states.'))
    for offset in range(0,len(items),32):
        subset=items[offset:offset+32]
        messages=[dict(jsonrpc='2.0',id=0,method='initialize',params=dict(protocolVersion='2025-11-25',capabilities={},clientInfo=dict(name='focus330',version='1')))]
        messages.append(dict(jsonrpc='2.0',method='notifications/initialized'))
        for n,(_,pin) in enumerate(subset,1):
            messages.append(dict(jsonrpc='2.0',id=n,method='tools/call',params=dict(name='audit_screenshot',
                arguments=dict(imagePath=str(b.checked(pin)),platform='tvOS',minConfidence=.25,ocr=False))))
        process=subprocess.run([str(BINARY),'mcp','--root',str(b.ROOT)],input='\n'.join(map(json.dumps,messages))+'\n',
            text=True,capture_output=True,timeout=120,env=dict(os.environ,TMPDIR=str(b.ROOT/'.build/direct53-tmp')))
        b.write(OUT/f'detector-batch-{offset:03d}.json',dict(exit=process.returncode,stdout=process.stdout,stderr=process.stderr))
        b.require(process.returncode==0,'detector_process')
        replies=[json.loads(line) for line in process.stdout.splitlines()]
        b.require(len(replies)==len(subset)+1,'reply_count')
        for n,((digest,pin),reply) in enumerate(zip(subset,replies[1:]),1):
            b.require(reply['id']==n and 'result' in reply,'reply_order_or_error');payload=reply['result']['structuredContent']
            b.require(payload['inputSHA256']==digest,'image_identity')
            current=payload['runtime']['detector'];identity=identity or current
            b.require(identity==current,'model_changed')
            results[digest]=dict(image=pin,size=[payload['width'],payload['height']],boxes=boxes(payload),totalMs=payload['totalMs'])
        print('Scored unique frames',len(results),'/',len(items),flush=True)
    b.require(b.ref(BINARY)==binary,'binary_changed')
    b.write(OUT/'detections.json',dict(registration=b.ref(OUT/'detector-registration.json'),model=identity,
        rows=results,seconds=time.monotonic()-start))


def iou(x,y):
    left=max(x[0],y[0]);top=max(x[1],y[1]);right=min(x[0]+x[2],y[0]+y[2]);bottom=min(x[1]+x[3],y[1]+y[3])
    overlap=max(0,right-left)*max(0,bottom-top)
    return overlap/(x[2]*x[3]+y[2]*y[3]-overlap)


def encoded_box(box,size):
    w,h=size;scale=min(192/w,128/h);rw,rh=round(w*scale),round(h*scale)
    x,y,bw,bh=box
    return [x*rw/w+(192-rw)//2,y*rh/h+(128-rh)//2,bw*rw/w,bh*rh/h]


def select(value,proposals,size):
    """Rank fixed windows by pixel change. Do not read labels or scene metadata."""
    b.require(value.shape==(6,128,192) and np.isfinite(value).all(),'input_shape')
    delta=np.abs(value[3:]-value[:3]).mean(0); candidates={}
    for box in proposals:
        x,y,w,h=encoded_box(box,size)
        px=int(np.clip(round(x+w/2-16),0,160));py=int(np.clip(round(y+h/2-16),0,96))
        candidates[(px,py)]=float(delta[py:py+32,px:px+32].sum())
    selected=[]
    for (x,y),score in sorted(candidates.items(),key=lambda v:(-v[1],v[0])):
        if score<=0:continue
        if any(x<X+32 and x+32>X and y<Y+32 and y+32>Y for X,Y in selected):continue
        selected.append((x,y))
        if len(selected)==2:break
    return selected


def summarize(rows,key):
    values=[v[key] for v in rows if v[key] is not None]
    return dict(rows=len(values),median=float(np.median(values)) if values else None,mean=float(np.mean(values)) if values else None)


def audit():
    b.require(not (OUT/'audit.json').exists(),'output_collision');t.set_num_threads(2);start=time.monotonic()
    detections=b.read(OUT/'detections.json');membership=b.read(b.PACKAGE/'membership.json')
    previous=b.read(a.OUT/'audit.json');old={v['index']:v for v in previous['rows']}
    values=np.load(b.PACKAGE/'native.npy',allow_pickle=False,mmap_mode='r');records=[]
    for i,row in enumerate(membership['rows']):
        if row['role']!='train':continue
        scenes,error=a.scenes_for(row);paired,_,error=a.bodies(row,scenes) if not error else (None,[],error)
        b.require(error is None,'geometry_unavailable')
        frames=[r.s.image(pin['path'],pin['sha256']) for pin in row['images']]
        b.require(np.array_equal(r.s.encoded(*frames,(192,128))[0],values[i]),'encoded_parity')
        observed=[detections['rows'][pin['sha256']] for pin in row['images']]
        b.require(all(v['size']==list(frames[0].size) for v in observed),'dimension_mismatch')
        proposals=[box for frame in observed for box in frame['boxes']]
        selected=select(values[i],proposals,frames[0].size)
        oracle=select(values[i],[box for pair in paired for box in pair],frames[0].size)
        delta=np.abs(np.asarray(frames[1],dtype=np.float32)/255-np.asarray(frames[0],dtype=np.float32)/255).mean(2)
        inner,band=a.masks(delta.shape,paired);scores={}
        for name,windows in [('detector',selected),('known',oracle)]:
            mask=np.zeros(delta.shape,bool)
            for x,y in windows:
                x0,y0,x1,y1=a.source_window((x,y,x+32,y+32),frames[0].size)
                a.fill(mask,(x0,y0,x1-x0,y1-y0))
            score=a.measure(delta,inner,band,mask)
            scores[name+'Coverage']=score['proposalBoundaryCoverage'];scores[name+'Purity']=score['proposalBoundaryPurity']
        matches=[max([iou(body,box) for box in observed[n]['boxes']],default=0.) for pair in paired for n,body in enumerate(pair)]
        records.append(dict(index=i,id=row['id'],group=row['group'],conditions=row['conditions'],changed=row['changed'],
            windows=selected,knownWindows=oracle,controlMatches=matches,controls=len(matches),matched=sum(v>=.5 for v in matches),
            oldCoverage=old[i]['proposalBoundaryCoverage'],oldPurity=old[i]['proposalBoundaryPurity'],**scores))
        if len(records)%100==0:print('Audited',len(records),flush=True)
    summary={}
    for name,subset in [('all',records),('content',[v for v in records if 'content_contrast' in v['conditions']])]:
        summary[name]={key:summarize(subset,key) for key in ('oldCoverage','detectorCoverage','knownCoverage','oldPurity','detectorPurity')}
        summary[name]['recall']=sum(v['matched'] for v in subset)/sum(v['controls'] for v in subset)
        summary[name]['emptyProposals']=sum(not v['windows'] for v in subset)
    # Freeze this support rule before measuring. It does not define a deployment gate.
    justified=all(summary[k]['detectorCoverage']['median']>summary[k]['oldCoverage']['median']+.05 for k in ('all','content'))
    b.write(OUT/'audit.json',dict(detections=b.ref(OUT/'detections.json'),source=b.ref(Path(__file__)),
        prior=b.ref(a.OUT/'audit.json'),rows=records,summary=summary,candidateJustified=justified,
        supportRule='Median boundary coverage improves by more than 0.05 on all training rows and content rows.',
        seconds=time.monotonic()-start,knownBoxesDiagnosticOnly=True,rolesChanged=False))
    print(json.dumps(dict(summary=summary,candidateJustified=justified)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['collect','audit'])
    globals()[parser.parse_args().mode]()
