"""RESET604 T4.2 Arm B Prototype: Comparative Within-Screen Focus Selector with explicit no_focus outcome.

Trains strictly on `v2-focus-supervision/membership.json` (`0` TVBench overlap) using
screen-relative comparative border/halo/contrast descriptors across sibling focusable controls,
plus an explicit screen-level `no_focus` gate calibrated on verified paired baseline scenes.
"""
import argparse
import hashlib
import json
import math
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image

import focus_compare604 as fc
import real_app_benchmark543 as r543
import research_queue as q
import tvbench
from roles559 import ROLES

VERSION = 'comparative-focus-604-v2'
DEFAULT_MEMBERSHIP = q.ROOT / 'reports/work/RESET604/membership/v2-focus-supervision/membership.json'
DEFAULT_HELDOUT = q.ROOT / 'reports/work/RESET604/membership/v2-focus-supervision/held-out.json'
DEFAULT_DEV_MANIFEST = q.ROOT / 'dataset/real_apps/tvbench-v1/dev-manifest-v2.json'
DEFAULT_CACHE_DIR = q.ROOT / '.build/debug-output/comparative-focus-604'
DEFAULT_MODELS_DIR = q.ROOT / 'reports/work/RESET604/models'
DEFAULT_JSON_OUT = q.ROOT / 'reports/work/RESET604/comparative-focus-armb-v2.json'
DEFAULT_MD_OUT = q.ROOT / 'reports/work/RESET604/comparative-focus-armb-v2.md'

RAW_FEATURE_NAMES = (
    'rim_mean_luma',
    'rim_p90_luma',
    'rim_p95_luma',
    'rim_std_luma',
    'halo_mean_luma',
    'halo_p90_luma',
    'halo_std_luma',
    'inner_mean_luma',
    'inner_p90_luma',
    'inner_std_luma',
    'rim_minus_halo_luma',
    'rim_minus_inner_luma',
    'rim_p90_minus_halo_p90',
    'rim_grad_mean',
    'rim_grad_p90',
    'halo_grad_mean',
    'rim_sat_mean',
    'rim_minus_halo_sat',
    'log_area',
    'aspect_ratio',
)


def _clip_rect(x1, y1, x2, y2, w_img, h_img):
    ix1 = max(0, min(w_img, int(round(x1))))
    iy1 = max(0, min(h_img, int(round(y1))))
    ix2 = max(ix1 + 1, min(w_img, int(round(x2))))
    iy2 = max(iy1 + 1, min(h_img, int(round(y2))))
    return ix1, iy1, ix2, iy2


