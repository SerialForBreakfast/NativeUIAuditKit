"""Measure existing branch contributions without changing model decisions."""
import numpy as np
import research_queue as q
import generation352 as g
from research_campaign340 import pin
OUT=None


def run():
    g.OUT=OUT;ref=g.inspect();path=q.ROOT/ref['path'];doc=q.load(path)
    frames={r['id']:r for r in doc['frames']}
    config=q.load(OUT/'models.json')
    import report_additive341 as report
    t=report.a.t;t.set_num_threads(2)
    rows=[dict(id=p['case']+'-'+p['condition'],condition=p['condition'],changed=p['changed'],
        images=[pin(path.parent/frames[p[k]]['path']) for k in ('before','after')]) for p in doc['pairs']]
    x=np.stack([report.a.r.s.encoded(*[report.a.r.s.image(v['path'],v['sha256']) for v in row['images']],(192,128))[0] for row in rows])
    details,_=report.a.r.prepare(x,rows,2)
    inputs=t.from_numpy(np.concatenate([x,details],1))
    models={}
    for name,ref in config.items():
        q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'model_changed')
        net=report.a.e.load_candidate(q.ROOT/ref['path']);parts={}
        def hook(key):
            def record(module,args,value):parts[key]=value.detach().clone()
            return record
        handles=[net.change.whole[10].register_forward_hook(hook('context')),
                 net.change.correction.register_forward_hook(hook('correction'))]
        try:
            with t.inference_mode():logits=net.change(inputs)
        finally:
            for handle in handles:handle.remove()
        error=float((logits-parts['context']-parts['correction']).abs().max())
        q.require(error<1e-5,'branch_sum_parity')
        probabilities=t.sigmoid(logits).reshape(-1).tolist()
        models[name]=dict(context=parts['context'].reshape(-1).tolist(),
            correction=parts['correction'].reshape(-1).tolist(),probabilities=probabilities,
            maximumSumError=error,model=ref)
    q.save(OUT/'branches.json',dict(rows=rows,models=models,weightsChanged=False,
        limitation='Branch contributions describe this network, not independent causal effects or new deployment decisions.'))


def register():
    models=q.load(q.ROOT/'Research/ResearchSpecs/DATASET351/dataset351-00-movement-config.json')['models']
    folder=q.ROOT/'Research/ResearchSpecs/GENERATION354'
    mp=folder/'branch-models.json';q.save(mp,models)
    for factor in ('size','growth','shadow','position','background'):
        job=f'generation354b-{factor}-capture';producer=q.load(q.QUEUE/'jobs'/job/'spec.json')
        spec=dict(version=q.SPEC_VERSION,id=f'generation354b-{factor}-branches',task='GENERATION354',
            owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis=f'Measure whether context or the existing correction suppresses movements across {factor} values.',
            decisionRule='Require branch-sum parity. Report signed contributions without tuning or replacing weights.',
            inputs=[pin(q.ROOT/'scripts'/name) for name in ('branches354.py','generation352.py','report_additive341.py','edge329.py')]+list(models.values()),
            dependencies=[dict(job=job,specSHA256=q.text_digest(producer),outputs=['capture/capture.json'])],
            stage=[{'from':pin(mp),'to':'models.json'}],
            adapter=dict(type='python-callable',steps=['branches354.run'],outputAttributes=['branches354.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        p=folder/(spec['id']+'.json');q.save(p,spec);print(spec['id'],q.submit(p))


if __name__=='__main__':register()
