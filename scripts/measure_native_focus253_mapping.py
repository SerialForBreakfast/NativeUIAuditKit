"""Separate source mapping from native lighting on retained artwork pairs."""
import base64
import hashlib
import io
import json
import re
import time
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates

import measure_native_focus253 as m
import measure_native_focus253_edges as edges


def select_rows(rows):
    groups = ('234:recipe-00', '234:recipe-03')
    selected = [r for r in rows if r['group'] in groups and r['changed']
                and 'original_capture' in r['conditions']]
    if (len(selected) != 8 or len({r['id'] for r in selected}) != 8
            or any(r['role'] != 'train' for r in selected)
            or any(sum(r['group'] == g for r in selected) != 4 for g in groups)):
        raise ValueError('mapping_membership')
    return sorted(selected, key=lambda r: (r['group'], r['id']))


def decode_asset(asset):
    encoded = asset['bytes']
    if not isinstance(encoded, str) or len(encoded) > 24_000_000:
        raise ValueError('asset_size')
    raw = base64.b64decode(encoded, validate=True)
    if hashlib.sha256(raw).hexdigest() != asset['sha256']:
        raise ValueError('asset_hash')
    with Image.open(io.BytesIO(raw)) as image:
        if (image.format != 'PNG' or image.size != (asset['width'], asset['height'])
                or image.width * image.height > 16_777_216):
            raise ValueError('asset_dimensions')
        rgba = np.asarray(image.convert('RGBA'), dtype=np.float64) / 255
    return rgba


def endpoint_scene(doc, image_hash):
    matches = [doc[key] for key, hash_key in [('baseline_scene', 'unfocused_sha256'),
                                             ('focused_scene', 'focused_sha256')]
               if doc[hash_key] == image_hash]
    if len(matches) != 1:
        raise ValueError('endpoint_binding')
    return matches[0]


def source_for(row):
    metadata_path = m.checked(row['metadata'][1])
    doc = json.loads(metadata_path.read_text())
    scene = endpoint_scene(doc, row['images'][1]['sha256'])
    ref = scene['recipe']['source_reference']
    path = (metadata_path.parent / ref['path']).resolve()
    if not path.is_relative_to(metadata_path.parent.resolve()):
        raise ValueError('recipe_path')
    if ref['bytes'] > 32_000_000 or path.stat().st_size != ref['bytes']:
        raise ValueError('recipe_size')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ref['sha256']:
        raise ValueError('recipe_hash')
    recipe = json.loads(raw)
    composition = recipe['appearance']['composition']
    items = [item for region in composition['regions'] for item in region['items']
             if item['id'] == scene['focused_element_id']]
    if len(items) != 1:
        raise ValueError('target_item')
    content = composition['contents'][items[0]['content']]
    reference = content['asset']
    assets = [a for a in composition['asset_pack']['assets'] if a['sha256'] == reference['sha256']]
    if len(assets) != 1:
        raise ValueError('asset_identity')
    rgba = decode_asset(assets[0])
    info = dict(recipeSource={'path': str(path.relative_to(m.ROOT)), 'sha256': ref['sha256']},
                assetSHA256=reference['sha256'], sourceDimensions=[rgba.shape[1], rgba.shape[0]],
                fit=reference['fit'], anchor=reference['anchor'],
                opaque=bool(np.all(rgba[..., 3] == 1)),
                assetFamily=assets[0]['family_id'],
                cleanBackgroundAvailable=False, nativeAlphaSilhouetteAvailable=False)
    return rgba, reference, info


def map_asset(rgba, shape, box, fit, anchor):
    """Sample premultiplied artwork at pixel centers using a declared content rule."""
    box = np.asarray(box, float)
    anchor = np.asarray(anchor, float)
    if (box.shape != (4,) or not np.isfinite(box).all() or min(box[2:]) <= 0
            or anchor.shape != (2,) or not np.isfinite(anchor).all()
            or np.any(anchor < 0) or np.any(anchor > 1) or fit not in ('fill', 'fit')):
        raise ValueError('mapping_parameters')
    if (rgba.ndim != 3 or rgba.shape[2] != 4 or not np.isfinite(rgba).all()
            or np.any(rgba < 0) or np.any(rgba > 1)):
        raise ValueError('asset_pixels')
    height, width = rgba.shape[:2]
    scale = (max if fit == 'fill' else min)(box[2] / width, box[3] / height)
    origin = box[:2] + (box[2:] - [width * scale, height * scale]) * anchor
    y, x = np.indices(shape, dtype=float)
    sx = (x + .5 - origin[0]) / scale - .5
    sy = (y + .5 - origin[1]) / scale - .5
    valid = ((x + .5 >= origin[0]) & (x + .5 < origin[0] + width * scale)
             & (y + .5 >= origin[1]) & (y + .5 < origin[1] + height * scale)
             & (x + .5 >= box[0]) & (x + .5 < box[0] + box[2])
             & (y + .5 >= box[1]) & (y + .5 < box[1] + box[3]))
    premultiplied = np.concatenate([rgba[..., :3] * rgba[..., 3:], rgba[..., 3:]], axis=2)
    sampled = np.stack([map_coordinates(premultiplied[..., c], [sy, sx], order=1, mode='nearest')
                        for c in range(4)], axis=-1)
    sampled *= valid[..., None]
    alpha = sampled[..., 3]
    rgb = np.divide(sampled[..., :3], alpha[..., None], out=np.zeros_like(sampled[..., :3]),
                    where=alpha[..., None] > 0)
    return rgb, alpha


