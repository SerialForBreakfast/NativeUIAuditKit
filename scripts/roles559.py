"""ROLES559: map the 41 schema classes to 13 detector roles, after Apple Screen Recognition (Zhang et al., CHI 2021).

A role is what the element does (button, text, cell), not how it looks (filled or tinted).
This is a training-time map only. The schema raw values stay stable public API.
Keyboard and PIN keys map to `button`: by role they are buttons, not content cells.
Rule B (PILLS560 R4, maintainer 2026-11-02): text inside a button is part of the button. `button_text=False` drops `text` boxes inside `button` boxes.
Builds 1 role membership from an existing CELLS558 membership with the same rows, groups and boxes.
Usage: roles559.py --membership reports/work/REALAPP557/cells558/membership-c2.json --out reports/work/REALAPP557/roles559
"""
import argparse
from pathlib import Path
import research_queue as q
import detector_training419 as t

ROLE_MAP = {
    'button': ('primaryButton', 'secondaryButton', 'destructiveButton', 'cancelAction', 'menuButton', 'link', 'disclosureGroup'),
    'text': ('label',),
    'picture': ('imageView', 'mapView'),
    'textField': ('textField', 'secureField', 'searchField'),
    'toggle': ('toggle',),
    'adjustable': ('slider', 'stepperControl', 'picker', 'colorWell'),
    'segmentedControl': ('segmentedControl',),
    'pageControl': ('pageControl',),
    'cell': ('collectionItem', 'listRow'),
    'bar': ('tabBar', 'navigationBar', 'toolbar', 'sidebar', 'statusBar'),
    'dialog': ('alert', 'actionSheet', 'sheet', 'popover', 'contextMenu', 'tooltip'),
    'indicator': ('progressView', 'activityIndicator', 'refreshControl', 'scrollIndicator', 'dynamicIsland', 'homeIndicator'),
    'container': ('webContent',),
}
ROLES = list(ROLE_MAP)
CLASS_ROLE = {c: role for role, classes in ROLE_MAP.items() for c in classes}  # `unknown` has no role and is dropped.
KEY_PREFIXES = ('collectionItem_key_', 'collectionItem_keypad_')


def role(cls, element_id=''):
    """Return the role for 1 schema class, or None. Keys are buttons."""
    if element_id.startswith(KEY_PREFIXES):
        return 'button'
    return CLASS_ROLE.get(cls)


def inside(a, b, share=.9):
    """True when at least `share` of box `a` lies inside box `b` (boxes are x, y, width, height)."""
    w = min(a[0]+a[2], b[0]+b[2]) - max(a[0], b[0]); h = min(a[1]+a[3], b[1]+b[3]) - max(a[1], b[1])
    return w > 0 and h > 0 and w*h >= share*a[2]*a[3]


def without_button_text(boxes):
    """Rule B: remove `text` boxes that lie inside a `button` box. `boxes` maps id to dict(cls, box)."""
    buttons = [b['box'] for b in boxes.values() if b['cls'] == 'button']
    return {k: b for k, b in boxes.items() if b['cls'] != 'text' or not any(inside(b['box'], o) for o in buttons)}


def sidecar_roles(sidecar, button_text=True):
    """Role boxes of 1 generator sidecar, clipped to the 1920×1080 canvas, in the order of its elements."""
    d = q.load(sidecar); out = {}
    for i, e in enumerate(d['elements']):
        r = role(e['elementType'], e.get('id', ''))
        p = e['boundsPixels']; x, y = max(p['x'], 0), max(p['y'], 0)
        x2, y2 = min(p['x']+p['width'], 1920), min(p['y']+p['height'], 1080)
        if r and x2 > x and y2 > y:
            out[f'e{i:03}'] = dict(cls=r, box=[x, y, x2-x, y2-y])
    return out if button_text else without_button_text(out)


def build(source, out):
    doc = q.load(source); rows = []
    for row in doc['rows']:
        boxes = sidecar_roles(q.ROOT/Path(row['image']['path']).with_suffix('.json'))
        controls = [dict(c, **{'class': boxes[c['id']]['cls']}) for c in row['controls'] if c['id'] in boxes]
        rows.append(dict(row, controls=controls))
    new = dict(doc, names=ROLES, rows=rows,
               targetScope=doc['targetScope'] + ' ROLES559: 13 detector roles (Screen Recognition style).',
               limitation=doc['limitation'] + ' Classes mapped to roles by scripts/roles559.py; keys are buttons.')
    path = Path(out)/('membership-roles-' + Path(source).stem.removeprefix('membership-') + '.json')
    q.save(path, new, replace=True)
    check = q.ROOT/f'.build/debug-output/roles559-prepare-{q.digest(path)[:8]}'; check.mkdir(parents=True, exist_ok=True)
    counts = t.prepare(new, check)[1] if not (check/'dataset').exists() else 'checked earlier'
    return dict(path=str(path), sha256=q.digest(path), rows=len(rows), counts=counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--membership', type=Path, required=True); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(build(args.membership, args.out))


if __name__ == '__main__':
    main()
