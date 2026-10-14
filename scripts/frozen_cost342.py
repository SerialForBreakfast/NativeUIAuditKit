"""Measure frozen-branch reuse with exact outputs and gradients. Do not update weights."""
from pathlib import Path
import statistics
import time
import numpy as np
import research_queue as q
from research_campaign340 import pin

OUT=None


def run():
    import additive341 as a
    a.t.set_num_threads(2);config=q.load(OUT/'config.json')
    for ref in config['inputs']:q.require(q.digest(q.local_path(q.ROOT,ref['path']))==ref['sha256'],'input_hash')
    negatives=q.load(q.ROOT/'reports/work/FOCUS-341/negatives.json')['rows'][:4]
    source=q.load(q.ROOT/'reports/work/FOCUS-326/corpus.json')['rows']['independent']
    lookup={r['id']:r for r in source};rows=negatives+[lookup[r['matchedMovementID']] for r in negatives]
    q.require(all(r['role']=='train' for r in rows),'training_role')
    x=np.stack([a.r.s.encoded(*[a.r.s.image(v['path'],v['sha256']) for v in r['images']],(192,128))[0] for r in rows])
    detail,_=a.r.prepare(x,rows,2);inputs=a.t.from_numpy(np.concatenate((x,detail,a.added_details(x,rows)),1))
    net=a.load(q.ROOT/config['model']['path'])
    q.require(not any(isinstance(m,(a.t.nn.Dropout,a.t.nn.modules.batchnorm._BatchNorm)) for m in net.change.modules()),
              'stateful_or_random_layer')
    for name,p in net.named_parameters():p.requires_grad_(name.startswith(('change.detail.','change.correction.')))
    start=time.perf_counter()
    with a.t.no_grad():reference=net.change.whole(inputs[:,:18]).detach()
    setup=time.perf_counter()-start
    def direct():return net.change(inputs)
    def cached():
        added=inputs[:,18:]
        features=a.t.cat((a.r.s.c.model.change_inputs(None,added),a.e.gradient_channels(added)),1)
        return reference+net.change.correction(net.change.detail(features))
    def gradients(call):
        net.zero_grad(set_to_none=True);values=call();values.sum().backward()
        return values.detach(),{k:p.grad.clone() for k,p in net.named_parameters() if p.requires_grad}
    old,og=gradients(direct);new,ng=gradients(cached)
    logit_error=float((old-new).abs().max());gradient_error=max(float((og[k]-ng[k]).abs().max()) for k in og)
    q.require(logit_error<=1e-6 and gradient_error<=1e-6,'cache_parity')
    timings={'direct':[],'cached':[]}
    for _ in range(5):
        for name,call in [('direct',direct),('cached',cached)]:
            start=time.perf_counter();gradients(call);timings[name].append(time.perf_counter()-start)
    medians={k:statistics.median(v) for k,v in timings.items()}
    q.save(OUT/'diagnostic.json',dict(model=config['model'],inputs=config['inputs'],batchSize=len(rows),
        caseIDs=[r['id'] for r in rows],frozenSetupSeconds=setup,timingsSeconds=timings,medianSeconds=medians,
        maximumLogitError=logit_error,maximumGradientError=gradient_error,
        measuredRatio=medians['direct']/medians['cached'],weightsUpdated=False,
        limitation='One 8-example CPU batch with 2 threads. No end-to-end speedup or cache implementation is established.',
        nextAction='If useful, add an input-hash-bound frozen-logit cache with full-run parity before changing training.'))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS342';id='focus342-frozen-cost'
    q.require(not (q.QUEUE/'jobs'/id).exists(),'existing_job')
    model=pin(q.ROOT/'reports/work/research-queue/jobs/focus341-added-detail/attempts/1/out/run/added-detail/last.pt')
    refs=[pin(q.ROOT/p) for p in ['scripts/frozen_cost342.py','scripts/additive341.py',
          'scripts/edge329.py','scripts/regions313.py','reports/work/FOCUS-341/negatives.json','reports/work/FOCUS-326/corpus.json']]+[model]
    config=folder/(id+'-config.json');q.save(config,dict(inputs=refs,model=model))
    spec=dict(version=q.SPEC_VERSION,id=id,task='FOCUS342',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis='Reusing frozen branch outputs preserves gradients while reducing repeated computation.',
        decisionRule='Require output and gradient parity within 1e-6. Report microbenchmark timing, not end-to-end speedup.',
        adapter=dict(type='python-callable',steps=['frozen_cost342.run'],outputAttributes=['frozen_cost342.OUT']),
        inputs=refs,stage=[{'from':pin(config),'to':'config.json'}],
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    path=folder/(id+'.json');q.save(path,spec);print(q.submit(path))


if __name__=='__main__':register()
