"""Compare row and connected-group weights using the existing adaptation trainer."""
import argparse
from collections import Counter
import time
import numpy as np
import transition245 as t

OUT=t.h.ROOT/'reports/work/TRANSITION-248/artifacts'


def partition(rows):
    train=[i for i,r in enumerate(rows) if r['role']=='train']
    parent={rows[i]['group']:rows[i]['group'] for i in train}
    def root(g):
        while parent[g]!=g:g=parent[g]
        return g
    pixels={}
    for i in train:
        g=rows[i]['group']
        for pixel in rows[i]['pixelHashes']:
            if pixel in pixels:parent[root(g)]=root(pixels[pixel])
            pixels[pixel]=g
    components={}
    for group in parent:components.setdefault(root(group),[]).append(group)
    names={g:t.p.sha('|'.join(sorted(groups)).encode()) for groups in components.values() for g in groups}
    ordered=sorted(set(names.values()))
    t.p.review.require(len(ordered)>=2,'insufficient_components')
    held=set(ordered[:max(1,len(ordered)//5)])
    selected=[i for i in train if names[rows[i]['group']] not in held]
    holdout=[i for i in train if names[rows[i]['group']] in held]
    return selected,holdout,names


def weights(groups,replay_count,balanced):
    counts=Counter(groups);size=len(groups)
    t.p.review.require(size>0 and replay_count>0,'empty_training')
    native=np.array([size/(len(counts)*counts[g]) if balanced else 1. for g in groups],np.float32)
    result=np.concatenate((np.ones(replay_count,np.float32),native,native))
    t.p.review.require(np.isclose(result.sum(),replay_count+2*size),'weight_mass')
    return result


def group_report(prob,rows):
    out={}
    for group in sorted({r['group'] for r in rows}):
        ids=[i for i,r in enumerate(rows) if r['group']==group]
        y=np.array([rows[i]['changed'] for i in ids]);p=np.clip(prob[ids],1e-7,1-1e-7)
        out[group]=dict(summary=t.n.w.summary(prob[ids],y),
                        logLoss=float(np.mean(-y*np.log(p)-(1-y)*np.log(1-p))))
    return out


def run():
    t.p.review.require(not OUT.exists(),'output_collision')
    start=time.monotonic();rows,x,_,prior=t.prepare()
    selected,held,names=partition(rows)
    torch=t.n.d.torch_runtime();torch.set_num_threads(2)
    old_x,_,mask,_,_,_,_,_,replay,labels=t.n.inputs()
    ref=t.h.read(t.p.CONTROL/'result.json');cp=t.h.checked(t.h.ROOT,ref['model'])
    old_protocol=t.h.read(t.p.CONTROL/'protocol.json')
    t.p.review.require(t.p.sha(replay.tobytes())==old_protocol['trainingSHA256'] and
                       t.p.sha(labels.tobytes())==old_protocol['labelsSHA256'],'replay_changed')
    replay_endpoints={t.p.sha(v.tobytes()) for pair in replay for v in (pair[:3],pair[3:])}
    t.p.review.require(not any(t.p.sha(v.tobytes()) in replay_endpoints for i in held+
        [j for j,r in enumerate(rows) if r['role']!='train'] for v in (x[i,:3],x[i,3:])),'holdout_replay_overlap')
    y=np.array([r['changed'] for r in rows],np.float32)
    tx=np.concatenate((replay,x[selected],t.reverse(x[selected])))
    ty=np.concatenate((labels,y[selected],y[selected]))
    state=torch.load(cp,map_location='cpu',weights_only=True)['state']
    OUT.mkdir(parents=True)
    protocol=dict(source=t.h.ref(__file__),trainer=t.h.ref(t.n.__file__),initializer=t.h.ref(cp),
        configuration=t.n.CONFIG,rows=rows,selected=selected,held=held,components=names,
        trainingSHA256=t.p.sha(tx.tobytes()),labelsSHA256=t.p.sha(ty.tobytes()),
        connectedBy='named group and exact decoded endpoint pixels; broader ancestry not proven',
        excluded=prior['excluded'],productionEligible=False)
    t.h.write(OUT/'protocol.json',protocol,sealed=True)
    results={}
    for name,balanced in [('DTM066',False),('DTM067',True)]:
        net=t.n.make_model(torch,paired_context=True);net.load_state_dict(state)
        w=weights([names[rows[i]['group']] for i in selected],len(replay),balanced)
        target=OUT/name;target.mkdir()
        t.h.write(target/'registration.json',dict(protocol=t.h.ref(OUT/'protocol.json'),
            weightsSHA256=t.p.sha(w.tobytes()),weights=w.tolist(),balanced=balanced),sealed=True)
        tick=time.monotonic()
        net,history=t.n.fit(net,torch.from_numpy(tx),torch.from_numpy(ty),t.n.CONFIG,
            lambda r:print(name,r,flush=True),weights=torch.from_numpy(w))
        duration=time.monotonic()-tick
        torch.save(dict(state=net.state_dict(),protocol=t.h.ref(OUT/'protocol.json')),target/'last.pt')
        restored=t.n.make_model(torch,paired_context=True)
        restored.load_state_dict(torch.load(target/'last.pt',map_location='cpu',weights_only=True)['state']);restored.eval()
        prob=t.n.score(restored,torch.from_numpy(x))
        t.p.review.require(np.array_equal(prob,t.n.score(net,torch.from_numpy(x))),'checkpoint_parity')
        result=dict(model=t.h.ref(target/'last.pt'),summary=t.summaries(prob,rows),
            fitting=t.n.w.summary(prob[selected],y[selected]),held=t.n.w.summary(prob[held],y[held]),
            groups=group_report(prob,rows),probabilities=prob.tolist(),history=history,trainingSeconds=duration,
            regression=t.retained(restored,torch,replay,labels,old_x,mask),
            reverseSummary=t.summaries(t.n.score(restored,torch.from_numpy(t.reverse(x))),rows),
            checkpointParity=True,geometryFrozen=True,productionEligible=False)
        t.h.write(target/'result.json',result,sealed=True);results[name]=t.h.ref(target/'result.json')
        print(name,'DONE','held',result['held'],'artwork',result['summary']['artwork_contrast'],flush=True)
    t.h.write(OUT/'completion.json',dict(results=results,seconds=time.monotonic()-start),sealed=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true',required=True);p.parse_args();run()
