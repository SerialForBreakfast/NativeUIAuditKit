"""Disable only added edge channels after the fixed comparison."""
import time
from pathlib import Path
import numpy as np
import edge329 as e

b=e.b;r=e.r;t=e.t;OUT=e.OUT


def main():
    b.require(not (OUT/'edge-ablation.json').exists(),'output_collision');t.set_num_threads(2);start=time.monotonic()
    net=e.load_candidate(OUT/'run/last.pt');reference=b.read(OUT/'run/evaluation.json')
    member=b.read(b.PACKAGE/'membership.json');results={}
    for name in ('native.npy','reverse_replay.npy','center8.npy'):
        if name=='reverse_replay.npy':
            x=b.reporting.reverse(np.load(b.PACKAGE/'replay.npy',allow_pickle=False))
        else:x=np.load(b.PACKAGE/name,allow_pickle=False)
        if name=='native.npy':
            detail,_=r.prepare(x,member['rows'],2);x=np.concatenate((x,detail),1);del detail
            labels=np.array([v['changed'] for v in member['rows']])
        elif name=='reverse_replay.npy':labels=np.array(member['replayLabels'])
        else:labels=np.zeros(len(x))
        full=np.array(reference['conditions'][name]['probabilities'])
        check=b.worker.score(net,x[:8]);b.require(np.max(np.abs(check-full[:8]))<=1e-6,'ablation_input_parity')
        original=e.gradient_channels
        try:
            e.gradient_channels=lambda images:t.zeros_like(images)
            without=b.worker.score(net,x)
        finally:e.gradient_channels=original
        full_dec=np.where(full>=.85,1,np.where(full<=.15,0,-1))
        off_dec=np.where(without>=.85,1,np.where(without<=.15,0,-1))
        results[name]=dict(normal=b.trainer.w.summary(full,labels),withoutEdges=b.trainer.w.summary(without,labels),
            decisionChanges=int((full_dec!=off_dec).sum()),maximumScoreChange=float(np.abs(full-without).max()),
            cases=[dict(index=i,changed=int(labels[i]),normal=float(full[i]),withoutEdges=float(without[i]))
                   for i in range(len(x)) if full_dec[i]!=off_dec[i]],probabilitiesWithoutEdges=without.tolist())
        del x
    b.write(OUT/'edge-ablation.json',dict(model=b.ref(OUT/'run/last.pt'),source=b.ref(Path(__file__)),
        results=results,seconds=time.monotonic()-start,trainingStarted=False,
        limitation='Post-run diagnosis. Removing learned inputs does not reproduce the separately trained control. No model or threshold selection.'))
    print({k:{f:v[f] for f in ('normal','withoutEdges','decisionChanges')} for k,v in results.items()})


if __name__=='__main__':main()
