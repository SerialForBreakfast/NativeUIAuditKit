"""Prepare and run 25 fixed sensitivity tests using the existing queue."""
import argparse
import time
import numpy as np
import research_queue as q
from research_campaign340 import pin,decision
import additive341 as a

OUT=None
BASE=q.ROOT/'reports/work/FOCUS-346'
TESTS=[
 ('01-whole-floor','Limit the negative whole-frame contribution to -4.6.','Test whether whole-frame suppression hides useful detail without causing false changes.'),
 ('02-max-detail','Use maximum detail features instead of their mean.','Test whether averaging hides one useful crop.'),
 ('03-no-edges','Remove only the added gradient channels.','Measure reliance on explicit edges beyond RGB differences.'),
 ('04-first-detail','Use only the first detail feature vector.','Measure whether the second crop helps or distracts.'),
 ('05-second-detail','Use only the second detail feature vector.','Measure whether the first crop suppresses useful secondary evidence.'),
 ('06-brightness','Add 0.1 brightness to both frames.','Measure sensitivity to shared brightness and clipping.'),
 ('07-contrast','Reduce contrast around 0.5 by a factor of 0.65.','Measure dependence on absolute contrast.'),
 ('08-gamma','Apply gamma 1.5 to both frames.','Measure nonlinear luminance sensitivity.'),
 ('09-grayscale','Remove color while retaining luminance.','Measure reliance on color rather than effect geometry.'),
 ('10-saturation','Reduce saturation by half.','Test whether moderate artwork color variation changes decisions.'),
 ('11-blur','Apply a 3 by 3 average filter.','Measure sensitivity to softened boundaries.'),
 ('12-common-noise','Add paired noise with standard deviation 0.01.','Test texture noise without introducing temporal noise.'),
 ('13-quantization','Use 16 intensity levels per channel.','Measure sensitivity to coarse color precision.'),
 ('14-half-resolution','Downsample each encoded view by half and restore it.','Measure dependence on fine spatial detail.'),
 ('15-blocks','Use 8 by 8 block averages.','Measure sensitivity to block artifacts; this is not a codec simulation.'),
 ('16-horizontal','Reflect all encoded views horizontally.','Measure horizontal orientation bias with matched pairs.'),
 ('17-vertical','Reflect all encoded views vertically.','Measure vertical orientation bias with matched pairs.'),
 ('18-context-position','Move context 8 pixels right; retain detail.','Measure position dependence independently of local detail.'),
 ('19-padding','Replace the outer 8 context rows with gray.','Measure reliance on known letterbox padding.'),
 ('20-static-context','Replace exactly unchanged pixels with gray.','Measure dependence on unchanged appearance around the difference.'),
 ('21-partial-transition','Move the after frame halfway toward the before frame.','Measure sensitivity to incomplete visual transitions; settlement labels remain unavailable.'),
 ('22-first-stale','Repeat the before image in the first detail view.','Measure damage from a stale first detail view.'),
 ('23-second-stale','Repeat the before image in the second detail view.','Measure damage from a stale second detail view.'),
 ('24-exposure-flicker','Add 0.05 brightness to after frames only.','Measure nuisance exposure changes and stable-pair false alarms.'),
 ('25-frame-jitter','Move after frames right by 1 encoded pixel.','Measure nuisance alignment sensitivity and stable-pair false alarms.')]


def shifted(x,amount):
    out=x.clone();out.zero_();out[:,:,:,amount:]=x[:,:,:,:-amount]
    return out


