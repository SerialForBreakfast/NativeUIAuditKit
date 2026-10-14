"""Audit retained training coverage and rotate negative examples without more updates."""
from collections import Counter
from pathlib import Path
import numpy as np
import research_queue as q

OUT=q.ROOT/'reports/work/FOCUS-342'


def schedule(labels,rows,indices,negative_count,epochs):
    q.require(epochs>0 and negative_count>0,'schedule_support')
    labels=np.asarray(labels);indices=np.asarray(indices)
    q.require(indices.shape==labels.shape and set(np.unique(labels))=={0,1},'schedule_labels')
    q.require(all(v['role']=='train' for v in rows),'training_roles')
    q.require(np.array_equal(np.array([v['changed'] for v in rows])[indices],labels),'schedule_alignment')
    positions=np.flatnonzero(labels==0);newpos=positions[::2];oldpos=positions[1::2]
    oldpool=np.array([i for i,row in enumerate(rows) if row['changed']==0])
    q.require(len(oldpool)>0 and len(oldpos)>0,'schedule_support')
    result=np.tile(indices,(epochs,1))
    for epoch in range(epochs):
        result[epoch,oldpos]=oldpool[(np.arange(len(oldpos))+epoch*len(oldpos))%len(oldpool)]
        result[epoch,newpos]=len(rows)+(np.arange(len(newpos))+epoch*len(newpos))%negative_count
    return result


def audit():
    p=q.ROOT/'reports/work';cache=np.load(p/'FOCUS-326/independent.npz',allow_pickle=False)
    rows=q.load(p/'FOCUS-319/corpus.json')['rows']+q.load(p/'FOCUS-326/corpus.json')['rows']['independent']
    y,indices=cache['labels'],cache['indices'];mixed=indices.copy()
    positions=np.flatnonzero(y==0)[::2];mixed[positions]=len(rows)+np.arange(len(positions))%192
    balanced=schedule(y,rows,indices,192,30)
    def counts(values):
        c=Counter(int(v) for v in values.flatten() if v<len(rows))
        return dict(uniqueOld=len(c),uniqueOldNegative=sum(rows[k]['changed']==0 for k in c),
                    missingOld=len(rows)-len(c),conditions=dict(Counter(rows[k]['condition'] for k in c)))
    baseline=np.array(q.load(p/'FOCUS-329/run/training.json')['probabilities'])
    candidate=np.array(q.load(p/'FOCUS-341/added-detail-and-content-report.json')['authoredProbabilities'])
    labels=np.array([r['changed'] for r in rows]);signed=(2*labels-1)
    def margin(prob):return signed*np.log(np.clip(prob,1e-7,1-1e-7)/np.clip(1-prob,1e-7,1-1e-7))
    previous=margin(baseline)>=np.log(.85/.15);lost=previous&(margin(candidate)<np.log(.85/.15))
    removed=set(indices)-set(mixed)
    cases=[dict(id=row.get('id','authored-index-'+str(i)),group=row['group'],role=row['role'],condition=row['condition'],
                removedFromAuxiliary=i in removed,oldMargin=float(margin(baseline)[i]),
                newMargin=float(margin(candidate)[i]),lostPrevious=bool(lost[i])) for i,row in enumerate(rows)]
    q.save(OUT/'audit.json',dict(original=counts(indices),fixedReplacement=counts(mixed),rotating=counts(balanced),
        trainingViews=len(y),negativeViews=len(np.flatnonzero(y==0)),newExamplesPerEpoch=len(positions),
        oldNegativeExamplesPerEpoch=len(np.flatnonzero(y==0))-len(positions),
        removedConditions=dict(Counter(rows[i]['condition'] for i in removed)),
        lostRemoved=int(sum(lost[i] for i in removed)),lostRetained=int(sum(lost[i] for i in set(indices)-removed)),
        rotatingScheduleSHA256=q.text_digest(balanced.tolist()),rows=cases,
        balancedJustified=bool(removed),preservationJustified=bool(lost.any()),
        inference='Coverage loss and margin loss justify controlled tests. They do not prove the cause.',
        inputs=[dict(path=str(f.relative_to(q.ROOT)),sha256=q.digest(f)) for f in
                [p/'FOCUS-326/independent.npz',p/'FOCUS-329/run/training.json',
                 p/'FOCUS-341/added-detail-and-content-report.json']]))


def run():
    import additive341 as a
    a.OUT=OUT
    a.train()


if __name__=='__main__':audit()
