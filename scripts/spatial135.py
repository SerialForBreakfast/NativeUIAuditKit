"""Complete image-only proposal support audit for paired focus-change evidence."""
import argparse
import hashlib
import math
from pathlib import Path
import time
import numpy as np
from PIL import Image
import conditioned133 as c
import diagnose_focus116 as intervention
import human_auto_boxes as boxes
from audit_transition119 import endpoint_bank
from prepare_proposal74 import load_inputs
from focus_recorded_transition_eval import iou

d, h = c.d, c.h


def proposal_mask(candidates, size, target=(192, 128)):
    h.require(len(size) == 2 and all(type(v) is int and v > 0 for v in size)
              and len(candidates) <= 80, 'proposal_contract')
    w, ht = size
    W, H = target
    scale = min(W/w, H/ht)
    rw, rh = max(1, round(w*scale)), max(1, round(ht*scale))
    px, py = (W-rw)//2, (H-rh)//2
    out = np.zeros((H, W), dtype=bool)
    ids = set()
    for candidate in candidates:
        h.require(set(candidate) == {'id', 'bounds'} and isinstance(candidate['id'], str)
                  and candidate['id'] not in ids, 'proposal_truth_or_duplicate')
        ids.add(candidate['id'])
        b = candidate['bounds']
        h.require(len(b) == 4 and all(type(v) in (int, float) and math.isfinite(v) for v in b), 'proposal_bounds')
        l, t, bw, bh = b
        h.require(l >= 0 and t >= 0 and bw > 0 and bh > 0 and l+bw <= w and t+bh <= ht, 'proposal_bounds')
        x0, x1 = px+math.floor(l*rw/w), px+math.ceil((l+bw)*rw/w)
        y0, y1 = py+math.floor(t*rh/ht), py+math.ceil((t+bh)*rh/ht)
        out[y0:y1, x0:x1] = True
    return out


def support(x, masks):
    h.require(x.ndim == 4 and x.shape[1:] == (6,128,192) and masks.shape == (len(x),128,192)
              and masks.dtype == bool and np.isfinite(x).all(), 'support_contract')
    diff = np.abs(x[:, :3]-x[:, 3:]).mean(axis=1)
    result = []
    for m, delta in zip(masks, diff):
        total = float(delta.sum())
        result.append(dict(maskPixels=int(m.sum()), maskFraction=float(m.mean()),
            differenceTotal=total, insideDifferenceFraction=float(delta[m].sum())/total if total else None))
    return result


def score_modes(net, x, masks):
    torch = d.a.r.d.torch_runtime()
    return {mode: intervention.score(net, torch.from_numpy(x), torch.from_numpy(masks), mode)
            for mode in ('baseline', 'inside', 'outside')}