def frequency_scores(predicted, target, mask):
    if mask.dtype != bool or mask.shape != target.shape[:2] or mask.sum() < 100:
        raise ValueError('mapping_support')
    low_p = gaussian_filter(predicted, (2, 2, 0), mode='nearest')
    low_t = gaussian_filter(target, (2, 2, 0), mode='nearest')
    return dict(raw=m.metrics(predicted, target, mask),
                highFrequencyMAE255=float(np.mean(np.abs(((predicted-low_p)-(target-low_t))[mask]))*255),
                lowFrequencyMAE255=float(np.mean(np.abs((low_p-low_t)[mask]))*255))


def color_upper_bound(image, target, mask):
    """Fit and score the same pixels. This is an oracle diagnostic only."""
    coefficients = []
    for channel in range(3):
        x = np.c_[image[..., channel][mask], np.ones(int(mask.sum()))]
        coefficients.append(np.linalg.lstsq(x, target[..., channel][mask], rcond=None)[0])
    coefficients = np.asarray(coefficients)
    output = np.clip(image * coefficients[:, 0] + coefficients[:, 1], 0, 1)
    return output, coefficients.tolist()


def normalized_coordinates(shape, center, box, ratios, mode):
    ratios = np.asarray(ratios, float)
    box = np.asarray(box, float)
    if (mode not in ('body', 'longest') or ratios.shape != (2,) or not np.isfinite(ratios).all()
            or np.any(ratios <= 0) or box.shape != (4,) or not np.isfinite(box).all()
            or min(box[2:]) <= 0):
        raise ValueError('coordinate_parameters')
    denominator = ratios * (box[2:] if mode == 'body' else max(box[2:]))
    y, x = np.indices(shape, dtype=float)
    return (x-center[0])/denominator[0], (y-center[1])/denominator[1]


def coordinate_reference(rows):
    fitting = [r for r in rows if r['group'] == '233:recipe-00' and r['changed']
               and 'original_capture' in r['conditions']]
    if len(fitting) != 4 or any(r['role'] != 'train' for r in fitting):
        raise ValueError('coordinate_fit_membership')
    ratios = {'body': [], 'longest': []}
    for row in fitting:
        (before, _), _, _, _, regions = m.prepare(row, regions=True)
        denominators = np.asarray(before.shape[1::-1])/2
        ratios['body'].append(denominators/regions['before'][2:])
        ratios['longest'].append(denominators/max(regions['before'][2:]))
    return dict(parameters={k: np.median(v, axis=0).tolist() for k, v in ratios.items()},
                fittingIDs=[r['id'] for r in fitting])