def transform(x,mode,offset=0):
    y=x.clone()
    if mode=='06-brightness':y+=.1
    elif mode=='07-contrast':y=(y-.5)*.65+.5
    elif mode=='08-gamma':y=y.pow(1.5)
    elif mode in ('09-grayscale','10-saturation'):
        for j in range(0,18,3):
            rgb=y[:,j:j+3];gray=(rgb*a.t.tensor([.299,.587,.114])[None,:,None,None]).sum(1,keepdim=True)
            y[:,j:j+3]=gray if mode=='09-grayscale' else .5*rgb+.5*gray
    elif mode=='11-blur':y=a.t.nn.functional.avg_pool2d(a.t.nn.functional.pad(y,(1,1,1,1),mode='replicate'),3,stride=1)
    elif mode=='12-common-noise':
        for i in range(len(y)):
            generator=a.t.Generator().manual_seed(346000+offset+i)
            for j in (0,6,12):
                noise=a.t.randn((3,128,192),generator=generator)*.01
                y[i,j:j+3]+=noise;y[i,j+3:j+6]+=noise
    elif mode=='13-quantization':y=(y*15).round()/15
    elif mode=='14-half-resolution':
        y=a.t.nn.functional.interpolate(a.t.nn.functional.interpolate(y,scale_factor=.5,mode='bilinear',align_corners=False),size=(128,192),mode='bilinear',align_corners=False)
    elif mode=='15-blocks':y=a.t.nn.functional.interpolate(a.t.nn.functional.avg_pool2d(y,8),size=(128,192),mode='nearest')
    elif mode=='16-horizontal':y=y.flip(3)
    elif mode=='17-vertical':y=y.flip(2)
    elif mode=='18-context-position':y[:,:6]=shifted(y[:,:6],8)
    elif mode=='19-padding':y[:,:6,:8]=.5;y[:,:6,-8:]=.5
    elif mode=='20-static-context':
        for j in (0,6,12):
            mask=(y[:,j:j+3]==y[:,j+3:j+6]).all(1,keepdim=True)
            y[:,j:j+3]=a.t.where(mask,.5,y[:,j:j+3]);y[:,j+3:j+6]=a.t.where(mask,.5,y[:,j+3:j+6])
    elif mode=='21-partial-transition':
        for j in (0,6,12):y[:,j+3:j+6]=.5*(y[:,j:j+3]+y[:,j+3:j+6])
    elif mode in ('22-first-stale','23-second-stale'):
        j=6 if mode=='22-first-stale' else 12;y[:,j+3:j+6]=y[:,j:j+3]
    elif mode=='24-exposure-flicker':
        for j in (0,6,12):y[:,j+3:j+6]+=.05
    elif mode=='25-frame-jitter':
        for j in (0,6,12):y[:,j+3:j+6]=shifted(y[:,j+3:j+6],1)
    else:q.require(mode in {v[0] for v in TESTS[:5]},'unknown_mode')
    return y.clamp(0,1)


def logits(net,x,mode):
    if mode not in {v[0] for v in TESTS[:5]}:return net.change(x).flatten()
    context=net.change.whole[:10](a.r.s.c.model.change_inputs(None,x[:,:6]));features=[]
    for j in range(2):
        part=x[:,6+j*6:12+j*6];edges=a.e.gradient_channels(part)
        if mode=='03-no-edges':edges=edges*0
        features.append(net.change.detail(a.t.cat((a.r.s.c.model.change_inputs(None,part),edges),1)))
    pooled=a.t.stack(features).mean(0)
    if mode=='02-max-detail':pooled=a.t.stack(features).max(0).values
    elif mode=='04-first-detail':pooled=features[0]
    elif mode=='05-second-detail':pooled=features[1]
    whole=net.change.whole[10](context)
    if mode=='01-whole-floor':whole=whole.clamp(min=-4.6)
    return (whole+net.change.correction(a.t.cat((context,pooled),1))).flatten()


def count(rows,values,old):
    q.require(len(rows)==len(values)==len(old),'count_mismatch');groups={}
    for r,v,b in zip(rows,values,old):
        label=r['changed'];q.require(label in (0,1),'label')
        p=decision(float(v));prior=decision(float(b));key=r['sourceDomain']+'/'+r['condition']+'/'+r['group']
        item=groups.setdefault(key,dict(count=0,correct=0,falseChange=0,missedChange=0,abstentions=0,lost=0,gained=0))
        item['count']+=1;item['correct']+=p==label;item['falseChange']+=p==1 and label==0
        item['missedChange']+=p==0 and label==1;item['abstentions']+=p is None
        item['lost']+=prior==label and p!=label;item['gained']+=prior!=label and p==label
    return groups


def run():
    config=q.load(OUT/'config.json');start=time.monotonic();a.t.set_num_threads(2)
    for ref in config['inputs']:q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'input_hash')
    manifest=q.load(q.ROOT/config['manifest']['path']);net=a.e.load_candidate(q.ROOT/manifest['model']['path'])
    values=[];original=[]
    for chunk in manifest['chunks']:
        with np.load(q.ROOT/chunk['path'],allow_pickle=False) as data:
            tensor=a.t.from_numpy(data['tensor']);baseline=data['probabilities']
        with a.t.inference_mode():
            for offset in range(0,len(tensor),8):
                x=transform(tensor[offset:offset+8],config['mode'],len(values))
                values.extend(a.t.sigmoid(logits(net,x,config['mode'])).tolist())
        original.extend(baseline.tolist());print(f'{config["mode"]}: {len(values)}/{len(manifest["rows"])} cases',flush=True)
        q.save(OUT.parent/'progress.json',dict(step=config['mode'],completed=len(values),total=len(manifest['rows']),
            updatedAt=time.time(),message='Compare retained pairs with fixed baseline predictions.'),replace=True)
    rows=manifest['rows'];result=dict(version='sensitivity346-v1',mode=config['mode'],inputs=config['inputs'],
        originalProbabilities=original,probabilities=values,rows=rows,counts=count(rows,values,original),
        seconds=time.monotonic()-start,modelChanged=False,promotionAllowed=False,
        coverage=dict(themes='Unavailable unless a retained row records a verified theme.',
            archetypes='Retained groups only. This batch does not cover all 7 archetypes.',
            nativeQualification='Unresolved app/build match. Native pairs remain development-only.'),
        limitations=['Encoded-view interventions, not new native captures or deployment qualification.',
            'Counts compare with original pair labels. Altered views may remove the visible evidence.',
            'Related and reversed pairs are not independent. Roles and final-evaluation exclusions remain unchanged.',
            'Feature interventions are not calibrated models. Review gains and losses before any training proposal.'])
    q.save(OUT/'diagnostic.json',result)


