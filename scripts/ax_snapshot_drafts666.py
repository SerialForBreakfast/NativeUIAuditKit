"""TRAIN666 W2: convert passive XCUITest accessibility snapshots into benchmark review drafts.

Input: an `.xcresult` from `NativeOSFocusTests.testPassiveForegroundSnapshot` (`tvos-ax-snapshot-v1` JSON + PNG).
Output per screen: the PNG and a `tvbench-ax-draft-v1` JSON with class-agnostic target boxes in pixels,
a draft class in the 10 contract classes, and a focus draft.

The draft class comes from the accessibility element type. That is a runtime observation, not construction
evidence, so every object carries `roleSource: ax_element_type` and a reviewer confirms or corrects it.
A draft is never a reference and never a training label. `none_observed` focus stays `unknown`: it does not prove no focus.
Usage: ax_snapshot_drafts666.py --xcresult R.xcresult --out DIR
"""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import framework_projection604 as fp
import research_queue as q

# XCUIElement.ElementType raw values -> draft contract class.
KIND_CLASS = {
    9: 'button', 16: 'button', 17: 'button', 42: 'button', 20: 'button', 80: 'button', 54: 'button', 14: 'button',
    75: 'cell', 44: 'cell', 27: 'cell',
    49: 'textField', 50: 'textField', 45: 'textField',
    40: 'toggle', 41: 'toggle',
    37: 'segmentedControl', 34: 'pageControl',
    21: 'bar', 22: 'bar',
    7: 'dialog', 8: 'dialog', 5: 'dialog', 18: 'dialog',
    35: 'indicator', 36: 'indicator',
}
IMAGE_KIND, TEXT_KINDS = 43, {48, 52}
CONTAINER_CLASSES = {'bar', 'dialog'}  # A target inside these keeps its own box. Inside any other target it is owned content.
MIN_SIDE_PX = 8


