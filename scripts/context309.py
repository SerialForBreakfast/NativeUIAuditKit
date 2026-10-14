"""Compare full-frame context with a second aligned view using the existing trainer."""
import argparse
import copy
from pathlib import Path
import time
import types
import numpy as np
import condition292 as prior

c = prior.prior
base = c.base
torch = base.torch
OUT = base.ROOT/'reports/work/FOCUS-309'
VERSION = 'context309-v1'


def aligned_view(images):
    """Select one 32-pixel window from image differences, without labels."""
    base.require(images.ndim == 4 and images.shape[1:] == (6, 128, 192), 'view_shape')
    local = c.model.change_inputs(None, images)[:, 9:].mean(1, keepdim=True)
    energy = torch.nn.functional.avg_pool2d(local, 5, stride=1, padding=2)
    peak = energy.flatten(1).argmax(1)
    x = ((peak % 192)-16).clamp(0, 160)
    y = ((peak // 192)-16).clamp(0, 96)
    # Both frames use one window. Edge windows retain their full size.
    axis = (torch.arange(32, device=images.device, dtype=images.dtype)+.5)
    gx = 2*(x[:, None, None]+axis[None, None, :])/192-1
    gy = 2*(y[:, None, None]+axis[None, :, None])/128-1
    grid = torch.stack((gx.expand(-1, 32, -1), gy.expand(-1, -1, 32)), -1)
    crop = torch.nn.functional.grid_sample(images, grid, align_corners=False)
    crop = torch.nn.functional.interpolate(crop, size=(128, 192), mode='bilinear', align_corners=False)
    identical = (images[:, :3] == images[:, 3:]).flatten(1).all(1)
    return torch.where(identical[:, None, None, None], images, crop)


class ContextChange(torch.nn.Module):
    def __init__(self, old, local):
        super().__init__()
        self.whole = copy.deepcopy(old)
        self.detail = copy.deepcopy(old[:10])
        self.correction = torch.nn.Linear(64, 1)
        torch.nn.init.zeros_(self.correction.weight)
        torch.nn.init.zeros_(self.correction.bias)
        self.local = local

    def forward(self, images):
        whole = c.model.change_inputs(None, images)
        view = aligned_view(images) if self.local else images
        detail = c.model.change_inputs(None, view)
        context = self.whole[:10](whole)
        features = torch.cat((context, self.detail(detail)), 1)
        return self.whole[10](context)+self.correction(features)


def identity_inputs(self, images):
    return images


def extend(net, local):
    base.require(type(local) is bool, 'view_mode')
    net.change = ContextChange(net.change, local)
    net.change_inputs = types.MethodType(identity_inputs, net)
    return net


def load_candidate(path):
    saved = torch.load(path, map_location='cpu', weights_only=True)
    base.require(saved.get('representation') == VERSION and type(saved.get('local')) is bool, 'checkpoint_contract')
    net = extend(c.model.extend(base.worker.make_model(torch, paired_context=True)), saved['local'])
    net.load_state_dict(saved['state'])
    return net.eval()


def tiny_inputs():
    from PIL import Image
    from diagnose_signal95 import encoded
    path = base.ROOT/'reports/work/FOCUS-302/capture-r2/analysis/evaluation.json'
    rows = base.read(path)['rows']; values = []
    for row in rows:
        meta_path = base.checked(row['metadata']); meta = base.read(meta_path)
        images = []
        for prefix in ('unfocused', 'focused'):
            ref = dict(path=str((meta_path.parent/meta[prefix+'_png']).relative_to(base.ROOT)),
                       sha256=meta[prefix+'_sha256'])
            with Image.open(base.checked(ref)) as image: images.append(image.convert('RGB'))
        if row['condition'] == 'reverse': images.reverse()
        if row['condition'] == 'same-before': images[1] = images[0]
        if row['condition'] == 'same-after': images[0] = images[1]
        values.append(encoded(*images, (192, 128))[0])
    return np.stack(values), rows, base.ref(path)


def run(out):
    base.require(not out.exists(), 'output_collision')
    started = time.monotonic(); torch.set_num_threads(2)
    manifest, membership, full, labels, weights, extra, controls, _, registration = c.prepare()
    added = prior.mix(full[controls], extra, labels[1660:1740], True)
    values = np.concatenate((full, added, base.reporting.reverse(added)))
    del full, extra, added
    original = base.ROOT/'reports/work/TRANSITION-292/DTM085'
    base.require(base.sha(values.tobytes()) == base.read(original/'registration.json')['trainingSHA256'], 'schedule_identity')
    initializer = base.checked(base.read(original/'result.json')['model'])
    tiny, tiny_rows, tiny_ref = tiny_inputs()
    config = dict(registration['configuration'], epochs=30)
    out.mkdir(parents=True)
    base.write(out/'registration.json', dict(version=VERSION, runner=base.ref(Path(__file__)),
        trainer=base.ref(Path(base.trainer.__file__)), parent=base.ref(prior.OUT/'registration.json'),
        initializer=base.ref(initializer), configuration=config, torchVersion=str(torch.__version__),
        numpyVersion=np.__version__, device='cpu', trainingSHA256=base.sha(values.tobytes()),
        labelsSHA256=base.sha(labels.tobytes()), weightsSHA256=base.sha(weights.tobytes()),
        membership=base.ref(base.PACKAGE/'membership.json'), package=base.ref(base.PACKAGE/'manifest.json'),
        tiny=tiny_ref, tinySHA256=base.sha(tiny.tobytes()), rows=len(values),
        hypotheses=['A local enlarged view improves small-change detection when full-frame context remains available.',
                    'A second full-frame branch controls for extra parameters and continued training.'],
        runs={'whole-control': False, 'context-detail': True}, thresholds=[.15, .85],
        selection='fixed-last; no audit-based checkpoint selection', outputCapBytes=128*1024**2,
        detailWindow=[32, 32], selector='maximum local-residual energy with 5-pixel averaging',
        initialCorrection='zero', wallTimeLimit=None, rolesChanged=False, productionEligible=False,
        acceptance='Improve tiny changes without losing previous correct decisions at unchanged thresholds.',
        limitation='Detail enlarges encoded pixels. It does not recover original-image detail. Tiny cases are development only.'))
    refs = {'DTM085': c.model.load_candidate(initializer)}
    refs['DTM083'] = c.model.load_candidate(base.checked(base.read(c.OUT/'DTM083/result.json')['model']))
    sanity = np.load(base.PACKAGE/'sanity.npy', allow_pickle=False)
    completed = {}
    for name, local in [('whole-control', False), ('context-detail', True)]:
        folder = out/name; folder.mkdir()
        torch.manual_seed(42)
        net = extend(c.model.load_candidate(initializer), local)
        delta = float(np.abs(base.worker.score(net, sanity)-base.worker.score(refs['DTM085'], sanity)).max())
        base.require(delta <= 1e-6, 'initial_parity')
        base.write(folder/'registration.json', dict(parent=base.ref(out/'registration.json'), local=local,
            maximumInitialError=delta, parameters=sum(p.numel() for p in net.parameters())))
        begin = time.monotonic()
        def progress(row):
            base.write(folder/f"epoch-{row['epoch']:04d}.json", row)
            print(name, row, flush=True)
        net, history = base.trainer.fit(net, torch.from_numpy(values), torch.from_numpy(labels), config,
                                       progress, torch.from_numpy(weights))
        torch.save(dict(state=net.state_dict(), representation=VERSION, local=local,
                        registration=base.ref(folder/'registration.json')), folder/'last.pt')
        restored = load_candidate(folder/'last.pt')
        base.require(np.array_equal(base.worker.score(net, sanity), base.worker.score(restored, sanity)), 'reload_parity')
        base.write(folder/'fit.json', dict(history=history, fit=base.metrics(restored, values, labels),
            model=base.ref(folder/'last.pt'), checkpointParity=True, seconds=time.monotonic()-begin))
        # Reuse the existing evaluator, including all disturbance strengths and reversals.
        evaluation = base.evaluate_full(restored, refs, manifest)
        base.write(folder/'evaluation.json', evaluation)
        p = base.worker.score(restored, tiny)
        small = []
        for condition in sorted({r['condition'] for r in tiny_rows}):
            ids = [i for i, row in enumerate(tiny_rows) if row['condition'] == condition]
            small.append(dict(condition=condition, summary=base.trainer.w.summary(p[ids],
                np.array([tiny_rows[i]['changed'] for i in ids])), probabilities=p[ids].tolist()))
        base.write(folder/'tiny.json', dict(input=tiny_ref, results=small, independentFinalAudit=False))
        completed[name] = dict(regressionPassed=evaluation['regressionPassed'], tiny=small,
                               seconds=time.monotonic()-begin, model=base.ref(folder/'last.pt'))
        if not local: refs['whole-control'] = restored
    size = sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
    base.require(size < 128*1024**2, 'output_budget')
    base.write(out/'completion.json', dict(runs=completed, outputBytes=size,
        seconds=time.monotonic()-started, rolesChanged=False, productionEligible=False))
    print('Matched experiment complete.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', required=True, action='store_true')
    parser.add_argument('--output', type=Path, default=OUT)
    args = parser.parse_args()
    base.require(args.output.resolve().is_relative_to(base.ROOT) and args.output.resolve() != base.ROOT, 'output_boundary')
    run(args.output)
