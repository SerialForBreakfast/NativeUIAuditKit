"""Test fixed headless effects with reviewed training artwork and native checks."""
import argparse
from collections import Counter
import gc
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import numpy as np
from PIL import Image
import regions313 as r

b=r.b;t=r.t
OUT=b.ROOT/'reports/work/FOCUS-319'
SCRIPT=Path('/Users/josephmccraw/Developer/TVTestRig/Scripts/render-headless-screen.swift')
ART=b.ROOT/'reports/work/ARTWORK-204/artifacts'


def plan():
    inventory=ART/'normalized204-reviewed01.json'
    cache=ART/'cache204-reviewed01.json'
    paths={v['sha256']:v['path'] for v in b.read(cache)['files']}
    rows=[]
    for x in b.read(inventory)['resources']:
        if not re.fullmatch(r'artwork204-r1-s[0-4]-v0-t[12]',x['id']):continue
        b.require(x['dataRole']=='train' and x['rightsStatus']==x['reviewStatus']=='verified','artwork_admission')
        p=ART/'return02/artwork204-selected-originals-return02'/paths[x['sha256']]
        pin=b.ref(p);b.require(pin['sha256']==x['sha256'],'artwork_hash')
        with Image.open(p) as image:image.load();b.require(min(image.size)>0,'artwork_decode')
        rows.append(dict(id=x['id'],groups=x['ancestryGroups'],image=pin))
    b.require(len(rows)==10,'artwork_count')
    old=b.read(r.OUT/'headless-diagnostic/batch_corpora_manifest.json')
    return dict(version='authored319-v1',renderer=dict(path=str(SCRIPT),sha256=b.sha(SCRIPT.read_bytes())),
        inventory=b.ref(inventory),cache=b.ref(cache),assets=sorted(rows,key=lambda x:x['id']),
        layouts=[dict(name=m['layoutType'],targets=[n['id'] for n in m['nodes'][:2]]) for m in old['generatedScreens']],
        role='train',expectedRenders=80,expectedPairs=240,maximumOutputBytes=2*1024**3,
        hypothesis='Matched authored movement and fixed-focus artwork changes improve native transfer.',
        limitations=['Fixed layouts and effects only.','Authored labels are not native observations.',
                    'Existing placeholder checks are inspected development cases, not independent layout holdouts.'],
        training=dict(epochs=30,seed=42,batch=16,threads=2,auxiliaryWeight=.25,selection='fixed-last',
                      detailWindows=2,detailOnly=True,originalViews=1820,wallTimeLimit=None),
        acceptance='Improve tiny native decisions without losing previous successes or increasing false changes.')


def frame(folder,layout,target):
    m=b.read(folder/f'{layout}_annotations.json')
    b.require(m['schemaVersion']=='contract-v1-headless-focus','schema')
    b.require((m['canvasWidth'],m['canvasHeight'])==(1920,1080),'dimensions')
    focused=[x for x in m['nodes'] if x['isFocused']]
    b.require(m['focusedNodeID']==target and len(focused)==1 and focused[0]['id']==target,'focus_identity')
    for n in m['nodes']:
        for key in ('unfocusedBounds','focusedBounds'):
            a=np.array(n[key]);b.require(a.shape==(4,) and np.isfinite(a).all() and (a[2:]>0).all(),'bounds')
    for name,key in ((f'{layout}_focused_{target}.png','focusedImageSHA256'),(f'{layout}_unfocused.png','unfocusedImageSHA256')):
        pin=b.ref(folder/name);b.require(pin['sha256']==m[key],'png_hash')
        with Image.open(folder/name) as image:image.load();b.require(image.size==(1920,1080),'png_size')
    return b.ref(folder/f'{layout}_focused_{target}.png'),m


def pair_rows(frames,group,layout):
    rows=[]
    for variant in range(2):
        a,c=frames[variant]
        for reverse in range(2):
            rows.append(dict(condition='movement',changed=1,images=[a,c][::(-1 if reverse else 1)]))
    for focus in range(2):
        a,c=frames[0][focus],frames[1][focus]
        for reverse in range(2):
            rows.append(dict(condition='artwork-only',changed=0,images=[a,c][::(-1 if reverse else 1)]))
        for pin in (a,c):rows.append(dict(condition='identical',changed=0,images=[pin,pin]))
    return [dict(x,group=group,layout=layout,role='train') for x in rows]


