"""Test local differences with unchanged RGB context and training membership."""
from pathlib import Path
import argparse
import time
import types
import numpy as np
import transition270 as base

OUT=base.ROOT/'reports/work/SIGNAL-286/DTM080'


def change_inputs(self,images):
    delta=images[:,3:]-images[:,:3]
    functional=base.torch.nn.functional
    broad=functional.avg_pool2d(functional.pad(delta,(4,4,4,4),mode='reflect'),9,stride=1)
    local=(delta-broad).abs().clamp(0,1)
    return base.torch.cat((local,images),dim=1)


def treatment(net):
    net.change_inputs=types.MethodType(change_inputs,net)
    return net


def run():
    base.require(not OUT.exists(),'output_collision')
    base.torch.set_num_threads(2)
    manifest,prior,replacement,rx,_,_,_,initializer,pins=base.prepare()
    x=np.load(base.PACKAGE/'training.npy',allow_pickle=False)
    y=np.load(base.PACKAGE/'labels.npy',allow_pickle=False)
    membership=base.read(base.PACKAGE/'membership.json')
    count=len(membership['selected'])
    for row,value in zip(replacement['rows'],rx):
        index=row['trainingIndex']
        base.require(y[index]==y[index+count]==row['changed'],'label_identity')
        x[index]=value;x[index+count]=base.reporting.reverse(value[None])[0]
    control_dir=base.ROOT/'reports/work/CONFLICT-281'
    control_reg=base.read(control_dir/'registration.json')
    reg=base.read(base.ROOT/'reports/work/TRANSITION-266/DTM074/registration.json')
    weights=np.load(base.checked(reg['weights']),allow_pickle=False)
    base.require(base.sha(x.tobytes())==control_reg['trainingSHA256'],'training_identity')
    base.require(base.sha(y.tobytes())==control_reg['labelsSHA256'],'labels_identity')
    base.require(base.sha(weights.tobytes())==control_reg['weightsSHA256'],'weight_identity')
    base.require(base.ref(initializer)==control_reg['initializer'],'initializer_identity')
    config=control_reg['configuration']
    OUT.mkdir()
    registration=dict(version='representation286-v1',hypothesis='Broad content changes dominate image differences. Local residuals may preserve useful focus edges.',
        method='Replace absolute RGB difference with absolute residual after a reflected 9 by 9 mean. Preserve both RGB frames.',
        configuration=config,initializer=base.ref(initializer),trainingSHA256=control_reg['trainingSHA256'],
        labelsSHA256=control_reg['labelsSHA256'],weightsSHA256=control_reg['weightsSHA256'],
        runner=base.ref(Path(__file__)),trainer=base.ref(Path(base.trainer.__file__)),
        control=base.ref(control_dir/'DTM078/result.json'),diagnosis=base.ref(OUT.parent/'result.json'),
        outputCapBytes=64*1024**2,device='cpu',threads=2,wallTimeLimit=None,
        selection='fixed-last',geometryFrozen=True,dataRolesChanged=False,
        acceptance='No individual regression against DTM078 and DTM067. Report every existing condition, order, and strength.',
        exportAuthorized=False,productionEligible=False)
    base.write(OUT/'registration.json',registration)
    started=time.monotonic()
    net=treatment(base.load_model(initializer))
    def progress(row):
        base.write(OUT/f"epoch-{row['epoch']:04d}.json",row)
        print(row,flush=True)
    net,history=base.trainer.fit(net,base.torch.from_numpy(x),base.torch.from_numpy(y),config,progress,
                               base.torch.from_numpy(weights))
    base.torch.save(dict(state=net.state_dict(),representation='local-residual-9-v1',
                        registration=base.ref(OUT/'registration.json')),OUT/'last.pt')
    restored=treatment(base.load_model(OUT/'last.pt'))
    fit=base.metrics(restored,x,y)
    base.require(fit==base.metrics(net,x,y),'checkpoint_parity')
    base.write(OUT/'result.json',dict(model=base.ref(OUT/'last.pt'),fit=fit,history=history,
                                    seconds=time.monotonic()-started,checkpointParity=True,productionEligible=False))
    references={'DTM067':base.load_model(initializer),
                'DTM078':base.load_model(base.checked(base.read(control_dir/'DTM078/result.json')['model']))}
    evaluation=base.evaluate_full(restored,references,manifest)
    base.write(OUT/'evaluation.json',evaluation)
    total=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    base.require(total<registration['outputCapBytes'],'output_budget')
    base.write(OUT/'completion.json',dict(seconds=time.monotonic()-started,outputBytes=total,
                                        regressionPassed=evaluation['regressionPassed'],productionEligible=False))
    print('Complete',evaluation['regressionPassed'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args();run()
