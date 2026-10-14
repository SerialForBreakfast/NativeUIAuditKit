"""Compare completed candidates with retained successes and matched changes."""
import argparse
from pathlib import Path
import time
import numpy as np
import additive341 as a
import report291
from input_use289 import compare


def grouped_comparison(rows, baseline, candidate):
    labels=np.array([row['changed'] for row in rows])
    compare(baseline,candidate,labels)
    groups=sorted({row['group'] for row in rows})
    return {group:compare(np.asarray(baseline)[mask],np.asarray(candidate)[mask],labels[mask])
            for group in groups for mask in [np.array([row['group']==group for row in rows])]}


def score_rows(net,rows,extra,timing=None):
    result=[]
    for start in range(0,len(rows),8):
        prepared=time.monotonic()
        subset=rows[start:start+8]
        x=np.stack([a.r.s.encoded(*[a.r.s.image(v['path'],v['sha256']) for v in row['images']],(192,128))[0] for row in subset])
        detail,_=a.r.prepare(x,subset,2)
        parts=[x,detail]
        if extra:parts.append(a.added_details(x,subset))
        inputs=np.concatenate(parts,1)
        ready=time.monotonic()
        result.extend(a.b.worker.score(net,inputs).tolist())
        if timing is not None:
            timing['preprocessingSeconds']+=ready-prepared
            timing['inferenceSeconds']+=time.monotonic()-ready
            timing['examples']+=len(subset)
    return np.array(result)


def main(arm,job_id=None,destination=None):
    a.t.set_num_threads(2);started=time.monotonic()
    job=a.b.ROOT/'reports/work/research-queue/jobs'/(job_id or 'focus341-'+arm)/'attempts/1'
    a.b.require(a.b.read(job/'result.json')['status']=='complete','incomplete_attempt')
    root=job/'out';folder=root/'run'/arm
    destination=destination or a.OUT/(arm+'-report.json')
    a.b.require(not destination.exists(),'output_collision')
    net=a.load(folder/'last.pt');membership=a.b.read(a.b.PACKAGE/'membership.json')
    result=a.b.read(folder/'evaluation.json');comparisons={}
    for name,path in [('FOCUS319','FOCUS-319'),('FOCUS327','FOCUS-327'),('FOCUS329','FOCUS-329')]:
        summary,cases=report291.summarize_comparison(a.b.read(a.b.ROOT/f'reports/work/{path}/run/evaluation.json'),result,membership)
        comparisons[name]=dict(summary=summary,cases=cases)
    negatives=a.b.read(a.OUT/'negatives.json')['rows']
    source=a.b.read(a.b.ROOT/'reports/work/FOCUS-326/corpus.json')['rows']['independent']
    byid={row['id']:row for row in source};movement=[byid[row['matchedMovementID']] for row in negatives]
    old=a.b.read(a.e.OUT/'run/training.json')['probabilities'][240:]
    oldmap={row['id']:p for row,p in zip(source,old)}
    timing=dict(preprocessingSeconds=0.,inferenceSeconds=0.,examples=0,
                runtime='PyTorch CPU, 2 threads, batch up to 8. Training may run concurrently.')
    rows=negatives+movement;prob=score_rows(net,rows,True,timing)
    baseline=np.array([r['probability'] for r in a.b.read(a.OUT/'negative-validation.json')['rows']]+
                      [oldmap[row['id']] for row in movement])
    labels=np.array([row['changed'] for row in rows])
    matched=compare(baseline,prob,labels)
    bycondition={name:compare(baseline[index],prob[index],labels[index]) for name,index in
                 [('content',slice(0,len(negatives))),('movement',slice(len(negatives),None))]}
    oldrows=a.b.read(a.b.ROOT/'reports/work/FOCUS-319/corpus.json')['rows']+source
    oldprob=np.array(a.b.read(a.e.OUT/'run/training.json')['probabilities'])
    authored=score_rows(net,oldrows,True,timing)
    prior=compare(oldprob,authored,np.array([row['changed'] for row in oldrows]))
    placeholders={}
    for name,path in [('arrival',a.r.OUT/'headless-diagnostic/inspection.json'),('movement',a.r.OUT/'headless-moves/comparison.json')]:
        doc=a.b.read(path);pr=score_rows(net,doc['rows'],True)
        control=score_rows(a.e.load_candidate(a.e.OUT/'run/last.pt'),doc['rows'],False)
        placeholders[name]=compare(control,pr,np.array([row['authoredChanged'] for row in doc['rows']]))
    # The retained strength reports contain counts, not per-row predictions.
    # Report count changes without inventing lost-case identities.
    oldstrength=a.b.read(a.e.OUT/'run/evaluation.json')['strengths']
    strengths=[]
    for control,candidate in zip(oldstrength,result['strengths']):
        a.b.require(all(control[k]==candidate[k] for k in ('condition','strength','order')),'strength_alignment')
        strengths.append(dict(condition=control['condition'],strength=control['strength'],order=control['order'],
            control=control['summary'],candidate=candidate['summary'],lostCaseIdentity='unavailable from cached counts'))
    target_improves=bycondition['content']['gainedCorrect']>bycondition['content']['lostCorrect']
    losses=sum(v['lostCorrect'] for v in comparisons['FOCUS329']['summary'].values())+prior['lostCorrect']
    losses+=sum(v['lostCorrect'] for v in placeholders.values())
    a.b.write(destination,dict(model=a.b.ref(folder/'last.pt'),comparisons=comparisons,
        reporter=a.b.ref(Path(__file__)),inputs=[a.b.ref(p) for p in
            (a.OUT/'negatives.json',a.OUT/'negative-validation.json',a.b.PACKAGE/'membership.json',
             root/'registration.json',root/'views.json',folder/'evaluation.json')],
        matched=matched,byCondition=bycondition,matchedProbabilities=prob.tolist(),matchedLabels=labels.tolist(),
        matchedByGroup=grouped_comparison(rows,baseline,prob),
        matchedIDs=[row['id'] for row in rows],authored=prior,authoredProbabilities=authored.tolist(),
        authoredByGroup=grouped_comparison(oldrows,oldprob,authored),
        coverage=dict(archetype='Custom authored controls; no complete 7-archetype qualification.',
                      theme='No complete 3-theme qualification.',
                      negativeRegion='Central background panel only.'),
        parameters=dict(total=sum(v.numel() for v in net.parameters()),
                        added=sum(v.numel() for v in net.change.detail.parameters())+
                              sum(v.numel() for v in net.change.correction.parameters())),
        scoringTiming=timing,
        placeholders=placeholders,strengths=strengths,
        targetImproves=target_improves,knownLostPreviousSuccesses=losses,
        candidateAccepted=False,reason='No promotion in this comparison. Review every regression and native limitation.',
        seconds=time.monotonic()-started,groups=len({row['group'] for row in rows}),
        limitation='Matched cases are training examples from 3 related artwork families. They do not prove native generalization.'))
    print(arm,bycondition,'previous authored',prior,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('arm',choices=['added-detail','added-detail-and-content'])
    main(parser.parse_args().arm)