def extract_candidate_raw_features(img_rgb, boxes):
    """Compute concentric rim/halo/inner photometric + gradient + geometry features for N candidate boxes."""
    if not boxes:
        return np.zeros((0, len(RAW_FEATURE_NAMES)), dtype=np.float32)

    h_img, w_img = img_rgb.shape[:2]
    arr = img_rgb.astype(np.float32) / 255.0
    luma = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    cmax = arr.max(axis=2)
    cmin = arr.min(axis=2)
    sat = np.where(cmax > 1e-4, (cmax - cmin) / np.maximum(cmax, 1e-4), 0.0)

    gx = np.abs(np.diff(luma, axis=1, prepend=luma[:, :1]))
    gy = np.abs(np.diff(luma, axis=0, prepend=luma[:1, :]))
    grad = gx + gy

    feats = []
    for box in boxes:
        bx, by, bw, bh = [float(v) for v in box]
        bx1, by1, bx2, by2 = _clip_rect(bx, by, bx + bw, by + bh, w_img, h_img)

        # Halo: 16% expanded box minus exact control box
        ex, ey = max(3.0, bw * 0.16), max(3.0, bh * 0.16)
        hx1, hy1, hx2, hy2 = _clip_rect(bx - ex, by - ey, bx + bw + ex, by + bh + ey, w_img, h_img)

        # Rim: border band spanning [box - 4px .. inner inset 12%]
        rim_pad = max(2.0, min(6.0, min(bw, bh) * 0.06))
        ox1, oy1, ox2, oy2 = _clip_rect(bx - rim_pad, by - rim_pad, bx + bw + rim_pad, by + bh + rim_pad, w_img, h_img)
        ix_in = max(2.0, bw * 0.12)
        iy_in = max(2.0, bh * 0.12)
        ix1, iy1, ix2, iy2 = _clip_rect(bx + ix_in, by + iy_in, bx + bw - ix_in, by + bh - iy_in, w_img, h_img)

        # Slice outer ROI once for mask speed
        sub_l = luma[hy1:hy2, hx1:hx2]
        sub_g = grad[hy1:hy2, hx1:hx2]
        sub_s = sat[hy1:hy2, hx1:hx2]
        sh, sw = sub_l.shape

        yy, xx = np.ogrid[:sh, :sw]
        gx_off, gy_off = xx + hx1, yy + hy1
        in_box = (gx_off >= bx1) & (gx_off < bx2) & (gy_off >= by1) & (gy_off < by2)
        in_inner = (gx_off >= ix1) & (gx_off < ix2) & (gy_off >= iy1) & (gy_off < iy2)
        in_outer_rim = (gx_off >= ox1) & (gx_off < ox2) & (gy_off >= oy1) & (gy_off < oy2)
        in_rim = in_outer_rim & (~in_inner)
        in_halo = ~in_box

        rim_l = sub_l[in_rim] if in_rim.any() else sub_l.ravel()
        halo_l = sub_l[in_halo] if in_halo.any() else sub_l.ravel()
        inner_l = sub_l[in_inner] if in_inner.any() else sub_l.ravel()
        rim_g = sub_g[in_rim] if in_rim.any() else sub_g.ravel()
        halo_g = sub_g[in_halo] if in_halo.any() else sub_g.ravel()
        rim_s = sub_s[in_rim] if in_rim.any() else sub_s.ravel()
        halo_s = sub_s[in_halo] if in_halo.any() else sub_s.ravel()

        r_mean = float(rim_l.mean())
        r_p90 = float(np.percentile(rim_l, 90))
        r_p95 = float(np.percentile(rim_l, 95))
        r_std = float(rim_l.std())
        h_mean = float(halo_l.mean())
        h_p90 = float(np.percentile(halo_l, 90))
        h_std = float(halo_l.std())
        i_mean = float(inner_l.mean())
        i_p90 = float(np.percentile(inner_l, 90))
        i_std = float(inner_l.std())
        rs_mean = float(rim_s.mean())
        hs_mean = float(halo_s.mean())

        feats.append([
            r_mean, r_p90, r_p95, r_std,
            h_mean, h_p90, h_std,
            i_mean, i_p90, i_std,
            r_mean - h_mean,
            r_mean - i_mean,
            r_p90 - h_p90,
            float(rim_g.mean()),
            float(np.percentile(rim_g, 90)),
            float(halo_g.mean()),
            rs_mean,
            rs_mean - hs_mean,
            math.log(max(1.0, bw * bh) / float(max(1, w_img * h_img))),
            math.log(max(0.1, bw / max(1.0, bh))),
        ])
    return np.asarray(feats, dtype=np.float32)


def build_comparative_features(raw_mat):
    """Augment N x D raw features with within-screen mean/median deviations and z-scores -> N x 4D."""
    n, d = raw_mat.shape
    if n == 0:
        return np.zeros((0, d * 4), dtype=np.float32)
    if n == 1:
        zeros = np.zeros_like(raw_mat)
        return np.concatenate([raw_mat, zeros, zeros, zeros], axis=1)
    mean = raw_mat.mean(axis=0, keepdims=True)
    med = np.median(raw_mat, axis=0, keepdims=True)
    std = raw_mat.std(axis=0, keepdims=True) + 1e-3
    delta_mean = raw_mat - mean
    delta_med = raw_mat - med
    z = delta_mean / std
    return np.concatenate([raw_mat, delta_mean, delta_med, z], axis=1)


def _extract_screen_record(row):
    """Extract candidate features and ground-truth focused index for a membership row."""
    img_path = q.ROOT / row['image']['path']
    focus_boxes = [c['bounds'] for c in row['controls'] if c['class'] == 'focused']
    cands = [c for c in row['controls'] if c['class'] in tvbench.SWIFT_FOCUSABLE_ROLES]
    if not cands:
        return None
    gt_idx = -1
    if row.get('focusState') == 'focused' and len(focus_boxes) == 1:
        fbox = focus_boxes[0]
        ious = [r543._iou(c['bounds'], fbox) for c in cands]
        best_i = int(np.argmax(ious))
        if ious[best_i] >= tvbench.MATCH_IOU:
            gt_idx = best_i
        else:
            return None
    elif row.get('focusState') != 'no_focus':
        return None

    with Image.open(img_path) as im:
        rgb = np.asarray(im.convert('RGB'))
    raw = extract_candidate_raw_features(rgb, [c['bounds'] for c in cands])
    comp = build_comparative_features(raw)
    return dict(
        id=row['id'],
        role=row['role'],
        sourceRole=row.get('sourceRole', 'unknown'),
        focusState=row['focusState'],
        gtIndex=gt_idx,
        features=comp,
    )


