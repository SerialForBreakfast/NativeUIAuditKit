"""Source-bound binary temporal-order diagnosis and one conditional retention fit."""
import argparse
import hashlib
import math
import os
from pathlib import Path
import time
import numpy as np
import conditioned142 as f
import train_spatial135 as spatial

h, d, c = f.h, f.d, f.c


def reverse(x):
    h.require(x.ndim == 4 and x.shape[1:] == (6,128,192) and len(x) > 0
              and x.dtype == np.float32 and np.isfinite(x).all()
              and ((x >= 0) & (x <= 1)).all(), 'reversal_pixels')
    return np.concatenate([x[:,3:], x[:,:3]], axis=1)


def native_labels(families):
    h.require(set(families) == {'within_screen','screen_transition','identical_control'}, 'reversal_families')
    ids, labels = [], []
    for name, count in [('within_screen',5), ('screen_transition',2), ('identical_control',2)]:
        rows = families[name]
        h.require(len(rows) == count and all(type(i) is int and 0 <= i < 11 for i in rows), 'reversal_indices')
        ids.extend(rows); labels.extend([0 if name == 'identical_control' else 1]*count)
    h.require(len(set(ids)) == 9, 'reversal_duplicate')
    return ids, np.asarray(labels, np.float32)


def summary(probabilities, labels):
    p = np.asarray(probabilities); y = np.asarray(labels)
    h.require(p.shape == y.shape and np.isfinite(p).all() and ((p>=0)&(p<=1)).all()
              and np.isin(y,[0,1]).all(), 'reversal_scores')
    decisions = d.q.decisions(p)
    return dict(count=len(y), correct=int((decisions==y).sum()),
                wrong=int(((decisions!=-1)&(decisions!=y)).sum()), abstain=int((decisions==-1).sum()))


