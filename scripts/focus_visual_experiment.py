"""FOCUS-VISUAL-05: versioned input/prefix preparation and existing-trainer adapter."""
import argparse
import io
import importlib.metadata
import json
import math
import time
from collections import defaultdict

from PIL import Image, ImageDraw, ImageOps
import human_annotation_review as h
import focus_context_experiment as previous
import focus_context_inputs as spatial

VERSION = 'focus-visual-experiment-v1'
ARMS = {'visual-local-frozen':'fdr027-local-frozen',
        'visual-context-frozen':'fdr028-context-frozen',
        'visual-local-partial':'fdr029-local-partial',
        'visual-context-partial':'fdr030-context-partial'}
PACKET = 'reports/work/FOCUS-VISUAL-05'
CODE = ['focus_visual_experiment.py','focus_full_fit_experiment.py',
        'focus_learning_experiment.py','train_focus_ring_detector.py',
        'focus_representative_experiment.py','focus_representative_validation.py',
        'focus_pretrained_experiment.py','focus_retention_experiment.py',
        'focus_dataset_contract.py','human_focus_roles.py']


def packages():
    return {name:importlib.metadata.version(name) for name in ('torch','torchvision','Pillow','numpy')}


def window(bounds, size):
    x,y,w,ht = bounds; W,H = size
    h.require(all(math.isfinite(v) for v in bounds) and w>0 and ht>0 and W*H<=spatial.MAX_PIXELS,
              'invalid_visual_geometry')
    side=.6*max(W,H);cx=x+w/2;cy=y+ht/2
    return [cx-side/2,cy-side/2,side,side]


def context_image(image, bounds):
    x,y,w,ht=window(bounds,image.size)
    return image.convert('RGB').transform((256,256),Image.Transform.AFFINE,
        (w/256,0,x,0,ht/256,y),Image.Resampling.BILINEAR,fillcolor=(0,0,0))


def context_mask(record):
    """Label-free body+halo coverage at frozen-prefix resolution."""
    import torch
    side=record['contextSide'];w,ht=record['bounds'][2:]
    centers=(torch.arange(16,dtype=torch.float32)+.5)*side/16-side/2
    # Soft box/pixel overlap avoids disappearing tiny masks.
    left=centers-side/32;right=centers+side/32
    overlap=lambda size:(torch.minimum(right,torch.tensor(size*.66))-
                          torch.maximum(left,torch.tensor(-size*.66))).clamp(min=0)/(side/16)
    return overlap(ht)[:,None]*overlap(w)[None,:]


def protected(rows):
    allowed={('train','train-candidate'),('train','human-static-auxiliary'),
             ('validation','representative-selection'),('validation','retention-validation')}
    h.require(len({r['id'] for r in rows})==len(rows) and
              all((r['split'],r['use']) in allowed and r['label'] in (0,1) for r in rows),
              'visual_membership_or_protected_role')


def source_documents():
    e=h.read(h.ROOT/'reports/work/FOCUS-CONTEXT-04/envelope.json')
    base=previous.verified_base(e['baseProtocol'])
    context=previous.verified_context(e['context'],base)
    protected(base['samples'])
    return e,base,context


