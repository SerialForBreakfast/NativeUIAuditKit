"""Pair two existing authored focus states without changing the TTR renderer."""
import os
from pathlib import Path
import subprocess
import time
import numpy as np
from PIL import Image
import regions313 as r


def main():
    b=r.b;out=r.OUT/'headless-moves';b.require(not out.exists(),'output_collision')
    r.t.set_num_threads(2);out.mkdir();started=time.monotonic()
    root=r.OUT/'headless-diagnostic';original=b.read(root/'batch_corpora_manifest.json')
    script=Path('/Users/josephmccraw/Developer/TVTestRig/Scripts/render-headless-screen.swift')
    pin=b.read(root/'inspection.json')['renderer'];b.require(b.sha(script.read_bytes())==pin['sha256'],'renderer_changed')
    env=dict(os.environ,TMPDIR=str(b.ROOT/'.build'),CLANG_MODULE_CACHE_PATH=str(b.ROOT/'.build/ModuleCache'))
    records=[];values=[]
    for m in original['generatedScreens']:
        layout=m['layoutType'];target=m['nodes'][1]['id'];folder=out/layout
        command=['swift','-module-cache-path',str(b.ROOT/'.build/ModuleCache'),str(script),'--layout',layout,
            '--resolution','1080p','--assets-dir',str(r.OUT/'headless-empty-assets'),
            '--output-dir',str(folder),'--focus-id',target]
        with (out/f'{layout}.log').open('x') as log:
            subprocess.run(command,cwd=b.ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
        new=b.read(folder/f'{layout}_annotations.json')
        b.require(new['focusedNodeID']==target and new['unfocusedImageSHA256']==m['unfocusedImageSHA256'],'scene_changed')
        b.require(new['canvasWidth']==1920 and new['canvasHeight']==1080,'canvas_size')
        paths=[root/layout/f'{layout}_focused_{m["focusedNodeID"]}.png',folder/f'{layout}_focused_{target}.png']
        refs=[dict(path=str(p.relative_to(b.ROOT)),sha256=v['focusedImageSHA256']) for p,v in zip(paths,(m,new))]
        images=[]
        for ref in refs:
            with Image.open(b.checked(ref)) as image:
                image.load();b.require(image.size==(1920,1080),'png_size');images.append(image.convert('RGB'))
        for name,frames,pins in [('forward',images,refs),('reverse',images[::-1],refs[::-1])]:
            values.append(r.s.encoded(*frames,(192,128))[0])
            records.append(dict(layout=layout,order=name,images=pins,authoredChanged=True,
                focusIDs=[m['focusedNodeID'],target] if name=='forward' else [target,m['focusedNodeID']]))
    values=np.stack(values);scores={}
    for name in ('DTM085','regions-1','regions-2'):
        path=b.checked(b.read(b.ROOT/'reports/work/TRANSITION-292/DTM085/result.json')['model']) if name=='DTM085' else r.OUT/name/'last.pt'
        net=r.s.c.model.load_candidate(path) if name=='DTM085' else r.load_candidate(path);inputs=values
        if name!='DTM085':
            detail,_=r.prepare(values,records,net.change.count);inputs=np.concatenate((values,detail),1)
        p=b.worker.score(net,inputs)
        scores[name]=dict(model=b.ref(path),probabilities=p.tolist(),summary=b.trainer.w.summary(p,np.ones(len(p))))
    b.write(out/'comparison.json',dict(renderer=pin,rows=records,scores=scores,seconds=time.monotonic()-started,
        matchingUnfocusedImagesVerified=True,trainingEligible=False,nativeQualified=False,
        limitation='Authored A-to-B states with placeholders. Native focus and actual navigation remain untested.'))
    print({name:value['summary'] for name,value in scores.items()})


if __name__=='__main__':main()
