"""Queue the 4 received native archive checks behind HCF work."""
import research_queue as q
from research_campaign340 import pin

if __name__=='__main__':
    base=q.ROOT/'reports/work/FOCUS372/intake-20261013'
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS373-native';folder.mkdir(exist_ok=True)
    additions=[]
    for group,count in [('atlas-solstice',12),('hearth-folio',12),('kinetic-circuit',12),('stillwater',6)]:
        root=base/('focus372-20261013-v1-'+group);ident='focus373-native-'+group
        config=folder/(ident+'-config.json');q.save(config,dict(root=q.relative(root),cases=count,membersSHA256=q.digest(root/'MEMBERS.json')))
        spec=dict(version=q.SPEC_VERSION,id=ident,task='FOCUS373',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
            hypothesis='Do the original '+group+' scene records show focused controls and valid body bounds?',
            decisionRule='Verify raw brackets, geometry, image dimensions, and hashes. Correct misleading summary interpretation; do not admit training data.',
            inputs=[pin(root/'MEMBERS.json'),pin(q.ROOT/'scripts/native_receipt373.py')],
            stage=[{'from':pin(config),'to':'config.json'}],
            adapter=dict(type='python-callable',steps=['native_receipt373.run'],outputAttributes=['native_receipt373.OUT']),
            limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
        path=folder/(ident+'.json');q.save(path,spec);q.submit(path)
        additions.append(dict(id=ident,sha256=q.text_digest(spec)))
    q.save(folder/'additions.json',additions);print('Registered 4 native record checks. No capture or model execution.')
