"""Read-only independent accounting for the bounded three-frame native artwork probe."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from shared_transfer import document, require


def validate(root, catalog_path):
    root = Path(root).resolve()
    catalog = document(Path(catalog_path))
    receipt = document(root/'receipt.json')
    require(receipt.get('schemaVersion') == 'ios-artwork-probe-v1' and receipt.get('complete') is True, 'incomplete')
    require(receipt.get('catalogSHA256') == hashlib.sha256(Path(catalog_path).read_bytes()).hexdigest(), 'catalog_hash')
    frames = receipt.get('frames', [])
    require([f.get('file') for f in frames] == ['default.png', 'fit.png', 'fill.png'], 'membership')
    assets = {a['id']: a for a in catalog['assets']}
    expected = {'receipt.json'} | {n+s for n in ('default', 'fit', 'fill') for s in ('.json', '.png')}
    require({p.name for p in root.iterdir()} == expected, 'unexpected_members')
    baseline, annotations, mask = None, None, None
    rows = []
    for f in frames:
        path = root/f['file']
        require(path.is_file() and not path.is_symlink() and path.stat().st_size <= 32*1024*1024, 'image_type')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        a = document(path.with_suffix('.json'))
        require(a.get('image', {}).get('colorScheme') == 'light', 'probe_theme')
        require(f['sha256'] == digest == a['imageSHA256'], 'image_hash')
        require(f['dataRole'] == 'development', 'role')
        with Image.open(path) as im:
            require(im.format == 'PNG' and im.size == (1179, 2556), 'dimensions')
            pixels = np.array(im.convert('RGB'))
        by_id = {e['id']: e for e in a['elements']}
        require(len(by_id) == len(a['elements']), 'duplicate_element')
        thumbs = {k: v for k, v in by_id.items() if k.startswith('imageView_thumb_')}
        require(len(thumbs) == 4, 'target_count')
        if baseline is None:
            baseline, annotations = pixels, by_id
            mask = np.zeros(pixels.shape[:2], dtype=bool)
            require(f['bindings'] == [], 'default_binding')
            for e in thumbs.values():
                b = e['boundsPixels']; x,y,w,h = (b[k] for k in ('x','y','width','height'))
                require(0 <= x < x+w <= 1179 and 0 <= y < y+h <= 2556, 'bounds')
                mask[y:y+h, x:x+w] = True
            continue
        require(by_id == annotations, 'annotation_drift')
        require(len(f['bindings']) == 4 and {b['elementID'] for b in f['bindings']} == set(thumbs), 'bindings')
        diff = np.any(pixels != baseline, axis=2)
        require(not np.any(diff & ~mask), 'outside_viewport_change')
        for b in f['bindings']:
            asset = assets[b['assetID']]
            require(b['sha256'] == asset['sha256'] and b['ancestryGroup'] == asset['ancestryGroup'], 'asset_binding')
            e = thumbs[b['elementID']]; v = e['boundsPoints']
            viewport = [v[k] for k in ('x','y','width','height')]
            require(np.allclose(b['viewportPoints'], viewport, rtol=0, atol=1e-9), 'viewport')
            x,y,w,h = viewport
            mode = f['file'].split('.')[0]
            require(b['placement'] == mode, 'placement')
            scale = (min if mode == 'fit' else max)(w/asset['width'], h/asset['height'])
            aw,ah = asset['width']*scale, asset['height']*scale
            require(np.allclose(b['contentExtentPoints'], [x+(w-aw)/2,y+(h-ah)/2,aw,ah], rtol=0,atol=1e-8), 'content_geometry')
            p = e['boundsPixels']; px,py,pw,ph = (p[k] for k in ('x','y','width','height'))
            require(np.any(diff[py:py+ph,px:px+pw]), 'unchanged_target')
        rows.append({'frame': f['file'], 'changedPixels': int(diff.sum()), 'outsideViewportChanges': 0})
    return {'scope': 'three-frame grid development probe', 'frames': 3, 'bindings': 8,
            'checks': rows, 'trainingAdmission': 'not_assessed',
            'limitations': 'Pixel difference bounds and geometry do not independently prove image identity; visual review required.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--catalog', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(validate(a.root, a.catalog), indent=2))
