"""Independent180B consumer: complete score audit and bounded CPU sample replay."""
import argparse
import gzip
import json
import time
from pathlib import Path
import numpy as np
import replay_envelope166 as a
v,h=a.v,a.h
OLD=a.BASE/'extracted/reports/work/ENVELOPE166/attempt01'
REQUEST=h.ROOT/'reports/coordination/worker180-backlog.yaml'


def placed(torch,pair,rect,index,placement):
    h.require(placement in (0,1),'placement')
    swapped=torch.cat((pair[3:],pair[:3]))
    before=a.transform(torch,swapped,rect,index)[3:]
    out=torch.cat((before,pair[3:]))
    return out if placement==0 else a.transform(torch,out,rect,index)


def scores(chunks,count=a.COUNT):
    vectors=np.empty((3,2,count),np.float32);expected=(0,0,0)
    for row in chunks:
        m,p,start=expected
        h.require(all(type(row[k]) is int for k in ('model','placement','start')) and
            m<3 and (row['model'],row['placement'],row['start'])==expected,'chunk_order')
        h.require(isinstance(row['probabilities'],list) and all(type(x) in (int,float) for x in row['probabilities']),'numeric_scores')
        values=np.asarray(row['probabilities'],np.float32)
        h.require(values.shape==(min(1024,count-start),) and np.isfinite(values).all()
            and ((values>=0)&(values<=1)).all(),'chunk_values')
        end=start+len(values);vectors[m,p,start:end]=values
        expected=(m,p,end) if end<count else ((m,p+1,0) if p==0 else (m+1,0,0))
    h.require(expected==(3,0,0),'incomplete_scores');return vectors


def local(path):
    value=Path(path).resolve();h.require(value.is_relative_to(h.ROOT) and value!=h.ROOT,'outside_project');return value


def run(root,output):
    start=time.monotonic();root=local(root);output=local(output)
    h.require(not output.exists(),'output_collision')
    def check(ref):
        path=v.w.t.path_under(root,ref.get('file',ref.get('path')));v.w.t.verified(path,ref);return path
    inventory=h.read(root/'inventory.json',2*1024**2)
    h.require(isinstance(inventory,list) and len(inventory)<=5000,'inventory_bound')
    for ref in inventory:check(ref)
    work=root/'reports/work/WORKER180/b01';pins=h.read(work/'pins.json',4*1024**2);state=h.read(work/'cursor.json',4*1024**2)
    h.require(state['state']=='completed' and state['cursor']==[3,0,0]
        and state['pinsSHA256']==h.sha(work/'pins.json') and state['scores']==6*a.COUNT and state['swappedCount']==858,'terminal_state')
    cfg=pins['config'];h.require(cfg['placements']==['before','both'] and cfg['count']==a.COUNT and cfg['chunk']==1024 and cfg['batch']==32 and cfg['tolerance']==1e-4,'configuration')
    refs={r['file']:r for r in pins['refs']}
    h.require(refs['reports/work/WORKER180/request.yaml']['sha256']==h.sha(REQUEST),'request_pin')
    old=h.read(OLD/'pins.json',2*1024**2)
    for name in ('pins.json','cursor.json'):
        h.require(refs['reports/work/ENVELOPE166/attempt01/'+name]['sha256']==h.sha(OLD/name),'old_pin')
    for name,ref in old['sources'].items():h.require(h.sha(h.ROOT/'scripts'/name)==ref['sha256'],'source_pin')
    vectors=scores(h.read(check(ref)) for ref in state['chunks'])
    torch=v.n.d.torch_runtime();torch.set_num_threads(2)
    export=v.w.BASE.parent/'export01/payload';maskroot=v.BASE.parent/'export01/payload'
    for directory in (export,maskroot):
        for ref in v.w.t.document(directory/'manifest.json')['files']:v.w.t.verified(directory/ref['path'],ref)
    data=torch.load(export/'training.pt',weights_only=True,map_location='cpu');mask=torch.load(maskroot/'masks.pt',weights_only=True,map_location='cpu')['contentMask']
    _,_,groups=v.derived(torch,data['images'],data['labels'],mask);images=torch.cat([data['images'],groups['identity']])
    h.require(v.digest(images)==pins['imagesSHA256']==old['imagesSHA256'],'input_pin')
    rects=old['rects'];indices=a.sample_indices();selected=set(indices);samples=[{},{}];seen=[set(),set()]
    metadata=check(refs['reports/work/WORKER180/b01/variants.jsonl.gz'])
    with gzip.open(metadata,'rt') as stream:
        count=0
        while True:
            line=stream.readline(10001)
            if not line:break
            h.require(count<a.COUNT and len(line)<=10000,'metadata_bound');row=json.loads(line);c,y,x,z,t=a.spec(count)
            h.require(all(type(row[k]) is int for k in ('index','case','gy','gx','size','transform')) and
                [row[k] for k in ('index','case','gy','gx','size','transform')]==[count,c,y,x,z,t]
                and len(row['placements'])==2,'metadata_identity')
            for placement in range(2):
                digest=row['placements'][placement]['tensorSHA256'];seen[placement].add(digest)
                if count in selected:
                    value=placed(torch,images[c],rects[c],count,placement);h.require(v.digest(value)==digest,'sample_tensor_hash');samples[placement][count]=value
            count+=1
    h.require(count==a.COUNT and [len(s) for s in seen]==pins['uniqueTensors'],'metadata_count')
    labels=np.repeat([c['label'] for c in old['cases']],768);results={}
    for mi,name in enumerate(('DTM050','DTM051','DTM052')):
        cp=v.BASE/'extracted'/name/'last.pt';h.require(h.sha(cp)==old['checkpoints'][name]['sha256'],'checkpoint_pin')
        net=v.checked(torch,v.n.make_model(torch,paired_context=True),torch.load(cp,weights_only=True,map_location='cpu'),name);result={}
        for pi in range(2):
            actual=v.n.score(net,torch.stack([samples[pi][i] for i in indices]));expected=vectors[mi,pi,indices]
            delta=float(np.max(np.abs(actual-expected)));h.require(delta<=1e-4 and np.array_equal(a.decisions(actual),a.decisions(expected)),'sample_replay')
            cats=a.decisions(vectors[mi,pi]);result[['before','both'][pi]]=dict(maximumProbabilityDifference=delta,sampleScores=len(indices),unchanged=int((cats==0).sum()),changed=int((cats==1).sum()),abstentions=int((cats==-1).sum()),originalLabelAgreement=int((cats==labels).sum()))
        swapped=v.n.score(net,torch.cat([images[:,3:],images[:,:3]],dim=1));expected=np.asarray(state['swapped'][name],np.float32)
        h.require(expected.shape==(286,) and np.isfinite(expected).all() and ((expected>=0)&(expected<=1)).all(),'swapped_values')
        delta=float(np.max(np.abs(swapped-expected)));h.require(delta<=1e-4 and np.array_equal(a.decisions(swapped),a.decisions(expected)),'swapped_replay')
        result['swapped']=dict(scores=286,maximumProbabilityDifference=delta);results[name]=result
        print(name,result,flush=True)
    h.write(output,dict(results=results,allScores=6*a.COUNT,source=h.ref(__file__),inventory=h.ref(root/'inventory.json'),sampleIndices=indices,seconds=time.monotonic()-start,productionEligible=False,
        limitation='Counterfactual original-label agreement and independent numerical replay; not native accuracy, training labels or promotion.'),sealed=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();run(args.root,args.output)
