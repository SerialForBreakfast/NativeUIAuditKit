"""Measure two image-selected windows without changing model decisions."""
from pathlib import Path
import numpy as np
import effect312 as e

s=e.s;b=e.b


def windows(value):
    b.require(value.shape==(6,128,192) and np.isfinite(value).all(),'proposal_input')
    tensor=s.torch.from_numpy(value[None]);first=s.boxes(tensor)[0]
    residual=s.c.model.change_inputs(None,tensor)[:,9:].mean(1,keepdim=True)
    energy=s.torch.nn.functional.avg_pool2d(residual,5,stride=1,padding=2)[0,0]
    x,y=first
    energy[max(0,y-16):min(128,y+48),max(0,x-16):min(192,x+48)]=-1
    peak=int(energy.flatten().argmax())
    second=(min(160,max(0,peak%192-16)),min(96,max(0,peak//192-16)))
    return [first,second]


def measure(value):
    delta=np.abs(value[:3]-value[3:]).mean(0);total=float(delta.sum())
    if total==0:return dict(windows=[],energyFraction=None,identical=True)
    selected=windows(value);mask=np.zeros(delta.shape,bool)
    for x,y in selected:mask[y:y+32,x:x+32]=True
    return dict(windows=selected,energyFraction=min(1.,float(delta[mask].sum()/total)),identical=False)


def main():
    s.torch.set_num_threads(2);out=e.OUT/'proposal-diagnostic.json'
    b.require(not out.exists(),'output_collision')
    values,rows,pin=s.tiny_rows()
    records=[dict(index=i,condition=row['condition'],result=measure(values[i])) for i,row in enumerate(rows)]
    b.write(out,dict(runner=b.ref(Path(__file__)),input=pin,records=records,
        limitation='Pixel coverage only. No model decision changes, training, or label-based window selection.'))
    print('Two-window diagnostic complete.',flush=True)


if __name__=='__main__':main()
