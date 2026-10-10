"""Run the fixed matched comparison of content-group gradient projection."""
import argparse
import time
from pathlib import Path
import transition270 as base

np=base.np
torch=base.torch
OUT=base.ROOT/'reports/work/CONFLICT-281'


def run():
    torch.set_num_threads(2)
    base.require(not (OUT/'registration.json').exists(),'existing_run')
    manifest,prior,replacement,rx,_,_,_,initializer,pins=base.prepare()
    x=np.load(base.PACKAGE/'training.npy',allow_pickle=False)
    y=np.load(base.PACKAGE/'labels.npy',allow_pickle=False)
    membership=base.read(base.PACKAGE/'membership.json')
    replay=len(membership['replayLabels']); count=len(membership['selected'])
    base.require(len(x)==replay+2*count,'membership_size')
    for row,value in zip(replacement['rows'],rx):
        i=row['trainingIndex']
        base.require(y[i]==y[i+count]==row['changed'],'replacement_label')
        x[i]=value; x[i+count]=base.reporting.reverse(value[None])[0]
    base.require(base.sha(x.tobytes())==prior['fullTrainingSHA256'],'training_identity')
    old=base.read(base.ROOT/'reports/work/TRANSITION-266/DTM074/registration.json')
    weights=np.load(base.checked(old['weights']),allow_pickle=False)
    base.require(base.sha(y.tobytes())==old['labelsSHA256'],'label_identity')
    base.require(base.sha(weights.tobytes())=='a514ae513f66953e07e91694732337dab391e5f0e1657857c2bba8f596a81ce7','weight_identity')
    groups=np.full(len(x),-1,np.int64)
    for position,index in enumerate(membership['selected']):
        row=membership['rows'][index]
        base.require(row['role']=='train','training_role')
        if 'content_contrast' in row['conditions']:
            groups[replay+position]=groups[replay+count+position]=int(row['changed'])
    base.require([(groups==i).sum() for i in (0,1)]==[138,420],'group_counts')
    config=dict(base.CONFIG,epochs=120)
    registration=dict(configuration=config,initializer=base.ref(initializer),
        trainingSHA256=base.sha(x.tobytes()),labelsSHA256=base.sha(y.tobytes()),
        weightsSHA256=base.sha(weights.tobytes()),groupsSHA256=base.sha(groups.tobytes()),
        runner=base.ref(Path(__file__)),trainer=base.ref(Path(base.trainer.__file__)),
        pins=pins,updatesPerRun=12480,rows=len(x),outputCapBytes=64*1024**2,
        method='Symmetric projection of original content-group gradients; weighted sums divided by batch size.',
        selection='fixed-last',independentEvaluation=False)
    base.write(OUT/'registration.json',registration)
    refs={'DTM067':base.load_model(initializer),'DTM077':base.load_model(
        base.checked(base.read(base.ROOT/'reports/work/TRANSITION-270/DTM077/result.json')['model']))}
    tensor=torch.from_numpy(x); labels=torch.from_numpy(y); weight=torch.from_numpy(weights)
    results={}
    for name,group_tensor in [('DTM078',None),('DTM079',torch.from_numpy(groups))]:
        target=OUT/name; target.mkdir()
        net=base.load_model(initializer); started=time.monotonic()
        def progress(row):
            base.write(target/f"epoch-{row['epoch']:04d}.json",row)
            print(name,row,flush=True)
        net,history=base.trainer.fit(net,tensor,labels,config,progress,weight,group_tensor)
        torch.save(dict(state=net.state_dict(),registration=base.ref(OUT/'registration.json')),target/'last.pt')
        restored=base.load_model(target/'last.pt')
        fit=base.metrics(net,x,y)
        base.require(fit==base.metrics(restored,x,y),'checkpoint_parity')
        fit['conditions']={str(g):base.trainer.w.summary(np.array(fit['probabilities'])[groups==g],y[groups==g])
                           for g in (-1,0,1)}
        result=dict(fit=fit,history=history,model=base.ref(target/'last.pt'),seconds=time.monotonic()-started,
                    checkpointParity=True,geometryFrozen=True)
        if name=='DTM078':
            result['controlParameterParity']=all(torch.equal(v,refs['DTM077'].state_dict()[k]) for k,v in net.state_dict().items())
            base.require(result['controlParameterParity'],'control_reproduction')
        base.write(target/'result.json',result)
        evaluation=base.evaluate_full(restored,refs,manifest)
        base.write(target/'evaluation.json',evaluation)
        results[name]=dict(model=result['model'],fit=fit['summary'],regressionPassed=evaluation['regressionPassed'])
        refs[name]=restored
        print(name,results[name],flush=True)
    total=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    base.require(total<64*1024**2,'output_budget')
    base.write(OUT/'completion.json',dict(results=results,outputBytes=total,productionEligible=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true',required=True)
    parser.parse_args(); run()
