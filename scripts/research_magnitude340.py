"""Compare retained focus and artwork changes at similar pixel magnitudes."""
from collections import OrderedDict, defaultdict
from pathlib import Path
import time
import numpy as np
from PIL import Image
import research_queue as q
from research_campaign340 import pin, decision

OUT = None


def matched_pairs(rows):
    """Match within artwork families at a fixed 10 percent magnitude tolerance."""
    result=[]
    for group in sorted({r['group'] for r in rows}):
        positive=sorted((r for r in rows if r['group']==group and r['label']==1),key=lambda r:r['magnitude'])
        negative={r['id']:r for r in rows if r['group']==group and r['label']==0}
        for a in positive:
            candidates=[b for b in negative.values() if abs(a['magnitude']-b['magnitude'])<=.1*max(a['magnitude'],b['magnitude'])]
            if not candidates:continue
            b=min(candidates,key=lambda b:(abs(a['magnitude']-b['magnitude']),b['id']))
            del negative[b['id']]
            result.append(dict(group=group,movement=a,artwork=b))
    return result


def run():
    start=time.monotonic();config=q.load(OUT/'config.json')
    docs=[]
    for ref in config['inputs']:
        path=q.local_path(q.ROOT,ref['path']);q.require(q.digest(path)==ref['sha256'],'source_hash');docs.append(q.load(path))
    corpus,predictions,old=docs
    rows=corpus['rows']['independent'];probs=predictions['probabilities'][len(old['rows']):]
    q.require(len(rows)==len(probs),'prediction_membership')
    selected=[(r,p) for r,p in zip(rows,probs) if not r['reverse'] and r['condition']!='identical']
    cache=OrderedDict();verified=set();output=[]
    def image(ref):
        key=ref['sha256'];path=q.local_path(q.ROOT,ref['path'])
        if (str(path),key) not in verified:
            q.require(q.digest(path)==key,'image_hash');verified.add((str(path),key))
        if key not in cache:
            with Image.open(path) as im:
                q.require(im.size==(1920,1080),'image_dimensions')
                cache[key]=np.asarray(im.convert('RGB')).copy()
            if len(cache)>4:cache.popitem(last=False)
        cache.move_to_end(key);return cache[key]
    for i,(row,p) in enumerate(selected):
        q.require(row['role']=='train','data_role')
        a,b=[image(ref).astype(np.int16) for ref in row['images']]
        magnitude=float(np.abs(a-b).mean()/255)
        output.append(dict(id=row['id'],group=row['group'],label=row['changed'],probability=p,
                           decision=decision(p),magnitude=magnitude))
        q.save(OUT.parent/'progress.json',dict(step='Measure verified pixel differences',completed=i+1,total=len(selected),
                                              unit='pairs',updatedAt=time.time()),replace=True)
    pairs=matched_pairs(output)
    q.save(OUT/'diagnostic.json',dict(version='research-diagnostic-v1',evidenceKind='cached-diagnostic',
        rows=output,matches=pairs,matchedCount=len(pairs),groups=len({p['group'] for p in pairs}),
        bothCorrect=sum(p['movement']['decision']==1 and p['artwork']['decision']==0 for p in pairs),
        seconds=time.monotonic()-start,candidateJustified=False,
        limitations=['Authored training data only. Related rows are not independent trials.',
                     'A 10 percent matching tolerance tests magnitude, not semantic equivalence.',
                     'This does not complete native evaluation or all theme coverage.']))


def register():
    folder=q.ROOT/'Research/ResearchSpecs/RESEARCH340';id='measured340-a3-retained'
    if (q.QUEUE/'jobs'/id/'spec.json').exists():return
    sources=['reports/work/FOCUS-326/corpus.json','reports/work/FOCUS-329/run/training.json','reports/work/FOCUS-319/corpus.json']
    refs=[pin(q.ROOT/p) for p in sources]
    config=folder/(id+'-config.json');q.save(config,dict(inputs=refs))
    spec=dict(version=q.SPEC_VERSION,id=id,task='RESEARCH340-A3',owner='research-host-NUIAK',kind='screen',authority='diagnostic',
        batch='cached',hypothesis='Equal pixel-change magnitude does not imply equal focus-change decisions.',
        decisionRule='Match within artwork family at 10 percent magnitude tolerance. Report support and both-correct counts; do not fit thresholds.',
        adapter=dict(type='python-callable',steps=['research_magnitude340.run'],outputAttributes=['research_magnitude340.OUT']),
        inputs=refs+[pin(Path(__file__)),pin(q.ROOT/'scripts/research_campaign340.py')],
        stage=[{'from':pin(config),'to':'config.json'}],limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=2))
    path=folder/(id+'.json');q.save(path,spec);print(q.submit(path))


if __name__=='__main__':register()
