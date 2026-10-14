"""Register the Office comparison through the existing background queue."""
import research_queue as q
from research_campaign340 import pin


def register():
    folder=q.ROOT/'Research/ResearchSpecs/HCF362'
    intake=q.load(q.ROOT/'reports/work/FOCUS-349/office-intake/intake.json')
    index=q.load(q.ROOT/'reports/work/FOCUS-349/office/office-eval-20261012-case-index.json')
    office=[intake['frames'][r['frame_id']]['image'] for r in index if r['case_id'] in ('F121','F122')]
    q.require(len(office)==2,'office_membership')
    pairs=[dict(id='office-F121-F122',sourceDomain='physicalDeviceRealApp',images=office)]
    for name in ('hcf','hcf_card_unmatched'):
        folder_path=q.ROOT/'reports/work/HCF357/extracted'/name
        meta=q.load(folder_path/'synth-0_metadata.json')
        pairs.append(dict(id=name,sourceDomain='nativeFixtureSimulator',
            images=[pin(folder_path/meta[state+'_png']) for state in ('unfocused','focused')]))
    cp=folder/'office-config.json';q.save(cp,dict(pairs=pairs))
    spec=dict(version=q.SPEC_VERSION,id='hcf362-office-scale-compare',task='HCF362',owner='research-host-NUIAK',
        authority='diagnostic',kind='screen',
        hypothesis='Compare Office HCF-end pixel changes with retained native Fixture focus changes at original and matched resolution.',
        decisionRule='Where does resizing remove change evidence? Keep real-app transfer and accuracy unavailable without matched scenes and reviewed labels.',
        inputs=[pin(q.ROOT/'scripts/office_hcf362.py')]+[r for p in pairs for r in p['images']],
        stage=[dict(from_=pin(cp),to='config.json')],
        adapter=dict(type='python-callable',steps=['office_hcf362.run'],outputAttributes=['office_hcf362.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    spec['stage']=[{'from':pin(cp),'to':'config.json'}]
    path=folder/(spec['id']+'.json');q.save(path,spec);q.submit(path)
    q.save(q.ROOT/'reports/work/HCF362/office-addition.json',[dict(id=spec['id'],sha256=q.text_digest(spec))])


if __name__=='__main__': register()
