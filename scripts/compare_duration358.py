"""Compare complete 10-epoch and 30-epoch reports without promoting a model."""
import research_queue as q
OUT = None


def compare(old, new):
    rows={}
    for arm in ('control','position'):
        a,b=old['decisions'][arm],new['decisions'][arm]
        q.require(a['complete'] and b['complete'] and a['comparisons']==b['comparisons']==24,'incomplete_comparison')
        rows[arm]=dict(epochs10=a,epochs30=b,
            lostPreviousDelta=b['lostPrevious']-a['lostPrevious'],
            nativeMovementGainDelta=b['gainedNativeMovement']-a['gainedNativeMovement'],
            passesDevelopmentRule=b['passesDevelopmentRule'])
    return dict(durationComparison=rows,modelAccepted=False,
        limitation='Matched development reports guide the next decision. They do not establish deployment qualification.')


def run():
    config=q.load(OUT/'config.json');ref=config['earlier']
    q.require(q.digest(q.ROOT/ref['path'])==ref['sha256'],'earlier_changed')
    dependencies=q.load(OUT/'dependencies.json');q.require(len(dependencies)==1,'comparison_dependency')
    dep=dependencies[0]
    for item in [dep['result'],*dep['outputs']]:
        q.require(q.digest(q.ROOT/item['path'])==item['sha256'],'dependency_changed')
    q.save(OUT/'summary.json',compare(q.load(q.ROOT/ref['path']),q.load(q.ROOT/dep['outputs'][0]['path'])))