def load_or_extract_membership_screens(mem_path, cache_dir=DEFAULT_CACHE_DIR, limit=None):
    """Load or extract comparative candidate features across a focus-supervision membership."""
    mem = q.load(mem_path)
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(f"{q.digest(mem_path)}|{len(mem['rows'])}|{limit}".encode()).hexdigest()[:16]
    cache_file = cache_dir / f'screens-{key}.npz'
    meta_file = cache_dir / f'screens-{key}.json'
    if cache_file.is_file() and meta_file.is_file():
        meta = q.load(meta_file)
        arr = np.load(cache_file)
        X = arr['X']
        screens = []
        for item in meta:
            s, e = item['start'], item['end']
            screens.append(dict(item, features=X[s:e]))
        return screens

    rows = mem['rows'][:limit] if limit else mem['rows']
    with ThreadPoolExecutor(max_workers=8) as pool:
        extracted = [r for r in pool.map(_extract_screen_record, rows) if r is not None]

    xs, meta = [], []
    offset = 0
    for rec in extracted:
        f = rec['features']
        xs.append(f)
        meta.append(dict(
            id=rec['id'],
            role=rec['role'],
            sourceRole=rec['sourceRole'],
            focusState=rec['focusState'],
            gtIndex=rec['gtIndex'],
            start=offset,
            end=offset + len(f),
        ))
        offset += len(f)
    X_all = np.concatenate(xs, axis=0) if xs else np.zeros((0, len(RAW_FEATURE_NAMES) * 4), dtype=np.float32)
    np.savez_compressed(cache_file, X=X_all)
    q.save(meta_file, meta, replace=True)
    for item, rec in zip(meta, extracted):
        item['features'] = rec['features']
    return meta


def fit_comparative_selector(screens, seed=604, epochs=35, lr=0.05):
    """Train listwise comparative candidate scorer + explicit screen-level no_focus gate."""
    import torch
    import torch.nn as nn

    torch.manual_seed(seed)
    np.random.seed(seed)

GATE_FEATURE_DIM = 9


def _gate_vector(logits, probs, comp_mat, winner_idx):
    """Compute candidate-count-invariant screen summary features for the explicit no_focus gate."""
    order = np.argsort(-logits)
    m = len(order)
    top1 = float(logits[order[0]])
    top2 = float(logits[order[1]]) if m > 1 else top1 - 5.0
    med = float(np.median(logits))
    mean_l = float(logits.mean())
    std_l = float(logits.std()) + 1e-4
    top1_z = (top1 - mean_l) / std_l
    p1 = float(probs[order[0]])
    d = len(RAW_FEATURE_NAMES)
    return np.array([
        top1 - top2,
        top1 - med,
        top1_z,
        p1 * float(m),
        math.log(float(max(2, m))),
        float(comp_mat[winner_idx, 3 * d + 10]),
        float(comp_mat[winner_idx, 3 * d + 12]),
        float(comp_mat[winner_idx, 10]),
        float(comp_mat[winner_idx, 12]),
    ], dtype=np.float32)


def _train_scorer_torch(focus_screens, mu, sd, seed=604, epochs=35, lr=0.05):
    """Train listwise comparative scorer MLP on standardized candidate feature matrices."""
    import torch
    import torch.nn as nn

    torch.manual_seed(seed)
    src_counts = {}
    for s in focus_screens:
        src_counts[s['sourceRole']] = src_counts.get(s['sourceRole'], 0) + 1

    in_dim = int(mu.shape[1])
    scorer = nn.Sequential(
        nn.Linear(in_dim, 32),
        nn.GELU(),
        nn.Linear(32, 1),
    )
    opt = torch.optim.AdamW(scorer.parameters(), lr=lr, weight_decay=2e-2)

    max_m = max(len(s['features']) for s in focus_screens)
    n_scr = len(focus_screens)
    padded = np.zeros((n_scr, max_m, in_dim), dtype=np.float32)
    mask = np.full((n_scr, max_m), -1e9, dtype=np.float32)
    for idx, s in enumerate(focus_screens):
        m = len(s['features'])
        padded[idx, :m] = (s['features'] - mu) / sd
        mask[idx, :m] = 0.0

    X_pad = torch.from_numpy(padded)
    M_pad = torch.from_numpy(mask)
    y_idx = torch.tensor([s['gtIndex'] for s in focus_screens], dtype=torch.long)
    weights = [1.0 / max(1.0, math.sqrt(src_counts[s['sourceRole']])) for s in focus_screens]
    w_mean = sum(weights) / len(weights)
    w_t = torch.tensor([w / w_mean for w in weights], dtype=torch.float32)

    for _ in range(epochs):
        opt.zero_grad()
        logits = scorer(X_pad).squeeze(-1) + M_pad
        losses = nn.functional.cross_entropy(logits, y_idx, reduction='none')
        loss = (losses * w_t).mean()
        loss.backward()
        opt.step()

    scorer.eval()
    return scorer


