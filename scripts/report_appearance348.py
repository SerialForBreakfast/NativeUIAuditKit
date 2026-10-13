"""Compare equal-budget models with original and matched appearance predictions."""
import json
import numpy as np
import appearance348 as m

q=m.q


def totals(groups):
    result={}
    for row in groups.values():
        for key,value in row.items():result[key]=result.get(key,0)+value
    return result


def main(core_only=False,task='focus348'):
    q.require(task in ('focus348','focus349'),'unsupported_comparison_task')
    records=[];original_losses={'control':0,'gamma':0}
    for job in sorted((q.QUEUE/'jobs').glob(task+'-*')):
        path=job/'attempts/1/out/comparison.json'
        if not path.exists():continue
        q.require(q.load(job/'attempts/1/result.json')['status']=='complete','incomplete_result')
        doc=q.load(path);config=doc['configuration']
        for name,item in doc['sets'].items():
            baseline=item['originalProbabilities'];matched=None
            if config.get('kind')=='appearance' and config['scope']!='original':
                for oldjob in sorted((q.QUEUE/'jobs').glob('focus347-*')):
                    p=oldjob/'attempts/1/out/diagnostic.json'
                    if not p.exists():continue
                    receipt=oldjob/'attempts/1/result.json'
                    if not receipt.exists() or q.load(receipt)['status']!='complete':continue
                    previous=q.load(p);settings=previous['configuration']
                    if settings.get('factor')==config['factor'] and settings.get('scope')==config['scope']:
                        q.require([r['id'] for r in previous['rows']]==[r['id'] for r in item['rows']],'membership_changed')
                        matched=previous['probabilities'];break
                q.require(matched is not None,'missing_matched_baseline')
                baseline=matched
            counts={key:totals(m.f.prior.count(item['rows'],p,baseline)) for key,p in item['probabilities'].items()}
            if matched is None:
                for key in original_losses:original_losses[key]+=counts[key]['lost']
            records.append(dict(job=job.name,set=name,counts=counts,
                gammaAgainstControl=totals(item['gammaAgainstControl']),
                baseline='same transformed images' if matched is not None else 'original images',
                source=m.f.pin(path)))
    required={'focus348-01-original','focus348-02-regression-native','focus348-03-regression-replay',
              'focus348-04-regression-global','focus348-05-regression-left','focus348-06-regression-center',
              'focus348-18-gamma-source-reselect','focus348-27-neighbors-0','focus348-28-neighbors-2','focus348-29-placeholders'}
    required={v.replace('focus348',task) for v in required}
    q.require(required<={r['job'] for r in records},'incomplete_core')
    if not core_only:q.require(len(records)==56,'incomplete_comparisons')
    target=next(v for v in records if v['job'].endswith('gamma-source-reselect'))
    improves=target['gammaAgainstControl']['gained']>target['gammaAgainstControl']['lost']
    base=m.BASE if task=='focus348' else q.ROOT/'reports/work/FOCUS-349'
    out=base/('core-results.json' if core_only else 'results.json');out.parent.mkdir(exist_ok=True)
    q.save(out,dict(comparisons=records,originalLosses=original_losses,
        task=task,modelNames=({'control':'FOCUS348 unchanged-image','gamma':'FOCUS348 gamma'} if task=='focus348' else
                            {'control':'FOCUS348 gamma','gamma':'FOCUS349 movement emphasis'}),
        gammaTargetImproves=improves,complete=len(records)==56,
        replacementRecommended=len(records)==56 and improves and original_losses['gamma']==0,
        finalEvaluation=False,productionPromotion=False))
    print(json.dumps(dict(originalLosses=original_losses,target=target['counts'],
                         gammaAgainstControl=target['gammaAgainstControl']),indent=2))


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--core-only',action='store_true')
    parser.add_argument('--task',choices=['focus348','focus349'],default='focus348')
    args=parser.parse_args();main(args.core_only,args.task)
