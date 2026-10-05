"""Independent fixed-consensus accounting; incoming implementations are never run."""
import argparse
import numpy as np
import replay_worker180 as b
h,a=b.h,b.a


def counts(values, labels):
    values=np.asarray(values)
    h.require(values.shape==(3,len(labels)) and np.isfinite(values).all() and ((values>=0)&(values<=1)).all(),'scores')
    individual=np.where(values<=.15,0,np.where(values>=.85,1,-1))
    decision=np.where((values<=.15).all(axis=0),0,np.where((values>=.85).all(axis=0),1,-1))
    return dict(unchanged=int((decision==0).sum()),changed=int((decision==1).sum()),
        abstain=int((decision==-1).sum()),modelDisagreements=int((individual!=individual[0]).any(axis=0).sum()),
        confidentFlips=int(((decision>=0)&(decision!=labels)).sum()),baselineLabelAgreement=int((decision==labels).sum()),
        count=len(labels),confidentCoverage=float((decision>=0).mean()))


def run(root, broot, output):
    root,broot,output=map(b.local,(root,broot,output));h.require(not output.exists(),'output_collision')
    for ref in h.read(root/'inventory.json'):
        b.v.w.t.verified(b.v.w.t.path_under(root,ref['file']),ref)
    work=root/'reports/work/WORKER180/c02';pins=h.read(work/'pins.json');result=h.read(work/'result.json',4*1024**2)
    for key,path in dict(request=b.REQUEST,oldPins=b.OLD/'pins.json',oldCursor=b.OLD/'cursor.json',bPins=broot/'reports/work/WORKER180/b01/pins.json',bCursor=broot/'reports/work/WORKER180/b01/cursor.json').items():
        b.v.w.t.verified(path,pins[key])
    h.require(pins['config']==dict(batches=[1,8,32],warmup=1,passes=5,tolerance=.0001,thresholds=[.15,.85],fit=False) and result['state']=='completed','configuration')
    old=h.read(b.OLD/'pins.json');cursor=h.read(b.OLD/'cursor.json');bc=h.read(broot/'reports/work/WORKER180/b01/cursor.json')
    def readref(base,ref):
        path=b.v.w.t.path_under(base,ref['file']);b.v.w.t.verified(path,ref);return h.read(path)
    after=a.checked_scores(readref(a.BASE/'extracted',row['file']) for row in cursor['chunks'])
    other=b.scores(readref(broot,row) for row in bc['chunks'])
    labels=np.repeat([c['label'] for c in old['cases']],768);verified={}
    for name,values in [('after',after),('before',other[:,0]),('both',other[:,1])]:
        found=counts(values,labels);expected=result['consensus']['counterfactual'][name]
        h.require(all(expected[k]==v for k,v in found.items()),'consensus_mismatch');verified[name]=found
    timing={}
    for batch in (1,8,32):
        rows=[r for r in result['benchmark'] if r['batch']==batch]
        h.require(len(rows)==3 and {r['model'] for r in rows}=={'DTM050','DTM051','DTM052'},'benchmark_membership')
        for row in rows:
            times=np.asarray(row['timedSeconds']);h.require(times.shape==(5,) and np.isfinite(times).all() and (times>0).all() and row['cases']==286 and row['warmupPasses']==1,'timings')
            h.require(abs(float(times.mean())-row['meanSeconds'])<1e-12,'timing_mean')
        timing[str(batch)]=sum(r['meanSeconds'] for r in rows)
        h.require(abs(timing[str(batch)]-result['sequentialThreeModelSeconds'][str(batch)])<1e-12,'timing_total')
    h.write(output,dict(consensus=verified,workerReportedCUDATiming=timing,timingReproducedLocally=False,
        inventory=h.ref(root/'inventory.json'),result=h.ref(work/'result.json'),source=h.ref(__file__),
        productionEligible=False,limitation='Counterfactual agreement is not native accuracy; no training admission or navigation authority.'),sealed=True)
    print(verified,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--b-root',required=True);p.add_argument('--output',required=True);args=p.parse_args();run(args.root,args.b_root,args.output)
