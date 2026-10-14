"""Test independent authored effect coverage with retained training inputs."""
import argparse
import time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import pool325 as p

b=p.b;r=p.r;t=p.t;a=p.a
OUT=b.ROOT/'reports/work/FOCUS-326'
VERSION='effect326-v1'
ARMS=('coupled','independent')


def tile(art,size,width,contrast,focused,arm):
    b.require(size in (3,6) and width in (1,3) and contrast in (.25,.75) and arm in ARMS,'effect_parameters')
    body=(size*10,size*15); factor=size/6 if arm=='coupled' else 1
    border=width*10*factor; alpha=contrast*factor
    canvas=Image.new('RGB',(240,300),(20,20,25))
    w,h=[round(v*(1.14 if focused else 1)) for v in body]
    box=[120-w//2,150-h//2,w,h]
    x,y,w,h=box
    if focused:
        mask=Image.new('L',canvas.size);draw=ImageDraw.Draw(mask)
        outer=[round(x-border),round(y-border),round(x+w-1+border),round(y+h-1+border)]
        b.require(min(outer)>=30 and outer[2]<210 and outer[3]<270,'effect_clipped')
        draw.rectangle(outer,fill=round(255*alpha))
        halo=mask.filter(ImageFilter.GaussianBlur(border/2))
        canvas=Image.composite(Image.new('RGB',canvas.size,(150,150,155)),canvas,halo)
        canvas=Image.composite(Image.new('RGB',canvas.size,'white'),canvas,mask)
    canvas.paste(art.resize((w,h),Image.Resampling.LANCZOS),(x,y))
    return canvas,box,dict(borderPixels=border,contrast=alpha,scale=1.14)


def generate():
    b.require(not (OUT/'corpus.json').exists(),'output_collision')
    src=b.read(a.OUT/'corpus.json');review=b.read(a.OUT/'review.json')
    b.require(review['approvedForAuthoredTraining'] and review['corpusSHA256']==b.ref(a.OUT/'corpus.json')['sha256'],'source_review')
    plan=b.read(b.checked(src['plan']));rows={arm:[] for arm in ARMS};samples=[];sources=[]
    for arm in ARMS:
        dest=OUT/arm/'images';b.require(not dest.exists(),'output_collision');dest.mkdir(parents=True)
        for family in range(3):
            assets=[v for v in plan['assets'] if f'-s{family}-' in v['id']]
            b.require(len(assets)==2,'artwork_family')
            arts=[r.s.image(v['image']['path'],v['image']['sha256']) for v in assets];sources.extend(v['image'] for v in assets)
            for size in (3,6):
                for width in (1,3):
                    for contrast in (.25,.75):
                        parts=[[tile(im,size,width,contrast,focus,arm)[0] for focus in (False,True)] for im in arts]
                        for distance in (320,960):
                            for corner,(x,y,dx) in enumerate([(180,180,1),(1740,180,-1),(180,900,1),(1740,900,-1)]):
                                centers=[(x,y),(x+dx*distance,y)]
                                before,boxes=p.compose(parts,centers,0);moved,_=p.compose(parts,centers,1);art,_=p.compose(parts,centers,0,True)
                                stem=f'f{family}-s{size}-w{width}-c{contrast}-d{distance}-p{corner}';pins=[]
                                for name,im in [('before',before),('moved',moved),('art',art)]:
                                    path=dest/f'{stem}-{name}.png';im.save(path);pins.append(b.ref(path))
                                for condition,indices,label in [('movement',(0,1),1),('artwork-only',(0,2),0),('identical',(0,0),0)]:
                                    for reverse in ([False] if condition=='identical' else [False,True]):
                                        ids=[0,1] if label else [0,0]
                                        if reverse:ids.reverse()
                                        endpoints=[]
                                        for focus in ids:
                                            bodies=[]
                                            for j,(px,py,_,_) in enumerate(boxes):
                                                _,box,params=tile(arts[0],size,width,contrast,j==focus,arm)
                                                bodies.append([px+box[0],py+box[1],box[2],box[3]])
                                            endpoints.append(dict(focusID=f'control-{focus}',bodyBounds=bodies))
                                        rows[arm].append(dict(id=f'{stem}-{condition}-{int(reverse)}',images=[pins[i] for i in indices][::(-1 if reverse else 1)],
                                            role='train',group=assets[0]['groups'][0],changed=label,condition=condition,reverse=reverse,
                                            sizePixels=size,widthPixels=width,contrast=contrast,separationPixels=distance*.1,corner=corner,
                                            patchBounds=boxes,endpoints=endpoints,effect=params,labelAuthority='Authored composition states; not native observations.'))
                                if family==0 and size==3 and distance==960 and corner==0:samples.append(before)
            print('generated',arm,family,flush=True)
        b.require(len(rows[arm])==960,'pair_count')
    sheet=Image.new('RGB',(1280,360))
    for i,im in enumerate(samples):sheet.paste(im.resize((320,180)),((i%4)*320,(i//4)*180))
    sheet.save(OUT/'review.png')
    b.write(OUT/'corpus.json',dict(version=VERSION,rows=rows,sources=sources,sourceReview=b.ref(a.OUT/'review.json'),sourceCorpus=b.ref(a.OUT/'corpus.json'),
        renderer=b.ref(Path(__file__)),role='train',nativeQualified=False))


def validate():
    from effect312 import metrics
    corpus=b.read(OUT/'corpus.json');b.require(corpus['version']==VERSION,'version');reports={};seen={}
    for arm,rows in corpus['rows'].items():
        cells={};effects=[]
        for row in rows:
            b.require(row['role']=='train' and len(row['endpoints'])==2,'annotation_role')
            focus=[v['focusID'] for v in row['endpoints']]
            b.require((focus[0]!=focus[1])==bool(row['changed']),'focus_label')
            for endpoint in row['endpoints']:
                for x,y,w,h in endpoint['bodyBounds']:
                    b.require(np.isfinite([x,y,w,h]).all() and w>0 and h>0 and x>=0 and y>=0 and x+w<=1920 and y+h<=1080,'body_bounds')
            ims=[r.s.image(v['path'],v['sha256']) for v in row['images']]
            b.require(all(im.size==(1920,1080) for im in ims),'dimensions')
            arrays=[np.asarray(im) for im in ims];hashes=tuple(b.sha(v.tobytes()) for v in arrays)
            b.require(seen.setdefault(hashes,row['changed'])==row['changed'],'conflicting_labels')
            delta=np.any(arrays[0]!=arrays[1],2);allowed=np.zeros(delta.shape,bool)
            for x,y,w,h in row['patchBounds']:allowed[y:y+h,x:x+w]=True
            b.require(not delta[~allowed].any(),'outside_effect')
            b.require(bool(delta.any())==(row['condition']!='identical'),'visible_condition')
            if row['condition']=='artwork-only':
                x,y,w,h=row['patchBounds'][0];b.require(not delta[y:y+h,x:x+w].any(),'changed_focused_artwork')
            key=str((row['sizePixels'],row['widthPixels'],row['contrast'],row['separationPixels'],row['corner'],row['condition']))
            cells[key]=cells.get(key,0)+1
            if row['condition']=='movement' and not row['reverse']:
                encoded=r.s.encoded(*ims,(192,128))[0]
                effects.append(dict(id=row['id'],size=row['sizePixels'],width=row['widthPixels'],contrast=row['contrast'],metrics=metrics(encoded,[])))
        reports[arm]=dict(pairs=len(rows),cells=cells,effects=effects)
    b.write(OUT/'validation.json',dict(corpus=b.ref(OUT/'corpus.json'),reports=reports,uniquePairs=len(seen),passed=True))


def prepare():
    t.set_num_threads(2);start=time.monotonic();b.require(not (OUT/'inputs.json').exists(),'output_collision')
    corpus=b.read(OUT/'corpus.json');review=b.read(OUT/'review.json')
    b.require(review['approvedForAuthoredTraining'] and review['corpusSHA256']==b.ref(OUT/'corpus.json')['sha256'],'review')
    validation=b.read(b.checked(review['validation']));b.require(validation['passed'] and validation['corpus']==b.ref(OUT/'corpus.json'),'validation')
    parent=b.read(p.OUT/'inputs.json');data=np.load(b.checked(parent['cache']['average']),allow_pickle=False)
    initializer=b.ref(p.OUT/'average/last.pt');net=p.load(b.checked(initializer));old=b.read(b.checked(parent['oldCorpus']))
    cached_source=r.load_candidate(b.checked(parent['initializer']))
    for key,value in net.state_dict().items():
        if not key.startswith(('change.detail.8.','change.correction.')):
            b.require(t.equal(value,cached_source.state_dict()[key]),'cache_encoder_changed')
    membership=b.read(b.PACKAGE/'membership.json');protected={row['group'] for row in membership['rows'] if row['role']!='train'}
    native=np.load(b.PACKAGE/'native.npy',mmap_mode='r',allow_pickle=False)
    excluded={b.sha(v.tobytes()) for i,row in enumerate(membership['rows']) if row['role']!='train' for v in (native[i,:3],native[i,3:])}
    tiny,_,_=r.s.tiny_rows();excluded.update(b.sha(v.tobytes()) for pair in tiny for v in (pair[:3],pair[3:]))
    for arm in ARMS:
        rows=old['rows']+corpus['rows'][arm];cache=[]
        b.require(all(row['role']=='train' and row['group'] not in protected for row in rows),'protected_group')
        for startrow in range(0,len(rows),8):
            subset=rows[startrow:startrow+8];values=[]
            for row in subset:
                ims=[r.s.image(v['path'],v['sha256']) for v in row['images']];value=r.s.encoded(*ims,(192,128))[0]
                b.require(all(b.sha(v.tobytes()) not in excluded for v in (value[:3],value[3:])),'protected_pixel');values.append(value)
            values=np.stack(values);details,_=r.prepare(values,subset,2);features,_=p.cache(net,values,details);cache.append(features[0.])
        ids=a.schedule(data['labels'],rows);ay=np.array([v['changed'] for v in rows],np.float32)
        b.require(len(np.unique(ids))==len(rows) and np.array_equal(ay[ids],data['labels']),'schedule')
        np.savez(OUT/f'{arm}.npz',original=data['original'],labels=data['labels'],weights=data['weights'],auxiliary=np.concatenate(cache),indices=ids,auxiliaryLabels=ay)
    b.write(OUT/'inputs.json',dict(corpus=b.ref(OUT/'corpus.json'),review=b.ref(OUT/'review.json'),oldCorpus=parent['oldCorpus'],initializer=initializer,
        runner=b.ref(Path(__file__)),trainer=b.ref(Path(b.trainer.__file__)),pooling=b.ref(Path(p.__file__)),parent=b.ref(p.OUT/'inputs.json'),
        cache={n:b.ref(OUT/f'{n}.npz') for n in ARMS},parity=parent['parity'],configuration=parent['configuration'],seconds=time.monotonic()-start,
        thresholds=[.15,.85],originalViews=1820,auxiliaryRows=1200,rolesChanged=False))


def run(arm):
    start=time.monotonic();t.set_num_threads(2);reg=b.read(OUT/'inputs.json')
    for key in ('runner','trainer','pooling','corpus','review','oldCorpus','parent'):b.checked(reg[key])
    out=OUT/arm/'run';b.require(not out.exists(),'output_collision');out.mkdir()
    data=np.load(b.checked(reg['cache'][arm]),allow_pickle=False);net=p.load(b.checked(reg['initializer']))
    baseline={k:v.clone() for k,v in net.state_dict().items()};images=np.load(b.checked(reg['parity']),allow_pickle=False)
    with t.inference_mode():initial=net.change(t.from_numpy(data['original'][:8])).sigmoid().flatten().numpy()
    b.require(np.max(np.abs(initial-b.worker.score(net,images)))<1e-6,'initial_cache_parity')
    b.write(out/'registration.json',dict(inputs=b.ref(OUT/'inputs.json'),selection='fixed-last',arm=arm))
    def progress(row):b.write(out/f"epoch-{row['epoch']:04d}.json",row);print(arm,row,flush=True)
    net,history=b.trainer.fit(net,t.from_numpy(data['original']),t.from_numpy(data['labels']),reg['configuration'],progress,
        t.from_numpy(data['weights']),auxiliary_inputs=t.from_numpy(data['auxiliary'][data['indices']]),auxiliary_weight=.25)
    changed=[k for k,v in net.state_dict().items() if not t.equal(v,baseline[k])]
    b.require(all(k.startswith(('change.detail.8.','change.correction.')) for k in changed),'frozen_weights')
    t.save(dict(state=net.state_dict(),representation=p.VERSION,blend=0.),out/'last.pt');restored=p.load(out/'last.pt')
    with t.inference_mode():cached=restored.change(t.from_numpy(data['original'][:8])).sigmoid().flatten().numpy()
    actual=b.worker.score(restored,images);error=float(np.max(np.abs(cached-actual)))
    b.require(error<1e-6 and np.array_equal(actual,b.worker.score(net,images)),'parity')
    b.write(out/'fit.json',dict(history=history,changedTensors=changed,cacheImageMaximumError=error,seconds=time.monotonic()-start))
    membership=b.read(b.PACKAGE/'membership.json');native=np.load(b.PACKAGE/'native.npy',allow_pickle=False);nd,_=r.prepare(native,membership['rows'],2)
    def transform(key,x):
        if key=='native.npy':return np.concatenate((x,nd),1)
        if key=='reverse_native.npy':return np.concatenate((x,r.reverse_details(nd)),1)
        return x
    init=b.checked(b.read(r.OUT/'registration.json')['initializer'])
    result=b.evaluate_full(restored,{'DTM085':r.s.c.model.load_candidate(init)},b.read(b.PACKAGE/'manifest.json'),input_transform=transform)
    b.write(out/'evaluation.json',result)
    import report_authored319
    report_authored319.main(OUT,loader=p.load,run_folder=out)
    with t.inference_mode():prob=restored.change(t.from_numpy(data['auxiliary'])).sigmoid().flatten().numpy()
    b.write(out/'training.json',dict(summary=b.trainer.w.summary(prob,data['auxiliaryLabels']),probabilities=prob.tolist()))
    b.write(out/'completion.json',dict(seconds=time.monotonic()-start,model=b.ref(out/'last.pt'),productionEligible=False))
    b.require(sum(v.stat().st_size for v in OUT.rglob('*') if v.is_file())<2*1024**3,'output_limit')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['generate','validate','prepare',*ARMS]);args=parser.parse_args()
    if args.mode in ARMS:run(args.mode)
    else:globals()[args.mode]()