def generate():
    b.require(not OUT.exists(),'output_collision');p=plan();OUT.mkdir(parents=True)
    b.write(OUT/'plan.json',p);started=time.monotonic()
    names=sorted(set(re.findall(r'"([^"/]+\.jpg)"',SCRIPT.read_text())))
    b.require(len(names)==16,'asset_names_changed')
    env=dict(os.environ,TMPDIR=str(b.ROOT/'.build'),CLANG_MODULE_CACHE_PATH=str(b.ROOT/'.build/ModuleCache'))
    rows=[];renders=[]
    for family in range(5):
        assets=[a for a in p['assets'] if f'-s{family}-' in a['id']];b.require(len(assets)==2,'family_assets')
        directories=[]
        for variant in range(2):
            folder=OUT/f'assets-{family}-{variant}';folder.mkdir();directories.append(folder)
            for i,name in enumerate(names):
                # AppKit decodes by file contents. Keep original PNG bytes and their hashes.
                shutil.copyfile(b.checked(assets[(i+variant)%2]['image']),folder/name)
        for layout in p['layouts']:
            name=layout['name'];frames=[]
            for variant in range(2):
                states=[];base=None
                for target in layout['targets']:
                    folder=OUT/f'render-{family}-{variant}-{name}-{target}'
                    b.require(not folder.exists(),'render_collision')
                    b.require(b.sha(SCRIPT.read_bytes())==p['renderer']['sha256'],'renderer_changed')
                    cmd=['swift','-module-cache-path',str(b.ROOT/'.build/ModuleCache'),str(SCRIPT),
                         '--layout',name,'--resolution','1080p','--assets-dir',str(directories[variant]),
                         '--output-dir',str(folder),'--focus-id',target]
                    with (OUT/f'{folder.name}.log').open('x') as log:
                        subprocess.run(cmd,cwd=b.ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
                    pin,m=frame(folder,name,target)
                    if base is not None:b.require(base==m['unfocusedImageSHA256'],'base_pixels_changed')
                    base=m['unfocusedImageSHA256'];states.append(pin);renders.append(b.ref(folder/f'{name}_annotations.json'))
                frames.append(states)
            rows+=pair_rows(frames,assets[0]['groups'][0],name)
        print('Rendered family',family,flush=True)
    b.require(len(rows)==240 and len(renders)==80,'completion_count')
    hashes={};values=[]
    for row in rows:
        images=[r.s.image(x['path'],x['sha256']) for x in row['images']]
        pixels=[b.sha(np.asarray(x).tobytes()) for x in images];key=tuple(pixels)
        b.require(hashes.setdefault(key,row['changed'])==row['changed'],'conflicting_pixels')
        b.require((pixels[0]==pixels[1])==(row['condition']=='identical'),'visible_condition')
        row['decodedHashes']=pixels;values.append(r.s.encoded(*images,(192,128))[0])
    x=np.stack(values);np.save(OUT/'authored.npy',x,allow_pickle=False)
    b.require(sum(f.stat().st_size for f in OUT.rglob('*') if f.is_file())<p['maximumOutputBytes'],'storage_limit')
    b.write(OUT/'corpus.json',dict(plan=b.ref(OUT/'plan.json'),rows=rows,renders=renders,tensor=b.ref(OUT/'authored.npy'),
        seconds=time.monotonic()-started,uniquePairs=len(hashes),nativeQualified=False,trainingEligible=False,
        admission='Image review is required before training. Native and prior development roles stay unchanged.'))


def schedule(labels,rows):
    pools={label:[i for i,row in enumerate(rows) if row['changed']==label] for label in (0,1)}
    b.require(all(pools.values()),'missing_class');count=Counter();indices=[]
    for label in labels:
        label=int(label);indices.append(pools[label][count[label]%len(pools[label])]);count[label]+=1
    return np.array(indices)


def execute(out=OUT,auxiliary_projection=False):
    corpus=b.read(OUT/'corpus.json');b.checked(corpus['plan']);p=b.read(OUT/'plan.json')
    review=b.read(OUT/'review.json');b.require(review['corpusSHA256']==b.ref(OUT/'corpus.json')['sha256']
        and review['approvedForAuthoredTraining'] is True,'review_required')
    b.require(not (out/'run').exists(),'run_collision');run=out/'run';run.mkdir();t.set_num_threads(2)
    start=time.monotonic();authored=np.load(b.checked(corpus['tensor']),allow_pickle=False)
    ad,aa=r.prepare(authored,corpus['rows'],2)
    manifest,membership,full,labels,weights,extra,controls,_,reg=r.s.c.prepare()
    added=r.s.previous.prior.mix(full[controls],extra,labels[1660:1740],True)
    values=np.concatenate((full,added,b.reporting.reverse(added)));del full,extra,added
    prior=b.read(r.OUT/'registration.json');b.require(b.sha(values.tobytes())==prior['trainingSHA256'],'original_pixels')
    b.require(b.sha(labels.tobytes())==prior['labelsSHA256'] and b.sha(weights.tobytes())==prior['weightsSHA256'],'original_labels_weights')
    details,audit=r.prepare(values,r.s.schedule_rows(membership,reg,labels),2)
    b.require(b.sha(details.tobytes())==b.read(r.OUT/'regions-2/views.json')['sha256'],'original_details')
    ids=schedule(labels,corpus['rows']);initializer=b.checked(prior['initializer']);config=dict(reg['configuration'],epochs=30,detailOnly=True)
    b.write(run/'registration.json',dict(corpus=b.ref(OUT/'corpus.json'),initializer=prior['initializer'],runner=b.ref(Path(__file__)),
        trainer=b.ref(Path(b.trainer.__file__)),control=b.ref(r.OUT/'regions-2/last.pt'),configuration=config,
        gradientDiagnostic=b.ref(out/'diagnostic.json') if auxiliary_projection else None,
        originalHashes={k:prior[k] for k in ('trainingSHA256','labelsSHA256','weightsSHA256')},
        auxiliaryIndices=ids.tolist(),exposureByCondition=dict(Counter(corpus['rows'][i]['condition'] for i in ids)),
        weightedExposureByCondition={c:float(sum(weights[j] for j,i in enumerate(ids) if corpus['rows'][i]['condition']==c))
            for c in sorted({x['condition'] for x in corpus['rows']})},
        auxiliaryWeight=.25,auxiliaryProjection=auxiliary_projection,
        auxiliaryGradientRule='project-opposition-and-cap-to-original-norm' if auxiliary_projection else 'weighted-sum',
        thresholds=[.15,.85],selection='fixed-last',rolesChanged=False,
        admission='New authored pairs only. Existing images keep their roles.',outputCapBytes=2*1024**3,memoryLimitBytes=8*1024**3))
    t.manual_seed(42);net=r.extend(r.s.c.model.load_candidate(initializer),2)
    def progress(row):b.write(run/f"epoch-{row['epoch']:04d}.json",row);print(row,flush=True)
    net,history=b.trainer.fit(net,t.from_numpy(values),t.from_numpy(labels),config,progress,t.from_numpy(weights),
        detail_inputs=t.from_numpy(details),auxiliary_inputs=t.from_numpy(authored[ids]),
        auxiliary_detail=t.from_numpy(ad[ids]),auxiliary_weight=.25,auxiliary_projection=auxiliary_projection)
    t.save(dict(state=net.state_dict(),representation=r.VERSION,windows=2),run/'last.pt')
    restored=r.load_candidate(run/'last.pt');sanity=np.concatenate((values[:8],details[:8]),1)
    b.require(np.array_equal(b.worker.score(net,sanity),b.worker.score(restored,sanity)),'reload_parity')
    b.write(run/'fit.json',dict(history=history,seconds=time.monotonic()-start,checkpointParity=True))
    del values,details,net;gc.collect()
    native=np.load(b.PACKAGE/'native.npy',allow_pickle=False);nd,_=r.prepare(native,membership['rows'],2)
    def transform(key,x):
        if key=='native.npy':return np.concatenate((x,nd),1)
        if key=='reverse_native.npy':return np.concatenate((x,r.reverse_details(nd)),1)
        return x
    evaluation=b.evaluate_full(restored,{'DTM085':r.s.c.model.load_candidate(initializer)},manifest,input_transform=transform)
    b.write(run/'evaluation.json',evaluation)
    tiny,rows,pin=r.s.tiny_rows();td,_=r.prepare(tiny,rows,2);prob=b.worker.score(restored,np.concatenate((tiny,td),1))
    b.write(run/'tiny.json',dict(input=pin,results=[dict(condition=c,summary=b.trainer.w.summary(
        prob[[i for i,x in enumerate(rows) if x['condition']==c]],np.array([x['changed'] for x in rows if x['condition']==c])))
        for c in sorted({x['condition'] for x in rows})]))
    scores={}
    for name,model in [('control',r.load_candidate(r.OUT/'regions-2/last.pt')),('candidate',restored)]:
        pp=b.worker.score(model,np.concatenate((authored,ad),1));scores[name]=dict(probabilities=pp.tolist())
        for condition in sorted({x['condition'] for x in corpus['rows']}):
            ix=[i for i,x in enumerate(corpus['rows']) if x['condition']==condition]
            scores[name][condition]=b.trainer.w.summary(pp[ix],np.array([corpus['rows'][i]['changed'] for i in ix]))
        scores[name]['byLayout']={}
        for layout in p['layouts']:
            ix=[i for i,x in enumerate(corpus['rows']) if x['layout']==layout['name']]
            scores[name]['byLayout'][layout['name']]=b.trainer.w.summary(pp[ix],np.array([corpus['rows'][i]['changed'] for i in ix]))
    import report291
    summary,cases=report291.summarize_comparison(b.read(r.OUT/'regions-2/evaluation.json'),evaluation,membership)
    b.write(run/'comparison.json',dict(summaries=summary,cases=cases,authoredTraining=scores,seconds=time.monotonic()-start,
        model=b.ref(run/'last.pt'),productionEligible=False))
    b.require(sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<2*1024**3,'output_budget')
    print('Completed comparison',summary,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['plan','generate','train'])
    args=parser.parse_args()
    if args.mode=='plan':print(plan())
    elif args.mode=='generate':generate()
    else:execute()
