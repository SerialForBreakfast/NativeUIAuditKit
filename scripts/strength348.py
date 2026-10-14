"""Check retained distraction strengths in both frame orders."""
import time
import numpy as np
import appearance348 as m
from transition250 import interpolate

q=m.q;OUT=None


def run():
    start=time.monotonic();config=q.load(OUT/'config.json');m.check_inputs(config);m.t.set_num_threads(2)
    models={k:m.a.e.load_candidate(q.ROOT/v['path']) for k,v in config['models'].items()}
    baseline=m.a.e.load_candidate(m.a.e.OUT/'run/last.pt')
    source=np.load(q.ROOT/config['source']['path'],allow_pickle=False);sets={}
    for strength in (0.,.25,.5,1.):
        values=interpolate(source,strength)
        if config['order']=='reverse':values=m.a.b.reporting.reverse(values)
        old=m.a.b.worker.score(baseline,values).tolist()
        scores={k:m.a.b.worker.score(net,values).tolist() for k,net in models.items()}
        rows=[dict(id=f'{config["condition"]}-{config["order"]}-{strength}-{i}',changed=0,
                   sourceDomain='retained-disturbance',condition=config['condition'],group='ancestry-unavailable')
              for i in range(len(values))]
        sets[str(strength)]=m.report(rows,scores,old)
        q.save(OUT.parent/'progress.json',dict(step=config['condition']+'/'+config['order'],
            completed=len(sets),total=4,updatedAt=time.time()),replace=True)
    q.save(OUT/'comparison.json',dict(sets=sets,configuration=config,seconds=time.monotonic()-start,
        productionEligible=False,limitations=['Strength variants and reversed frames are related. No independent-trial claim.']))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS348'
    models={k:m.f.pin(q.QUEUE/'jobs'/('focus348-00-'+k)/'attempts/1/out/last.pt') for k in ('control','gamma')}
    for i,(condition,order) in enumerate((a,b) for a in ('left8','center8','global8') for b in ('forward','reverse')):
        identity=f'focus348-{30+i}-strength-{condition}-{order}';source=m.f.pin(m.a.b.PACKAGE/(condition+'.npy'))
        refs=list(models.values())+[source]+[m.f.pin(q.ROOT/p) for p in
            ['scripts/strength348.py','scripts/appearance348.py','scripts/transition250.py','scripts/edge329.py',
             'reports/work/FOCUS-329/run/last.pt']]
        config=folder/(identity+'-config.json');q.save(config,dict(condition=condition,order=order,source=source,models=models,inputs=refs))
        spec=dict(version=q.SPEC_VERSION,id=identity,task='FOCUS348',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis='Appearance augmentation preserves stability across retained nuisance strengths and frame orders.',
            decisionRule='Report lost previous successes at all 4 retained strengths. No changed thresholds.',inputs=refs,
            adapter=dict(type='python-callable',steps=['strength348.run'],outputAttributes=['strength348.OUT']),
            stage=[{'from':m.f.pin(config),'to':'config.json'}],limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        path=folder/(identity+'.json');q.save(path,spec);print(identity,q.submit(path))


if __name__=='__main__':register()