def run(output_name='mapping-r4', compare_coordinates=False):
    if not re.fullmatch(r'mapping-r4(?:-[a-z0-9]+)?', output_name):
        raise ValueError('output_name')
    destination = m.OUT / output_name
    if destination.exists():
        raise ValueError('output_collision')
    start = time.monotonic()
    prior_path = m.OUT / 'formula-r2/result.json'
    prior = json.loads(prior_path.read_text())
    membership = m.ROOT / 'reports/work/TRANSITION-249/artifacts/package/membership.json'
    if hashlib.sha256(membership.read_bytes()).hexdigest() != prior['membershipSHA256']:
        raise ValueError('changed_membership')
    all_rows = json.loads(membership.read_text())['rows']
    rows = select_rows(all_rows)
    coordinate_fit = coordinate_reference(all_rows) if compare_coordinates else None
    destination.mkdir()
    results = []
    for index, row in enumerate(rows):
        (before, after), center, interior, observed, regions = m.prepare(row, regions=True)
        rgba, reference, info = source_for(row)
        resting, rest_alpha = map_asset(rgba, interior.shape, regions['before'], reference['fit'], reference['anchor'])
        focused, focus_alpha = map_asset(rgba, interior.shape, regions['after'], reference['fit'], reference['anchor'])
        # Inset the resting body separately. Focused support is not resting support.
        box = regions['before'].copy()
        inset = .15 * min(box[2:]); box[:2] += inset; box[2:] -= 2 * inset
        rest_mask = edges.rectangle(interior.shape, box) & (rest_alpha > .999)
        mask = interior & (focus_alpha > .999)
        if min(mask.sum(), rest_mask.sum()) < 100:
            raise ValueError('opaque_support')
        x, y = m.coordinates(interior.shape, center)
        geometry = [observed['scaleX'], observed['scaleY'], *observed['centerShift'], 1, 0]
        warped = m.warp(before, geometry, center)
        source_highlight = m.highlight(focused, x, y, prior['selectedParameters'])
        screenshot_highlight = m.highlight(warped, x, y, prior['selectedParameters'])
        outputs = {'sourceRaw': focused, 'sourceHighlight': source_highlight,
                   'screenshotHighlight': screenshot_highlight}
        if coordinate_fit:
            for mode, ratios in coordinate_fit['parameters'].items():
                cx, cy = normalized_coordinates(interior.shape, center, regions['before'], ratios, mode)
                outputs[mode+'Coordinates'] = m.highlight(warped, cx, cy, prior['selectedParameters'])
        trials = []
        for sigma in (0, 1, 2, 4):
            blurred = gaussian_filter(focused, (sigma, sigma, 0), mode='nearest') if sigma else focused
            corrected, coefficients = color_upper_bound(blurred, after, mask)
            trials.append(dict(sigmaPixels=sigma, coefficientsRGB=coefficients,
                               scores=frequency_scores(corrected, after, mask),
                               role='same_pair_fitted_diagnostic_not_transfer'))
        result = dict(id=row['id'], group=row['group'], role=row['role'], sourceImages=row['images'],
                      sourceMetadata=row['metadata'], source=info, observedGeometry=observed,
                      resting=frequency_scores(resting, before, rest_mask),
                      focused={name: frequency_scores(value, after, mask) for name, value in outputs.items()},
                      blurColorDiagnostics=trials, support={'resting': int(rest_mask.sum()), 'focused': int(mask.sum())})
        results.append(result)
        if index % 4 == 0:
            panels = [before, after, source_highlight, screenshot_highlight,
                      np.minimum(abs(source_highlight-after)*4, 1)]
            panel = np.concatenate([np.where(mask[..., None], v, 0) for v in panels], axis=1)
            Image.fromarray(np.rint(panel*255).astype('uint8')).save(destination / (row['group'].replace(':', '-')+'.png'))
    summary = {}
    for group in sorted({r['group'] for r in results}):
        selected = [r for r in results if r['group'] == group]
        summary[group] = dict(restingMAE255=float(np.mean([r['resting']['raw']['meanAbsolute255'] for r in selected])),
            focusedMAE255={name: float(np.mean([r['focused'][name]['raw']['meanAbsolute255'] for r in selected]))
                          for name in selected[0]['focused']},
            highFrequencyMAE255={name: float(np.mean([r['focused'][name]['highFrequencyMAE255'] for r in selected]))
                                for name in selected[0]['focused']},
            blurColorMAE255={str(s): float(np.mean([r['blurColorDiagnostics'][i]['scores']['raw']['meanAbsolute255'] for r in selected]))
                             for i, s in enumerate((0, 1, 2, 4))})
    report = dict(version=1, seconds=time.monotonic()-start, results=results, summary=summary,
                  membershipSHA256=prior['membershipSHA256'], priorSHA256=hashlib.sha256(prior_path.read_bytes()).hexdigest(),
                  scripts={Path(mod.__file__).name: hashlib.sha256(Path(mod.__file__).read_bytes()).hexdigest()
                           for mod in (m, edges)}, scriptSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  colorConvention='Decoded RGB values; no linear-light or native color-management equivalence claimed.',
                  trainingEligible=False, usesObservedFocusedGeometry=True,
                  coordinateReference=coordinate_fit,
                  scope='Source and content mapping diagnosis. Same-pair color fits are not independent evaluation.')
    (destination/'result.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'seconds': report['seconds'], 'summary': summary}, indent=2))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-name', default='mapping-r4')
    parser.add_argument('--compare-coordinates', action='store_true')
    args = parser.parse_args()
    run(args.output_name, args.compare_coordinates)
