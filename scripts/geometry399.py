"""Bounded geometry diagnostics. Labels explain errors but never select runtime boxes."""
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
import research_queue as q
from template_inputs398 import checked
from template_adapters395 import document, resolve_inputs, command, runtime_items, verified_export

OUT=None


def overlap(a,b):
    from score_hcf_pilot import iou
    from hcf_compare371 import box
    return iou(box(a),box(b))


def flip(box,height):
    x,y,w,h=box
    return [x,height-y-h,w,h]


def audit(catalog, proposals, selection, mode):
    q.require(mode in ('orientation','insets','coverage'),'geometry_mode')
    frames={r['id']:r for r in catalog}
    q.require(len(frames)==len(catalog),'catalog_duplicate')
    chosen={r['id']:r for r in selection['rows']}
    q.require(len(chosen)==len(selection['rows']),'selection_duplicate')
    records=proposals['rows'];q.require(records and len({r['id'] for r in records})==len(records),'proposal_duplicate')
    q.require(set(chosen)=={r['id'] for r in records},'selection_membership')
    rows=[];roles={}
    for record in records:
        frame=frames[record['id']];selected=chosen[record['id']]
        q.require(frame['role'] in ('development','retained'),'audit_locked')
        q.require(roles.setdefault(frame['group'],frame['role'])==frame['role'],'group_role_leak')
        q.require(all(frame[k]==record[k]==selected[k] for k in ('sha256','group','role','profile')),'geometry_identity')
        width,height=frame['width'],frame['height'];body=frame['boxes'][frame['focus']]
        boxes=record['prediction']['candidates']
        for b in boxes:
            q.require(len(b)==4 and all(type(v) in (int,float) and math.isfinite(v) for v in b),'geometry_nonfinite')
            q.require(b[0]>=0 and b[1]>=0 and b[2]>0 and b[3]>0 and b[0]+b[2]<=width+.01 and b[1]+b[3]<=height+.01,'geometry_bounds')
        direct=[overlap(b,body) for b in boxes];inverted=[overlap(flip(b,height),body) for b in boxes]
        best=max(range(len(boxes)),key=lambda i:direct[i]) if boxes else None
        row=dict(id=frame['id'],profile=frame['profile'],group=frame['group'],role=frame['role'],
            outcome=selected['outcome'],candidateCount=len(boxes),directIoU=max(direct,default=0),
            invertedIoU=max(inverted,default=0),bodyWidth=body[2],bodyHeight=body[3],
            region=[min(2,int((body[0]+body[2]/2)/width*3)),min(2,int((body[1]+body[3]/2)/height*3))])
        if mode=='insets' and best is not None and direct[best]>=.5:
            b=boxes[best]
            row['ringInsetsPixels']=[b[0]-body[0],b[1]-body[1],body[0]+body[2]-b[0]-b[2],body[1]+body[3]-b[1]-b[3]]
            row['widthRatio']=b[2]/body[2];row['heightRatio']=b[3]/body[3]
        rows.append(row)
    summary={}
    for profile in sorted({r['profile'] for r in rows}):
        values=[r for r in rows if r['profile']==profile]
        entry=dict(frames=len(values),groups=len({r['group'] for r in values}),
            directMatches=sum(r['directIoU']>=.5 for r in values),invertedMatches=sum(r['invertedIoU']>=.5 for r in values),
            lostOrientationMatches=[r['id'] for r in values if r['directIoU']>=.5 and r['invertedIoU']<.5],
            gainedOrientationMatches=[r['id'] for r in values if r['directIoU']<.5 and r['invertedIoU']>=.5])
        if mode=='insets':
            matched=[r for r in values if 'ringInsetsPixels' in r]
            entry['matchedSupport']=len(matched)
            entry['medianInsetsPixels']=[statistics.median(r['ringInsetsPixels'][i] for r in matched) for i in range(4)] if matched else None
        if mode=='coverage':
            entry['regions']={str([x,y]):dict(frames=sum(r['region']==[x,y] for r in values),
                matched=sum(r['region']==[x,y] and r['directIoU']>=.5 for r in values)) for x in range(3) for y in range(3)}
        summary[profile]=entry
    return dict(mode=mode,rows=rows,summary=summary,modelAccepted=False,standardChanged=False,
        limitation='Inspected cases only. Matching uses labels for diagnosis. Do not apply fitted insets or per-case orientation in deployment.')


