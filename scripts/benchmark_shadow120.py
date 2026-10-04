"""Paired consumer throughput comparison on unchanged DTM030 inputs and model."""
import json
import statistics
from pathlib import Path
import verify_transition_shadow106 as v

h=v.h
BASE=h.ROOT/'reports/work/SHADOW-THROUGHPUT-120/artifacts/attempt02'
SOURCE=h.ROOT/'reports/work/TRANSITION-SHADOW-118/artifacts'


def classes(examples):
    """Expected request-owned LRU behavior for fully valid parity input."""
    labels=[]
    for offset in range(0,len(examples),32):
        cache=[]
        for pair in examples[offset:offset+32]:
            hits=0
            for side in ('before','after'):
                key=pair[side]['sha256']
                if key in cache:cache.remove(key);hits+=1
                elif len(cache)==8:cache.pop(0)
                cache.append(key)
            labels.append(('cold','mixed','cached')[hits])
    return labels


def main():
    h.fresh(BASE);BASE.mkdir(parents=True)
    tools={'delivered':SOURCE/'portable-check/.build/arm64-apple-macosx/release/TransitionShadowTool',
           'optimized':h.ROOT/'.build/arm64-apple-macosx/release/TransitionShadowTool'}
    reports={}
    for name,tool in tools.items():
        v.verify(tool,BASE/name,base=SOURCE)
        reports[name]=h.read(BASE/name/'parity.json')
    labels=classes(h.read(SOURCE/'parity-inputs/reference.json')['examples'])
    timings={}
    for name in tools:
        results=[]
        for offset in range(0,len(labels),32):
            results.extend(h.read(BASE/name/f'reply-{offset}.json')['results'])
        h.require(len(results)==len(labels),'membership')
        timings[name]={kind:dict(count=labels.count(kind),medianSeconds=statistics.median(
            row['preprocessingSeconds'] for label,row in zip(labels,results) if label==kind))
            for kind in sorted(set(labels))}
    old,new=reports['delivered'],reports['optimized']
    result=dict(version='shadow-throughput-v1',membership=h.ref(SOURCE/'parity-inputs/reference.json'),
        modelTreeSHA256=new['modelTreeSHA256'],reports={name:h.ref(BASE/name/'parity.json') for name in tools},
        preprocessingRatio=new['preprocessingMedianSeconds']/old['preprocessingMedianSeconds'],
        totalRatio=new['elapsedSeconds']/old['elapsedSeconds'],groups=timings,
        exactParity=all(r['passed'] and r['exactEncodings']==438 and r['decisionsEqual']==438 for r in reports.values()),
        scope='Consecutive CPU CLI replays; same data/order/batch size; filesystem may be warm. No independent accuracy.',
        maxRetainedTensorBytes=8*3*192*128*4,fullFrameCache=False,releaseEligible=False)
    h.require(old['modelTreeSHA256']==new['modelTreeSHA256'],'model_changed')
    h.write(BASE/'comparison.json',result,sealed=True)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
