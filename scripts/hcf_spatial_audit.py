"""Measure whether native profile differences follow the observed focused control."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def rectangle_mask(shape, rectangles, padding=0):
    mask = np.zeros(shape, dtype=bool)
    height, width = shape
    for rectangle in rectangles:
        require(len(rectangle) == 4 and np.isfinite(rectangle).all(), 'invalid_rectangle')
        x, y, w, h = rectangle
        require(w > 0 and h > 0, 'empty_rectangle')
        left = max(0, min(width, int(np.floor(x-padding))))
        top = max(0, min(height, int(np.floor(y-padding))))
        right = max(0, min(width, int(np.ceil(x+w+padding))))
        bottom = max(0, min(height, int(np.ceil(y+h+padding))))
        mask[top:bottom, left:right] = True
    return mask


def spatial_metrics(standard, hcf, bodies, focus, padding=64):
    require(standard.shape == hcf.shape and standard.ndim == 3 and standard.shape[2] == 3,
            'image_shape')
    require(focus in bodies and len(bodies) > 1, 'control_support')
    delta = np.abs(standard.astype(np.int16)-hcf.astype(np.int16)).sum(axis=2)
    total = int(delta.sum())
    union = np.zeros(delta.shape, dtype=bool)
    controls = {}
    for identity, boxes in sorted(bodies.items()):
        body = rectangle_mask(delta.shape, boxes)
        mask = rectangle_mask(delta.shape, boxes, padding)
        require(not np.any(union & mask), 'overlapping_control_windows')
        union |= mask
        pixels = int(mask.sum())
        require(pixels > 0, 'control_outside_frame')
        energy = int(delta[mask].sum())
        controls[identity] = dict(pixels=pixels, changedPixels=int(np.count_nonzero(delta[mask])),
            absoluteRGBDifference=energy, meanChannelDifference=energy/(3*pixels),
            bodyDifference=int(delta[body].sum()), surroundDifference=int(delta[mask & ~body].sum()),
            fractionOfDifference=energy/total if total else None)
    focused = controls[focus]
    other = max(row['meanChannelDifference'] for key, row in controls.items() if key != focus)
    follows = (total > 0 and focused['fractionOfDifference'] >= .9 and
               focused['meanChannelDifference'] > 10*other)
    return dict(focus=focus, paddingPixels=padding, controls=controls,
        absoluteRGBDifference=total, changedPixels=int(np.count_nonzero(delta)),
        outsideDifference=int(delta[~union].sum()), followsFocus=follows,
        criterion='At least 90% of difference near focus; density exceeds every other control by 10 times.')


def body_bounds(frame):
    result = None
    for key in ('before', 'after'):
        scene = frame[key]['scene']
        observation = scene['focus_observation']
        require(observation['verified'] is True and observation['source'] == 'uikit_focus_system',
                'unverified_focus')
        require(observation['observedID'] == scene['focused_element_id'] == frame['focus'], 'focus_conflict')
        require(scene['is_settled'] is True, 'unsettled_capture')
        boxes = {}
        focused = []
        for element in scene['elements']:
            if element.get('is_hidden'):
                continue
            identity = element['element_id']
            require(identity not in boxes, 'duplicate_control')
            body = element['rendered_body_geometry']
            require(body['availability'] == 'measured' and
                    body['coordinate_space'] == 'image_top_left_pixels' and
                    body['source'] == 'native_body_presentation_layer', 'unmeasured_body')
            boxes[identity] = body['visible_pixel_bounds']
            if element['is_focused']:
                focused.append(identity)
        require(focused == [frame['focus']], 'focus_count')
        require(result is None or result == boxes, 'body_changed_during_capture')
        result = boxes
    return result


def read_image(root, frame):
    path = (root/frame['path']).resolve()
    require(path.is_relative_to(root.resolve()), 'image_outside_capture')
    require(hashlib.sha256(path.read_bytes()).hexdigest() == frame['sha256'], 'image_hash')
    with Image.open(path) as image:
        return np.asarray(image.convert('RGB'))


def audit(manifest):
    manifest = Path(manifest)
    document = json.loads(manifest.read_text())
    require(document['version'] == 'native-hcf362-v1', 'capture_version')
    require(document['complete'] is True and document['cleanup'] is True, 'capture_incomplete')
    require(document['role'] == 'development' and document['trainingEligible'] is False, 'data_role')
    frames = {}
    for frame in document['frames']:
        key = frame['profile'], frame['focus'], frame['repeat']
        require(key not in frames, 'duplicate_frame')
        profile = frame['profileReceipt']['receipt']['hcf']
        require(profile['status'] == 'completed' and profile['desiredVerified'] is True and
                profile['requested'] == profile['observed'] == frame['profile'], 'profile_unverified')
        frames[key] = frame
    targets = sorted({key[1] for key in frames})
    require(len(targets) >= 2 and set(frames) == {
        (profile, target, repeat) for profile in ('standard', 'hcf') for target in targets for repeat in (0, 1)
    }, 'missing_counterparts')
    rows = []
    for target in targets:
        images, geometries, noise = {}, {}, {}
        recipes = []
        for profile in ('standard', 'hcf'):
            first = frames[profile, target, 0]
            second = frames[profile, target, 1]
            images[profile] = read_image(manifest.parent, first)
            repeated = read_image(manifest.parent, second)
            require(images[profile].shape == repeated.shape, 'repeat_shape')
            noise[profile] = int(np.count_nonzero(np.any(images[profile] != repeated, axis=2)))
            geometries[profile] = body_bounds(first)
            require(geometries[profile] == body_bounds(second), 'repeat_geometry_changed')
            for frame in (first, second):
                recipes.extend(frame[key]['scene']['recipe'] for key in ('before', 'after'))
        require(all(recipe == recipes[0] for recipe in recipes), 'recipe_changed_between_profiles')
        require(geometries['standard'].keys() == geometries['hcf'].keys(), 'controls_changed')
        bodies = {key: [geometries[profile][key] for profile in ('standard', 'hcf')]
                  for key in geometries['standard']}
        row = spatial_metrics(images['standard'], images['hcf'], bodies, target)
        row['repeatChangedPixels'] = noise
        row['qualifiedSpatialDifference'] = row['followsFocus'] and not any(noise.values())
        rows.append(row)
    return dict(version='hcf-spatial-audit-v1', captureSHA256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
        group=document['group'], rows=rows, followsFocus=all(r['qualifiedSpatialDifference'] for r in rows),
        trainingEligible=False, modelAccepted=False,
        limitation='Related development captures. Spatial differences do not establish detection accuracy or device parity.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.manifest), indent=2))
