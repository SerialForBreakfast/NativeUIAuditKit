"""Measure rendered differences without changing frames or model crops."""
import numpy as np
from PIL import Image
import research_queue as q
import compare351
OUT = None


def difference(left, right):
    arrays=[]
    for path in (left,right):
        with Image.open(path) as image:
            arrays.append(np.asarray(image.convert('RGB'),dtype=np.int16))
    q.require(arrays[0].shape==arrays[1].shape,'dimension_mismatch')
    delta=np.abs(arrays[0]-arrays[1])
    return dict(changedPixels=int(np.any(delta,axis=2).sum()),meanAbsoluteDifference=float(delta.mean()))


def run():
    results=[]
    for dep in q.load(OUT/'dependencies.json'):
        for ref in [dep['result'],*dep['outputs']]:
            q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'dependency_changed')
        path=q.ROOT/dep['outputs'][0]['path'];doc=q.load(path)
        frames=compare351.validate_capture(doc,path.parent)
        plan=q.load(path.parent/'plan.json')
        q.require(q.digest(path.parent/'plan.json')==doc['planSHA256'],'plan_changed')
        rows=[]
        for pair in doc['pairs']:
            rows.append(dict(pair,**difference(*[path.parent/frames[pair[k]]['path'] for k in ('before','after')])))
        endpoints=[r for r in frames.values() if r['phase']=='before']
        q.require(len(endpoints)==2,'matched_case_count')
        geometry=[]
        for frame in frames.values():
            if frame['phase'] not in ('before','settled'):continue
            geometry.append(dict(frame=frame['id'],focus=frame['observedFocusID'],
                elements=frame['after']['scene']['elements']))
        results.append(dict(job=dep['job'],cases=plan['cases'],pairs=rows,geometry=geometry,
            factorPixels=difference(*[path.parent/r['path'] for r in endpoints])))
    q.save(OUT/'rendering-audit.json',dict(results=results,trainingEligible=False,independentGroups=1,
        limitation='Pixel differences confirm a rendered change, not correct effect fidelity or model accuracy.'))


def register():
    from research_campaign340 import pin
    deps=[]
    for factor in ('size','growth','shadow','position','background'):
        job=f'generation354b-{factor}-capture';spec=q.load(q.QUEUE/'jobs'/job/'spec.json')
        deps.append(dict(job=job,specSHA256=q.text_digest(spec),outputs=['capture/capture.json']))
    spec=dict(version=q.SPEC_VERSION,id='generation354b-rendering-audit',task='GENERATION354',
        owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis='Requested factors must produce measured changes before model differences receive a causal interpretation.',
        decisionRule='Report exact pixel differences, native body geometry, and clipping. Do not label fidelity from pixel changes alone.',
        inputs=[pin(q.ROOT/'scripts'/name) for name in ('audit_generation354.py','compare351.py')],
        dependencies=deps,adapter=dict(type='python-callable',steps=['audit_generation354.run'],outputAttributes=['audit_generation354.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    p=q.ROOT/'Research/ResearchSpecs/GENERATION354/rendering-audit.json';q.save(p,spec);print(q.submit(p))


if __name__=='__main__':register()