def prepare():
    q.require(not BASE.exists(),'output_collision');BASE.mkdir();start=time.monotonic();a.t.set_num_threads(2)
    source=['reports/work/FOCUS-319/corpus.json','reports/work/FOCUS-326/corpus.json','reports/work/FOCUS-341/negatives.json',
        'reports/work/research-queue/jobs/focus343-native/attempts/1/out/diagnostic.json']
    rows=q.load(q.ROOT/source[0])['rows']+q.load(q.ROOT/source[1])['rows']['independent']+q.load(q.ROOT/source[2])['rows']
    rows=[dict(r,originalID=r.get('id'),id='retained346-'+str(i),sourceDomain='authored') for i,r in enumerate(rows)]
    rows += [dict(r,sourceDomain='native-fixture') for r in q.load(q.ROOT/source[3])['rows']]
    q.require(len(rows)==1408,'membership_count')
    model=pin(q.ROOT/'reports/work/FOCUS-329/run/last.pt');net=a.e.load_candidate(q.ROOT/model['path']);chunks=[]
    for offset in range(0,len(rows),32):
        subset=rows[offset:offset+32];encoded=[]
        for row in subset:
            images=[a.r.s.image(v['path'],v['sha256']) for v in row['images']]
            q.require(all(abs(image.width/image.height-16/9)<.001 for image in images),'padding_contract')
            encoded.append(a.r.s.encoded(*images,(192,128))[0])
        values=np.stack(encoded);detail,_=a.r.prepare(values,subset,2);tensor=np.concatenate((values,detail),1);prob=[]
        with a.t.inference_mode():
            for j in range(0,len(tensor),8):prob.extend(a.t.sigmoid(net.change(a.t.from_numpy(tensor[j:j+8]))).flatten().tolist())
        path=BASE/f'chunk-{offset:04d}.npz';np.savez_compressed(path,tensor=tensor,probabilities=np.array(prob,np.float32));chunks.append(pin(path))
        q.require(sum((q.ROOT/v['path']).stat().st_size for v in chunks)<1024**3,'prepared_input_limit')
        print(f'Prepared {offset+len(subset)}/{len(rows)}',flush=True)
    q.save(BASE/'inputs.json',dict(rows=rows,chunks=chunks,model=model,sources=[pin(q.ROOT/p) for p in source],
        preparationSeconds=time.monotonic()-start,complete=True))


def register():
    manifest=pin(BASE/'inputs.json');data=q.load(BASE/'inputs.json');q.require(data['complete'],'partial_inputs')
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS346';folder.mkdir(exist_ok=True)
    refs=[manifest,data['model']]+data['chunks']+[pin(q.ROOT/p) for p in
        ['scripts/reserve346.py','scripts/additive341.py','scripts/edge329.py','scripts/regions313.py','scripts/source310.py','scripts/detail307.py','scripts/research_campaign340.py']]
    for mode,hypothesis,rule in TESTS:
        id='focus346-'+mode;q.require(not (q.QUEUE/'jobs'/id).exists(),'existing_job')
        config=folder/(id+'-config.json');q.save(config,dict(inputs=refs,manifest=manifest,mode=mode))
        spec=dict(version=q.SPEC_VERSION,id=id,task='FOCUS346',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis=hypothesis,decisionRule=rule+' Keep all original-label counts and lost-success cases. No automatic model change.',
            adapter=dict(type='python-callable',steps=['reserve346.run'],outputAttributes=['reserve346.OUT']),
            inputs=refs,stage=[{'from':pin(config),'to':'config.json'}],limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        path=folder/(id+'.json');q.save(path,spec);print(q.submit(path))


def review():
    report=[]
    for mode,hypothesis,rule in TESTS:
        job=q.QUEUE/'jobs'/('focus346-'+mode)
        status,attempts=q.state(job)
        row=dict(mode=mode,status=status,hypothesis=hypothesis,nextDecision=rule)
        if status=='complete':
            result=q.load(attempts[-1]/'out/diagnostic.json')
            row['domains']={}
            for group,counts in result['counts'].items():
                domain=group.split('/')[0]
                total=row['domains'].setdefault(domain,{key:0 for key in counts})
                for key,value in counts.items():total[key]+=value
            row['seconds']=result['seconds']
        report.append(row)
    print(__import__('json').dumps(dict(experiments=report,modelChanged=False),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','register','review']);args=parser.parse_args()
    globals()[args.action]()
