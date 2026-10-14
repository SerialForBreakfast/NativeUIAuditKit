"""Report boundary support and matched candidate regressions."""
from collections import Counter
import numpy as np
import boundary329 as a

b=a.b;OUT=a.OUT


def diagnostic_summary(doc):
    groups={}
    for group in sorted({v['group'] for v in doc['rows']}):
        rows=[v for v in doc['rows'] if v['group']==group and v['status']=='measured']
        valid=[v for v in rows if v['boundaryFraction'] is not None]
        coverage=[v['proposalBoundaryCoverage'] for v in rows if v['changed'] and v['proposalBoundaryCoverage'] is not None]
        groups[group]=dict(rows=len(rows),changed=sum(v['changed'] for v in rows),
            boundaryFractionAUC=a.auc([v['boundaryFraction'] for v in valid],[v['changed'] for v in valid]),
            edgeRatioAUC=a.auc([v['imageEdgeRatio'] for v in rows],[v['changed'] for v in rows]),
            medianBoundaryCoverage=float(np.median(coverage)) if coverage else None)
    measured=[v for v in doc['rows'] if v['status']=='measured']
    return dict(groups=groups,clipping=Counter(v for row in measured for v in row['clipping']),
        distinctGeometryPatterns=len({tuple(tuple(box) for pair in v['pairedBodies'] for box in pair) for v in measured}),
        limitation='Geometry patterns and related rows are not independent capture trials.')


def main():
    b.require(not (OUT/'comparison.json').exists(),'output_collision')
    audit=b.read(OUT/'audit.json');reg=b.read(OUT/'inputs.json')
    b.checked(reg['diagnostic']);b.checked(reg['runner']);b.checked(reg['decision'])
    report=b.read(OUT/'report.json');member=b.read(b.PACKAGE/'membership.json')
    files={'FOCUS327':b.ROOT/'reports/work/FOCUS-327/run/evaluation.json',
           'FOCUS328':b.ROOT/'reports/work/FOCUS-328/run/evaluation.json','FOCUS329':OUT/'run/evaluation.json'}
    docs={k:b.read(p) for k,p in files.items()};rows=member['rows'];y=np.array([v['changed'] for v in rows])
    probabilities={k:np.array(v['conditions']['native.npy']['probabilities']) for k,v in docs.items()}
    from report_contrast328 import grouped
    content={}
    for label in (0,1):
        ids=[i for i,v in enumerate(rows) if v['role']=='train' and 'content_contrast' in v['conditions'] and v['changed']==label]
        content[str(label)]={k:b.trainer.w.summary(p[ids],y[ids]) for k,p in probabilities.items()}
    original=report['comparisons']['FOCUS327']['cases'];native=[v for v in original if v['input']=='native.npy']
    result=dict(registration=b.ref(OUT/'inputs.json'),diagnostic=diagnostic_summary(audit),
        roles=grouped(rows,y,probabilities),trainingContentByLabel=content,
        conditions={key:{name:doc['conditions'][key]['summary'] for name,doc in docs.items()} for key in docs['FOCUS329']['conditions']},
        lostGroups=dict(Counter(v['group'] for v in native if v['lostCorrect'])),
        gainedGroups=dict(Counter(v['group'] for v in native if v['gainedCorrect'])),
        comparisons=report['comparisons'],productionEligible=False)
    b.write(OUT/'comparison.json',result)
    print('Native',result['conditions']['native.npy'],flush=True)
    print('Roles',result['roles'],flush=True)
    print('Content',content,flush=True)


if __name__=='__main__':main()