def fit_comparative_selector(screens, seed=604, epochs=35, lr=0.05):
    """Train listwise comparative candidate scorer + OOF-calibrated explicit no_focus gate."""
    import torch
    import torch.nn as nn

    torch.manual_seed(seed)
    np.random.seed(seed)

    train_screens = [s for s in screens if s['role'] == 'train' and len(s['features']) >= 2]
    focus_train = [s for s in train_screens if s['focusState'] == 'focused' and s['gtIndex'] >= 0]
    q.require(focus_train, 'comparative_focus_no_focused_train_screens')

    # Standardize using train candidate statistics only
    all_train_x = np.concatenate([s['features'] for s in focus_train], axis=0)
    mu = all_train_x.mean(axis=0, keepdims=True)
    sd = all_train_x.std(axis=0, keepdims=True) + 1e-4
    in_dim = int(all_train_x.shape[1])

    # Fit full scorer on all focused train screens
    scorer = _train_scorer_torch(focus_train, mu, sd, seed=seed, epochs=epochs, lr=lr)

    def _summarize_with(model, feat_mat):
        with torch.no_grad():
            tx = torch.from_numpy(((feat_mat - mu) / sd).astype(np.float32))
            logits = model(tx).squeeze(-1).numpy()
        probs = np.exp(logits - logits.max())
        probs = probs / probs.sum()
        winner_idx = int(np.argmax(logits))
        return winner_idx, float(probs[winner_idx]), _gate_vector(logits, probs, feat_mat, winner_idx)

    # Generate 5-fold out-of-fold gate vectors for focused screens so margin thresholds are uninflated
    nf_screens = [s for s in train_screens if s['focusState'] == 'no_focus']
    gate_X, gate_y = [], []
    if nf_screens and len(focus_train) >= 10:
        n_folds = 5
        fold_ids = [idx % n_folds for idx in range(len(focus_train))]
        for f in range(n_folds):
            tr_sub = [s for idx, s in enumerate(focus_train) if fold_ids[idx] != f]
            va_sub = [s for idx, s in enumerate(focus_train) if fold_ids[idx] == f]
            fold_model = _train_scorer_torch(tr_sub, mu, sd, seed=seed + f + 1, epochs=epochs, lr=lr)
            for s in va_sub:
                _, _, gv = _summarize_with(fold_model, s['features'])
                gate_X.append(gv)
                gate_y.append(1.0)
    else:
        for s in focus_train:
            _, _, gv = _summarize_with(scorer, s['features'])
            gate_X.append(gv)
            gate_y.append(1.0)

    for s in nf_screens:
        _, _, gv = _summarize_with(scorer, s['features'])
        gate_X.append(gv)
        gate_y.append(0.0)

    gate_weights = None
    gate_mu = None
    gate_sd = None
    gate_thresh = 0.5
    if nf_screens:
        gX = np.asarray(gate_X, dtype=np.float32)
        gy = np.asarray(gate_y, dtype=np.float32)
        gate_mu = gX.mean(axis=0, keepdims=True)
        gate_sd = gX.std(axis=0, keepdims=True) + 1e-4
        gX_n = (gX - gate_mu) / gate_sd
        gate_layer = nn.Linear(gX.shape[1], 1)
        g_opt = torch.optim.AdamW(gate_layer.parameters(), lr=0.08, weight_decay=2e-2)
        sample_w = torch.from_numpy(np.where(gy > 0.5, 1.0, float(len(focus_train)) / max(1.0, len(nf_screens))).astype(np.float32))
        tX = torch.from_numpy(gX_n)
        ty = torch.from_numpy(gy)
        for _ in range(150):
            g_opt.zero_grad()
            out = gate_layer(tX).squeeze(-1)
            loss = (nn.functional.binary_cross_entropy_with_logits(out, ty, reduction='none') * sample_w).mean()
            loss.backward()
            g_opt.step()
        gate_layer.eval()
        gate_weights = (gate_layer.weight.detach().numpy().copy(), gate_layer.bias.detach().numpy().copy())
        with torch.no_grad():
            oof_probs = torch.sigmoid(gate_layer(tX).squeeze(-1)).numpy()
        best_bal = -1.0
        for th in np.linspace(0.25, 0.75, 51):
            tpr = float(((oof_probs >= th) & (gy > 0.5)).sum()) / max(1, int((gy > 0.5).sum()))
            tnr = float(((oof_probs < th) & (gy < 0.5)).sum()) / max(1, int((gy < 0.5).sum()))
            if tpr >= 0.85:
                bal = 0.5 * (tpr + tnr)
                if bal > best_bal:
                    best_bal = bal
                    gate_thresh = round(float(th), 4)

    return dict(
        mu=mu,
        sd=sd,
        scorerState=scorer.state_dict(),
        inDim=in_dim,
        gateMu=gate_mu,
        gateSd=gate_sd,
        gateWeights=gate_weights,
        gateThreshold=gate_thresh,
        trainStats=dict(focusedScreens=len(focus_train), noFocusScreens=len(nf_screens), gateThreshold=gate_thresh),
    )