def prepare(output):
    started=time.monotonic();out=h.fresh(output)
    e,base,context=source_documents()
    members={m['id']:m for m in context['members']};rows=base['samples']
    h.require(len(rows)==1883,'visual_corpus_count')
    out.mkdir(parents=True);(out/'images').mkdir();(out/'sheets').mkdir()
    records=[];cache={};pairs=defaultdict(dict)
    for row in rows:
        m=members[row['id']];scene=context['scenes'][m['sceneKey']]
        W,H=scene['transform']['sourceSize']
        x,y,w,ht=m['geometry']['normalizedBounds'];bounds=[x*W,y*H,w*W,ht*H]
        original=scene['original'];key=(original['path'],original['sha256'])
        # At most one decoded original stays resident.
        if key not in cache:
            cache.clear()
            with Image.open(h.ROOT/original['path']) as im:cache[key]=im.convert('RGB')
        im=cache[key];name=h.digest(row['id'])+'.png';path=out/'images'/name
        context_image(im,bounds).save(path)
        side=.6*max(W,H)
        records.append(dict(id=row['id'],local=row['crop'],context=h.ref(path),
            original=original,bounds=bounds,sourceSize=[W,H],contextSide=side,
            targetPixels=[bounds[2]*256/side,bounds[3]*256/side],
            contextClipsBody=bounds[2]>side or bounds[3]>side,
            viewportClipped=any(m['geometry']['clipped'])))
        if row.get('sourceElementID'):
            pairs[(row['sourceID'],row['sourceElementID'])].setdefault(row['label'],len(records)-1)
    growth=[]
    for pair,indices in sorted(pairs.items()):
        if set(indices)!={0,1}:continue
        a,b=indices[0],indices[1]
        u,f=records[a],records[b]
        if u['sourceSize']!=f['sourceSize']:continue
        ratios=[f['bounds'][i]/u['bounds'][i] for i in (2,3)]
        observed=[f['targetPixels'][i]/u['targetPixels'][i] for i in (0,1)]
        h.require(all(math.isclose(x,y,rel_tol=1e-9) for x,y in zip(ratios,observed)), 'growth_erased')
        if min(ratios)>1.08:growth.append(dict(pair=pair,indices=[a,b],ratios=ratios))
    # Deterministic evidence selection, not model-score selection or new data admission.
    selected=[]
    for g in growth[:2]:selected.extend(g['indices'])
    for control in ('collectionItem','listRow','primaryButton','75'):
        for label in (0,1):
            match=next((i for i,r in enumerate(rows) if r.get('control')==control and r['label']==label
                        and i not in selected and r['split']=='validation'),None)
            if match is not None:selected.append(match)
    clipped=next((i for i,r in enumerate(records) if r['viewportClipped'] or r['contextClipsBody']),None)
    if clipped is not None and clipped not in selected:selected.append(clipped)
    sheet_refs=[]
    from focus_dataset_contract import expanded_box
    for number,i in enumerate(selected,1):
        r=records[i]
        with Image.open(h.ROOT/r['original']['path']) as im:
            original=im.convert('RGB');x,y,w,ht=r['bounds']
            overlay=original.copy();ImageDraw.Draw(overlay).rectangle((x,y,x+w,y+ht),outline='lime',width=4)
            box=expanded_box(r['bounds'],im.size)
            raw=original.crop(tuple(box));aspect=ImageOps.pad(raw,(256,256),color=(0,0,0))
            scene=ImageOps.pad(overlay,(512,288),color=(0,0,0))
        with Image.open(h.ROOT/r['local']['path']) as im:detail=im.convert('RGB')
        with Image.open(h.ROOT/r['context']['path']) as im:ctx=im.convert('RGB')
        sheet=Image.new('RGB',(1024,620),'#222222');draw=ImageDraw.Draw(sheet)
        draw.text((8,8),f'{number:02d} {rows[i].get("control")} label={rows[i]["label"]}',fill='white')
        draw.text((8,28),r['id'],fill='white');sheet.paste(scene,(0,65))
        for j,(label,img) in enumerate([('Production detail',detail),('Aspect fit (diagnostic)',aspect),('Fixed-scale context',ctx)]):
            sheet.paste(img,(256*j,360));draw.text((256*j+5,340),label,fill='white')
        path=out/'sheets'/f'{number:02d}.png';sheet.save(path);sheet_refs.append(dict(id=r['id'],image=h.ref(path)))
    doc=dict(version='focus-visual-input-v1',baseProtocol=e['baseProtocol'],sourceContext=e['context'],
        sourceSamples=rows,records=records,sourceConfiguration=base['configuration'],
        representation=base['representation'],selection=base['selection'],fullFit=base['fullFit'],
        unmetQualificationBlockers=base['unmetQualificationBlockers'],
        counts=base['counts'],growthPairs=growth,sheets=sheet_refs,
        contextBodyClips=sum(r['contextClipsBody'] for r in records),
        elapsedSeconds=time.monotonic()-started)
    h.write(out/'inputs.json',doc)
    lines=['# Input comparison sheets','', 'Original with candidate box, production detail, diagnostic aspect-fit, fixed-scale context.','']
    for s in sheet_refs:lines.extend([f'## {s["id"]}','',f'![Comparison]({str((h.ROOT/s["image"]["path"]).resolve())})',''])
    (out/'review.md').write_text('\n'.join(lines))
    print(json.dumps(dict(inputs=h.ref(out/'inputs.json'),growthPairs=len(growth),sheets=len(sheet_refs),
                         contextBodyClips=doc['contextBodyClips'])),flush=True)


