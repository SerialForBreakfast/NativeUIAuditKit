"""Local geometry templates, never ground truth or review attestations."""
import math
import re
import human_annotation_review as h

DIRECTORY = h.ROOT/'reports/work/HUMAN-REVIEW-01/rectangle-presets'


def validate(doc, size):
    h.require(doc.get('version') in ('rectangle-preset-v1', 'rectangle-preset-v2'), 'unsupported_preset')
    if doc['version'] == 'rectangle-preset-v2':
        h.require(doc.get('roleSchema') == h.ROLE_SCHEMA, 'unsupported_preset_roles')
    h.require(doc.get('taxonomy') == h.sha(h.CATEGORY), 'preset_taxonomy_changed')
    h.require(doc.get('size') == list(size), 'preset_image_dimensions_differ')
    h.require(len(size) == 2 and all(type(v) is int and v > 0 for v in size), 'invalid_dimensions')
    boxes = doc['boxes']
    h.require(0 < len(boxes) <= 100, 'preset_requires_1_to_100_boxes')
    for box in boxes:
        allowed = h.review_labels() if doc['version'] == 'rectangle-preset-v2' else h.taxonomy()
        h.require(box['label'] in allowed, 'invalid_preset_label')
        points = box['points']
        h.require(len(points) == 2 and all(len(p) == 2 for p in points), 'invalid_rectangle')
        h.require(all(type(v) in (int, float) and math.isfinite(v) for p in points for v in p), 'invalid_coordinates')
        x, y = points[0]; r, b = points[1]
        h.require(0 <= x < r <= size[0] and 0 <= y < b <= size[1], 'preset_bounds_outside_image')
    return boxes


def save(name, size, boxes, directory=None):
    h.require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 _-]{0,63}', name) is not None, 'use_simple_preset_name')
    directory = h.local(directory or DIRECTORY)
    doc = dict(version='rectangle-preset-v1', name=name, size=list(size),
               taxonomy=h.sha(h.CATEGORY), boxes=[dict(label=b['label'], points=b['points']) for b in boxes])
    if any(b['label'].startswith('focus:') for b in boxes):
        doc.update(version='rectangle-preset-v2', roleSchema=h.ROLE_SCHEMA)
    validate(doc, size)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory/(name+'.json')
    h.require(not path.exists(), 'preset_name_already_exists')
    h.write(path, doc)
    return path


def load(path, size):
    return validate(h.read(path), size)
