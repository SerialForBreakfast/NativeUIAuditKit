"""Check retained authored neighbors and placeholder controls after training."""
import time
import appearance348 as m
import report_additive341 as r

q=m.q;OUT=None


def run():
    start=time.monotonic();config=q.load(OUT/'config.json');m.check_inputs(config);m.t.set_num_threads(2)
    models={k:m.a.e.load_candidate(q.ROOT/v['path']) for k,v in config['models'].items()}
    baseline=m.a.e.load_candidate(m.a.e.OUT/'run/last.pt');sets={}
    for ref in config['sources']:
        doc=q.load(q.ROOT/ref['path']);rows=doc['rows']
        rows=[dict(row,changed=row.get('changed',row.get('authoredChanged')),
                   id=row.get('id',ref['path']+':'+str(i)),group=row.get('group','ancestry-unavailable'),
                   sourceDomain='authored',condition=row.get('condition','placeholder')) for i,row in enumerate(rows)]
        old=r.score_rows(baseline,rows,False).tolist()
        predictions={key:r.score_rows(net,rows,False).tolist() for key,net in models.items()}
        sets[ref['path']]=m.report(rows,predictions,old)
    q.save(OUT/'comparison.json',dict(sets=sets,configuration=config,seconds=time.monotonic()-start,
        productionEligible=False,limitations=['Retained development controls are not independent final evaluation.']))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS348'
    models={k:m.f.pin(q.QUEUE/'jobs'/('focus348-00-'+k)/'attempts/1/out/last.pt') for k in ('control','gamma')}
    sets=[('27-neighbors-0',[q.QUEUE/'jobs/focus343-identical-neighbors-r2-0/attempts/1/out/diagnostic.json']),
          ('28-neighbors-2',[q.QUEUE/'jobs/focus343-identical-neighbors-r2-2/attempts/1/out/diagnostic.json']),
          ('29-placeholders',[m.a.r.OUT/'headless-diagnostic/inspection.json',m.a.r.OUT/'headless-moves/comparison.json'])]
    for suffix,paths in sets:
        identity='focus348-'+suffix;sources=[m.f.pin(p) for p in paths]
        inputs=sources+list(models.values())+[m.f.pin(q.ROOT/p) for p in
            ['scripts/retained348.py','scripts/appearance348.py','scripts/report_additive341.py','scripts/edge329.py']]
        inputs.append(m.f.pin(m.a.e.OUT/'run/last.pt'))
        config=folder/(identity+'-config.json');q.save(config,dict(inputs=inputs,models=models,sources=sources))
        spec=dict(version=q.SPEC_VERSION,id=identity,task='FOCUS348',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis='Appearance augmentation preserves retained authored neighbor and placeholder successes.',
            decisionRule='Reject a replacement with any lost previous success. Keep thresholds 0.15/0.85.',inputs=inputs,
            adapter=dict(type='python-callable',steps=['retained348.run'],outputAttributes=['retained348.OUT']),
            stage=[{'from':m.f.pin(config),'to':'config.json'}],limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        path=folder/(identity+'.json');q.save(path,spec);print(identity,q.submit(path))


if __name__=='__main__':register()
