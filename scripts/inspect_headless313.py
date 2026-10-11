"""Inspect authored placeholder screens without admitting training labels."""
from pathlib import Path
import time
import numpy as np
from PIL import Image
import regions313 as r


def main():
    b=r.b;root=r.OUT/'headless-diagnostic';out=root/'inspection.json'
    b.require(not out.exists(),'output_collision');r.t.set_num_threads(2)
    doc=b.read(root/'batch_corpora_manifest.json')
    expected={'shelf','grid','hero_detail','top_nav_shelf'}
    b.require(doc['schemaVersion']=='contract-v1-batch-corpora' and doc['totalScreens']==4,'batch_contract')
    b.require(set(doc['layouts'])==expected and len(doc['generatedScreens'])==4,'batch_count')
    b.require({x['layoutType'] for x in doc['generatedScreens']}==expected,'layout_membership')
    records=[];values=[]
    for m in doc['generatedScreens']:
        layout=m['layoutType'];folder=root/layout
        b.require(b.read(folder/f'{layout}_annotations.json')==m,'sidecar_identity')
        b.require(m['schemaVersion']=='contract-v1-headless-focus','sidecar_version')
        b.require((m['canvasWidth'],m['canvasHeight'])==(1920,1080),'dimensions')
        nodes=[n for n in m['nodes'] if n['isFocused']]
        b.require(len(nodes)==1 and nodes[0]['id']==m['focusedNodeID'],'authored_focus_identity')
        images=[];refs=[]
        for filename,key in [(f'{layout}_unfocused.png','unfocusedImageSHA256'),
                             (f'{layout}_focused_{m["focusedNodeID"]}.png','focusedImageSHA256')]:
            ref=dict(path=str((folder/filename).relative_to(b.ROOT)),sha256=m[key])
            with Image.open(b.checked(ref)) as image:
                image.load();b.require(image.size==(1920,1080),'png_dimensions');images.append(image.convert('RGB'))
            refs.append(ref)
        b.require(not np.array_equal(np.asarray(images[0]),np.asarray(images[1])),'unchanged_render')
        for name,frames,label in [('arrival',images,1),('departure',images[::-1],1),
                                  ('same-before',[images[0]]*2,0),('same-after',[images[1]]*2,0)]:
            values.append(r.s.encoded(*frames,(192,128))[0])
            ordered=refs[::-1] if name=='departure' else [refs[0]]*2 if name=='same-before' else [refs[1]]*2 if name=='same-after' else refs
            records.append(dict(layout=layout,condition=name,authoredChanged=label,images=ordered,
                bodyBefore=nodes[0]['unfocusedBounds'],bodyAfter=nodes[0]['focusedBounds']))
    values=np.stack(values);scores={}
    paths={'DTM085':b.checked(b.read(b.ROOT/'reports/work/TRANSITION-292/DTM085/result.json')['model'])}
    for n in (1,2):
        p=r.OUT/f'regions-{n}/last.pt'
        if p.exists():paths[f'regions-{n}']=p
    for name,path in paths.items():
        net=r.s.c.model.load_candidate(path) if name=='DTM085' else r.load_candidate(path)
        inputs=values
        if name!='DTM085':
            detail,_=r.prepare(values,records,net.change.count)
            inputs=np.concatenate((values,detail),1)
        start=time.monotonic();p=b.worker.score(net,inputs)
        scores[name]=dict(model=b.ref(path),probabilities=p.tolist(),seconds=time.monotonic()-start,
            summary=b.trainer.w.summary(p,np.array([x['authoredChanged'] for x in records])))
    b.write(out,dict(version='headless313-inspection-v1',sourceCommit='d06a64bd',
        renderer=dict(path='/Users/josephmccraw/Developer/TVTestRig/Scripts/render-headless-screen.swift',
                      sha256=b.sha(Path('/Users/josephmccraw/Developer/TVTestRig/Scripts/render-headless-screen.swift').read_bytes())),
        manifest=b.ref(root/'batch_corpora_manifest.json'),rows=records,scores=scores,
        inputSHA256=b.sha(values.tobytes()),trainingEligible=False,nativeQualified=False,
        assetMode='Deliberate empty artwork directory; built-in placeholders only.',
        limitation='Four related layouts. Authored arrival/departure, not observed native A-to-B movement.'))
    print({name:value['summary'] for name,value in scores.items()})


if __name__=='__main__':main()
