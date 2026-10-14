"""Measure branch conflicts across retained training groups in bounded batches."""
import time
import numpy as np
import research_queue as q
from research_campaign340 import pin
import additive341 as a

OUT=None

def run():
    start=time.monotonic();config=q.load(OUT/'config.json');a.t.set_num_threads(2)
    for ref in config['inputs']:q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'input_hash')
    net=a.e.load_candidate(q.ROOT/config['model']['path']);rows=config['rows'];results=[]
    q.require(rows and all(r['role']=='train' for r in rows),'training_only')
    for offset in range(0,len(rows),8):
        part=rows[offset:offset+8]
        values=np.stack([a.r.s.encoded(*[a.r.s.image(v['path'],v['sha256']) for v in r['images']],(192,128))[0] for r in part])
        detail,_=a.r.prepare(values,part,2);tensor=a.t.from_numpy(np.concatenate((values,detail),1))
        with a.t.inference_mode():
            context=net.change.whole[:10](a.r.s.c.model.change_inputs(None,tensor[:,:6]));features=[]
            for j in range(2):
                image=tensor[:,6+j*6:12+j*6]
                features.append(net.change.detail(a.t.cat((a.r.s.c.model.change_inputs(None,image),a.e.gradient_channels(image)),1)))
            whole=net.change.whole[10](context).flatten()
            correction=net.change.correction(a.t.cat((context,a.t.stack(features).mean(0)),1)).flatten()
            logits=net.change(tensor).flatten()
            q.require(float((whole+correction-logits).abs().max())<1e-5,'branch_parity')
        for i,row in enumerate(part):
            results.append(dict(id=row['id'],group=row['group'],label=row['changed'],
                wholeLogit=float(whole[i]),detailCorrection=float(correction[i]),probability=float(a.t.sigmoid(logits[i]))))
        print(f'Compared {len(results)} of {len(rows)} cases',flush=True)
    q.save(OUT/'diagnostic.json',dict(inputs=config['inputs'],model=config['model'],rows=rows,predictions=results,
        seconds=time.monotonic()-start,modelChanged=False,selectionRole='training-only',
        limitation='Branch outputs are not separate probabilities. Related examples are not independent trials.',
        nextDecision='Compare conflicts by group and cause before defining a correction. Do not fit on native development failures.'))

def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS344';rows=q.load(q.ROOT/'reports/work/FOCUS-319/corpus.json')['rows']
    rows+=q.load(q.ROOT/'reports/work/FOCUS-326/corpus.json')['rows']['independent']
    rows=[dict(r,id=r.get('id',f'authored344-{i}')) for i,r in enumerate(rows)]
    model=pin(q.ROOT/'reports/work/FOCUS-329/run/last.pt')
    batches=[(f'0{i+6}-full-{condition}',[r for r in rows if r['condition']==condition])
             for i,condition in enumerate(('movement','artwork-only','identical'))]
    batches.append(('09-matched-content',q.load(q.ROOT/'reports/work/FOCUS-341/negatives.json')['rows']))
    movement=[dict(r,id=r['id']+'-reversed',images=r['images'][::-1]) for r in rows if r['condition']=='movement']
    batches.append(('10-reversed-movement',movement))
    for name,selected in batches:
        id='focus344-'+name;q.require(not (q.QUEUE/'jobs'/id).exists(),'existing_job');q.require(selected,'no_cases')
        refs=[pin(q.ROOT/p) for p in ['scripts/branches344.py','scripts/additive341.py','scripts/edge329.py','scripts/regions313.py','scripts/source310.py','scripts/detail307.py']]+[model]
        refs+=list({v['path']:v for r in selected for v in r['images']}.values())
        config=folder/(id+'-config.json');q.save(config,dict(inputs=refs,rows=selected,model=model))
        spec=dict(version=q.SPEC_VERSION,id=id,task='FOCUS344',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis='Measure whole-frame suppression and detail support for '+name+' across retained training groups.',
            decisionRule='Identify group-specific branch conflicts. No coefficient fit, training, or threshold selection.',
            adapter=dict(type='python-callable',steps=['branches344.run'],outputAttributes=['branches344.OUT']),
            inputs=refs,stage=[{'from':pin(config),'to':'config.json'}],limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        path=folder/(id+'.json');q.save(path,spec);print(q.submit(path))

if __name__=='__main__':register()