def export_comparative_coreml(model_bundle, out_dir=q.ROOT / 'reports/work/RESET604/models'):
    """Export trained Arm B comparative scorer and no_focus gate to Core ML .mlpackage."""
    import coremltools as ct
    import torch
    import torch.nn as nn

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    in_dim = model_bundle['inDim']

    class _ScorerWrapper(nn.Module):
        def __init__(self, net, mu, sd):
            super().__init__()
            self.register_buffer('mu', torch.from_numpy(mu.astype(np.float32)))
            self.register_buffer('sd', torch.from_numpy(sd.astype(np.float32)))
            self.net = net

        def forward(self, x):
            return self.net((x - self.mu) / self.sd).squeeze(-1)

    base = nn.Sequential(nn.Linear(in_dim, 32), nn.GELU(), nn.Linear(32, 1))
    base.load_state_dict(model_bundle['scorerState'])
    base.eval()
    wrapped_scorer = _ScorerWrapper(base, model_bundle['mu'], model_bundle['sd']).eval()
    traced_scorer = torch.jit.trace(wrapped_scorer, torch.zeros((4, in_dim), dtype=torch.float32))
    scorer_ml = ct.convert(
        traced_scorer,
        inputs=[ct.TensorType(name='candidates', shape=(ct.RangeDim(1, 256), in_dim), dtype=np.float32)],
        outputs=[ct.TensorType(name='logits', dtype=np.float32)],
        convert_to='mlprogram',
        compute_precision=ct.precision.FLOAT32,
        minimum_deployment_target=ct.target.macOS14,
    )
    scorer_pkg = out_dir / 'ComparativeFocusScorer.mlpackage'
    scorer_ml.save(str(scorer_pkg))

    gate_pkg = None
    if model_bundle['gateWeights'] is not None:
        class _GateWrapper(nn.Module):
            def __init__(self, w, b, mu, sd):
                super().__init__()
                self.register_buffer('mu', torch.from_numpy(mu.astype(np.float32)))
                self.register_buffer('sd', torch.from_numpy(sd.astype(np.float32)))
                self.linear = nn.Linear(mu.shape[1], 1)
                with torch.no_grad():
                    self.linear.weight.copy_(torch.from_numpy(w.astype(np.float32)))
                    self.linear.bias.copy_(torch.from_numpy(b.astype(np.float32)))

            def forward(self, g):
                return torch.sigmoid(self.linear((g - self.mu) / self.sd).squeeze(-1))

        gw, gb = model_bundle['gateWeights']
        wrapped_gate = _GateWrapper(gw, gb, model_bundle['gateMu'], model_bundle['gateSd']).eval()
        traced_gate = torch.jit.trace(wrapped_gate, torch.zeros((1, GATE_FEATURE_DIM), dtype=torch.float32))
        gate_ml = ct.convert(
            traced_gate,
            inputs=[ct.TensorType(name='screenSummary', shape=(1, GATE_FEATURE_DIM), dtype=np.float32)],
            outputs=[ct.TensorType(name='hasFocusProb', dtype=np.float32)],
            convert_to='mlprogram',
            compute_precision=ct.precision.FLOAT32,
            minimum_deployment_target=ct.target.macOS14,
        )
        gate_pkg = out_dir / 'ComparativeFocusGate.mlpackage'
        gate_ml.save(str(gate_pkg))
    return dict(scorerPackage=str(scorer_pkg), gatePackage=str(gate_pkg) if gate_pkg else None)