def make_network(rep):
    import torch
    from torchvision.models import mobilenet_v3_small
    from focus_pretrained_experiment import WEIGHTS_SHA
    h.require(rep['weights']['sha256']==WEIGHTS_SHA,'visual_weights_identity')
    network=mobilenet_v3_small(weights=None)
    network.load_state_dict(torch.load(h.checked(h.ROOT,rep['weights']),map_location='cpu',weights_only=True))
    return network


def validate_inputs(doc):
    h.require(doc['version']=='focus-visual-input-v1','visual_input_version')
    protected(doc['sourceSamples'])
    h.require([r['id'] for r in doc['records']]==[r['id'] for r in doc['sourceSamples']], 'visual_input_order')
    h.require(all(doc['counts'].get(k)==n for k,n in dict(training=1550,development=315,retention=18).items()),
              'visual_counts')
    h.require(len(doc['records'])==1883 and sum(r['split']=='train' for r in doc['sourceSamples'])==1550,
              'visual_count_membership')
    for r in doc['records']:
        side=window(r['bounds'],r['sourceSize'])[2]
        h.require(math.isclose(r['contextSide'],side),'visual_window_changed')
        for role in ('local','context'):h.checked(h.ROOT,r[role])


def encode(inputs,output):
    doc=h.read(h.local(inputs),limit=32*1024**2);validate_inputs(doc);out=h.fresh(output)
    import torch
    import numpy as np
    from focus_pretrained_experiment import state_digest
    h.require(torch.backends.mps.is_available(),'visual_requires_mps')
    start=time.monotonic();prefix=make_network(doc['representation']).features[:9].eval().to('mps')
    for p in prefix.parameters():p.requires_grad_(False)
    before=state_digest(prefix);values=[]
    rep=doc['representation'];mean=torch.tensor(rep['normalization']['mean'],device='mps')[None,:,None,None]
    std=torch.tensor(rep['normalization']['std'],device='mps')[None,:,None,None]
    with torch.no_grad():
        for offset in range(0,len(doc['records']),32):
            h.require(time.monotonic()-start<300,'visual_encoding_timeout');streams=[]
            for role in ('local','context'):
                images=[]
                for r in doc['records'][offset:offset+32]:
                    with Image.open(h.ROOT/r[role]['path']) as im:
                        h.require(im.size==(256,256),'visual_image_size')
                        images.append(torch.from_numpy(np.array(im.convert('RGB'),copy=True)).permute(2,0,1))
                x=torch.stack(images).to('mps').float()/255
                features=prefix((x-mean)/std).cpu()
                masks=torch.stack([context_mask(r) if role=='context' else torch.ones(16,16)
                                   for r in doc['records'][offset:offset+32]])[:,None]
                streams.append(torch.cat((features,masks),dim=1))
            values.append(torch.stack(streams,dim=1))
            print(f'prefix {min(offset+32,len(doc["records"]))}/{len(doc["records"])}',flush=True)
    x=torch.cat(values)
    h.require(x.shape==(1883,2,49,16,16) and bool(torch.isfinite(x).all()) and state_digest(prefix)==before,
              'visual_prefix_output')
    receipt=dict(version='focus-visual-prefix-v1',inputs=h.ref(h.local(inputs)),
        ids=[r['id'] for r in doc['records']],prefixSHA256=before,
        featureSHA256=previous.tensor_digest(x),elapsedSeconds=time.monotonic()-start,
        prefixUnchanged=True,shape=list(x.shape))
    buffer=io.BytesIO();torch.save(dict(features=x,receipt=receipt),buffer)
    h.require(buffer.tell()<=512*1024**2 and time.monotonic()-start<=300,'visual_cache_budget')
    out.mkdir(parents=True);(out/'prefix.pt').write_bytes(buffer.getbuffer());h.write(out/'receipt.json',receipt)
    refs=dict(cache=h.ref(out/'prefix.pt'),receipt=h.ref(out/'receipt.json'))
    h.write(out/'references.json',refs);print(json.dumps(refs),flush=True)


