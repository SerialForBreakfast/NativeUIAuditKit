"""Audit the unchanged detail selector on controlled native pairs."""
import numpy as np
import generation352 as g
import research_queue as q
from research_campaign340 import pin
OUT=None


def run():
    g.OUT=OUT
    ref=g.inspect();path=q.ROOT/ref['path'];doc=q.load(path)
    frames={r['id']:r for r in doc['frames']}
    import regions313 as r
    r.t.set_num_threads(2)
    results=[]
    for pair in doc['pairs']:
        row=dict(images=[pin(path.parent/frames[pair[k]]['path']) for k in ('before','after')])
        values=r.s.encoded(*[r.s.image(v['path'],v['sha256']) for v in row['images']],(192,128))[0][None]
        details,audit=r.prepare(values,[row],2)
        results.append(dict(pair,selection=audit[0],
            wholeMeanDifference=float(np.abs(values[0,:3]-values[0,3:]).mean()),
            detailMeanDifferences=[float(np.abs(details[0,i:i+3]-details[0,i+3:i+6]).mean()) for i in (0,6)]))
    q.save(OUT/'detail-audit.json',dict(results=results,modelsChanged=False,cropsChanged=False,
        limitation='Selected change energy is not focus accuracy. Content changes can also occupy these windows.'))


def register():
    for factor in ('size','growth','shadow','position','background'):
        job=f'generation354b-{factor}-capture';producer=q.load(q.QUEUE/'jobs'/job/'spec.json')
        spec=dict(version=q.SPEC_VERSION,id=f'generation354b-{factor}-detail-audit',task='GENERATION354',
            owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis=f'Check whether unchanged detail windows retain movement evidence across {factor} values.',
            decisionRule='Report retained change energy and detail differences. Do not replace crops or tune a threshold.',
            inputs=[pin(q.ROOT/'scripts'/name) for name in ('detail354.py','generation352.py','regions313.py','source310.py')],
            dependencies=[dict(job=job,specSHA256=q.text_digest(producer),outputs=['capture/capture.json'])],
            adapter=dict(type='python-callable',steps=['detail354.run'],outputAttributes=['detail354.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        path=q.ROOT/'Research/ResearchSpecs/GENERATION354'/(spec['id']+'.json')
        q.save(path,spec);print(spec['id'],q.submit(path))


if __name__=='__main__':register()