def predict_comparative_on_detections(model_bundle, cases, detections_by_id, class_names=None, use_gate=True, coreml_paths=None, gate_threshold=None):
    """Score Stage 1 or supplied detections comparatively per frame (PyTorch or exported Core ML)."""
    import torch
    import torch.nn as nn

    eff_threshold = float(model_bundle['gateThreshold'] if gate_threshold is None else gate_threshold)
    if coreml_paths:
        import coremltools as ct
        scorer_ml = ct.models.MLModel(str(coreml_paths['scorerPackage']))
        gate_ml = ct.models.MLModel(str(coreml_paths['gatePackage'])) if coreml_paths.get('gatePackage') else None
    else:
        scorer_ml, gate_ml = None, None
        scorer = nn.Sequential(nn.Linear(model_bundle['inDim'], 32), nn.GELU(), nn.Linear(32, 1))
        scorer.load_state_dict(model_bundle['scorerState'])
        scorer.eval()
        mu, sd = model_bundle['mu'], model_bundle['sd']

    preds = {}
    for c in cases:
        if c.get('status', 'captured') != 'captured':
            continue
        cid = c['id']
        dets = detections_by_id.get(cid, [])
        focusable = [x for x in dets if tvbench._is_focusable_class(x.get('cls', x.get('class')), class_names=class_names)]
        unsupported_count = len(dets) - len(focusable)
        if not focusable:
            preds[cid] = dict(
                id=cid, imageSHA256=c['image']['sha256'], status='ok',
                detections=dets, focusBox=None,
                focusExecution=dict(
                    policy='comparative-armb-v2', threshold=eff_threshold,
                    winnerProbability=None, maxProbability=None,
                    eligibleCount=0, scoredCount=0, unsupportedRoleCount=unsupported_count,
                    cropRejectedCount=0, failedCount=0, candidates=[],
                ),
            )
            continue

        img_path = q.ROOT / c['image']['path']
        with Image.open(img_path) as im:
            rgb = np.asarray(im.convert('RGB'))
        raw = extract_candidate_raw_features(rgb, [x['box'] for x in focusable])
        comp = build_comparative_features(raw)

        if len(focusable) == 1:
            winner_idx = 0
            winner_prob = 1.0
            has_focus = not use_gate
            gate_prob = 0.0 if use_gate else 1.0
            logits = np.array([0.0], dtype=np.float32)
            probs = np.array([1.0], dtype=np.float32)
        else:
            if scorer_ml is not None:
                logits = np.asarray(scorer_ml.predict({'candidates': comp.astype(np.float32)})['logits'], dtype=np.float32).reshape(-1)
            else:
                with torch.no_grad():
                    tx = torch.from_numpy(((comp - mu) / sd).astype(np.float32))
                    logits = scorer(tx).squeeze(-1).numpy()
            exps = np.exp(logits - logits.max())
            probs = exps / exps.sum()
            winner_idx = int(np.argmax(logits))
            winner_prob = float(probs[winner_idx])
            gv = _gate_vector(logits, probs, comp, winner_idx)
            if use_gate and (gate_ml is not None or model_bundle['gateWeights'] is not None):
                if gate_ml is not None:
                    gate_prob = float(np.asarray(gate_ml.predict({'screenSummary': gv.reshape(1, -1)})['hasFocusProb']).reshape(-1)[0])
                else:
                    gw, gb = model_bundle['gateWeights']
                    gn = (gv - model_bundle['gateMu'][0]) / model_bundle['gateSd'][0]
                    gate_logit = float(np.dot(gn, gw[0]) + gb[0])
                    gate_prob = 1.0 / (1.0 + math.exp(-max(-20.0, min(20.0, gate_logit))))
                has_focus = gate_prob >= eff_threshold
            else:
                gate_prob = 1.0
                has_focus = True

        cands = [
            dict(
                cls=cand.get('cls', cand.get('class')),
                box=list(cand['box']),
                disposition='scored',
                probability=float(probs[idx]),
                comparativeLogit=float(logits[idx]),
                isFocused=(has_focus and idx == winner_idx),
            )
            for idx, cand in enumerate(focusable)
        ]
        preds[cid] = dict(
            id=cid,
            imageSHA256=c['image']['sha256'],
            status='ok',
            detections=dets,
            focusBox=list(focusable[winner_idx]['box']) if has_focus else None,
            focusExecution=dict(
                policy='comparative-armb-v2',
                threshold=eff_threshold,
                winnerProbability=winner_prob if has_focus else None,
                maxProbability=float(max(probs)) if len(probs) else None,
                hasFocusGateProb=round(gate_prob, 6),
                eligibleCount=len(focusable),
                scoredCount=len(focusable),
                unsupportedRoleCount=unsupported_count,
                cropRejectedCount=0,
                failedCount=0,
                candidates=cands,
            ),
        )
    return preds