def build_protocol(inputs,cache,authority,output):
    doc=h.read(h.local(inputs),limit=32*1024**2);validate_inputs(doc)
    refs=h.read(h.local(cache));receipt=previous.read(refs['receipt']);h.checked(h.ROOT,refs['cache'],limit=512*1024**2)
    h.require(receipt['inputs']==h.ref(h.local(inputs)) and receipt['ids']==[r['id'] for r in doc['records']]
              and receipt['prefixUnchanged'] is True,'visual_cache_binding')
    protocol=dict(version=VERSION,inputs=h.ref(h.local(inputs)),features=refs,
        authority=h.ref(h.local(authority)),arms=ARMS,samples=doc['sourceSamples'],
        representation=doc['representation'],selection=doc['selection'],counts=doc['counts'],
        configuration=dict(doc['sourceConfiguration'],model='mobilenet_v3_small_partial_visual',
                           initialization='imagenet-prefix-tail-fresh-mlp',epochs=100),
        fullFit=dict(doc['fullFit'],microbatch=32,tailLR=.0001,validationEvery=10,stopOnFit=False),
        runtime=dict(code=[h.ref(h.ROOT/'scripts'/n) for n in CODE],packages=packages()),
        limits=dict(runs=4,secondsPerRun=300,wallSeconds=1800,outputBytes=2*1024**3),
        unmetQualificationBlockers=doc['unmetQualificationBlockers'],releaseEligible=False)
    protocol['protocolSHA256']=h.digest(protocol);out=h.fresh(output);out.mkdir(parents=True)
    h.write(out/'protocol.json',protocol);h.write(out/'approval.json',approval(protocol))
    print(protocol['protocolSHA256'])


def approval(doc):
    return dict(version='focus-visual-tranche-approval-v1',protocolSHA256=doc['protocolSHA256'],
                authority=doc['authority'],arms=ARMS,scope='four-local-comparisons-no-export')


def load_protocol(path,arm,run_name,approval_path=None):
    ref=h.ref(h.local(path));doc=previous.sealed(ref)
    h.require(doc['version']==VERSION and doc['arms']==ARMS and ARMS.get(arm)==run_name,'visual_arm_binding')
    h.checked(h.ROOT,doc['authority']);protected(doc['samples'])
    source=previous.read(doc['inputs'])
    expected_cfg=dict(source['sourceConfiguration'],model='mobilenet_v3_small_partial_visual',
                      initialization='imagenet-prefix-tail-fresh-mlp',epochs=100)
    h.require(doc['configuration']==expected_cfg and doc['fullFit']==dict(source['fullFit'],
        microbatch=32,tailLR=.0001,validationEvery=10,stopOnFit=False)
        and doc['limits']==dict(runs=4,secondsPerRun=300,wallSeconds=1800,outputBytes=2*1024**3)
        and doc['runtime']==dict(code=[h.ref(h.ROOT/'scripts'/n) for n in CODE],packages=packages()),
        'visual_protocol_configuration')
    h.require(doc['samples']==source['sourceSamples'] and doc['selection']==source['selection']
              and doc['fullFit']['weights']==source['fullFit']['weights'],'visual_source_changed')
    for r in doc['runtime']['code']:h.checked(h.ROOT,r)
    h.checked(h.ROOT,doc['features']['cache'],limit=512*1024**2);receipt=previous.read(doc['features']['receipt'])
    h.require(receipt['inputs']==doc['inputs'] and receipt['ids']==[r['id'] for r in doc['samples']],
              'visual_cache_membership')
    out=h.ROOT/'NativeUITrainer/focus_ring_runs'/run_name
    h.require(not out.exists() and not any(p.is_symlink() for p in (out,*out.parents)),'output_collision')
    ar=h.ref(h.local(approval_path)) if approval_path else None
    if ar:h.require(previous.read(ar)==approval(doc),'visual_approval_binding')
    report=dict(protocolVersion=VERSION,protocolFile=ref,approval=ar,arm=arm,visualTraining=True,
        features=doc['features'],warmCheckpoint=None,configurationValid=True,executionAuthorized=False,releaseEligible=False,
        launchEligible=ar is not None,blockers=[] if ar else ['missing_visual_approval'],
        **{k:doc[k] for k in ('configuration','fullFit','representation','selection','counts',
                             'runtime','protocolSHA256','unmetQualificationBlockers')})
    return report,[dict(r,path=h.ROOT/r['crop']['path']) for r in doc['samples']]


