"""Bounded retention-constrained comparison and frozen nuisance falsification."""
import argparse
import hashlib
import math
import os
from pathlib import Path
import time

import numpy as np
import conditioned133 as c

d = c.d
a, h = d.a, d.h
audit = c.audit
FLOOR = math.log(.85 / .15) + .05


def constrained_model(original, labels):
    """Training-only constraints; materialize a plain effective head for inference."""
    torch = a.r.d.torch_runtime()
    h.require(original.ndim == 2 and original.shape[1] == 1153 and len(original) > 0
              and labels.shape == (len(original),) and np.isfinite(original).all()
              and np.isin(labels, [0, 1]).all(), 'constraint_contract')
    signs = 2 * labels.astype(np.float64) - 1
    margins = signs * original[:, 0]
    h.require((margins >= math.log(.85 / .15)).all(), 'baseline_not_confident_correct')
    signed = signs[:, None] * original[:, 1:].astype(np.float64)
    slack = margins - np.minimum(margins, FLOOR)

    class Head(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(1152, 1, bias=False)
            torch.nn.init.zeros_(self.linear.weight)
            self.register_buffer('signed', torch.from_numpy(signed))
            self.register_buffer('slack', torch.from_numpy(slack))

        def effective(self):
            movement = self.signed @ self.linear.weight.flatten().double()
            bounds = torch.where(movement < 0, self.slack / (-movement).clamp_min(1e-30),
                                 torch.ones_like(movement))
            radius = bounds.min().clamp(0, 1)
            radius = torch.where(radius < 1, radius * .999, radius)
            return self.linear.weight * radius.float(), radius

        def forward(self, z):
            weight, _ = self.effective()
            return z[:, :1] + torch.nn.functional.linear(z[:, 1:], weight)

    class Net(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.change = Head()

    return Net()


def gradient_conflict(z, y, weights):
    """Descriptive BCE gradients; never select parameters from diagnostics."""
    torch = a.r.d.torch_runtime()
    zz, yy = torch.from_numpy(z), torch.from_numpy(y)
    w = torch.from_numpy(weights.copy()).requires_grad_()
    gradients = []
    for rows in (slice(0, 207), slice(207, 1073)):
        logits = zz[rows, 0] + zz[rows, 1:] @ w.flatten()
        loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, yy[rows])
        gradients.append(torch.autograd.grad(loss, w)[0].flatten())
    left, right = gradients
    denom = float(left.norm() * right.norm())
    return dict(originalNorm=float(left.norm()), augmentationNorm=float(right.norm()),
                cosine=float(left @ right) / denom if denom else None)


def localized(x, mask, mode):
    h.require(mode in ('global8', 'left8', 'center8') and x.ndim == 4 and x.shape[1] == 6
              and mask.shape == x.shape and mask.dtype == bool and np.isfinite(x).all()
              and ((x >= 0) & (x <= 1)).all(), 'intervention_contract')
    out = x.copy()
    for i in range(len(x)):
        h.require(np.array_equal(mask[i, :3], mask[i, 3:]), 'content_mismatch')
        ys, xs = np.where(mask[i, 3])
        h.require(len(xs) > 0, 'empty_content')
        top, bottom, left, right = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        selected = np.zeros_like(mask[i, 3:])
        if mode == 'left8':
            right = left + (right - left) // 2
        elif mode == 'center8':
            ht, width = bottom - top, right - left
            top, bottom = top + ht // 4, top + 3 * ht // 4
            left, right = left + width // 4, left + 3 * width // 4
        selected[:, top:bottom, left:right] = True
        selected &= mask[i, 3:]
        changed = np.rint((out[i, 3:] * .8 + .1) * 255) / 255
        out[i, 3:] = np.where(selected, changed, out[i, 3:])
    h.require(np.array_equal(out[~mask], x[~mask]), 'padding_changed')
    return out


def run(output):
    started = time.monotonic()
    out = h.fresh(output)
    p = audit.sealed(d.READY / 'protocol.json')
    for key in ('source', 'trainer', 'normalizer', 'model'):
        h.checked(h.ROOT, p[key])
    h.require(p['configuration'] == d.CONFIG, 'configuration_changed')
    h.require('Run DTM034 — RETENTION-134' in (h.ROOT / 'Research/ExperimentLog.md').read_text(), 'unlogged')
    cache = {k: np.load(h.checked(h.ROOT, v), allow_pickle=False) for k, v in p['featureCache'].items()}
    labels = np.asarray(p['labels'], dtype=np.float32)
    z = np.concatenate([cache['original'][:207], cache['contrast_0'], cache['contrast_1'], cache['original'][207:]])
    y = np.concatenate([labels[:207], labels, labels, labels[207:]])
    h.require(z.shape == (1299, 1153) and (z[-226:, 1:] == 0).all(), 'membership')
    scale = c.scale_for(z)
    z = c.scaled(z, scale)
    peers = c.peer_inputs()  # Validate hashes; no peer input participates in fitting.
    torch = a.r.d.torch_runtime()
    torch.set_num_threads(2)
    net = constrained_model(z[:207], y[:207])
    run_dir = a.r.d.old.fresh_run('retention134-dtm034')
    run_dir.mkdir(parents=True)
    out.mkdir(parents=True)
    config = dict(d.CONFIG, initializer='DTM031-constrained-scaled-dual',
                  constraintFloor=FLOOR, constraintInterior=.999)
    h.write(run_dir / 'execution.json', dict(experiment='DTM034', pid=os.getpid(),
        configuration=config, source=h.ref(__file__), scalingSource=h.ref(c.__file__),
        trainer=h.ref(a.r.d.__file__), parent=h.ref(d.READY / 'protocol.json'),
        scaleSHA256=hashlib.sha256(scale.tobytes()).hexdigest(),
        authority='Assigned RETENTION134 under standing local training authority',
        peerTraining=False, status='started'), sealed=True)
    conflict_before = gradient_conflict(z, y, np.zeros((1, 1152), dtype=np.float32))
    tick = time.monotonic()
    net, history = a.r.d.fit_change_features(net, torch.from_numpy(z), torch.from_numpy(y), config)
    fit_seconds = time.monotonic() - tick
    with torch.no_grad():
        weights, radius = net.change.effective()
        weights = weights.detach().clone()
    torch.save(dict(version='constrained-scaled-dual-v1', weights=weights,
                    rawState=net.state_dict(), scale=torch.from_numpy(scale), configuration=config,
                    baseline=p['model']), run_dir / 'last.pt')
    saved = torch.load(run_dir / 'last.pt', weights_only=True, map_location='cpu')
    replay = d.model()
    replay.change.linear.weight.data.copy_(saved['weights'])
    h.require(np.array_equal(saved['scale'].numpy(), scale), 'scale_roundtrip')
    records = {}
    original = d.probabilities(torch.from_numpy(cache['original'][:, 0]))
    with torch.inference_mode():
        for name, features in cache.items():
            tx = torch.from_numpy(c.scaled(features, scale))
            probs = d.probabilities(replay.change(tx))
            h.require(np.array_equal(probs, d.probabilities(net.change(tx))), 'materialized_replay')
            records[name] = dict(summary=d.q.summarize(probs, labels, p['groups'],
                d.probabilities(torch.from_numpy(features[:, 0]))), probabilities=probs.tolist())
    h.require(np.array_equal(np.asarray(records['original']['probabilities'], dtype=np.float32)[207:], original[207:]), 'identity_changed')
    margins = (2 * y[:207] - 1) * (z[:207, 0] + z[:207, 1:] @ weights.numpy().flatten())
    baseline_margins = (2 * y[:207] - 1) * z[:207, 0]
    h.require((margins >= np.minimum(baseline_margins, FLOOR) - 1e-5).all(), 'constraint_violated')
    base = a.r.model(a.r.d.model(a.r.d.PAIRED_TEMPORAL_CONFIG))
    base.load_state_dict(torch.load(h.checked(h.ROOT, p['model']), weights_only=True, map_location='cpu')['state'])
    base.eval()
    cases = []
    for x, mask, row in peers:
        features = d.features(base, x[None], mask[None])
        with torch.inference_mode():
            probability = float(replay.change(torch.from_numpy(c.scaled(features, scale))).sigmoid()[0, 0])
        cases.append(dict(row, dtm034=c.decision(probability), dtm034Probability=probability))
    retention = all(v['correct'] == v['count'] for v in records['original']['summary'].values())
    h.require(retention, 'retention_gate_failed')
    result = dict(experiment='DTM034', model=h.ref(run_dir / 'last.pt'),
        execution=h.ref(run_dir / 'execution.json'), history=history, records=records,
        retainedCases=cases, radius=float(radius),
        bindingOriginalIndices=np.flatnonzero(margins - np.minimum(baseline_margins, FLOOR) < .01).tolist(),
        gradientConflictBefore=conflict_before, gradientConflictAfter=gradient_conflict(z, y, weights.numpy()),
        fitSeconds=fit_seconds, elapsedSeconds=time.monotonic() - started,
        retentionPassed=retention, independentEvaluation=False, productionEligible=False)
    h.write(run_dir / 'result.json', result, sealed=True)
    print('DTM034', 'radius', float(radius), 'fitSeconds', fit_seconds, flush=True)
    print({k: {g: r['correct'] for g, r in v['summary'].items()} for k, v in records.items()}, flush=True)

    # Independent companion: actual model/guard entrypoints, no fitting or threshold selection.
    x, truth, mask, _, _, groups, _ = d.c.setup()
    h.require(hashlib.sha256(x.tobytes()).hexdigest() == p['tensorSHA256'] and
              hashlib.sha256(mask.tobytes()).hexdigest() == p['maskSHA256'] and
              np.array_equal(truth, labels) and groups == p['groups'], 'guard_binding')
    guard = {}
    for name in ('global8', 'left8', 'center8'):
        v = localized(x, mask, name)
        with torch.inference_mode():
            probs = a.score(base, torch.from_numpy(v)).numpy()
        residuals = audit.residuals(v, mask)
        controls = {}
        for key, tolerance in audit.TOLERANCES.items():
            after, flags = audit.abstain(probs, residuals, tolerance)
            controls[key] = dict(summary=d.q.summarize(after, truth, groups, probs),
                flaggedIndices=np.flatnonzero(flags).tolist(), probabilities=after.tolist())
        guard[name] = dict(before=d.q.summarize(probs, truth, groups, original),
            tensorSHA256=hashlib.sha256(v.tobytes()).hexdigest(), residuals=residuals, controls=controls)
        print('guard', name, {k: r['summary']['identical'] for k, r in controls.items()}, flush=True)
    h.write(out / 'report.json', dict(version=1, modelResult=h.ref(run_dir / 'result.json'),
        source=h.ref(__file__), guardSource=h.ref(audit.__file__), parent=h.ref(d.READY / 'protocol.json'),
        guard=guard, elapsedSeconds=time.monotonic() - started, trainingRoleChanges=False,
        independentEvaluation=False, productionEligible=False), sealed=True)
    audit.sealed(out / 'report.json')
    h.require(sum(v.stat().st_size for root in (out, run_dir) for v in root.rglob('*') if v.is_file()) < 2 * 1024**3, 'output_budget')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output)
