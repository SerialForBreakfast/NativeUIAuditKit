"""Compare the authored candidate with retained native and placeholder results."""
import math
import argparse
from pathlib import Path
import numpy as np
import authored319 as a
import report291


def report_folder(folder):
    folder=folder if folder.is_absolute() else a.b.ROOT/folder
    folder=folder.resolve()
    a.b.require(folder.is_relative_to(a.b.ROOT/'reports/work') and folder.is_dir(),'report_folder')
    return folder


def main(folder=a.OUT,loader=None,run_folder=None):
    folder=report_folder(folder)
    b=a.b;r=a.r;t=a.t;t.set_num_threads(2);run=folder/'run' if run_folder is None else report_folder(run_folder);out=folder/'report.json'
    if folder.name in ('FOCUS-325','FOCUS-326'):out=run/'report.json'
    b.require(run.is_relative_to(folder),'run_folder')
    b.require(not out.exists(),'output_collision')
    registration=b.read(run/'registration.json')
    if 'inputs' in registration:
        parent=b.read(b.checked(registration['inputs']))
        for key in ('corpus','review','oldCorpus','initializer','runner','trainer'):b.checked(parent[key])
    elif 'parent' in registration:
        parent=b.read(b.checked(registration['parent']))
        for key in ('corpus','model','runner','regions','sourceDetail'):b.checked(parent[key])
        b.checked(registration['trainer'])
    else:
        for key in ('corpus','initializer','runner','trainer','control'):b.checked(registration[key])
    candidate=b.read(run/'evaluation.json');membership=b.read(b.PACKAGE/'membership.json')
    references={
        'DTM085':b.ROOT/'reports/work/TRANSITION-292/DTM085/evaluation.json',
        'FOCUS313':r.OUT/'regions-2/evaluation.json'}
    if folder!=a.OUT:references['FOCUS319']=a.OUT/'run/evaluation.json'
    if folder.name in ('FOCUS-321','FOCUS-322','FOCUS-323','FOCUS-324'):references['FOCUS320']=b.ROOT/'reports/work/FOCUS-320/run/evaluation.json'
    if folder.name in ('FOCUS-322','FOCUS-323','FOCUS-324'):references['FOCUS321']=b.ROOT/'reports/work/FOCUS-321/run/evaluation.json'
    if folder.name in ('FOCUS-323','FOCUS-324'):references['FOCUS322']=b.ROOT/'reports/work/FOCUS-322/nonlinear/evaluation.json'
    if folder.name=='FOCUS-324':references['FOCUS323']=b.ROOT/'reports/work/FOCUS-323/run/evaluation.json'
    if folder.name=='FOCUS-325':
        for number in (320,321,323,324):references[f'FOCUS{number}']=b.ROOT/f'reports/work/FOCUS-{number}/run/evaluation.json'
        references['FOCUS322']=b.ROOT/'reports/work/FOCUS-322/nonlinear/evaluation.json'
        if run.name=='mixed':references['FOCUS325-average']=folder/'average/evaluation.json'
    comparisons={}
    if folder.name in ('FOCUS-326','FOCUS-327','FOCUS-328','FOCUS-329'):
        for name in ('average','mixed'):references[f'FOCUS325-{name}']=b.ROOT/f'reports/work/FOCUS-325/{name}/evaluation.json'
        for number in (320,321,323,324):references[f'FOCUS{number}']=b.ROOT/f'reports/work/FOCUS-{number}/run/evaluation.json'
        references['FOCUS322']=b.ROOT/'reports/work/FOCUS-322/nonlinear/evaluation.json'
    if folder.name in ('FOCUS-327','FOCUS-328','FOCUS-329'):
        references['FOCUS326-independent']=b.ROOT/'reports/work/FOCUS-326/independent/run/evaluation.json'
        references['FOCUS326-coupled']=b.ROOT/'reports/work/FOCUS-326/coupled/run/evaluation.json'
    if folder.name in ('FOCUS-328','FOCUS-329'):references['FOCUS327']=b.ROOT/'reports/work/FOCUS-327/run/evaluation.json'
    if folder.name=='FOCUS-329':references['FOCUS328']=b.ROOT/'reports/work/FOCUS-328/run/evaluation.json'
    for name,path in references.items():
        summary,cases=report291.summarize_comparison(b.read(path),candidate,membership)
        comparisons[name]=dict(summary=summary,cases=cases)
    net=(loader or r.load_candidate)(run/'last.pt');placeholder={}
    for name,path in [('arrival',r.OUT/'headless-diagnostic/inspection.json'),
                      ('movement',r.OUT/'headless-moves/comparison.json')]:
        doc=b.read(path);rows=doc['rows'];values=[]
        for row in rows:
            frames=[r.s.image(p['path'],p['sha256']) for p in row['images']]
            values.append(r.s.encoded(*frames,(192,128))[0])
        values=np.stack(values);details,_=r.prepare(values,rows,2)
        prob=b.worker.score(net,np.concatenate((values,details),1));labels=np.array([row['authoredChanged'] for row in rows])
        placeholder[name]=dict(input=b.ref(path),summary=b.trainer.w.summary(prob,labels),probabilities=prob.tolist(),
            control=doc['scores']['regions-2']['summary'],independentLayoutEvaluation=False)
    tiny,rows,pin=r.s.tiny_rows();detail,audit=r.prepare(tiny,rows,2)
    inputs=t.from_numpy(np.concatenate((tiny,detail),1))
    with t.inference_mode():
        whole=net.change.whole(r.s.c.model.change_inputs(None,inputs[:,:6])).flatten()
        total=net.change(inputs).flatten()
    logits=[dict(index=i,condition=row['condition'],whole=float(whole[i]),correction=float(total[i]-whole[i]),
                 total=float(total[i]),needed=math.log(.85/.15)-float(whole[i])) for i,row in enumerate(rows)]
    geometry={}
    for ref in b.read(a.OUT/'corpus.json')['renders']:
        doc=b.read(b.checked(ref));node=next(x for x in doc['nodes'] if x['isFocused'])
        key=f"{doc['layoutType']}:{node['id']}"
        geometry[key]=dict(body=node['unfocusedBounds'],effectBody=node['focusedBounds'],
            encodedSmallestBody=min(node['unfocusedBounds'][2:])*.1,
            labelAuthority='Authored renderer geometry. Not native measurements.')
    b.write(out,dict(comparisons=comparisons,placeholder=placeholder,tinyLogits=logits,
        geometry=geometry,correctionMeaning='Total score minus the original whole-frame score. This includes any change to its weight.',
        candidate=b.ref(run/'last.pt'),input=pin,productionEligible=False,
        limitation='Previously inspected development checks. No new final audit or threshold selection.'))
    for name,value in comparisons.items():
        print(name,{k:dict(lost=v['lostCorrect'],gained=v['gainedCorrect']) for k,v in value['summary'].items()})
    print('placeholder',{k:v['summary'] for k,v in placeholder.items()})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--folder',type=Path,default=a.OUT)
    main(parser.parse_args().folder)
