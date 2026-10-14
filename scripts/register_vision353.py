"""Register a native Vision batch on retained Fixture frames."""
import research_queue as q
from research_campaign340 import pin
from compare351 import validate_capture


def main():
    folder=q.ROOT/'Research/ResearchSpecs/VISION353';folder.mkdir(exist_ok=True)
    path=q.ROOT/'reports/work/DATASET351/capture/capture.json'
    capture=q.load(path);validate_capture(capture,path.parent)
    binary=pin(q.ROOT/'.build/vision353/probe')
    inputs=[pin(p) for p in sorted(path.parent.iterdir()) if p.is_file()]
    inputs += [binary, *[pin(q.ROOT/'scripts'/name) for name in (
        'vision353.py','vision_annotation_probe.swift','compare351.py','perception_benchmark.py')]]
    settings=[('fit-v2',dict(mode='features',revision=2,crop='scaleFit'), 'Preserving frame edges retains focus movement evidence.'),
        ('center-v2',dict(mode='features',revision=2,crop='centerCrop'), 'Center cropping may discard native corner movement evidence.'),
        ('fit-v1',dict(mode='features',revision=1,crop='scaleFit'), 'Feature-print revision changes sensitivity to small focus changes.'),
        ('rectangles',dict(mode='rectangles'), 'Vision rectangle proposals may cover native bodies missed by the focus model.')]
    dependencies=[]
    for index,(name,setting,hypothesis) in enumerate(settings):
        ident=f'vision353-{index:02d}-{name}'
        config=folder/(ident+'-config.json')
        q.save(config,dict(setting,capture=pin(path),binary=binary,inputs=inputs))
        spec=dict(version=q.SPEC_VERSION,id=ident,task='VISION353',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis=hypothesis,decisionRule='Report raw distances or body coverage. Preserve every operating point; no threshold selection or model change.',
            inputs=inputs,stage=[{'from':pin(config),'to':'config.json'}],
            adapter=dict(type='python-callable',steps=['vision353.run'],outputAttributes=['vision353.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        sp=folder/(ident+'.json');q.save(sp,spec);print(ident,q.submit(sp))
        dependencies.append(dict(job=ident,specSHA256=q.text_digest(spec),outputs=['diagnostic.json']))
    ident='vision353-04-comparison'
    refs=[pin(q.QUEUE/f'jobs/dataset351-{i:02d}-{mode}/attempts/1/out/diagnostic.json')
          for i,mode in enumerate(('movement','content','recapture'))]
    config=folder/(ident+'-config.json');q.save(config,dict(inputs=refs))
    spec=dict(version=q.SPEC_VERSION,id=ident,task='VISION353',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis='Matched native results distinguish input loss from inadequate proposals and weak model decisions.',
        decisionRule='Compare matched retained counts with all frozen Vision settings. Do not infer real-app accuracy or select a production threshold.',
        inputs=refs+[pin(q.ROOT/'scripts/vision353.py')],dependencies=dependencies,
        stage=[{'from':pin(config),'to':'config.json'}],
        adapter=dict(type='python-callable',steps=['vision353.summarize'],outputAttributes=['vision353.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    sp=folder/(ident+'.json');q.save(sp,spec);print(ident,q.submit(sp))


if __name__=='__main__':main()