def run_armb_experiment(
    mem_path=DEFAULT_MEMBERSHIP,
    heldout_path=DEFAULT_HELDOUT,
    dev_manifest_path=DEFAULT_DEV_MANIFEST,
    models_dir=DEFAULT_MODELS_DIR,
    json_out=DEFAULT_JSON_OUT,
    md_out=DEFAULT_MD_OUT,
):
    """Train comparative Arm B on v2-focus-supervision only, export Core ML, verify parity, and compare vs FocusRing."""
    screens = load_or_extract_membership_screens(mem_path)
    model_bundle = fit_comparative_selector(screens)
    coreml_paths = export_comparative_coreml(model_bundle, out_dir=models_dir)

    # 1. Held-out TTR validation (from v2-focus-supervision/held-out.json) via exported Core ML
    held_doc = q.load(heldout_path) if Path(heldout_path).is_file() else dict(rows=[])
    held_cases, held_dets, held_labels = [], {}, {}
    for row in held_doc.get('rows', []):
        cands = [c for c in row['controls'] if c['class'] in tvbench.SWIFT_FOCUSABLE_ROLES]
        if len(cands) < 2:
            continue
        fboxes = [c['bounds'] for c in row['controls'] if c['class'] == 'focused']
        if row.get('focusState') == 'focused' and len(fboxes) != 1:
            continue
        held_cases.append(dict(
            id=row['id'], app=row.get('sourceRole', 'ttr-heldout'), flow=row.get('group', 'g'),
            status='captured', image=row['image'],
        ))
        held_dets[row['id']] = [dict(cls=c['class'], box=c['bounds'], score=1.0) for c in cands]
        held_labels[row['id']] = dict(
            complete=True,
            focus=dict(state=row['focusState'], box=fboxes[0] if fboxes else None),
        )
    held_manifest = dict(cases=held_cases)
    held_preds_gated = predict_comparative_on_detections(
        model_bundle, held_cases, held_dets, class_names=list(ROLES), use_gate=True, coreml_paths=coreml_paths,
    )
    held_preds_nogate = predict_comparative_on_detections(
        model_bundle, held_cases, held_dets, class_names=list(ROLES), use_gate=False, coreml_paths=coreml_paths,
    )
    held_sum_gated = fc.summarize_focus_condition('heldout_armb_gated', held_manifest, held_preds_gated, held_labels)
    held_sum_nogate = fc.summarize_focus_condition('heldout_armb_ungated', held_manifest, held_preds_nogate, held_labels)

    # 2. Dev real-app evaluation using identical proposals + supplied boxes via exported Core ML
    dev_manifest = q.load(dev_manifest_path)
    labels_by_id = {c['id']: q.load(q.ROOT / c['labels']['path']) for c in dev_manifest['cases']}
    import coremltools as ct
    v3_baseline_preds = tvbench.predict_coreml(
        fc.DEFAULT_MODELS['phase6b_tvos_v3'], dev_manifest['cases'], conf=0.25,
        focusring_model=fc.DEFAULT_FOCUSRING, focusring_threshold=0.85, nms_iou=tvbench.NMS_IOU,
    )
    v3_ctrl = fc.summarize_focus_condition('phase6b_tvos_v3_focusring', dev_manifest, v3_baseline_preds, labels_by_id)
    ctrl_outcomes = v3_ctrl['outcomesById']

    dev_results = [v3_ctrl]
    parity_checks = []
    for name, mlpkg in fc.DEFAULT_MODELS.items():
        if not Path(mlpkg).exists():
            continue
        mod = ct.models.MLModel(str(mlpkg))
        cnames = tvbench.model_class_names(mod)
        dets_by_id = tvbench._coreml_predict_preproc_keyed(mod, cnames, dev_manifest['cases'], conf=0.25, nms_iou=tvbench.NMS_IOU)
        for gated_flag, tag in ((True, 'armb_gated'), (False, 'armb_ungated')):
            preds = predict_comparative_on_detections(
                model_bundle, dev_manifest['cases'], dets_by_id, class_names=cnames, use_gate=gated_flag, coreml_paths=coreml_paths,
            )
            if name == 'phase6b_tvos_v3' and gated_flag:
                pt_preds = predict_comparative_on_detections(
                    model_bundle, dev_manifest['cases'], dets_by_id, class_names=cnames, use_gate=True, coreml_paths=None,
                )
                max_logit_diff = 0.0
                max_gate_diff = 0.0
                winner_matches = 0
                for cid, cp in preds.items():
                    pp = pt_preds[cid]
                    if cp['focusBox'] == pp['focusBox']:
                        winner_matches += 1
                    g_c = cp['focusExecution'].get('hasFocusGateProb')
                    g_p = pp['focusExecution'].get('hasFocusGateProb')
                    if isinstance(g_c, float) and isinstance(g_p, float):
                        max_gate_diff = max(max_gate_diff, abs(g_c - g_p))
                    for cc, pc in zip(cp['focusExecution']['candidates'], pp['focusExecution']['candidates']):
                        max_logit_diff = max(max_logit_diff, abs(cc['comparativeLogit'] - pc['comparativeLogit']))
                parity_checks.append(dict(
                    frames=len(preds),
                    winnerMatches=winner_matches,
                    maxLogitDiff=round(max_logit_diff, 6),
                    maxGateProbDiff=round(max_gate_diff, 6),
                ))
            dev_results.append(fc.summarize_focus_condition(f'{name}_{tag}', dev_manifest, preds, labels_by_id, control_outcomes=ctrl_outcomes))

    # Supplied reference boxes (on NewsTV complete screens + focusable objects across manifest)
    sup_dets = fc.supplied_detections(dev_manifest, focusable_only=True)
    for gated_flag, tag in ((True, 'armb_gated'), (False, 'armb_ungated')):
        preds = predict_comparative_on_detections(
            model_bundle, dev_manifest['cases'], sup_dets, class_names=dev_manifest['classes'], use_gate=gated_flag, coreml_paths=coreml_paths,
        )
        dev_results.append(fc.summarize_focus_condition(f'supplied_reference_{tag}', dev_manifest, preds, labels_by_id, control_outcomes=ctrl_outcomes))

    report = dict(
        version=VERSION,
        metricsStatus='provisional',
        trainMembership=dict(path=str(mem_path), sha256=q.digest(mem_path)),
        trainStats=model_bundle['trainStats'],
        coremlArtifacts=coreml_paths,
        coremlPyTorchParity=parity_checks,
        heldOutTTR=[
            {k: held_sum_gated[k] for k in ('condition', 'overall', 'perApp')},
            {k: held_sum_nogate[k] for k in ('condition', 'overall', 'perApp')},
        ],
        devComparison=[{k: v for k, v in r.items() if k != 'outcomesById'} for r in dev_results],
    )
    if json_out:
        Path(json_out).parent.mkdir(parents=True, exist_ok=True)
        q.save(json_out, report, replace=True)
    if md_out:
        par = parity_checks[0] if parity_checks else {}
        lines = [
            '# RESET604 Comparative Focus Selector (`T4.2 Arm B` v2 Core ML, `provisional`)',
            '',
            f"- Trained on `v2-focus-supervision` `train` split only (`{model_bundle['trainStats']['focusedScreens']}` focused + `{model_bundle['trainStats']['noFocusScreens']}` `no_focus` frames; `0` TVBench frames).",
            f"- OOF-calibrated gate threshold: `{model_bundle['gateThreshold']}`; Core ML parity (`phase6b_tvos_v3`): `{par.get('winnerMatches')}/{par.get('frames')}` winner matches, `maxLogitDiff={par.get('maxLogitDiff')}`, `maxGateProbDiff={par.get('maxGateProbDiff')}`.",
            '',
            '## TTR Held-Out (`v2-focus-supervision/held-out.json`)',
            '',
            '| Condition | Correct Focused | Wrong | Abstain | No-Focus False Sel |',
            '| --- | --- | --- | --- | --- |',
        ]
        for hr in report['heldOutTTR']:
            o = hr['overall']
            lines.append(
                f"| `{hr['condition']}` | {o['correctFocused']} / {o['focusedFrames']} | "
                f"{o['wrongSelection']} | {o['abstention']} | {o['noFocusFalseSelections']} / {o['noFocusFrames']} |"
            )
        lines.extend([
            '',
            '## TVBench Development (`dev-manifest-v2.json`, 42 frames)',
            '',
            '| Condition | Focused Correct | Wrong | Abstain | No-Focus False Sel | Complete Subset (23) | Recovered / Lost vs v3+FocusRing |',
            '| --- | --- | --- | --- | --- | --- | --- |',
        ])
        for dr in report['devComparison']:
            o = dr['overall']
            co = dr['completeOnly']
            lines.append(
                f"| `{dr['condition']}` | {o['correctFocused']} / {o['focusedFrames']} | "
                f"{o['wrongSelection']} | {o['abstention']} | {o['noFocusFalseSelections']} / {o['noFocusFrames']} | "
                f"{co['correctFocused']} / {co['focusedFrames']} (+{co['noFocusCorrectAbstention']}/{co['noFocusFrames']} nf) | "
                f"+{len(dr['recoveredVsControl'])} / -{len(dr['lostPreviousSuccessesVsControl'])} |"
            )
        Path(md_out).parent.mkdir(parents=True, exist_ok=True)
        Path(md_out).write_text('\n'.join(lines) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--membership', type=Path, default=DEFAULT_MEMBERSHIP)
    parser.add_argument('--heldout', type=Path, default=DEFAULT_HELDOUT)
    parser.add_argument('--dev-manifest', type=Path, default=DEFAULT_DEV_MANIFEST)
    parser.add_argument('--json-out', type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument('--md-out', type=Path, default=DEFAULT_MD_OUT)
    args = parser.parse_args()
    rep = run_armb_experiment(
        mem_path=args.membership, heldout_path=args.heldout, dev_manifest_path=args.dev_manifest,
        json_out=args.json_out, md_out=args.md_out,
    )
    print(json.dumps(dict(
        heldOutTTR=rep['heldOutTTR'],
        devComparison=[{k: d[k] for k in ('condition', 'overall', 'completeOnly', 'recoveredVsControl', 'lostPreviousSuccessesVsControl')} for d in rep['devComparison']],
    ), indent=2))


if __name__ == '__main__':
    main()
