"""Separate appearance changes from padding and test a fixed pooling correction."""
import argparse
import time
import numpy as np
from PIL import Image
import reserve346 as prior

q=prior.q
a=prior.a
pin=prior.pin
OUT=None
BASE=q.ROOT/'reports/work/FOCUS-347'
FACTORS=['06-brightness','07-contrast','08-gamma','09-grayscale','10-saturation']
SCOPES=['whole-content','detail-content','all-content','source-reselect']
REGRESSIONS=[('native',['native.npy','reverse_native.npy']),
             ('replay',['replay.npy','reverse_replay.npy']),
             ('global',['global8.npy']),('left',['left8.npy']),('center',['center8.npy'])]


def masks(x):
    """Find source support from renderer geometry, not pixel color."""
    result=a.t.zeros_like(x,dtype=a.t.bool)
    result[:,:6,10:118]=True
    white=Image.new('RGB',(192,108),'white')
    for i,boxes in enumerate(a.r.windows(x[:,:6])):
        for j in range(2):
            if not boxes:result[i,6+j*6:12+j*6]=result[i,:6];continue
            left,top=boxes[min(j,len(boxes)-1)]
            support=a.r.s.crop_pair([white,white],[left,top,left+32,top+32],preserve_padding=True)
            result[i,6+j*6:12+j*6]=a.t.from_numpy(support)>=1
    return result


def alter(x,mask,factor,scope):
    q.require(factor in FACTORS and scope in SCOPES[:3],'intervention')
    selected=mask.clone()
    if scope=='whole-content':selected[:,6:]=False
    elif scope=='detail-content':selected[:,:6]=False
    return a.t.where(selected,prior.transform(x,factor),x)


def source_image(image,factor):
    q.require(factor in FACTORS,'factor')
    values=np.asarray(image,dtype=np.float32)/255
    if factor=='06-brightness':values=values+.1
    elif factor=='07-contrast':values=(values-.5)*.65+.5
    elif factor=='08-gamma':values=values**1.5
    else:
        gray=(values*np.array([.299,.587,.114],np.float32)).sum(2,keepdims=True)
        values=np.repeat(gray,3,axis=2) if factor=='09-grayscale' else .5*(values+gray)
    return Image.fromarray(np.rint(values.clip(0,1)*255).astype(np.uint8))


def source_views(rows,factor):
    output=[];changed=0
    for row in rows:
        original=[a.r.s.image(v['path'],v['sha256']) for v in row['images']]
        images=[source_image(v,factor) for v in original]
        whole=a.r.s.encoded(*images,(192,128))[0]
        boxes=a.r.windows(a.t.from_numpy(whole[None]))[0]
        old=a.r.s.encoded(*original,(192,128))[0]
        changed+=boxes!=a.r.windows(a.t.from_numpy(old[None]))[0]
        parts=[whole]
        for j in range(2):
            if not boxes:parts.append(whole.copy());continue
            left,top=boxes[min(j,len(boxes)-1)]
            parts.append(a.r.s.crop_pair(images,[left,top,left+32,top+32],preserve_padding=True))
        output.append(np.concatenate(parts))
    return a.t.from_numpy(np.stack(output)),changed


def progress(step,n,total):
    q.save(OUT.parent/'progress.json',dict(step=step,completed=n,total=total,updatedAt=time.time()),replace=True)
    print(step,n,total,flush=True)


def run():
    config=q.load(OUT/'config.json');start=time.monotonic();a.t.set_num_threads(2)
    for ref in config['inputs']:q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'input_changed')
    if config['kind']=='regression':return regression(config,start)
    manifest=q.load(q.ROOT/config['manifest']['path']);net=a.e.load_candidate(q.ROOT/manifest['model']['path'])
    values=[];baseline=[];proposal_changes=0
    for chunk in manifest['chunks']:
        with np.load(q.ROOT/chunk['path'],allow_pickle=False) as data:
            tensor=a.t.from_numpy(data['tensor']);old=data['probabilities'].tolist()
        start_index=len(values)
        for offset in range(0,len(tensor),8):
            x=tensor[offset:offset+8]
            if config['scope']=='source-reselect':
                subset=manifest['rows'][start_index+offset:start_index+offset+len(x)]
                y,changed=source_views(subset,config['factor']);proposal_changes+=changed
            else:y=alter(x,masks(x),config['factor'],config['scope'])
            with a.t.inference_mode():values.extend(a.t.sigmoid(net.change(y)).flatten().tolist())
        baseline.extend(old);progress(config['factor']+'/'+config['scope'],len(values),len(manifest['rows']))
    q.save(OUT/'diagnostic.json',dict(version='followup347-v1',configuration=config,rows=manifest['rows'],
        probabilities=values,originalProbabilities=baseline,counts=prior.count(manifest['rows'],values,baseline),
        changedProposalPairs=proposal_changes,seconds=time.monotonic()-start,modelChanged=False,
        limitations=['Development diagnostics only. Native app/build matching remains unresolved.',
            'Source tests include quantization, resizing, and proposal selection. They do not isolate only one pipeline stage.',
            'Content masks exclude geometric padding. Native pixel fidelity still requires capture.',
            'Related pairs are not independent. Full theme and archetype coverage is unavailable.']))