def _pixel_box(bounds, scale, width, height):
    x, y, w, h = bounds
    x0, y0 = max(int(x * scale[0] // 1), 0), max(int(y * scale[1] // 1), 0)
    x1, y1 = min(int(-(-(x + w) * scale[0] // 1)), width), min(int(-(-(y + h) * scale[1] // 1)), height)
    return [x0, y0, x1 - x0, y1 - y0] if x1 - x0 >= MIN_SIDE_PX and y1 - y0 >= MIN_SIDE_PX else None


def draft_from_snapshot(snap):
    """Return 1 draft document for 1 `tvos-ax-snapshot-v1` record."""
    q.require(snap.get('version') == 'tvos-ax-snapshot-v1', 'ax_snapshot_version')
    scope = snap.get('annotationScope', 'legacy-app-only')
    capture_owner = snap.get('captureOwnerBundleIdentifier', snap['bundleIdentifier'])
    q.require(scope in ('legacy-app-only', 'application', 'system-overlay'), 'annotation_scope')
    q.require((scope != 'application' or capture_owner == snap['bundleIdentifier']) and
              (scope != 'system-overlay' or capture_owner in ('com.apple.PineBoard', 'com.apple.TVSystemUIService')), 'capture_owner_scope')
    width, height = snap['pixelDimensions']
    vp = snap['viewportPoints']
    scale = (width / vp[2], height / vp[3])
    nodes = snap['nodes']
    classes = fp.tvos_classes()

    def target_ancestor(i):
        """Nearest strict ancestor that is a draft target, or None."""
        p = nodes[i]['parent']
        while p >= 0:
            if nodes[p]['kind'] in KIND_CLASS:
                return p
            p = nodes[p]['parent']
        return None

    objects, index_of, owned = [], {}, []
    for i, n in enumerate(nodes):
        box = _pixel_box(n['bounds'], scale, width, height)
        cls = KIND_CLASS.get(n['kind'])
        anc = target_ancestor(i)
        if cls is None and n['kind'] == IMAGE_KIND and anc is None and box and box[2] * box[3] < 0.9 * width * height:
            cls = 'picture'
        nested = anc is not None and KIND_CLASS[nodes[anc]['kind']] not in CONTAINER_CLASSES
        if cls is None or box is None or nested:
            if anc is not None and box and (nested or n['kind'] in TEXT_KINDS | {IMAGE_KIND}):
                owned.append(dict(node=i, parentNode=anc, kind=n['kind'], box=box, label=n['label'][:80]))
            continue
        q.require(cls in classes, 'ax_draft_class')
        index_of[i] = len(objects)
        objects.append(dict(id=f'ax-{len(objects):03}', node=i, box=box, **{'class': cls}, roleSource='ax_element_type', axKind=n['kind'],
                            axIdentifier=n['identifier'][:120], axLabel=n['label'][:120], enabled=n['enabled'], selected=n['selected'],
                            parentObject=None, visibility='unknown',
                            clippedByScreen=bool(n['bounds'][0] < vp[0] or n['bounds'][1] < vp[1] or n['bounds'][0] + n['bounds'][2] > vp[0] + vp[2]
                                                 or n['bounds'][1] + n['bounds'][3] > vp[1] + vp[3]), hasDisclosure=False))
    for i, j in index_of.items():
        anc = target_ancestor(i)
        if anc in index_of:
            objects[j]['parentObject'] = objects[index_of[anc]]['id']
    for item in owned:
        if item['label'] == 'chevron' and item['parentNode'] in index_of:
            objects[index_of[item['parentNode']]]['hasDisclosure'] = True
    focused = [i for i, n in enumerate(nodes) if n['focused']]
    focus = dict(state='unknown', source='xcuitest_hasFocus', observed=snap['focusState'])
    if snap['focusState'] == 'focused' and snap['settled']:
        i = focused[0]
        owner = i
        while owner is not None and owner not in index_of:
            owner = target_ancestor(owner)
        if owner in index_of:
            focus = dict(state='focused', objectId=objects[index_of[owner]]['id'], box=objects[index_of[owner]]['box'], source='xcuitest_hasFocus', observed='focused')
        else:
            focus['reason'] = 'focused_element_is_not_a_draft_target'
    return dict(version='tvbench-ax-draft-v1', imageSHA256=snap['pngSHA256'], width=width, height=height,
                bundleIdentifier=snap['bundleIdentifier'], screenID=snap['screenID'], settled=snap['settled'], inputsSent=snap['inputsSent'],
                annotationScope=scope, captureOwnerBundleIdentifier=capture_owner,
                complete=False, classes=classes, objects=objects, ownedContent=owned, focus=focus,
                review=dict(status='draft', reviewer=None, note='Accessibility draft. A reviewer must confirm boxes, classes, missing controls and focus.'))


def export(xcresult, out):
    """Export attachments of 1 result bundle and write `<screen>.png` + `<screen>.draft.json` into `out`."""
    xcresult, out = Path(xcresult), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    with tempfile.TemporaryDirectory(dir=q.ROOT / '.build') as tmp:
        subprocess.run(['xcrun', 'xcresulttool', 'export', 'attachments', '--path', str(xcresult), '--output-path', tmp], check=True, capture_output=True)
        manifest = json.loads((Path(tmp) / 'manifest.json').read_text())
        files = {a['suggestedHumanReadableName']: Path(tmp) / a['exportedFileName'] for t in manifest for a in t['attachments']}
        for name, path in sorted(files.items()):
            if path.suffix != '.json':
                continue
            snap = json.loads(path.read_text())
            if snap.get('version') != 'tvos-ax-snapshot-v1':
                continue
            png = next((p for n, p in files.items() if p.suffix == '.png' and hashlib.sha256(p.read_bytes()).hexdigest() == snap['pngSHA256']), None)
            q.require(png is not None, f"ax_draft_png_missing:{snap['screenID']}")
            draft = draft_from_snapshot(snap)
            stem = f"{snap['bundleIdentifier'].split('.')[-1]}-{snap['screenID']}"
            q.require(not (out / f'{stem}.draft.json').exists(), f'ax_draft_exists:{stem}')
            (out / f'{stem}.png').write_bytes(png.read_bytes())
            q.save(out / f'{stem}.snapshot.json', snap)
            q.save(out / f'{stem}.draft.json', draft)
            written.append(dict(screen=stem, objects=len(draft['objects']), owned=len(draft['ownedContent']), focus=draft['focus']['state'],
                                classes={c: sum(o['class'] == c for o in draft['objects']) for c in sorted({o['class'] for o in draft['objects']})}))
    return written


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--xcresult', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.xcresult, args.out), indent=2))
