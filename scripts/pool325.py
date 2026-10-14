"""Compare fixed pooled detail features with the existing trainer."""
import argparse
import gc
from pathlib import Path
import time
import types
import numpy as np
from PIL import Image,ImageDraw
import authored319 as a

b=a.b;r=a.r;t=a.t
OUT=b.ROOT/'reports/work/FOCUS-325'
VERSION='pool325-v1'


def pool(values,blend):
    b.require(blend in (0.,.5),'pool_blend')
    avg=t.nn.functional.adaptive_avg_pool2d(values,(4,6))
    return avg if blend==0 else (avg+t.nn.functional.adaptive_max_pool2d(values,(4,6)))*.5


class PoolChange(r.RegionChange):
    cache_contract=VERSION

    def cached(self,images):
        b.require(images.ndim==4 and images.shape[1] in (6,18) and images.shape[2:]==(128,192),'pool_images')
        whole=images[:,:6];details=images[:,6:] if images.shape[1]==18 else r.encoded_details(whole,2)
        context=self.whole[:10](r.s.c.model.change_inputs(None,whole));score=self.whole[10](context)
        maps=[self.detail[:6](r.s.c.model.change_inputs(None,details[:,6*j:6*(j+1)])) for j in range(2)]
        return {blend:t.cat([context,score]+[pool(v,blend).flatten(1) for v in maps],1) for blend in (0.,.5)}

    def forward(self,images):
        if images.ndim!=2:images=self.cached(images)[self.blend]
        b.require(images.shape[1]==1185 and t.isfinite(images).all(),'pool_cache')
        context=images[:,:32];score=images[:,32:33]
        features=t.stack([self.detail[8:](images[:,33+576*j:33+576*(j+1)]) for j in range(2)]).mean(0)
        return score+self.correction(t.cat((context,features),1))


def make(net,blend):
    b.require(blend in (0.,.5),'pool_blend')
    net.change.__class__=PoolChange;net.change.blend=blend
    return net


def load(path):
    saved=t.load(path,map_location='cpu',weights_only=True)
    b.require(saved.get('representation')==VERSION,'pool_checkpoint')
    net=make(r.extend(r.s.c.model.extend(b.worker.make_model(t,paired_context=True)),2),saved['blend'])
    net.load_state_dict(saved['state']);return net.eval()


def patch(images,size):
    b.require(size in (3,6,12) and len(images)==2 and images[0].size==images[1].size==(1920,1080),'patch_inputs')
    # Retain the same control body, nearby background, and bounded effect area.
    return [im.crop((197,272,613,848)).resize((round(416*size/32),round(576*size/32)),Image.Resampling.LANCZOS) for im in images]


def compose(parts,centers,focus,variant=False):
    b.require(focus in (0,1) and len(parts)==2 and len(centers)==2,'compose_inputs')
    image=Image.new('RGB',(1920,1080),(20,20,25));bounds=[]
    for i,(x,y) in enumerate(centers):
        tile=parts[1 if variant and i==1 else 0][int(i==focus)]
        w,h=tile.size;left=round(x-w/2);top=round(y-h/2)
        b.require(left>=0 and top>=0 and left+w<=1920 and top+h<=1080,'patch_clipped')
        image.paste(tile,(left,top));bounds.append([left,top,w,h])
    return image,bounds


