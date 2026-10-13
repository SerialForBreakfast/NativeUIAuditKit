"""Combine completed private shadow reports without assigning focus labels."""
import argparse
from collections import Counter
import math
from pathlib import Path
import office_shadow349 as s

q=s.q


def summarize(paths):
    models=None;rows=[];seen=set();sources=[];timing={}
    for path in paths:
        path=Path(path).resolve()
        q.require(q.load(path.parent.parent/'result.json')['status']=='complete','incomplete_job')
        doc=q.load(path);config=q.load(path.parent/'config.json');s.m.check_inputs(config)
        q.require(doc.get('version')=='office-shadow349-v1' and doc.get('accuracy') is None and
                  doc.get('trainingEligible') is False and doc.get('productionEligible') is False,'invalid_shadow_report')
        q.require(doc['models']==config['models'],'changed_model_identity')
        if models is None:models=doc['models']
        q.require(doc['models']==models,'incompatible_models')
        q.require([r['id'] for r in doc['rows']]==[r['id'] for r in config['rows']],'changed_membership')
        for row,original in zip(doc['rows'],config['rows']):
            q.require(all(row.get(k)==v for k,v in original.items()),'changed_input_row')
            q.require(row['id'] not in seen,'duplicate_pair');seen.add(row['id'])
            q.require(row.get('focusChanged') is None and row.get('actionLinked') is False and
                      row.get('trainingEligible') is False and row.get('role')=='development','unsupported_label_role')
            p=row['probabilities'];q.require(set(p)==set(models),'missing_prediction')
            q.require(all(type(v) in (int,float) and math.isfinite(v) and 0<=v<=1 for v in p.values()),'invalid_probability')
            decisions={k:s.decision(v) for k,v in p.items()}
            q.require(row['decisions']==decisions,'decision_mismatch')
            disagreement=len(set(decisions.values()))>1
            q.require(row['disagreement']==disagreement,'disagreement_mismatch')
            rows.append(dict(id=row['id'],group=row['group'],probabilities=p,decisions=decisions,
                disagreement=disagreement,abstentions=sum(v=='abstain' for v in decisions.values()),
                reviewReason='model disagreement' if disagreement else 'shared abstention' if 'abstain' in decisions.values()
                             else 'agreement audit; agreement is not truth'))
        sources.append(s.m.f.pin(path))
        timing[str(path)]=doc['timing']
    q.require(rows,'zero_support')
    return dict(version='office-review-summary349-v1',models=models,sources=sources,counts=dict(pairs=len(rows),
        groups=len({r['group'] for r in rows}),disagreements=sum(r['disagreement'] for r in rows)),
        decisions={name:dict(Counter(r['decisions'][name] for r in rows)) for name in models},
        review=sorted(rows,key=lambda r:(not r['disagreement'],-r['abstentions'],r['id'])),timing=timing,
        accuracy=None,trainingEligible=False,finalEvaluation=False,productionPromotion=False,
        limitations=['Model agreement does not establish correct focus.',
            'Selected pairs share one recording. Do not count them as independent trials.',
            'The reports do not connect visual changes to particular commands.'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output');p.add_argument('reports',nargs='+');a=p.parse_args()
    result=summarize(a.reports);q.save(Path(a.output),result);print(result['counts'])
