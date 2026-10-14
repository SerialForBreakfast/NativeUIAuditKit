"""Link region coverage with retained model errors without new inference."""
from collections import Counter
from pathlib import Path
import numpy as np
import controls330 as c

b=c.b;OUT=c.OUT


def counts(probabilities,labels):
    p=np.asarray(probabilities);y=np.asarray(labels)
    return dict(rows=len(y),correct=int(((p<=.15)&(y==0)|(p>=.85)&(y==1)).sum()),
        falseChange=int(((p>=.85)&(y==0)).sum()),missedChange=int(((p<=.15)&(y==1)).sum()),
        abstentions=int(((p>.15)&(p<.85)).sum()))


def main():
    doc=b.read(OUT/'audit.json');b.checked(doc['source']);prior=b.read(b.checked(doc['prior']))
    old={v['index']:v for v in prior['rows']};det=b.read(b.checked(doc['detections']))
    registration=b.read(b.checked(det['registration']));b.checked(registration['membership'])
    member=b.read(b.PACKAGE/'membership.json');unique={};sizes=[]
    for row in doc['rows']:
        source=member['rows'][row['index']]
        b.require(source['role']=='train' and source['id']==row['id'],'membership_role')
        pairs=old[row['index']]['pairedBodies']
        b.require(len(row['controlMatches'])==2*len(pairs),'control_count')
        for j,pair in enumerate(pairs):
            for n,box in enumerate(pair):
                digest=source['images'][n]['sha256'];key=(digest,*box)
                match=row['controlMatches'][2*j+n]
                b.require(key not in unique or unique[key]['iou']==match,'duplicate_disagreement')
                unique[key]=dict(image=digest,body=box,iou=match)
    for value in unique.values():
        dims=det['rows'][value['image']]['size'];box=c.encoded_box(value['body'],dims)
        sizes.append(dict(**value,encodedMinimum=min(box[2:])))
    groups={}
    for name in sorted({v['group'] for v in doc['rows']}):
        rows=[v for v in doc['rows'] if v['group']==name]
        groups[name]=dict(rows=len(rows),controls=sum(v['controls'] for v in rows),matched=sum(v['matched'] for v in rows),
            oldCoverage=c.summarize(rows,'oldCoverage'),detectorCoverage=c.summarize(rows,'detectorCoverage'),
            knownCoverage=c.summarize(rows,'knownCoverage'))
    comparisons={};pins={}
    for model in ('FOCUS-327','FOCUS-329'):
        path=b.ROOT/f'reports/work/{model}/run/evaluation.json';pins[model]=b.ref(path)
        probabilities=b.read(path)['conditions']['native.npy']['probabilities']
        comparisons[model]={}
        for label,subset in [('allTraining',doc['rows']),('noMatchedControls',[v for v in doc['rows'] if not v['matched']]),
                ('coverageWorse',[v for v in doc['rows'] if v['oldCoverage'] is not None and v['detectorCoverage']<v['oldCoverage']]),
                ('coverageBetter',[v for v in doc['rows'] if v['oldCoverage'] is not None and v['detectorCoverage']>v['oldCoverage']])]:
            comparisons[model][label]=counts([probabilities[v['index']] for v in subset],[v['changed'] for v in subset])
    b.write(OUT/'report.json',dict(audit=b.ref(OUT/'audit.json'),source=b.ref(Path(__file__)),groups=groups,
        distinctFrameBodies=len(unique),matchedDistinctFrameBodies=sum(v['iou']>=.5 for v in unique.values()),
        uniqueImages=len(det['rows']),countsAreIndependentTrials=False,modelReports=pins,retainedComparisons=comparisons,
        sizes=sizes,trainingStarted=False,productionEligible=False,
        outcome='Reject this detector-centered region rule before training. Keep all current models.',
        limits='IoU measures geometry, not class correctness. Cached model errors do not measure the proposed crop model.'))
    print('Distinct frame bodies',len(unique),'matched',sum(v['iou']>=.5 for v in unique.values()),flush=True)
    print('Cached comparisons',comparisons,flush=True)


if __name__=='__main__':main()
