"""Add local differences while preserving the starting model's predictions."""
import argparse
from pathlib import Path
import time
import types
import numpy as np
import representation286 as previous

base=previous.base
torch=base.torch
OUT=base.ROOT/'reports/work/TRANSITION-287/DTM081'
REPRESENTATION='rgb-difference-plus-local-residual-v1'


def change_inputs(self,images):
    local=previous.change_inputs(self,images)[:,:3]
    return torch.cat(((images[:,3:]-images[:,:3]).abs(),images,local),1)


def extend(net):
    old=net.change[0]
    base.require(old.in_channels==9 and old.groups==1,'input_architecture')
    new=torch.nn.Conv2d(12,old.out_channels,old.kernel_size,old.stride,old.padding,
                        bias=old.bias is not None).to(old.weight)
    with torch.no_grad():
        new.weight.zero_();new.weight[:,:9].copy_(old.weight)
        if old.bias is not None:new.bias.copy_(old.bias)
    net.change[0]=new
    net.change_inputs=types.MethodType(change_inputs,net)
    return net


def load_candidate(path):
    record=torch.load(path,map_location='cpu',weights_only=True)
    base.require(record.get('representation')==REPRESENTATION,'representation_identity')
    net=extend(base.worker.make_model(torch,paired_context=True))
    net.load_state_dict(record['state'])
    return net.eval()


def run():
    base.require(not OUT.exists(),'output_collision')
    torch.set_num_threads(2)
    manifest,prior,replacement,rx,_,_,_,initializer,pins=base.prepare()
    x=np.load(base.PACKAGE/'training.npy',allow_pickle=False)
    y=np.load(base.PACKAGE/'labels.npy',allow_pickle=False)
    membership=base.read(base.PACKAGE/'membership.json')
    count=len(membership['selected'])
    for row,value in zip(replacement['rows'],rx):
        i=row['trainingIndex']
        base.require(y[i]==y[i+count]==row['changed'],'label_identity')
        x[i]=value;x[i+count]=base.reporting.reverse(value[None])[0]
    control=base.ROOT/'reports/work/CONFLICT-281'
    registration=base.read(control/'registration.json')
    old=base.read(base.ROOT/'reports/work/TRANSITION-266/DTM074/registration.json')
    weights=np.load(base.checked(old['weights']),allow_pickle=False)
    for name,values in [('training',x),('labels',y),('weights',weights)]:
        base.require(base.sha(values.tobytes())==registration[name+'SHA256'],name+'_identity')
    base.require(base.ref(initializer)==registration['initializer'],'initializer_identity')
    base.require(base.ref(Path(base.trainer.__file__))==registration['trainer'],'trainer_identity')
    original=base.load_model(initializer)
    net=extend(base.load_model(initializer))
    sanity=np.load(base.PACKAGE/'sanity.npy',allow_pickle=False)
    before=base.worker.score(original,sanity);after=base.worker.score(net,sanity)
    error=float(np.max(np.abs(before-after)))
    parity=error<=1e-6 and np.array_equal(base.decisions(before),base.decisions(after))
    OUT.mkdir(parents=True)
    config=registration['configuration']
    base.write(OUT/'registration.json',dict(version='representation287-v1',
        hypothesis='Added local differences may improve disturbances without removing useful broad focus evidence.',
        representation=REPRESENTATION,configuration=config,initializer=base.ref(initializer),
        trainingSHA256=registration['trainingSHA256'],labelsSHA256=registration['labelsSHA256'],
        weightsSHA256=registration['weightsSHA256'],control=base.ref(control/'DTM078/result.json'),
        runner=base.ref(Path(__file__)),residualImplementation=base.ref(Path(previous.__file__)),
        trainer=base.ref(Path(base.trainer.__file__)),pins=pins,initialParity=parity,
        maximumInitialScoreError=error,sanity=base.ref(base.PACKAGE/'sanity.npy'),
        device='cpu',threads=2,outputCapBytes=64*1024**2,wallTimeLimit=None,
        torchVersion=torch.__version__,selection='fixed-last',dataRolesChanged=False,
        acceptance='No individual regression against DTM067 or DTM078.',productionEligible=False))
    base.require(parity,'initial_score_parity')
    print('Initial parity passed:',error,flush=True)
    started=time.monotonic()
    def progress(row):
        base.write(OUT/f"epoch-{row['epoch']:04d}.json",row);print(row,flush=True)
    net,history=base.trainer.fit(net,torch.from_numpy(x),torch.from_numpy(y),config,progress,
                               torch.from_numpy(weights))
    torch.save(dict(state=net.state_dict(),representation=REPRESENTATION,
                    registration=base.ref(OUT/'registration.json')),OUT/'last.pt')
    restored=load_candidate(OUT/'last.pt')
    fit=base.metrics(restored,x,y)
    base.require(fit==base.metrics(net,x,y),'checkpoint_parity')
    base.write(OUT/'result.json',dict(fit=fit,history=history,model=base.ref(OUT/'last.pt'),
        representation=REPRESENTATION,seconds=time.monotonic()-started,checkpointParity=True,productionEligible=False))
    refs={'DTM067':original,'DTM078':base.load_model(base.checked(base.read(control/'DTM078/result.json')['model']))}
    evaluation=base.evaluate_full(restored,refs,manifest)
    base.write(OUT/'evaluation.json',evaluation)
    total=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    base.require(total<64*1024**2,'output_budget')
    base.write(OUT/'completion.json',dict(seconds=time.monotonic()-started,outputBytes=total,
        regressionPassed=evaluation['regressionPassed'],productionEligible=False))
    print('Complete:',evaluation['regressionPassed'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args();run()
