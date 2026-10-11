"""Measure the added correction's effect without saving changed weights."""
from pathlib import Path
import numpy as np
import retain312 as run


def main():
    b=run.b;s=run.s;out=run.OUT/'correction-diagnostic.json'
    b.require(not out.exists(),'output_collision');s.torch.set_num_threads(2)
    checkpoint=run.OUT/'last.pt';pin=b.ref(checkpoint);net=s.load_candidate(checkpoint)
    original=b.read(run.OUT/'evaluation.json');results=[]
    with s.torch.no_grad():
        net.change.correction.weight.zero_();net.change.correction.bias.zero_()
    for name in ('left8.npy','center8.npy','global8.npy'):
        values=np.load(b.PACKAGE/name,allow_pickle=False);labels=np.zeros(len(values))
        scores=b.worker.score(net,values)
        results.append(dict(condition=name,input=b.ref(b.PACKAGE/name),
            withCorrection=original['conditions'][name]['summary'],
            withoutCorrection=b.trainer.w.summary(scores,labels),probabilities=scores.tolist()))
    b.checked(pin)
    b.write(out,dict(runner=b.ref(Path(__file__)),model=pin,results=results,
        limitation='Inference-only ablation. The whole-frame branch retains its adapted weights. No model is saved or selected.'))
    for row in results:print({k:v for k,v in row.items() if k not in ('probabilities','input')},flush=True)


if __name__=='__main__':main()
