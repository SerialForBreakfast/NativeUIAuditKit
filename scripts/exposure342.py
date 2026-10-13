"""Measure executed weighted exposure without changing either fixed comparison."""
from collections import defaultdict
import numpy as np
import balance342 as b
import research_queue as q


def main():
    p=q.ROOT/'reports/work';z=np.load(p/'FOCUS-326/independent.npz',allow_pickle=False)
    rows=q.load(p/'FOCUS-319/corpus.json')['rows']+q.load(p/'FOCUS-326/corpus.json')['rows']['independent']
    negatives=q.load(p/'FOCUS-341/negatives.json')['rows'];allrows=rows+negatives
    y,i,w=z['labels'],z['indices'],z['weights'];fixed=i.copy();positions=np.flatnonzero(y==0)[::2]
    fixed[positions]=len(rows)+np.arange(len(positions))%len(negatives)
    schedules={'original':np.tile(i,(30,1)),'fixedReplacement':np.tile(fixed,(30,1)),
               'rotating':b.schedule(y,rows,i,len(negatives),30)}
    output={}
    for name,schedule in schedules.items():
        groups=defaultdict(lambda:dict(updates=0,weight=0.,members=set()))
        for epoch in schedule:
            for index,weight in zip(epoch,w):
                row=allrows[index];key=row['group']+'/'+row['condition'];v=groups[key]
                v['updates']+=1;v['weight']+=float(weight);v['members'].add(int(index))
        output[name]={k:dict(updates=v['updates'],weight=v['weight'],uniqueExamples=len(v['members'])) for k,v in groups.items()}
    q.save(p/'FOCUS-342/weighted-exposure.json',dict(epochs=30,auxiliaryWeight=.25,
        minimumPrimaryWeight=float(w.min()),maximumPrimaryWeight=float(w.max()),
        schedules=output,totalUpdatesPerSchedule=30*len(y),
        meaning='Weight sums precede the common auxiliary coefficient and batch mean. They measure exposure, not causal importance.',
        noTrainingChange=True,inputs=[dict(path=str(f.relative_to(q.ROOT)),sha256=q.digest(f)) for f in
            [p/'FOCUS-326/independent.npz',p/'FOCUS-341/negatives.json',q.ROOT/'scripts/balance342.py']]))


if __name__=='__main__':main()