def geometry(inputs,params,out):
    catalog=[r for name in ('catalog','retained') for r in document(inputs[name])['rows']]
    q.save(out/'geometry.json',audit(catalog,document(inputs['proposals']),document(inputs['selection']),params['mode']))


def coordinates(inputs,params,out):
    from PIL import Image,ImageDraw
    cases=[]
    for i,bounds in enumerate(([40,30,120,80],[390,260,140,90],[220,70,130,100])):
        image=Image.new('RGB',(600,400),(0,0,0));draw=ImageDraw.Draw(image)
        x,y,w,h=bounds;draw.rectangle([x,y,x+w-1,y+h-1],outline=(255,255,255),width=4)
        path=out/f'coordinate-{i}.png';image.save(path)
        cases.append(dict(id=str(i),path=str(path),sha256=q.digest(path),expected=bounds))
    q.save(out/'inputs.json',[{k:v for k,v in c.items() if k!='expected'} for c in cases])
    command([str(checked(inputs['kernel'])),str(out/'inputs.json'),str(out/'raw.json')],out,'probe',timeout=60)
    raw=q.load(out/'raw.json');q.require([r['id'] for r in raw]==[c['id'] for c in cases],'coordinate_membership')
    results=[]
    for case,row in zip(cases,raw):
        q.require(row['sha256']==case['sha256'] and row['report']['navigationEligible'] is False,'coordinate_identity')
        boxes=[[c['bounds'][k]*s for k,s in zip(('x','y','width','height'),(600,400,600,400))] for c in row['report']['candidates']]
        results.append(dict(id=case['id'],directIoU=max((overlap(b,case['expected']) for b in boxes),default=0),
            invertedIoU=max((overlap(flip(b,400),case['expected']) for b in boxes),default=0),candidates=boxes))
    q.save(out/'coordinate-check.json',dict(rows=results,topLeftSupported=all(r['directIoU']>=.9 for r in results),
        modelAccepted=False,limitation='Authored software fixtures test axes only. They are not native HCF training data.'))


def observer(inputs,params,out):
    from crop_observer398 import run as observe
    from observer_identity398 import verify_receipt
    _,compiled=verified_export(inputs['export']);rows,items=runtime_items(inputs['membership'])
    prior=document(inputs['parity']);q.require(prior['membership']==inputs['membership'],'observer_membership_pin')
    observed=prior['observed']['results'];q.require([r['id'] for r in observed]==[r['id'] for r in rows],'observer_reference_order')
    bundle=document(inputs['bundle']);bundle_hash=inputs['bundle']['sha256']
    q.require(bundle['export']==inputs['export'] and bundle['parity']==inputs['parity'],'observer_bundle_binding')
    expected=dict(bundleSHA256=bundle_hash,results=[dict(id=i['id'],candidateID=i['id'],parentSHA256=i['sha256'],
        bounds=i['bounds'],modelInputRGBSHA256=r['modelInputRGBSHA256'],score=r['probability']) for i,r in zip(items,observed)])
    request=dict(version=1,root=str(q.ROOT),mode='vision',model=str(compiled),items=items)
    receipt=observe(request,checked(inputs['tool']),bundle_hash,params['sourceRevision'])
    receipt.update(osVersion=subprocess.check_output(['/usr/bin/sw_vers','-productVersion'],text=True).strip(),
        architecture=os.uname().machine,compilerVersion=subprocess.check_output(['/usr/bin/xcrun','swiftc','--version'],text=True).strip())
    verification=verify_receipt(receipt,expected)
    q.save(out/'expected-v2.json',expected);q.save(out/'observer-receipt.json',receipt)
    q.save(out/'verification.json',dict(verification,owner='research-host-NUIAK',TTRIntegrationVerified=False))


def run():
    contract=q.load(OUT.parents[2]/'spec.json')['template'];start=time.monotonic()
    try:
        inputs=resolve_inputs(contract,OUT)
        {'T26':geometry,'T27':coordinates,'T28':observer}[contract['id']](inputs,contract['parameters'],OUT)
        q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
            dict(path=str(p.relative_to(OUT)),sha256=q.digest(p)) for p in sorted(OUT.rglob('*')) if p.is_file()]))
        q.save(OUT/'template-result.json',dict(execution='complete',modelAccepted=False,seconds=time.monotonic()-start))
    except Exception as error:
        q.save(OUT/'template-result.json',dict(execution='failed',code=str(error)[:500],modelAccepted=False));raise
