"""Register one read-only TTR request check for the existing runner."""
import research_queue as q
from research_campaign340 import pin
from qualify_hcf362 import CLI


if __name__=='__main__':
    folder=q.ROOT/'Research/ResearchSpecs/FOCUS373'
    ident='focus373-e-native-plans'
    q.require(not (q.QUEUE/'jobs'/ident).exists(),'already_registered')
    requests=[pin(p) for p in sorted((q.ROOT/'docs/experiment-graph-v1-requests').glob('*.json'))]
    cp=folder/(ident+'-config.json');q.save(cp,dict(requests=requests,helperSHA256=q.digest(CLI.resolve())))
    spec=dict(version=q.SPEC_VERSION,id=ident,task='FOCUS373',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        hypothesis='Does the qualified TTR helper accept all 7 native campaign requests without taking the capture target?',
        decisionRule='Report each compiler response. Plan acceptance is not training admission or live capture qualification.',
        inputs=requests+[pin(q.ROOT/'scripts/producer373.py'),pin(q.ROOT/'scripts/qualify_hcf362.py')],
        stage=[{'from':pin(cp),'to':'config.json'}],
        adapter=dict(type='python-callable',steps=['producer373.run'],outputAttributes=['producer373.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1))
    path=folder/(ident+'.json');q.save(path,spec);q.submit(path)
    q.save(folder/'producer-additions.json',[dict(id=ident,sha256=q.text_digest(spec))])
    print(ident)
