"""Freeze and qualify controlled native page-indicator development captures."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'reports/work/IOS-NATIVE-PAGE-150/artifacts'
TARGET='F3EF9DB8-0B0F-4757-B653-D1628269F6FF'


def catalog():
    return [dict(id=f'{f}-{str(n).lower()}-{str(d).lower()}-{p}-{str(l).lower()}-{s}',
        family=f,native=n,dark=d,pages=p,left=l,seed=s)
        for f,n,d,p,l,s in itertools.product(['reader-footer','gallery-inspector'],[False,True],[False,True],[3,5,7],[False,True],[7,19])]


def bounds(visible,hidden,frame,scale):
    if visible.shape!=hidden.shape or visible.ndim!=3 or visible.shape[2]!=3:raise ValueError('image_shape')
    diff=np.max(np.abs(visible.astype(np.int16)-hidden.astype(np.int16)),axis=2)>4
    yy,xx=np.where(diff)
    if not len(xx):raise ValueError('empty_indicator')
    box=np.array([xx.min(),yy.min(),xx.max()+1,yy.max()+1],float)/scale
    x,y,w,h=frame
    if box[0]<x-1 or box[1]<y-1 or box[2]>x+w+1 or box[3]>y+h+1:raise ValueError('outside_control_change')
    return [float(box[0]),float(box[1]),float(box[2]-box[0]),float(box[3]-box[1])]


def run(mode):
    cp=BASE/'compose155-catalog.json'
    if mode=='plan':
        with cp.open('x') as f:json.dump(dict(version=1,target=TARGET,role='development',rows=catalog()),f,indent=2)
        print(hashlib.sha256(cp.read_bytes()).hexdigest());return
    root=BASE/'compose155-capture';doc=json.loads((root/'receipt.json').read_text());planned=json.loads(cp.read_text())
    expected={r['id']:r for r in catalog()}
    if planned['rows']!=catalog() or planned['target']!=TARGET or doc['target']!=TARGET or doc['version']!='page-composition155-v1':raise ValueError('catalog_identity')
    if len(doc['rows'])!=96 or {r['id'] for r in doc['rows']}!=set(expected):raise ValueError('membership')
    output=BASE/'compose155-audit';output.mkdir();results=[];seen={};examples=[]
    for row in doc['rows']:
        if any(row[k]!=v for k,v in expected[row['id']].items()):raise ValueError('recipe')
        images=[]
        for suffix,key in [('', 'sha256'),('-hidden','hiddenSHA256')]:
            p=root/(row['id']+suffix+'.png')
            if hashlib.sha256(p.read_bytes()).hexdigest()!=row[key]:raise ValueError('image_hash')
            with Image.open(p) as im:
                if im.size!=(row['width'],row['height']) or im.size!=(1179,2556) or row['scale']!=3:raise ValueError('dimensions')
                images.append(np.array(im.convert('RGB')))
        digest=hashlib.sha256(images[0].tobytes()).hexdigest();duplicate=seen.get(digest);seen[digest]=row['id']
        try:box=bounds(*images,row['frame'],row['scale']);reason=None
        except ValueError as e:box=None;reason=str(e)
        result=dict(row,visualBox=box,rejection=reason,decodedSHA256=digest,duplicateOf=duplicate,role='development')
        results.append(result)
        if row['pages']==5 and not row['left'] and row['seed']==19:
            im=Image.fromarray(images[0]);draw=ImageDraw.Draw(im)
            if box:
                x,y,w,h=box;draw.rectangle([x*3,y*3,(x+w)*3,(y+h)*3],outline='red',width=3)
            im.thumbnail((294,639));examples.append((row['id'],im))
    mosaic=Image.new('RGB',(4*294,2*665),'#888888');draw=ImageDraw.Draw(mosaic)
    for i,(name,im) in enumerate(examples):
        x=(i%4)*294;y=(i//4)*665;mosaic.paste(im,(x,y));draw.text((x,y+640),name[:45],fill='white')
    mosaic.save(output/'representatives.png')
    report=dict(version='compose155-audit-v1',rows=results,count=96,accepted=sum(r['rejection'] is None for r in results),
        duplicateCount=sum(r['duplicateOf'] is not None for r in results),catalogSHA256=hashlib.sha256(cp.read_bytes()).hexdigest(),
        receiptSHA256=hashlib.sha256((root/'receipt.json').read_bytes()).hexdigest(),productionEligible=False,
        labels='Controlled same-scene indicator removal difference; no model labels. Other classes intentionally not annotated; not a full detector training corpus.')
    with (output/'report.json').open('x') as f:json.dump(report,f,indent=2)
    print({k:v for k,v in report.items() if k!='rows'})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['plan','audit']);run(p.parse_args().mode)
