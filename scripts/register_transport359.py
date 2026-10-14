"""Prepare input transport tests for the existing background runner."""
import research_queue as q
from research_campaign340 import pin


def register():
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS359';folder.mkdir(exist_ok=True)
    source=pin(q.ROOT/'scripts/transport359.py');specs=[]
    def submit(ident,config,hypothesis,rule):
        cp=folder/(ident+'-config.json');q.save(cp,config)
        spec=dict(version=q.SPEC_VERSION,id=ident,task='FOCUS359',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis=hypothesis,decisionRule=rule,inputs=[source,*config['inputs']],stage=[{'from':pin(cp),'to':'config.json'}],
            adapter=dict(type='python-callable',steps=['transport359.run'],outputAttributes=['transport359.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        p=folder/(ident+'.json');q.save(p,spec);q.submit(p);specs.append(spec)
    model=pin(q.ROOT/'reports/work/FOCUS-329/run/last.pt')
    for factor in ('size','growth','shadow','position','background'):
        path=q.QUEUE/f'jobs/generation354b-{factor}-capture/attempts/1/out/capture/capture.json'
        doc=q.load(path);refs=[pin(path),model]+[pin(path.parent/f['path']) for f in doc['frames']]
        refs += [pin(q.ROOT/'scripts'/n) for n in ('compare351.py','report_additive341.py','diagnostics343.py','regions313.py','edge329.py')]
        submit('focus359-compression-'+factor,dict(mode='model',capture=pin(path),model=model,inputs=refs),
            'Test resolution and compression sensitivity across '+factor+' on matched retained frames.',
            'Report misses, false changes, abstentions, and lost previous successes. Do not tune thresholds or claim HDMI equivalence.')
    images=[];seen=set()
    for path in sorted((q.ROOT/'reports/work/HCF357/extracted').rglob('*.png')):
        ref=pin(path)
        if ref['sha256'] not in seen:images.append(ref);seen.add(ref['sha256'])
    for level in (1,6,9):
        submit('focus359-lossless-'+str(level),dict(mode='storage',images=images,inputs=images,level=level),
            'Measure exact PNG pixel preservation, bytes, and encoding cost at compression level '+str(level)+'.',
            'Require exact decoded parity. Keep current originals and the 250 GiB study limit.')
    dest=q.ROOT/'reports/work/FOCUS359';dest.mkdir(exist_ok=True)
    q.save(dest/'additions.json',[dict(id=s['id'],sha256=q.text_digest(s)) for s in specs])


if __name__=='__main__':register()
