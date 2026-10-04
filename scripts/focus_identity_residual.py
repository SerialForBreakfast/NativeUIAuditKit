"""Identity-preserving change correction; fixed experimental entrypoint, not exporter."""
import argparse
import copy
import os
from pathlib import Path
import time
import numpy as np
import focus_direct_transition as d
import focus_change_adaptation as c

h = d.h
CONFIG = dict(c.COLLECTION_CONFIG, epochs=600, lr=.01, originalGroupCount=202,
              derivedGroupCount=217, initializer='DTM025', batch=202)
READY = h.ROOT/'reports/work/IDENTITY-RESIDUAL-114/artifacts/ready'
PARENT = h.ROOT/'reports/work/REGION-REVIEW-112/artifacts/ready02/protocol.json'
VERSION = 'identity-residual-v1'


def model(base):
    torch = d.torch_runtime()

    class Correction(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(576, 1, bias=False)
            torch.nn.init.zeros_(self.linear.weight)

        def forward(self, z):
            return z[:, :1] + self.linear(z[:, 1:])

    class Residual(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder = copy.deepcopy(base.change[:8])
            self.base_readout = copy.deepcopy(base.change[8:])
            for p in list(self.encoder.parameters()) + list(self.base_readout.parameters()):
                p.requires_grad_(False)
            self.change = Correction()

        def change_inputs(self, x):
            h.require(x.ndim == 4 and x.shape[1:] == (6,128,192) and
                      bool(torch.isfinite(x).all()) and bool(((x>=0)&(x<=1)).all()), 'residual_inputs')
            rows = []
            with torch.no_grad():
                for chunk in x.split(16):
                    a, b = chunk[:, :3], chunk[:, 3:]
                    phi = self.encoder(torch.cat([(b-a).abs(), a, b], 1))
                    aa = self.encoder(torch.cat([torch.zeros_like(a), a, a], 1))
                    bb = self.encoder(torch.cat([torch.zeros_like(b), b, b], 1))
                    rows.append(torch.cat([self.base_readout(phi), phi-(aa+bb)/2], 1))
            return torch.cat(rows).detach()

    return Residual().eval()


def pins():
    return [h.ref(h.ROOT/v) for v in ('scripts/focus_identity_residual.py',
            'scripts/focus_direct_transition.py', 'scripts/focus_change_adaptation.py')]


def prepare():
    out = h.fresh(READY)
    p = h.read(PARENT)
    h.require(p['protocolSHA256'] == h.digest({k:v for k,v in p.items() if k!='protocolSHA256'}), 'parent_seal')
    doc = dict(version=VERSION, parent=h.ref(PARENT), configuration=CONFIG, pins=pins(),
               experiment='DTM029', output='identity114-dtm029')
    doc['protocolSHA256'] = h.digest(doc)
    out.mkdir(parents=True)
    h.write(out/'protocol.json', doc)
    print(doc['protocolSHA256'])


def execute():
    start = time.monotonic()
    p = h.read(READY/'protocol.json')
    h.require(p['protocolSHA256']==h.digest({k:v for k,v in p.items() if k!='protocolSHA256'}) and
              p['configuration']==CONFIG and p['pins']==pins() and p['output']=='identity114-dtm029', 'protocol_changed')
    h.require(p['protocolSHA256'] in (h.ROOT/'Research/ExperimentLog.md').read_text(), 'experiment_not_logged')
    out = d.old.fresh_run(p['output'])
    parent = h.read(h.checked(h.ROOT,p['parent']))
    admission = h.read(h.checked(h.ROOT,parent['admission']))
    h.require(admission['seal']==h.digest({k:v for k,v in admission.items() if k!='seal'}) and admission['training'] is True, 'admission')
    for ref in admission['images']: h.checked(h.ROOT,ref)
    h.checked(h.ROOT,admission['sourceManifest'])
    x,y,e = [np.load(h.checked(h.ROOT,parent['inputs'][k],256*1024**2),allow_pickle=False) for k in ('train','labels','evaluation')]
    h.require(x.shape==(419,6,128,192) and y.shape==(419,) and e.shape==(424,6,128,192), 'membership')
    torch=d.torch_runtime();torch.set_num_threads(2);torch.manual_seed(42)
    state=torch.load(h.checked(h.ROOT,parent['initializer']),map_location='cpu',weights_only=True)
    h.require(state['configuration']==d.PAIRED_TEMPORAL_CONFIG and state['adaptation']==c.COLLECTION_CONFIG,'initializer')
    base=d.model(state['configuration']);base.load_state_dict(state['state']);base.eval()
    net=model(base);tx=torch.from_numpy(e)
    frozen={k:v.clone() for k,v in net.state_dict().items() if not k.startswith('change.')}
    with torch.no_grad():
        before=c.score_change(net,tx,CONFIG).numpy()
        original=c.score_change(base,tx,CONFIG).numpy()
    h.require(np.allclose(before,original,rtol=0,atol=1e-6),'baseline_initialization')
    out.mkdir(parents=True)
    h.write(out/'execution.json',dict(pid=os.getpid(),status='started',protocolSHA256=p['protocolSHA256']))
    fit=time.monotonic()
    net,history=d.fit_change_head(net,torch.from_numpy(x),torch.from_numpy(y),CONFIG)
    seconds=time.monotonic()-fit
    h.require(all(torch.equal(v,net.state_dict()[k]) for k,v in frozen.items()),'baseline_changed')
    torch.save(dict(version=VERSION,state=net.state_dict(),configuration=CONFIG,initializer=parent['initializer']),out/'last.pt')
    with torch.no_grad(): after=c.score_change(net,tx,CONFIG).numpy()
    replay=model(base);replay.load_state_dict(torch.load(out/'last.pt',map_location='cpu',weights_only=True)['state'])
    with torch.no_grad(): again=c.score_change(replay,tx,CONFIG).numpy()
    h.require(np.array_equal(after,again),'checkpoint_replay')
    h.require(np.array_equal(before[207:],after[207:]),'identity_changed')
    truth=np.array(parent['oldLabels']+[True]*94+[False]*217)
    groups=dict(oldTrain=parent['oldTrainIndices'],relatedSettings=parent['relatedSettingsIndices'],region=list(range(113,207)),oldDerived=list(range(207,329)),regionDerived=list(range(329,424)))
    summary={}
    for name,ids in groups.items():
        a,b,t=before[ids],after[ids],truth[ids]
        oldgood=((a<=.15)|(a>=.85))&((a>=.5)==t)
        newgood=((b<=.15)|(b>=.85))&((b>=.5)==t)
        summary[name]=dict(count=len(ids),beforeConfidentCorrect=int(oldgood.sum()),afterConfidentCorrect=int(newgood.sum()),lostConfidentSuccesses=int((oldgood&~newgood).sum()),abstentions=int(((b>.15)&(b<.85)).sum()),rawCorrect=int(((b>=.5)==t).sum()))
    latency=[]
    with torch.no_grad():
        for _ in range(11):
            tick=time.monotonic();c.score_change(net,tx[:1],CONFIG);latency.append(time.monotonic()-tick)
    passed=summary['region']['afterConfidentCorrect']==94 and all(v['lostConfidentSuccesses']==0 for v in summary.values())
    h.write(out/'result.json',dict(experiment='DTM029',model=h.ref(out/'last.pt'),protocolSHA256=p['protocolSHA256'],summary=summary,
        before=before.tolist(),after=after.tolist(),history=history,fitSeconds=seconds,totalSeconds=time.monotonic()-start,
        baselineUnchanged=True,identityExactlyPreserved=True,checkpointReplay=True,trainableParameters=576,
        inferenceFirstSeconds=latency[0],inferenceWarmMedianSeconds=float(np.median(latency[1:])),
        developmentGatesPassed=passed,productionEligible=False),sealed=True)
    h.require(sum(v.stat().st_size for v in out.iterdir())<2*1024**3,'output_budget')
    h.write(out/'completion.json',dict(status='completed',exitCode=0,result=h.ref(out/'result.json')))
    print(summary)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','execute'])
    prepare() if parser.parse_args().mode=='prepare' else execute()