def regression(config,start):
    manifest=q.load(q.ROOT/config['manifest']['path']);net=a.e.load_candidate(q.ROOT/manifest['model']['path'])
    member=q.load(a.b.PACKAGE/'membership.json');cached=q.load(q.ROOT/'reports/work/FOCUS-329/run/evaluation.json')
    outputs={}
    for name in config['sets']:
        data=np.load(a.b.PACKAGE/name,allow_pickle=False,mmap_mode='r');values=[];base=[]
        labels=[r['changed'] for r in member['rows']] if 'native' in name else member['replayLabels'] if 'replay' in name else [0]*len(data)
        for offset in range(0,len(data),8):
            x=np.array(data[offset:offset+8]);rows=None
            if 'native' in name:
                rows=member['rows'][offset:offset+len(x)]
                if name.startswith('reverse_'):
                    forward=np.concatenate((x[:,3:6],x[:,:3]),1)
                    detail,_=a.r.prepare(forward,rows,2)
                    detail=a.r.reverse_details(detail)
                else:detail,_=a.r.prepare(x,rows,2)
            else:detail=a.r.encoded_details(a.t.from_numpy(x),2).numpy()
            tensor=a.t.from_numpy(np.concatenate((x,detail),1))
            with a.t.inference_mode():
                base.extend(a.t.sigmoid(net.change(tensor)).flatten().tolist())
                values.extend(a.t.sigmoid(prior.logits(net,tensor,'02-max-detail')).tolist())
            progress('Maximum detail: '+name,len(values),len(data))
        error=float(np.max(np.abs(np.array(base)-cached['conditions'][name]['probabilities'])))
        q.require(error<=1e-6,'baseline_parity')
        rows=[dict(changed=int(y),sourceDomain='retained-regression',condition=name,
            group=member['rows'][i]['group'] if 'native' in name else 'ancestry-unavailable',
            role=member['rows'][i].get('role','unknown') if 'native' in name else 'retained-evaluation',id=name+':'+str(i)) for i,y in enumerate(labels)]
        outputs[name]=dict(rows=rows,probabilities=values,originalProbabilities=base,maximumParityError=error,
            counts=prior.count(rows,values,base))
    q.save(OUT/'diagnostic.json',dict(version='regression347-v1',configuration=config,sets=outputs,
        seconds=time.monotonic()-start,promotionAllowed=False,
        decision='Reject replacement if any previous success is lost. FOCUS346 already records 41 authored losses.',
        limitations=['Fixed inference correction only. No fitted weights or threshold changes.',
            'Previously inspected regression sets are not untouched final evaluation.',
            'Replay and nuisance groups lack independent ancestry. Do not calculate independent-trial bounds.']))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS347';folder.mkdir(exist_ok=True)
    manifest=pin(prior.BASE/'inputs.json');data=q.load(prior.BASE/'inputs.json')
    refs=[manifest,data['model']]+data['chunks']+[pin(q.ROOT/p) for p in
        ['scripts/followup347.py','scripts/reserve346.py','scripts/edge329.py','scripts/regions313.py',
         'scripts/detail307.py','scripts/source310.py','scripts/research_campaign340.py']]
    jobs=[]
    for index,(name,sets) in enumerate(REGRESSIONS):
        extra=[pin(a.b.PACKAGE/p) for p in sets+['membership.json']]
        extra+=[pin(q.ROOT/'reports/work/FOCUS-329/run/evaluation.json')]
        jobs.append((f'{index+1:02d}-regression-{name}',dict(kind='regression',sets=sets),refs+extra,
            'Test maximum detail pooling on retained '+name+' cases.',
            'Reject replacement after any lost previous success. Require baseline parity within 1e-6.'))
    for index,(factor,scope) in enumerate((f,s) for f in FACTORS for s in SCOPES):
        jobs.append((f'{index+6:02d}-{factor[3:]}-{scope}',dict(kind='appearance',factor=factor,scope=scope),refs,
            'Separate '+factor[3:]+' sensitivity using '+scope+'.',
            'Compare gains and losses with the fixed baseline and FOCUS346. Select data correction only after source-level confirmation.'))
    for suffix,settings,inputs,hypothesis,rule in jobs:
        id='focus347-'+suffix;q.require(not (q.QUEUE/'jobs'/id).exists(),'existing_job')
        config=folder/(id+'-config.json');q.save(config,dict(settings,manifest=manifest,inputs=inputs))
        spec=dict(version=q.SPEC_VERSION,id=id,task='FOCUS347',owner='Maximum-mini-NUIAK',kind='screen',authority='diagnostic',
            hypothesis=hypothesis,decisionRule=rule,inputs=inputs,stage=[{'from':pin(config),'to':'config.json'}],
            adapter=dict(type='python-callable',steps=['followup347.run'],outputAttributes=['followup347.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        path=folder/(id+'.json');q.save(path,spec);print(id,q.submit(path),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['register']);globals()[parser.parse_args().action]()
