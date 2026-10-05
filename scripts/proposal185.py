"""Summarize sealed185 evidence and freeze one loss-weight comparison; no launch."""
import collections
import statistics
from pathlib import Path
import diagnose185 as d
h,p=d.h,d.p


def config(args):
    h.require(args['box']==7.5 and args['epochs']==10 and args['batch']==8,'control_configuration')
    return dict(args,box=15.)


def summary(values):
    geometry=[v['geometry'] for v in values if v['geometry'] is not None]
    return dict(count=len(values),geometrySupport=len(geometry),medianGeometry={k:statistics.median(v[k] for v in geometry) if geometry else None
        for k in ('heightRatio','widthRatio','centerXErrorInWidths','centerYErrorInHeights','iou')})


def run():
    out=d.OUT/'proposal.json';h.require(not out.exists(),'output_collision')
    diag=p.sealed(d.OUT/'diagnosis.json')
    for ref in diag['references']+diag['sources']:h.checked(h.ROOT,ref,256*1024**2)
    protocol=p.sealed(d.LATEST/'protocol.json');membership=p.sealed(h.checked(h.ROOT,protocol['membership']))
    family={row['id']:row.get('family') for row in membership['rows']}
    summaries={}
    for arm in ('021','022'):
        summaries[arm]={}
        for name,cases in diag['arms'][arm]['combined']['cases'].items():
            families=collections.Counter();scores=[]
            for row in cases:
                key=row['id'].replace('/images/','/')
                h.require(key in family and family[key],'missing_family')
                families[family[key]]+=row['fp'];scores.extend(v['score'] for v in row['falsePredictions'])
            summaries[arm][name]=dict(falseByFamily={k:v for k,v in families.items() if v},medianFalseConfidence=statistics.median(scores) if scores else None)
    fit={};transitions={}
    for arm,rows in diag['fit'].items():
        groups=collections.defaultdict(list)
        for row in rows:
            groups['|'.join(row['metadata'][k] for k in ('family','placement'))+'|'+row['disposition']].append(row)
        fit[arm]={key:summary(values) for key,values in groups.items()}
    for arm in ('020','021'):
        before={r['id']:r for r in diag['fit'][arm]};after=diag['fit']['022'];h.require(set(before)=={r['id'] for r in after},'changed_fit')
        transitions[arm+'-022']=dict(collections.Counter(before[r['id']]['disposition']+' -> '+r['disposition'] for r in after))
    rows=protocol['rows'];h.require(len(rows)==432 and all(r['split']=='train' for r in rows),'membership_role')
    h.write(out,dict(version='geometry185-proposal-v1',diagnosis=h.ref(d.OUT/'diagnosis.json'),
        referenceProtocol=h.ref(d.LATEST/'protocol.json'),referenceEvaluation=h.ref(d.LATEST/'evaluation.json'),source=h.ref(__file__),
        rows=rows,membership=protocol['membership'],initializer=protocol['initializer'],config=config(protocol['args']),schedule=protocol['schedule'],
        falsePositiveSummary=summaries,fitGeometry=fit,fitTransitions=transitions,
        hypothesis='double localization box-loss weight only; residual over-tall native page boxes',
        selection='same432already-admitted train members; no outcome-based sampling',
        acceptance='unchanged179 fourteen gates plus exact matched022 comparison; no DS-G8 claim',
        launchEligible=False,preflight=['new isolated paths','source and membership checks','register next run','actual one-field treatment verification'],
        budgetBytes=2*1024**3,trainingLaunched=False,productionEligible=False),sealed=True)
    print('Frozen one box7.5→15 comparison; unchanged432members; no training',flush=True)


if __name__=='__main__':run()