def run(output):
    started = time.monotonic(); out = h.fresh(output)
    h.require('DTM047 — REVERSAL-147' in (h.ROOT/'Research/ExperimentLog.md').read_text(), 'unlogged')
    p, cache, ref, families, prior, labels, _, _, guard, truth, _ = f.a.inputs()
    native, ny = native_labels(families)
    torch = d.a.r.d.torch_runtime(); torch.set_num_threads(2)
    old_result = c.audit.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/global146-dtm046/result.json')
    old_state = torch.load(h.checked(h.ROOT,old_result['model']),weights_only=True,map_location='cpu')
    old_head = d.model(); old_head.change.linear.weight.data.copy_(old_state['correction'])
    x, y, _, encoder, _, _, _ = spatial.d.c.setup()
    h.require(np.array_equal(y,labels), 'reversal_labels')
    encoder.load_state_dict(torch.load(h.checked(h.ROOT,p['model']),weights_only=True,map_location='cpu')['state'])
    encoder.eval()
    audit = c.audit.sealed(h.checked(h.ROOT,p['audit']))
    proposals = c.audit.sealed(h.checked(h.ROOT,audit['proposals']))
    masks = spatial.pair_masks(x,proposals['frames'])
    peer = c.peer_inputs(); px = np.stack([row[0] for row in peer])
    h.require([row[2] for row in peer] == p['peer'], 'reversal_peer_binding')
    pm = spatial.pair_masks(px,proposals['frames'])
    base_state = torch.load(h.checked(h.ROOT,prior['model']),weights_only=True,map_location='cpu')
    base_head = d.model(); base_head.change.linear.weight.data.copy_(base_state['weights'])

    def encode(pixels, mask):
        z = c.scaled(spatial.features(encoder,pixels,mask)['spatial'],base_state['scale'].numpy())
        with torch.inference_mode(): z[:,0] = base_head.change(torch.from_numpy(z)).flatten().numpy()
        return z

    # Exact original feature replay checks the entire encoder/scale/readout chain.
    for name, pixels, mask in [('original',x,masks),('peer',px,pm)]:
        h.require(np.array_equal(encode(pixels,mask),cache[name]), 'reversal_feature_replay_'+name)
    reversed_cache = dict(reversed_original=encode(reverse(x),masks), reversed_peer=encode(reverse(px),pm))
    all_cache = dict(cache, **reversed_cache)
    targets = dict(original=labels,reversed_original=labels,peer=ny,reversed_peer=ny)

    def score(net):
        records = {}
        with torch.inference_mode():
            for name, z in all_cache.items():
                logits = net.change(torch.from_numpy(z)).flatten()
                probabilities = logits.sigmoid().numpy() if 'peer' in name else d.probabilities(logits)
                ids = native if 'peer' in name else list(range(len(z)))
                target = ny if 'peer' in name else labels
                records[name] = dict(probabilities=probabilities.tolist(),
                    summary=summary(probabilities[ids],target))
        return records

    before = score(old_head)
    for name in cache:
        expected = ([r['probability'] for r in old_result['records'][name]] if name=='peer'
                    else old_result['records'][name]['probabilities'])
        h.require(np.array_equal(np.asarray(before[name]['probabilities'],np.float32),np.asarray(expected,np.float32)), 'reference_replay')
    out.mkdir(parents=True)
    role, extra = f.global_admission(cache)
    train = np.concatenate([guard,cache['peer'][native],extra,reversed_cache['reversed_original'],reversed_cache['reversed_peer'][native]])
    train_y = np.concatenate([truth,ny,np.zeros(226,np.float32),labels,ny])
    h.require(train.shape==(1661,1153), 'reversal_training_membership')
    h.write(out/'protocol.json',dict(version='reversal147-v1',source=h.ref(__file__),solver=h.ref(f.__file__),
        featureSource=h.ref(spatial.__file__),parent=h.ref(f.a.PARENT),baseline=old_result['model'],
        nativeAdmission=h.ref(f.j.a.ADMISSION),globalAdmission=h.ref(role),nativeIndices=native,
        tensorSHA256=hashlib.sha256(x.tobytes()).hexdigest(),featuresSHA256=hashlib.sha256(train.tobytes()).hexdigest(),
        labelsSHA256=hashlib.sha256(train_y.tobytes()).hexdigest(),configuration=dict(rows=1661,solverSeconds=60,
        trainingMargin=math.log(.85/.15)+.01,runtimeMargin=f.TARGET,threads=2),
        admission='Reversal preserves binary focus equality only; same exposed train ancestry, not inverse-route or geometry supervision',
        independentEvaluation=False),sealed=True)
    h.write(out/'diagnosis.json',dict(before=before,seconds=time.monotonic()-started),sealed=True)
    needs_fit = any(before[name]['summary']['correct'] != before[name]['summary']['count']
                    for name in ('reversed_original','reversed_peer'))
    report = dict(trainingExecuted=False,before=before,independentEvaluation=False,productionEligible=False)
    if needs_fit:
        run_dir = d.a.r.d.old.fresh_run('reversal147-dtm047'); run_dir.mkdir(parents=True)
        h.write(run_dir/'execution.json',dict(experiment='DTM047',pid=os.getpid(),protocol=h.ref(out/'protocol.json'),
            status='started',authority='Standing local training and source-preserving derived admission'),sealed=True)
        tick = time.monotonic()
        solver, w = f.solve(train,train_y,strict=True,preserve=True,margin=math.log(.85/.15)+.01)
        report.update(trainingExecuted=True,solver=solver,solveSeconds=time.monotonic()-tick)
        if w is not None:
            net = d.model(); net.change.linear.weight.data.copy_(torch.from_numpy(w.astype(np.float32)[None]))
            torch.save(dict(version='reversal147-v1',correction=net.change.linear.weight.detach().clone(),
                baseline=prior['model'],protocol=h.ref(out/'protocol.json')),run_dir/'last.pt')
            replay = d.model(); replay.change.linear.weight.data.copy_(torch.load(run_dir/'last.pt',weights_only=True,map_location='cpu')['correction'])
            after = score(net); h.require(after==score(replay), 'reversal_checkpoint_replay')
            with torch.inference_mode(): margins=(2*train_y-1)*net.change(torch.from_numpy(train)).flatten().numpy()
            report.update(after=after,model=h.ref(run_dir/'last.pt'),float32MinimumMargin=float(margins.min()),
                float32GatesPassed=bool((margins>=f.TARGET-1e-6).all()),checkpointReplay=True)
        report['seconds']=time.monotonic()-started
        h.write(run_dir/'result.json',report,sealed=True)
    report['seconds']=time.monotonic()-started
    h.write(out/'report.json',report,sealed=True)
    print('before', {k:v['summary'] for k,v in before.items()},flush=True)
    print('after', {k:v['summary'] for k,v in report.get('after',{}).items()},flush=True)
    print('fit',report['trainingExecuted'],'margin',report.get('float32MinimumMargin'),'seconds',report['seconds'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
