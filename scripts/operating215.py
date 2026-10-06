"""Rank accepted worker operating errors, retaining roles and original frame links."""
from collections import Counter
from pathlib import Path
import json
from artwork200_campaign import sha, write
from export_artwork204 import ROOT
from shared_transfer import require

REPORT=ROOT/'reports/work/WORKER-198/artifacts/paired-return04/worker198-paired-return04/report04.json'
MAPPING=ROOT/'reports/work/WORKER-198/artifacts/eval02701/payload/proposal-mapping.json'
PINS=('c175552677291d0654e68a8d6e4e306b24d180062dddf808efac3a091ee65589',
      'c0aa6595748835e98aa64abe3c7ee9eb3b785160a7c7c1e2576b7184471a0a70')
OUT=ROOT/'reports/work/OPERATING-FEEDBACK-215/artifacts/report01.json'
REASONS={'duplicate_FP','unmatched_FP','absent_same_class_FN','assignment_competition_FN','localization_FN','no_overlap_FN'}


def rank(report,mapping):
    require(report['operating_confidence_threshold']==.25 and report['matching_IoU']==.5,'operating_contract')
    require([p['partition'] for p in report['partitions']]==['fit','page','combined'],'partitions')
    categories=[];parts=[]
    for part in report['partitions']:
        kind=part['partition'];cases=part['cases']
        sources={r['cropID']:r for r in mapping['plans'][kind]['records'] if r['cropID'] is not None}
        ids=[c['imageID'] for c in cases]
        require(len(ids)==len(set(ids))==part['images'] and set(ids)==set(sources),'case_mapping')
        gt=sum(c['GT_count'] for c in cases);require(gt==part['support'],'support')
        buckets={};totals={};low=[]
        for arm in ('control','treatment'):
            totals[arm]=Counter()
            for case in cases:
                result=case['operating_'+arm]
                require(all(type(result[k])==int and result[k]>=0 for k in ('TP','FP','FN')),'counts')
                require(result['TP']+result['FN']==case['GT_count'],'case_support')
                matches=result['matched_GT_indices']
                require(len(matches)==len(set(matches))==result['TP'] and all(type(i)==int and 0<=i<case['GT_count'] for i in matches),'matches')
                errors=result['failures'];require(set(errors)<=REASONS and all(type(v)==int and v>=0 for v in errors.values()),'reasons')
                for suffix in ('FP','FN'):
                    require(sum(n for k,n in errors.items() if k.endswith(suffix))==result[suffix],'failure_accounting')
                totals[arm].update({k:result[k] for k in ('TP','FP','FN')})
                if arm=='treatment':
                    src=sources[case['imageID']]
                    for reason,n in errors.items():
                        if n:buckets.setdefault(reason,[]).append(dict(roiID=case['imageID'],imageID=src['imageID'],window=src['window'],count=n))
                    candidates=case['low_confidence_candidate_GT_indices'][arm]
                    require(all(type(i)==int and 0<=i<case['GT_count'] for i in candidates),'candidate_indices')
                    missing=sorted(set(candidates)-set(matches))
                    if missing:low.append(dict(roiID=case['imageID'],imageID=src['imageID'],indices=missing))
            require(dict(totals[arm])==part['operating_'+arm],'partition_accounting')
            for key in ('TP','FP','FN'):
                require(sum(r['operating_'+arm][key] for r in part['per_class'])==totals[arm][key],'class_accounting')
        for reason,rows in buckets.items():
            denominator=gt if reason.endswith('FN') else totals['treatment']['TP']+totals['treatment']['FP']
            categories.append(dict(partition=kind,role=part['role'],reason=reason,count=sum(r['count'] for r in rows),
                denominator=denominator,denominatorKind='ground_truth' if reason.endswith('FN') else 'operating_detections',
                affectedROIs=len(rows),parentFrames=len({r['imageID'] for r in rows}),
                representatives=sorted(rows,key=lambda r:(-r['count'],r['roiID']))[:3]))
        regressions=[]
        for row in part['per_class']:
            a,b=row['operating_control'],row['operating_treatment']
            if b['TP']<a['TP'] or b['FP']>a['FP']:
                regressions.append(dict(className=row['class'],support=row['support'],control=a,treatment=b))
        parts.append(dict(partition=kind,role=part['role'],totals=totals,regressions=regressions,
                          unmatchedLowConfidence=low))
    return dict(scope='raw_ROI_only_not_fullframe_or_native_focus',threshold=.25,
        topTen=sorted(categories,key=lambda r:(-r['count'],r['partition'],r['reason']))[:10],
        partitions=parts,modelGatePassed=False,causalDiagnosis=False)


def run():
    require(not OUT.exists(),'output_collision')
    require((sha(REPORT),sha(MAPPING))==PINS,'source_changed')
    result=rank(json.loads(REPORT.read_text()),json.loads(MAPPING.read_text()))
    result['sources']=dict(reportSHA256=PINS[0],mappingSHA256=PINS[1],toolSHA256=sha(__file__))
    OUT.parent.mkdir(parents=True,exist_ok=True);write(OUT,result)
    for row in result['topTen']:print(row['partition'],row['reason'],row['count'],row['denominator'],row['parentFrames'])


if __name__=='__main__':run()
