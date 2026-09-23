"""Inspection-only audit of preserved smoke bytes; does not admit training data."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import time
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from harvest_bundle_validation import validate_bundle, HarvestValidationError
from focus_runtime import invoke, identity, RUNTIME_PREPROCESSING

BUNDLE = ROOT / 'dataset/tvos_captures/ttr-smoke-20260922-2119/ipc-received'
start = time.monotonic()
index = json.loads((BUNDLE / 'dataset-index.json').read_text())
rows = json.loads((BUNDLE / 'manifest.json').read_text())
report = {'purpose': 'inspection-only; no training admission', 'runtime': identity(),
          'preprocessing': RUNTIME_PREPROCESSING, 'files': [], 'pairs': [], 'gaps': []}
try:
    validate_bundle(BUNDLE)
    report['entrypointValidation'] = 'passed'
except HarvestValidationError as e:
    report['entrypointValidation'] = str(e)
for f in json.loads((HERE / 'receive-result.json').read_text())['files']:
    path = BUNDLE / f['path']
    assert path.stat().st_size == f['bytes']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == f['sha256']
    result = dict(f)
    if path.suffix == '.png':
        with Image.open(path) as im:
            im.load()
            result['dimensions'] = list(im.size)
            result['decodedRGBSHA256'] = hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
            assert im.size == (3840, 2160)
    report['files'].append(result)
items = []
for row in rows:
    meta = json.loads((BUNDLE / row['metadata']['metadataPath']).read_text())
    pair = {'id': row['id'], 'elementID': row['expectedFocus'], 'split': row['split'], 'frames': {}}
    for role, scene_key in [('focused', 'focused_scene'), ('unfocused', 'baseline_scene')]:
        scene = meta[scene_key]
        element = next(e for e in scene['elements'] if e['element_id'] == row['expectedFocus'])
        assert element['is_focused'] == (role == 'focused')
        x, y, w, h = element['pixel_bounds']
        expected = [x / 3840, y / 2160, (x+w)/3840, (y+h)/2160]
        assert max(abs(a-b) for a,b in zip(expected, element['normalized_bounds'])) < 1e-9
        provenance = meta[role+'_provenance']
        assert provenance['pngSHA256'] == meta[role+'_sha256']
        assert provenance['sourceDeviceID'] == '9026ECA9-77DB-4AE6-8FE6-BB239E9571FA'
        pair['frames'][role] = {'bounds': element['pixel_bounds'], 'observation': scene['focus_observation'], 'imageProvenance': provenance}
        items.append({'id': row['id']+'-'+role, 'path': str(BUNDLE / meta[role+'_png']), 'sha256': meta[role+'_sha256'], 'bounds': element['pixel_bounds']})
    report['pairs'].append(pair)
report['gaps'] = [
    'sourceDescription.collectedAt is numeric Swift Date; consumer requires nonempty string',
    'recipe.theme missing in both sidecars; explicit requested theme is not resolved-theme evidence',
    'baseline native observedID absent; reference focus mapping must be source-reviewed, not invented',
    'per-frame focus freshness and capture bracketing not retained in sidecar; image observationID is not a focus-callback frameID',
    'focused visual enlargement exists while recorded focused and baseline bounds are identical; distinguish nominal layout bounds from focus-effect bounds',
]
reply = invoke(items)
out = HERE / 'inspection-crops'
out.mkdir(exist_ok=False)
for row in reply['results']:
    b = base64.b64decode(row.pop('png'), validate=True)
    path = out / (row['id']+'.png')
    with path.open('xb') as f: f.write(b)
    with Image.open(path) as im: assert im.size == (256, 256)
    row['cropSHA256'] = hashlib.sha256(b).hexdigest()
report['runtimeCrops'] = reply
report['seconds'] = time.monotonic()-start
(HERE / 'intake-audit.json').write_text(json.dumps(report, indent=2))
print(json.dumps({'files': len(report['files']), 'pairs': len(report['pairs']), 'entrypoint': report['entrypointValidation'], 'runtimeCrops': len(reply['results']), 'seconds': report['seconds']}))
