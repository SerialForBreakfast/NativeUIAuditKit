"""Compare controlled Fixture endpoints without changing model preprocessing."""
import time
import research_queue as q
from research_campaign340 import pin
OUT = None


def validate_capture(doc, root):
    q.require(doc.get('version') == 'controlled-fixture351-v1', 'capture_version')
    q.require(doc.get('complete') is True and doc.get('cleanup') is True, 'incomplete_capture')
    q.require(doc.get('trainingEligible') is False and doc.get('role') == 'development', 'data_role')
    frames = {r['id']: r for r in doc['frames']}
    expected = doc.get('expectedFrames', 40)
    q.require(isinstance(expected, int) and 5 <= expected <= 40 and expected % 5 == 0, 'capture_counts')
    q.require(len(frames) == len(doc['frames']) == expected and len(doc['pairs']) == expected // 5 * 3, 'capture_counts')
    for r in frames.values():
        path = q.local_path(root, r['path'])
        q.require(q.digest(path) == r['sha256'], 'image_hash')
        q.require(r['before']['finishedAt'] <= r['start'] <= r['end'] <= r['after']['startedAt'], 'capture_interval')
    for pair in doc['pairs']:
        left, right = (frames[pair[k]] for k in ('before', 'after'))
        q.require(left['verifiedInterval'] and right['verifiedInterval'], 'unverified_endpoint')
        q.require((left['observedFocusID'] != right['observedFocusID']) == pair['changed'], 'label_conflict')
    return frames


def run():
    config = q.load(OUT / 'config.json')
    for ref in config['inputs']:
        q.require(q.digest(q.ROOT / ref['path']) == ref['sha256'], 'changed_input')
    path = q.ROOT / config['capture']['path']
    doc = q.load(path)
    frames = validate_capture(doc, path.parent)
    mode = config['mode']
    if mode == 'timing':
        rows = []
        for p in sorted(path.parent.glob('*-sequence.json')):
            seq = q.load(p)
            rows.append(dict(case=seq['case']['id'], samples=[dict(id=i,
                startAfterCommand=frames[i]['start']-seq['command']['end'],
                duration=frames[i]['end']-frames[i]['start'], verified=frames[i]['verifiedInterval'],
                settledBefore=frames[i]['before']['scene']['is_settled'],
                settledAfter=frames[i]['after']['scene']['is_settled']) for i in seq['frames'][1:3]]))
        result = dict(rows=rows, settlingAccuracy=None,
            limitation='Screenshot intervals may miss animation. Do not infer readiness latency from first retained settled frame.')
    elif mode == 'pixels':
        import numpy as np
        from PIL import Image
        rows = []
        for pair in doc['pairs']:
            arrays = []
            for key in ('before', 'after'):
                with Image.open(path.parent / frames[pair[key]]['path']) as image:
                    arrays.append(np.asarray(image.convert('RGB'), dtype=np.int16))
            delta = np.abs(arrays[1]-arrays[0])
            rows.append(dict(pair, changedPixels=int(np.any(delta>0,axis=2).sum()), meanAbsoluteDifference=float(delta.mean())))
        result = dict(rows=rows, limitation='Pixel change is not semantic focus truth. Effect settings still need visual fidelity qualification.')
    else:
        import report_additive341 as report
        from diagnostics343 import counts
        report.a.t.set_num_threads(2)
        rows=[]
        for pair in doc['pairs']:
            if pair['condition'] != mode: continue
            rows.append(dict(id=pair['case']+'-'+mode, images=[pin(path.parent/frames[pair[k]]['path']) for k in ('before','after')],
                changed=int(pair['changed']), condition=mode, layout=pair['case'], group=doc['group'], role='development'))
        q.require(len(rows)==len(frames)//5,'condition_support')
        scores={};baseline=None
        for name, ref in config['models'].items():
            start=time.monotonic()
            values=report.score_rows(report.a.e.load_candidate(q.ROOT/ref['path']),rows,False)
            scores[name]=dict(probabilities=values.tolist(),counts=counts(rows,values,baseline),seconds=time.monotonic()-start)
            if baseline is None:baseline=values
        result=dict(rows=rows,scores=scores,models=config['models'],independentGroups=1,
            limitation='Counts use observed Fixture endpoint labels. Capture-era source matching and real-app transfer remain unqualified.')
    q.save(OUT/'diagnostic.json',dict(version='dataset351-diagnostic-v1',mode=mode,inputs=config['inputs'],
        trainingEligible=False,modelAccepted=False,**result))


def register():
    path=q.ROOT/'reports/work/DATASET351/capture/capture.json'
    doc=q.load(path);validate_capture(doc,path.parent)
    folder=q.ROOT/'Research/ResearchSpecs/DATASET351';folder.mkdir(exist_ok=True)
    models={
        'FOCUS329':pin(q.ROOT/'reports/work/FOCUS-329/run/last.pt'),
        'gamma348':pin(q.QUEUE/'jobs/focus348-00-gamma/attempts/1/out/last.pt'),
        'movement349':pin(q.QUEUE/'jobs/focus349-00-gamma/attempts/1/out/last.pt')}
    refs=[pin(p) for p in sorted(path.parent.iterdir()) if p.is_file()]
    refs += [pin(q.ROOT/'scripts'/name) for name in ('compare351.py','report_additive341.py','diagnostics343.py','regions313.py','edge329.py')]
    refs += list(models.values())
    for index,mode in enumerate(('movement','content','recapture','timing','pixels')):
        ident=f'dataset351-{index:02d}-{mode}'
        cp=folder/(ident+'-config.json');q.save(cp,dict(mode=mode,capture=pin(path),models=models,inputs=refs))
        spec=dict(version=q.SPEC_VERSION,id=ident,task='DATASET351',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis='Controlled native and authored effects expose '+mode+' failures without changing original model crops.',
            decisionRule='Report paired errors and exclusions. Preserve existing models; no training or threshold selection.',
            inputs=refs,stage=[{'from':pin(cp),'to':'config.json'}],
            adapter=dict(type='python-callable',steps=['compare351.run'],outputAttributes=['compare351.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        sp=folder/(ident+'.json');q.save(sp,spec);print(ident,q.submit(sp))


if __name__=='__main__':register()