def generate():
    b.require(not (OUT/'corpus.json').exists() and not (OUT/'images').exists(),'output_collision')
    OUT.mkdir(exist_ok=True);(OUT/'images').mkdir();old=b.read(a.OUT/'corpus.json');review=b.read(a.OUT/'review.json')
    b.require(review['approvedForAuthoredTraining'] and review['corpusSHA256']==b.ref(a.OUT/'corpus.json')['sha256'],'source_admission')
    plan=b.read(b.checked(old['plan']));rows=[];sources=[];samples=[];pixels={}
    for family in range(3):
        assets=[v for v in plan['assets'] if f'-s{family}-' in v['id']]
        b.require(len(assets)==2,'asset_family');group=assets[0]['groups'][0]
        base=[]
        for variant in range(2):
            folder=a.OUT/f'render-{family}-{variant}-shelf-shelf_poster_0'
            focused,meta=a.frame(folder,'shelf','shelf_poster_0')
            un=b.ref(folder/'shelf_unfocused.png');sources.extend([un,focused])
            base.append([r.s.image(v['path'],v['sha256']) for v in (un,focused)])
        for size in (3,6,12):
            parts=[patch(v,size) for v in base]
            for separation in (320,960):
                for corner,(x,y,dx) in enumerate([(180,180,1),(1740,180,-1),(180,900,1),(1740,900,-1)]):
                    centers=[(x,y),(x+dx*separation,y)]
                    before,boxes=compose(parts,centers,0)
                    moved,_=compose(parts,centers,1);art,_=compose(parts,centers,0,True)
                    stem=f'f{family}-s{size}-d{separation}-c{corner}';pins=[]
                    for name,image in [('before',before),('moved',moved),('art',art)]:
                        path=OUT/'images'/f'{stem}-{name}.png';image.save(path);pins.append(b.ref(path))
                    for condition,indices,label in [('movement',(0,1),1),('artwork-only',(0,2),0),('identical',(0,0),0)]:
                        for reverse in (False,True):
                            pair=[pins[i] for i in indices][::(-1 if reverse else 1)]
                            ims=[r.s.image(v['path'],v['sha256']) for v in pair]
                            hashes=[b.sha(np.asarray(im).tobytes()) for im in ims]
                            b.require(pixels.setdefault(tuple(hashes),label)==label,'label_conflict')
                            b.require((hashes[0]==hashes[1])==(condition=='identical'),'invisible_pair')
                            rows.append(dict(id=f'{stem}-{condition}-{int(reverse)}',images=pair,decodedHashes=hashes,
                                group=group,role='train',changed=label,condition=condition,reverse=reverse,
                                sizePixels=size,separationPixels=separation*.1,corner=corner,patchBounds=boxes,
                                labelAuthority='Authored composition states. Not native focus observations.'))
                    if family==0 and separation==960 and corner==0:samples.extend([before,moved,art])
        print('Prepared family',family,flush=True)
    b.require(len(rows)==432,'pair_count')
    sheet=Image.new('RGB',(960,540));draw=ImageDraw.Draw(sheet)
    for i,im in enumerate(samples):sheet.paste(im.resize((320,180)),((i%3)*320,(i//3)*180))
    sheet.save(OUT/'review.png')
    b.write(OUT/'corpus.json',dict(version=VERSION,rows=rows,sources=sources,sourceCorpus=b.ref(a.OUT/'corpus.json'),
        sourceReview=b.ref(a.OUT/'review.json'),assets=plan['assets'][:6],role='train',nativeQualified=False,
        expectedPairs=432,uniquePairs=len(pixels),sizes=[3,6,12],separations=[32,96],corners=4,
        limitation='Bounded source patches include clipped shadows and background. These are authored compositions, not exact native effects.'))


def cache(net,values,details):
    result={0.:[],.5:[]};ratios=[]
    with t.inference_mode():
        for start in range(0,len(values),8):
            x=t.from_numpy(np.concatenate((values[start:start+8],details[start:start+8]),1))
            cached=net.change.cached(x)
            for blend in result:result[blend].append(cached[blend].numpy())
            avg=cached[0.][:,33:];mixed=cached[.5][:,33:]
            ratios.extend(((mixed-avg).abs().mean(1)/(avg.abs().mean(1)+1e-6)).tolist())
    return {k:np.concatenate(v) for k,v in result.items()},ratios


def validate():
    corpus=b.read(OUT/'corpus.json');records=[]
    for family in range(3):
        for variant in range(2):
            meta=b.read(a.OUT/f'render-{family}-{variant}-shelf-shelf_poster_0/shelf_annotations.json')
            node=next(v for v in meta['nodes'] if v['id']=='shelf_poster_0')
            b.require(np.allclose(node['unfocusedBounds'],[245,320,320,480]) and
                np.allclose(node['focusedBounds'],[222.6,286.4,364.8,547.2]),'source_geometry')
    for row in corpus['rows']:
        arrays=[]
        for ref in row['images']:
            with Image.open(b.checked(ref)) as image:
                b.require(image.size==(1920,1080) and image.mode=='RGB','image_contract')
                arrays.append(np.asarray(image).copy())
        delta=np.any(arrays[0]!=arrays[1],axis=2);allowed=np.zeros(delta.shape,bool)
        for x,y,w,h in row['patchBounds']:allowed[y:y+h,x:x+w]=True
        b.require(not delta[~allowed].any(),'outside_patch_change')
        if row['condition']=='identical':b.require(not delta.any(),'identity_change')
        else:b.require(delta.any(),'invisible_condition')
        if row['condition']=='artwork-only':
            x,y,w,h=row['patchBounds'][0];b.require(not delta[y:y+h,x:x+w].any(),'focused_artwork_changed')
        ids=[0,1] if row['changed'] else [0,0]
        if row['reverse']:ids.reverse()
        endpoints=[]
        for focus in ids:
            boxes=[]
            for i,(x,y,w,h) in enumerate(row['patchBounds']):
                raw=(222.6,286.4,364.8,547.2) if i==focus else (245,320,320,480)
                boxes.append([x+(raw[0]-197)*w/416,y+(raw[1]-272)*h/576,raw[2]*w/416,raw[3]*h/576])
            endpoints.append(dict(focusID=f'control-{focus}',bodyBounds=boxes))
        records.append(dict(id=row['id'],endpoints=endpoints,changedPixels=int(delta.sum()),
            imageHashes=[v['sha256'] for v in row['images']],labelAuthority=row['labelAuthority']))
    b.write(OUT/'annotations.json',dict(corpus=b.ref(OUT/'corpus.json'),rows=records,coordinateSpace='image_top_left_pixels',
        boundsMeaning='Transformed authored control bodies. Shadow clipping remains limited by the retained patch.'))
    print('Validated',len(records),'pairs',flush=True)


def prepare():
    t.set_num_threads(2);started=time.monotonic();b.require(not (OUT/'inputs.json').exists(),'output_collision')
    corpus=b.read(OUT/'corpus.json');review=b.read(OUT/'review.json')
    b.require(review['approvedForAuthoredTraining'] and review['corpusSHA256']==b.ref(OUT/'corpus.json')['sha256'],'review_required')
    annotations=b.read(b.checked(review['annotations']))
    b.require(annotations['corpus']==b.ref(OUT/'corpus.json') and len(annotations['rows'])==432,'annotations_required')
    manifest,membership,full,labels,weights,extra,controls,_,reg=r.s.c.prepare()
    added=r.s.previous.prior.mix(full[controls],extra,labels[1660:1740],True)
    values=np.concatenate((full,added,b.reporting.reverse(added)));del full,extra,added
    parent=b.read(r.OUT/'registration.json')
    for k,v in [('training',values),('labels',labels),('weights',weights)]:b.require(b.sha(v.tobytes())==parent[k+'SHA256'],'original_'+k)
    rows=r.s.schedule_rows(membership,reg,labels);details,_=r.prepare(values,rows,2)
    b.require(b.sha(details.tobytes())==b.read(r.OUT/'regions-2/views.json')['sha256'],'original_details')
    initializer=b.ref(a.OUT/'run/last.pt');net=make(r.load_candidate(b.checked(initializer)),0.)
    original,ratios=cache(net,values,details)
    np.save(OUT/'parity-images.npy',np.concatenate((values[:8],details[:8]),1),allow_pickle=False)
    del values,details;gc.collect()
    old=b.read(a.OUT/'corpus.json');arows=old['rows']+corpus['rows']
    protected={row['group'] for row in membership['rows'] if row['role']!='train'}
    b.require(all(row['role']=='train' and row['group'] not in protected for row in arows),'protected_group')
    native=np.load(b.PACKAGE/'native.npy',mmap_mode='r',allow_pickle=False)
    excluded={b.sha(v.tobytes()) for i,row in enumerate(membership['rows']) if row['role']!='train' for v in (native[i,:3],native[i,3:])}
    tiny,_,_=r.s.tiny_rows();excluded.update(b.sha(v.tobytes()) for pair in tiny for v in (pair[:3],pair[3:]))
    aux={0.:[],.5:[]};auxratios=[]
    for start in range(0,len(arows),8):
        subset=arows[start:start+8];values=[]
        for row in subset:
            ims=[r.s.image(v['path'],v['sha256']) for v in row['images']]
            for pin in row['images']:b.checked(pin)
            value=r.s.encoded(*ims,(192,128))[0]
            b.require(all(b.sha(v.tobytes()) not in excluded for v in (value[:3],value[3:])),'protected_pixel')
            values.append(value)
        values=np.stack(values);details,_=r.prepare(values,subset,2);parts,rr=cache(net,values,details)
        for blend in aux:aux[blend].append(parts[blend])
        auxratios.extend(rr)
    aux={k:np.concatenate(v) for k,v in aux.items()};ids=a.schedule(labels,arows)
    ay=np.array([row['changed'] for row in arows],np.float32)
    b.require(np.array_equal(labels,ay[ids]) and len(np.unique(ids))==len(arows),'auxiliary_coverage')
    for blend,name in [(0.,'average'),(.5,'mixed')]:
        np.savez(OUT/f'{name}.npz',original=original[blend],auxiliary=aux[blend],labels=labels,weights=weights,indices=ids,auxiliaryLabels=ay)
    b.write(OUT/'inputs.json',dict(corpus=b.ref(OUT/'corpus.json'),review=b.ref(OUT/'review.json'),initializer=initializer,
        oldCorpus=b.ref(a.OUT/'corpus.json'),runner=b.ref(Path(__file__)),trainer=b.ref(Path(b.trainer.__file__)),
        originalHashes={k:parent[k] for k in ('trainingSHA256','labelsSHA256','weightsSHA256')},
        cache={name:b.ref(OUT/f'{name}.npz') for name in ('average','mixed')},parity=b.ref(OUT/'parity-images.npy'),
        configuration=dict(epochs=30,lr=.0001,batch=16,seed=42,threads=2,detailOnly=True,cachedDetailOnly=True),
        thresholds=[.15,.85],auxiliaryWeight=.25,rolesChanged=False,protectedOverlap=False,
        trainingRows=len(labels),auxiliaryRows=len(arows),scheduledUnique=len(np.unique(ids)),
        poolingContrast=dict(originalQuantiles=np.quantile(ratios,[0,.5,.9,1]).tolist(),
            newSmallQuantiles=np.quantile(auxratios[240:],[0,.5,.9,1]).tolist()),seconds=time.monotonic()-started))
    print('Preparation complete',time.monotonic()-started,flush=True)


def run(name):
    started=time.monotonic();reg=b.read(OUT/'inputs.json');t.set_num_threads(2)
    for key in ('runner','trainer','corpus','review','oldCorpus'):b.checked(reg[key])
    data=np.load(b.checked(reg['cache'][name]),allow_pickle=False);blend=0. if name=='average' else .5
    out=OUT/name;b.require(not out.exists(),'output_collision');out.mkdir()
    net=make(r.load_candidate(b.checked(reg['initializer'])),blend)
    images=np.load(b.checked(reg['parity']),allow_pickle=False)
    with t.inference_mode():cached=net.change(t.from_numpy(data['original'][:8])).sigmoid().flatten().numpy()
    b.require(np.max(np.abs(cached-b.worker.score(net,images)))<1e-6,'initial_cache_parity')
    b.write(out/'registration.json',dict(inputs=b.ref(OUT/'inputs.json'),blend=blend,configuration=reg['configuration'],
        selection='fixed-last',thresholds=[.15,.85],epochs=30,outputCapBytes=2*1024**3))
    def progress(row):b.write(out/f"epoch-{row['epoch']:04d}.json",row);print(name,row,flush=True)
    net,history=b.trainer.fit(net,t.from_numpy(data['original']),t.from_numpy(data['labels']),reg['configuration'],progress,
        t.from_numpy(data['weights']),auxiliary_inputs=t.from_numpy(data['auxiliary'][data['indices']]),auxiliary_weight=.25)
    t.save(dict(state=net.state_dict(),representation=VERSION,blend=blend),out/'last.pt');restored=load(out/'last.pt')
    with t.inference_mode():cached=restored.change(t.from_numpy(data['original'][:8])).sigmoid().flatten().numpy()
    actual=b.worker.score(restored,images);b.require(np.max(np.abs(cached-actual))<1e-6,'final_cache_parity')
    b.require(np.array_equal(actual,b.worker.score(net,images)),'checkpoint_parity')
    b.write(out/'fit.json',dict(history=history,seconds=time.monotonic()-started,cacheImageMaximumError=float(np.max(np.abs(cached-actual))),checkpointParity=True))
    membership=b.read(b.PACKAGE/'membership.json');native=np.load(b.PACKAGE/'native.npy',allow_pickle=False)
    nd,_=r.prepare(native,membership['rows'],2)
    def transform(key,x):
        if key=='native.npy':return np.concatenate((x,nd),1)
        if key=='reverse_native.npy':return np.concatenate((x,r.reverse_details(nd)),1)
        return x
    init=b.checked(b.read(r.OUT/'registration.json')['initializer'])
    result=b.evaluate_full(restored,{'DTM085':r.s.c.model.load_candidate(init)},b.read(b.PACKAGE/'manifest.json'),input_transform=transform)
    b.write(out/'evaluation.json',result)
    import report_authored319
    report_authored319.main(OUT,loader=load,run_folder=out)
    b.write(out/'completion.json',dict(seconds=time.monotonic()-started,model=b.ref(out/'last.pt'),productionEligible=False))
    b.require(sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<2*1024**3,'output_limit')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['generate','validate','prepare','average','mixed']);args=parser.parse_args()
    if args.mode=='generate':generate()
    elif args.mode=='validate':validate()
    elif args.mode=='prepare':prepare()
    else:run(args.mode)
