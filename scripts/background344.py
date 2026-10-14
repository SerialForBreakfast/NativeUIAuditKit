"""Run fixed diagnostic interventions through the existing background queue."""
import time
import numpy as np
import research_queue as q
from research_campaign340 import pin,decision
import additive341 as a

OUT=None
MODES=[
 ('01-branches','Separate whole-frame and detail contributions on native misses.','Identify which branch suppresses change without treating branch output as calibrated probability.'),
 ('02-detail-size','Compare fixed detail windows of 16, 24, 32, and 48 input pixels.','Measure target gains and previous successes lost. Keep original images and production preprocessing unchanged.'),
 ('03-context','Keep detail fixed while replacing whole-frame after pixels with before pixels.','Measure dependence on whole-frame context. This intervention is not a deployable accuracy claim.'),
 ('04-detail','Keep context fixed while replacing detail after pixels with before pixels.','Measure dependence on original detail. Do not train from this intervention.'),
 ('05-features','Compare native and authored detail activations before scalar compression.','Measure distances and activation norms by source and label. Do not infer generalization from proximity.')]


def inputs():
    rows=q.load(q.QUEUE/'jobs/focus343-native/attempts/1/out/diagnostic.json')['rows']
    for index in (0,2):
        rows+=q.load(q.QUEUE/f'jobs/focus343-identical-neighbors-r2-{index}/attempts/1/out/diagnostic.json')['rows']
    # Use fixed retained training negatives as a nuisance-change control.
    rows+=q.load(q.ROOT/'reports/work/FOCUS-341/negatives.json')['rows'][::12]
    q.require(len(rows)==64,'membership_count')
    return rows


def summary(rows,values,reference):
    result={}
    for i,row in enumerate(rows):
        domain='native' if row['id'].startswith('native343-') else 'authored'
        key=domain+'/'+row['condition'];r=result.setdefault(key,dict(count=0,correct=0,falseChange=0,missedChange=0,abstentions=0,lost=0,gained=0))
        pred=decision(float(values[i]));old=decision(float(reference[i]));label=row['changed']
        r['count']+=1;r['correct']+=pred==label;r['falseChange']+=pred==1 and label==0
        r['missedChange']+=pred==0 and label==1;r['abstentions']+=pred is None
        r['lost']+=old==label and pred!=label;r['gained']+=old!=label and pred==label
    return result


def detail_size(values,rows,width):
    q.require(width in (16,24,32,48),'window_width');output=np.empty((len(rows),12,128,192),np.float32)
    for i,boxes in enumerate(a.r.windows(a.t.from_numpy(values))):
        if not boxes:
            output[i]=np.concatenate((values[i],values[i]));continue
        images=[a.r.s.image(v['path'],v['sha256']) for v in rows[i]['images']]
        for j in range(2):
            x,y=boxes[min(j,len(boxes)-1)];cx,cy=x+16,y+16
            output[i,j*6:(j+1)*6]=a.r.s.crop_pair(images,[cx-width/2,cy-width/2,cx+width/2,cy+width/2],preserve_padding=True)
    return output


def run():
    start=time.monotonic();config=q.load(OUT/'config.json')
    for ref in config['inputs']:q.require(q.digest(q.local_path(q.ROOT,ref['path']))==ref['sha256'],'input_hash')
    rows=config['rows'];q.require(len(rows)==64,'membership');a.t.set_num_threads(2)
    values=np.stack([a.r.s.encoded(*[a.r.s.image(v['path'],v['sha256']) for v in row['images']],(192,128))[0] for row in rows])
    details,_=a.r.prepare(values,rows,2);tensor=a.t.from_numpy(np.concatenate((values,details),1))
    net=a.e.load_candidate(q.ROOT/config['model']['path']);mode=config['mode'];variants={};extra={}
    with a.t.inference_mode():
        reference=a.t.sigmoid(net.change(tensor)).flatten().numpy()
        if mode=='02-detail-size':
            for width in (16,24,32,48):
                inputs=a.t.from_numpy(np.concatenate((values,detail_size(values,rows,width)),1))
                variants[str(width)]=a.t.sigmoid(net.change(inputs)).flatten().numpy()
            q.require(np.max(np.abs(reference-variants['32']))<=1e-6,'original_crop_parity')
        elif mode in ('03-context','04-detail'):
            changed=tensor.clone()
            for offset in ([0] if mode=='03-context' else [6,12]):changed[:,offset+3:offset+6]=changed[:,offset:offset+3]
            variants[mode]=a.t.sigmoid(net.change(changed)).flatten().numpy()
        else:
            context=net.change.whole[:10](a.r.s.c.model.change_inputs(None,tensor[:,:6]))
            features=[]
            for j in range(2):
                part=tensor[:,6+j*6:12+j*6]
                features.append(net.change.detail(a.t.cat((a.r.s.c.model.change_inputs(None,part),a.e.gradient_channels(part)),1)))
            features=a.t.stack(features).mean(0)
            if mode=='01-branches':
                whole=net.change.whole[10](context);correction=net.change.correction(a.t.cat((context,features),1))
                q.require(float((a.t.sigmoid(whole+correction).flatten()-a.t.from_numpy(reference)).abs().max())<=1e-6,'branch_parity')
                extra=dict(wholeLogits=whole.flatten().tolist(),correctionLogits=correction.flatten().tolist())
            else:
                array=features.numpy();native=array[:16];authored=array[16:]
                distances=np.sqrt(((native[:,None,:]-authored[None,:,:])**2).sum(2))
                extra=dict(featureNorms=np.linalg.norm(array,axis=1).tolist(),
                    nearestAuthoredIndex=(distances.argmin(1)+16).tolist(),nearestDistances=distances.min(1).tolist(),
                    features=array.tolist())
    q.save(OUT/'diagnostic.json',dict(version='focus344-diagnostic-v1',mode=mode,inputs=config['inputs'],model=config['model'],rows=rows,
        originalProbabilities=reference.tolist(),original=summary(rows,reference,reference),
        variants={k:dict(probabilities=v.tolist(),counts=summary(rows,v,reference)) for k,v in variants.items()},
        extra=extra,seconds=time.monotonic()-start,modelChanged=False,trainingEligible=False,
        limitations=['64 fixed development/training-derived cases, not independent final evaluation.',
                    'Native source/build matching remains unresolved. No image admission or model promotion.',
                    'Interventions are diagnostics. Full retained regression checks precede any candidate.']))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS344';folder.mkdir(exist_ok=True)
    rows=inputs();model=pin(q.ROOT/'reports/work/FOCUS-329/run/last.pt')
    paths=['scripts/background344.py','scripts/additive341.py','scripts/edge329.py','scripts/regions313.py',
        'scripts/source310.py','scripts/detail307.py','scripts/research_campaign340.py']
    refs=[pin(q.ROOT/p) for p in paths]+[model]
    refs+=list({v['path']:v for r in rows for v in r['images']}.values())
    for mode,hypothesis,rule in MODES:
        id='focus344-'+mode;q.require(not (q.QUEUE/'jobs'/id).exists(),'existing_job')
        config=folder/(id+'-config.json');q.save(config,dict(mode=mode,inputs=refs,rows=rows,model=model))
        spec=dict(version=q.SPEC_VERSION,id=id,task='FOCUS344',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis=hypothesis,decisionRule=rule,
            adapter=dict(type='python-callable',steps=['background344.run'],outputAttributes=['background344.OUT']),
            inputs=refs,stage=[{'from':pin(config),'to':'config.json'}],
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        path=folder/(id+'.json');q.save(path,spec);print(q.submit(path))


if __name__=='__main__':register()