def make_model(rep,arm,device):
    import torch
    from torch import nn
    h.require(arm in ARMS,'visual_arm')
    network=make_network(rep);partial=arm.endswith('partial');context='context' in arm
    class Visual(nn.Module):
        def __init__(self):
            super().__init__();self.tail=network.features[9:]
            torch.manual_seed(42);self.head=nn.Sequential(nn.Linear(1152,64),nn.ReLU(),nn.Linear(64,1))
            with torch.no_grad():self.head[0].weight[:,576:]=0
            for p in self.tail.parameters():p.requires_grad_(partial)
            for m in self.tail.modules():
                if isinstance(m,nn.modules.batchnorm._BatchNorm):
                    for p in m.parameters():p.requires_grad_(False)
        def train(self,mode=True):
            super().train(mode)
            for m in self.tail.modules():
                if isinstance(m,nn.modules.batchnorm._BatchNorm):m.eval()
            return self
        def forward(self,x):
            a=self.tail(x[:,0,:-1]).mean((-2,-1))
            if context:
                features=self.tail(x[:,1,:-1])
                mask=nn.functional.interpolate(x[:,1,-1:],size=features.shape[-2:],mode='area')
                b=(features*mask).sum((-2,-1))/mask.sum((-2,-1)).clamp(min=1e-9)
            else:b=torch.zeros_like(a)
            return self.head(torch.cat((a,b),1))
        def optimizer_groups(self,lr,tail_lr):
            return [dict(params=self.head.parameters(),lr=lr),
                    dict(params=[p for p in self.tail.parameters() if p.requires_grad],lr=tail_lr)]
    return Visual().to(device).eval()


def prepare_features(report,train,val,device,out):
    import torch
    from focus_pretrained_experiment import state_digest
    refs=report['features'];receipt=previous.read(refs['receipt'])
    data=torch.load(h.checked(h.ROOT,refs['cache'],limit=512*1024**2),map_location='cpu',weights_only=True)
    x=data['features']
    h.require(data['receipt']==receipt and receipt['ids']==[r['id'] for r in train+val]
              and x.shape==(len(train)+len(val),2,49,16,16) and x.dtype==torch.float32
              and bool(torch.isfinite(x).all()) and previous.tensor_digest(x)==receipt['featureSHA256'],
              'visual_cache_tensors')
    model=make_model(report['representation'],report['arm'],device)
    report['initialTailSHA256']=state_digest(model.tail)
    report['initialBNSHA256']=state_digest(torch.nn.ModuleList([m for m in model.tail.modules()
        if isinstance(m,torch.nn.modules.batchnorm._BatchNorm)]))
    y=torch.tensor([r['label'] for r in train+val],dtype=torch.float32).reshape(-1,1);n=len(train)
    h.write(out/'visual-input-receipt.json',dict(features=refs,encoderPrefixLoaded=False,
        partialBackbone=report['arm'].endswith('partial'),initialTailSHA256=report['initialTailSHA256']))
    return model,torch.utils.data.TensorDataset(x[:n],y[:n]),torch.utils.data.TensorDataset(x[n:],y[n:])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','encode','protocol'])
    p.add_argument('--inputs');p.add_argument('--cache');p.add_argument('--authority');p.add_argument('--output',required=True)
    a=p.parse_args()
    if a.mode=='prepare':prepare(a.output)
    elif a.mode=='encode':encode(a.inputs,a.output)
    else:build_protocol(a.inputs,a.cache,a.authority,a.output)


if __name__=='__main__':main()
