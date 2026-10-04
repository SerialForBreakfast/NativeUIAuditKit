"""Complete admitted endpoint invariants and exposure closure, not final evaluation."""
import argparse
from pathlib import Path
import time
import numpy as np
import adapt_reflow117 as a
from diagnose_reflow115 import decisions

h=a.h


def endpoint_bank(pairs,x):
    h.require(len(pairs)==len(x) and x.ndim==4 and x.shape[1:]==(6,128,192),'endpoint_membership')
    bank={}
    for i,pair in enumerate(pairs):
        for j,ref in enumerate(pair):
            pixels=x[i,3*j:3*j+3]
            key=ref['sha256']
            if key in bank:h.require(np.array_equal(bank[key]['pixels'],pixels),'same_image_different_tensor')
            else:bank[key]=dict(image=ref,pixels=pixels,origins=[])
            bank[key]['origins'].append([i,j])
    return list(bank.values())


def run(output):
    start=time.monotonic();out=h.fresh(output)
    parent,rows,x,y,_=a.inputs()
    region=h.read(h.checked(h.ROOT,parent['admission']))['images']
    pairs=[v['images'] for v in rows]+[[b,c] for b,c in zip(region,region[1:])]
    h.require(len(pairs)==207,'original_pairs')
    endpoints=endpoint_bank(pairs,x[:207])
    identities=np.stack([np.concatenate([v['pixels']]*2) for v in endpoints])
    torch=a.r.d.torch_runtime();torch.set_num_threads(2)
    state=torch.load(h.checked(h.ROOT,parent['initializer']),map_location='cpu',weights_only=True)
    base=a.r.d.model(state['configuration']);base.load_state_dict(state['state']);base.eval()
    result_path=h.ROOT/'NativeUITrainer/focus_ring_runs/reflow117-dtm030/result.json'
    result=h.read(result_path);h.require(result['seal']==h.digest({k:v for k,v in result.items() if k!='seal'}),'result')
    model=torch.load(h.checked(h.ROOT,result['model']),map_location='cpu',weights_only=True)
    net=a.r.model(base);net.load_state_dict(model['state']);net.eval()
    with torch.no_grad():
        tx=torch.from_numpy(x);forward=a.score(net,tx).numpy()
        reverse=a.score(net,torch.cat([tx[:,3:],tx[:,:3]],1)).numpy()
        ix=torch.from_numpy(identities)
        ip=a.r.c.score_change(net,ix,a.CONFIG).numpy()
        bp=a.r.c.score_change(base,ix,a.CONFIG).numpy()
    h.require(np.array_equal(forward,np.array(result['after'],dtype=np.float32)),'baseline_replay')
    h.require(np.allclose(ip,bp,atol=1e-6,rtol=0),'identity_base_changed')
    records=[]
    for v,prob,base_prob in zip(endpoints,ip,bp):
        ref=v['image'];h.checked(h.ROOT,ref)
        origins=v['origins'];settings=any(i in range(24,29) or i>=113 for i,j in origins)
        records.append(dict(image=ref,origins=origins,probability=float(prob),baseProbability=float(base_prob),
            ancestry='tvos-settings-native-layout-family' if settings else 'fixture-procedural-renderer-v1',
            currentRole='training_exposed',finalEligible=False))
    labels=y.astype(int);rd=decisions(reverse);fd=decisions(forward)
    doc=dict(version='transition119-coverage-v1',model=result['model'],sourceResult=h.ref(result_path),
        sourceProtocol=h.ref(a.READY/'protocol.json'),implementation=h.ref(__file__),
        identities=dict(count=len(ip),confidentUnchanged=int((ip<=.15).sum()),uncertain=int(((ip>.15)&(ip<.85)).sum()),
            confidentFalseChanges=int((ip>=.85).sum()),maximumProbability=float(ip.max()),
            maxBaseDelta=float(np.abs(ip-bp).max())),
        reversal=dict(count=len(x),categoricalDisagreements=int((fd!=rd).sum()),
            confidentCorrect=int((rd==labels).sum()),maxProbabilityDelta=float(np.abs(reverse-forward).max()),
            disagreementIndices=np.flatnonzero(fd!=rd).tolist()),
        exposure=records,originalPairCount=207,independentFinalMembership=[],
        independentFinalStatus='not_reserved',elapsedSeconds=time.monotonic()-start,
        limitation='Identical/reversed examples are metamorphic diagnostics, not new capture or independent evaluation.',training=False)
    out.mkdir(parents=True);h.write(out/'report.json',doc,sealed=True)
    print(doc['identities']);print(doc['reversal'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);run(p.parse_args().output)