def run(output):
    started = time.monotonic()
    out = h.fresh(output)
    parent, rows, x, y, _ = d.a.inputs()
    h.require(len(rows) == 113, 'known_membership')
    region = h.read(h.checked(h.ROOT, parent['admission']))['images']
    pairs = [r['images'] for r in rows] + [[u,v] for u,v in zip(region, region[1:])]
    bank = endpoint_bank(pairs, x[:207])
    peers = c.peer_inputs()
    peer_refs = []
    for _, _, row in peers:
        root = h.checked(h.ROOT, row['manifest']).parent
        request = c.transfer.document(root/'transition/request.template.json')
        match = [p for p in request['pairs'] if p['id'] == row['id']]
        h.require(len(match) == 1, 'peer_pair')
        peer_refs.append([h.ref(root/'originals'/f"{match[0][side]['sha256']}.png") for side in ('before', 'after')])
    peer_bank = endpoint_bank(peer_refs, np.stack([p[0] for p in peers]))
    original_count = len(bank)
    by_hash = {v['image']['sha256']: v for v in bank}
    for entry in peer_bank:
        key = entry['image']['sha256']
        if key in by_hash:
            h.require(np.array_equal(entry['pixels'], by_hash[key]['pixels']), 'peer_overlap_encoding')
        else:
            by_hash[key] = entry
    inputs_path = h.ROOT/'reports/work/COLLECTION-104/ready/inputs.json'
    inputs = load_inputs(inputs_path)
    retained = {f['id']: f for f in inputs['frames']}
    h.require(len(retained) == 187 and set(retained).issubset(by_hash), 'proposal_bank_membership')
    out.mkdir(parents=True)
    frames, masks, tensor_masks = {}, {}, {}
    fresh = reused = 0
    tick = time.monotonic()
    for key, entry in by_hash.items():
        path = h.checked(h.ROOT, entry['image'])
        with Image.open(path) as im:
            size = list(im.size)
            if key in retained:
                h.require(size == retained[key]['size'], 'retained_dimensions')
                candidates = retained[key]['candidates']
                origin = 'retained-COLLECTION104-image-only'
                reused += 1
            else:
                points = boxes.detect(im)
                candidates = [dict(id=str(i), bounds=[p[0][0],p[0][1],p[1][0]-p[0][0],p[1][1]-p[0][1]]) for i,p in enumerate(points)]
                origin = 'bounded-raster-image-only'
                fresh += 1
        m = proposal_mask(candidates, size)
        tensor_key = hashlib.sha256(entry['pixels'].tobytes()).hexdigest()
        # Distinct source images can collapse at192x128; keep their original masks
        # separately and explicitly union for already-encoded identity controls.
        tensor_masks[tensor_key] = tensor_masks.get(tensor_key, np.zeros_like(m)) | m
        masks[key] = m
        frames[key] = dict(image=entry['image'], size=size, candidates=candidates, source=origin,
            encodedSHA256=tensor_key, proposalPixels=int(m.sum()), role='exposed-diagnostic' if key not in {e['image']['sha256'] for e in bank} else 'existing-training')
        if (fresh+reused) % 40 == 0:
            print('proposals', fresh+reused, 'of', len(by_hash), flush=True)
    preparation_seconds = time.monotonic()-tick
    h.write(out/'proposals.json', dict(version='spatial135-proposals-v1', source=h.ref(boxes.__file__),
        retainedSource=h.ref(inputs_path), frames=frames, originalFrames=original_count,
        fresh=fresh, reused=reused, seconds=preparation_seconds), sealed=True)
    original_masks = [masks[u['sha256']] | masks[v['sha256']] for u,v in pairs]
    identity_masks = [tensor_masks[hashlib.sha256(v[:3].tobytes()).hexdigest()] for v in x[207:]]
    m = np.stack(original_masks+identity_masks)
    peer_masks = np.stack([masks[u['sha256']] | masks[v['sha256']] for u,v in peer_refs])
    result_ref = h.ROOT/'NativeUITrainer/focus_ring_runs/content127-dtm031/result.json'
    result = c.audit.sealed(result_ref)
    torch = d.a.r.d.torch_runtime()
    torch.set_num_threads(2)
    net = d.a.r.model(d.a.r.d.model(d.a.r.d.PAIRED_TEMPORAL_CONFIG))
    net.load_state_dict(torch.load(h.checked(h.ROOT,result['model']), weights_only=True, map_location='cpu')['state'])
    net.eval()
    groups = dict(oldTrain=parent['oldTrainIndices'], admittedSettings=parent['relatedSettingsIndices'],
                  region=list(range(113,207)), identical=list(range(207,433)))
    scores = score_modes(net, x, m)
    expected = np.asarray(result['reports']['original']['probabilities'], dtype=np.float32)
    h.require(np.allclose(scores['baseline'], expected, atol=1e-6, rtol=0) and
              np.array_equal(d.q.decisions(scores['baseline']), d.q.decisions(expected)), 'baseline_replay')
    for name, values in scores.items():
        h.require(np.array_equal(values[207:], scores['baseline'][207:]), 'identity_changed')
    peer_scores = score_modes(net, np.stack([p[0] for p in peers]), peer_masks)
    old_peer = c.audit.sealed(h.ROOT/'NativeUITrainer/focus_ring_runs/conditioned133-dtm033/result.json')['retainedCases']
    h.require([v['id'] for v in old_peer] == [v[2]['id'] for v in peers] and
              np.allclose(peer_scores['baseline'], [v['dtm031Probability'] for v in old_peer], atol=1e-6, rtol=0), 'peer_baseline_replay')
    # Evaluation annotations are consulted only after all inference/masks are fixed.
    truths = {}
    for row in rows:
        for image, box in zip(row['images'], row['boxes']):
            truths.setdefault(image['sha256'], set()).add(tuple(box))
    coverage = []
    for key, alternatives in truths.items():
        valid = len(alternatives) == 1
        candidates = frames[key]['candidates']
        coverage.append(dict(imageSHA256=key, geometryEligible=valid,
            bestIoU=max((iou(v['bounds'], next(iter(alternatives))) for v in candidates), default=0) if valid else None))
    summaries = {mode:d.q.summarize(values, y, groups, scores['baseline']) for mode,values in scores.items()}
    peer_records = [dict(row, proposalSupport=info,
        decisions={k:c.decision(float(v[i])) for k,v in peer_scores.items()},
        probabilities={k:float(v[i]) for k,v in peer_scores.items()})
        for i, ((_,_,row),info) in enumerate(zip(peers,support(np.stack([p[0] for p in peers]),peer_masks)))]
    report = dict(version='spatial135-audit-v1', source=h.ref(__file__), scorer=h.ref(intervention.__file__),
        model=result['model'], sourceProtocol=h.ref(d.a.r.PARENT), proposals=h.ref(out/'proposals.json'),
        tensorSHA256=hashlib.sha256(x.tobytes()).hexdigest(), groups=groups, labels=y.tolist(),
        pairIDs=[r['id'] for r in rows]+[f'region-{i}-{i+1}' for i in range(94)],
        support=support(x,m), summary=summaries, probabilities={k:v.tolist() for k,v in scores.items()},
        retained=peer_records, coverage=coverage,
        geometryUnavailable=dict(conflicting=sum(not v['geometryEligible'] for v in coverage),
            regionFrames=len(region), peerFrames=len(peer_bank), reason='No invented rendered-body labels'),
        preparationSeconds=preparation_seconds, totalSeconds=time.monotonic()-started,
        training=False, independentEvaluation=False, productionEligible=False,
        limitation='Difference-channel ablation leaves RGB context intact; proposal support is not focus correctness.')
    h.write(out/'report.json', report, sealed=True)
    c.audit.sealed(out/'report.json')
    print({mode:{g:(v['correct'],v['lostCorrect']) for g,v in group.items()} for mode,group in summaries.items()}, flush=True)
    print('peer', [v['decisions'] for v in peer_records], flush=True)
    h.require(sum(p.stat().st_size for p in out.rglob('*') if p.is_file()) < 2*1024**3, 'output_budget')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output)
