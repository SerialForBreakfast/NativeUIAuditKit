"""Independent pixel/annotation audit for actual-template native page capture."""
import hashlib
import argparse
import itertools
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from compose155 import BASE,TARGET,bounds


def main(partial=False):
    root=BASE/('context157-failed1' if partial else 'context157-capture')
    receiptpath=root/('failure.json' if partial else 'receipt.json');receipt=json.loads(receiptpath.read_text())
    expected={f'{f}-{str(m).lower()}-{str(d).lower()}-{s}' for f,m,d,s in itertools.product(
        ['UIKitControls','KitchenSink'],[False,True],[False,True],[7,19,31])}
    rows=receipt['completed'] if partial else receipt['rows']
    if partial:
        if len(rows)!=3 or receipt['failed']!='UIKitControls-false-true-7' or not {r['id'] for r in rows}<expected:raise ValueError('partial_membership')
    elif receipt['version']!='native-context157-v1' or receipt['target']!=TARGET or len(rows)!=24 or {r['id'] for r in rows}!=expected:raise ValueError('membership')
    result=[];pictures=[]
    for row in rows:
        data=[]
        for suffix,key in [('', 'sha256'),('-hidden','hiddenSHA256')]:
            p=root/(row['id']+suffix+'.png')
            if hashlib.sha256(p.read_bytes()).hexdigest()!=row[key]:raise ValueError('image_hash')
            with Image.open(p) as im:data.append(np.array(im.convert('RGB')))
        actual=bounds(*data,row['frame'],row['scale'])
        if not np.allclose(actual,row['body'],atol=1/row['scale'],rtol=0):raise ValueError('native_measurement')
        annpath=root/(row['id']+'.json');ann=json.loads(annpath.read_text())
        if ann['imageSHA256']!=row['sha256'] or ann['image']['pixelWidth']!=data[0].shape[1] or ann['image']['pixelHeight']!=data[0].shape[0]:raise ValueError('sidecar_identity')
        elements=[e for e in ann['elements'] if e['elementType']=='pageControl']
        if len(elements)!=1:raise ValueError('page_count')
        b=elements[0]['boundsPoints']
        if not np.allclose([b[k] for k in ('x','y','width','height')],actual,atol=1/row['scale'],rtol=0):raise ValueError('annotation')
        result.append(dict(row,independentBody=actual,annotationSHA256=hashlib.sha256(annpath.read_bytes()).hexdigest()))
        if row['seed']==19:
            im=Image.fromarray(data[0]);d=ImageDraw.Draw(im);x,y,w,h=actual;s=row['scale']
            d.rectangle([x*s,y*s,(x+w)*s,(y+h)*s],outline='red',width=3)
            im.thumbnail((294,830));pictures.append((row['id'],im))
    output=BASE/('context157-partial-audit' if partial else 'context157-audit');output.mkdir()
    mosaic=Image.new('RGB',(4*294,2*860),'#888888');d=ImageDraw.Draw(mosaic)
    for i,(name,im) in enumerate(pictures):
        x=i%4*294;y=i//4*860;mosaic.paste(im,(x,y));d.text((x,y+832),name,fill='white')
    mosaic.save(output/'representatives.png')
    report=dict(version='context157-audit-v1',count=len(rows),accepted=len(result),expected=24,complete=not partial,
        failed=receipt.get('failed'),notAttempted=20 if partial else 0,rows=result,productionCorpusRewritten=False,
        receiptSHA256=hashlib.sha256(receiptpath.read_bytes()).hexdigest())
    with (output/'report.json').open('x') as f:json.dump(report,f,indent=2)
    print('qualified',len(result),'actual template captures')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--partial',action='store_true');main(p.parse_args().partial)
