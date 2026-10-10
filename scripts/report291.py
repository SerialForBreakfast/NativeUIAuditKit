"""Compare fixed model results and reuse verified inspection inputs."""
import argparse
from collections import defaultdict
from pathlib import Path
import time
import numpy as np
from PIL import Image
import condition291 as run
from diagnose_signal95 import encoded
from native_inspection290 import agreement
from input_use289 import compare

base=run.base
OUT=run.OUT


def added_condition_results(registration, results):
    rows=registration['addedRows']
    labels=np.asarray([row['changed'] for row in rows])
    output={}
    for name,result in results.items():
        probabilities=np.asarray(result['addedFit']['probabilities'])
        base.require(probabilities.shape==labels.shape,'added_score_shape')
        compare(probabilities,probabilities,labels)
        output[name]={}
        for condition in sorted({row['condition'] for row in rows}):
            mask=np.asarray([row['condition']==condition for row in rows])
            output[name][condition]=base.trainer.w.summary(probabilities[mask],labels[mask])
    return output


def summarize_comparison(control,candidate,membership):
    reports={};cases=[]
    for name,record in candidate['conditions'].items():
        rows=membership['rows'] if 'native' in name else None
        labels=np.array([r['changed'] for r in rows]) if rows else (
            np.array(membership['replayLabels']) if 'replay' in name else np.zeros(len(record['probabilities'])))
        before=np.asarray(control['conditions'][name]['probabilities'])
        after=np.asarray(record['probabilities'])
        reports[name]=compare(before,after,labels)
        a,b=base.decisions(before),base.decisions(after)
        for index in np.flatnonzero(a!=b):
            row=rows[index] if rows else {}
            cases.append(dict(input=name,index=int(index),id=row.get('id',f'{name}:{index}'),
                group=row.get('group'),role=row.get('role','development-diagnostic'),
                conditions=row.get('conditions',[]),changed=int(labels[index]),
                controlProbability=float(before[index]),candidateProbability=float(after[index]),
                controlDecision=int(a[index]),candidateDecision=int(b[index]),
                gainedCorrect=bool(a[index]!=labels[index] and b[index]==labels[index]),
                lostCorrect=bool(a[index]==labels[index] and b[index]!=labels[index])))
    return reports,cases


def inspect_tables():
    path=base.ROOT/'reports/work/TRANSITION-290/native24-inspection.json'
    old=base.read(path);base.checked(old['inventory']);base.checked(old['encoder'])
    base.require(old['version']=='native-inspection290-v1' and old['trainingEligible'] is False,'inspection_role')
    values=[]
    for row in old['rows']:
        base.require(row['sourceRole']=='calibration-inspection-only','row_role')
        images=[]
        for ref in row['images']:
            with Image.open(base.checked(ref)) as image:images.append(image.convert('RGB'))
        value,_=encoded(*images,(192,128))
        base.require(base.sha(value.tobytes())==row['tensorSHA256'],'inspection_encoding')
        values.append(value)
    values=np.stack(values)
    base.require(base.sha(values.tobytes())==old['inputSHA256'],'inspection_input')
    labels=np.array([r['reportedChanged'] for r in old['rows']])
    results={}
    for name in ('DTM083','DTM084'):
        ref=base.read(OUT/name/'result.json')['model']
        net=run.model.load_candidate(base.checked(ref))
        started=time.monotonic();p=base.worker.score(net,values)
        results[name]=dict(model=ref,probabilities=p.tolist(),seconds=time.monotonic()-started,
            overall=agreement(p,labels),
            byCondition={condition:agreement(p[[r['condition']==condition for r in old['rows']]],
                labels[[r['condition']==condition for r in old['rows']]])
                for condition in sorted({r['condition'] for r in old['rows']})})
    return dict(previous=base.ref(path),models=results,rows=old['rows'],
        labelAuthority=old['labelAuthority'],performanceQualified=False,trainingEligible=False)


def main():
    base.require(not (OUT/'comparison.json').exists(),'output_collision')
    base.require((OUT/'completion.json').exists(),'training_incomplete')
    base.torch.set_num_threads(2)
    membership=base.read(base.PACKAGE/'membership.json')
    control=base.read(OUT/'DTM083/evaluation.json')
    candidate=base.read(OUT/'DTM084/evaluation.json')
    reports,cases=summarize_comparison(control,candidate,membership)
    groups=defaultdict(lambda:dict(changedDecisions=0,lostCorrect=0,gainedCorrect=0))
    for row in cases:
        key=(row['input'],row['group'],row['role'])
        groups[key]['changedDecisions']+=1
        groups[key]['lostCorrect']+=int(row['lostCorrect'])
        groups[key]['gainedCorrect']+=int(row['gainedCorrect'])
    table=inspect_tables()
    added=added_condition_results(base.read(OUT/'registration.json'),
        {name:base.read(OUT/name/'result.json') for name in ('DTM083','DTM084')})
    base.write(OUT/'comparison.json',dict(version='condition291-report-v1',conditions=reports,
        cases=cases,groups=[dict(input=k[0],group=k[1],role=k[2],**v) for k,v in groups.items()],
        nativeTableInspection=table,trainingDerivedConditions=added,
        inputs=[base.ref(OUT/'registration.json'),base.ref(OUT/'DTM083/evaluation.json'),
                base.ref(OUT/'DTM084/evaluation.json'),base.ref(base.PACKAGE/'membership.json')],
        runner=base.ref(Path(__file__)),regressionPassed=candidate['regressionPassed'],productionEligible=False,
        limitations=[
            'This comparison tests the complete 80-example addition, not focus-only positives alone.',
            'Identical-image negatives take some weight from older unchanged-focus examples in the candidate.',
            'Group and label totals stay fixed. The mix of conditions within each total changes.',
            'Prepared comparisons share training frames. Their scores do not measure independent generalization.',
            'Reserved Fixture checks have been inspected repeatedly. They are not an untouched final audit.']))
    print({name:dict(control=r['normal']['correct'],candidate=r['suppressed']['correct'],
        lost=r['lostCorrect'],gained=r['gainedCorrect']) for name,r in reports.items()},flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args();main()
