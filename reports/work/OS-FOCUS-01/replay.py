"""One recorded journey audit/replay; not a general corpus admission tool."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from focus_runtime import invoke, identity
from focus_ring_baseline import artifact_digest

trial = ROOT / 'reports/work/OS-FOCUS-01/live-20260922-0712'
attachments = trial / 'attachments'
output = trial / 'replay'
output.mkdir(exist_ok=False)
manifest = json.loads((attachments / 'manifest.json').read_text())[0]['attachments']
assert len(manifest) == 15
assert all(a['deviceId'] == '9026ECA9-77DB-4AE6-8FE6-BB239E9571FA' and not a['isAssociatedWithFailure'] for a in manifest)
pngs = {}
records = []
for a in manifest:
    path = attachments / a['exportedFileName']
    if path.suffix == '.png':
        pngs[hashlib.sha256(path.read_bytes()).hexdigest()] = path
    elif path.suffix == '.json': records.append(json.loads(path.read_text()))
records.sort(key=lambda r:r['name'])
assert [r['action'] for r in records] == ['activate-settings', 'down', 'down', 'down', 'up', 'up', 'up']
terminal = next((attachments/a['exportedFileName']).read_text() for a in manifest if a['exportedFileName'].endswith('.txt'))
assert 'inputs=6; settingsForeground=true' in terminal
unique = []
for r in records:
    assert r['before']['nodes'] == r['after']['nodes']
    assert r['before']['timestamp'] <= r['captureStartedAt'] <= r['captureEndedAt'] <= r['after']['timestamp']
    assert r['pngSHA256'] in pngs
    image = Image.open(pngs[r['pngSHA256']]); image.load()
    assert list(image.size) == r['pixelDimensions'] == [3840, 2160]
    assert r['before']['viewportPoints'] == [0, 0, 1920, 1080]
    assert sum(n['focused'] for n in r['before']['nodes']) == 1
    if not any(x['pngSHA256'] == r['pngSHA256'] for x in unique): unique.append(r)
assert len(unique) == 4
labels = [r['before']['focus']['label'] for r in unique]
assert len(set(labels)) == 4
items, truth = [], {}
for r in unique:
    for index, label in enumerate(labels):
        nodes = [n for n in r['before']['nodes'] if n['kind'] == 75 and n['label'] == label]
        assert len(nodes) == 1
        node = nodes[0]
        item_id = r['name'] + '-row-' + str(index)
        items.append(dict(id=item_id, path=str(pngs[r['pngSHA256']]), sha256=r['pngSHA256'], bounds=[v*2 for v in node['bounds']]))
        truth[item_id] = node['focused']
model = ROOT / 'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc'
model_hash = artifact_digest(model)
scores = []
for offset in range(0, len(items), 4):
    batch = items[offset:offset+4]
    crops = invoke(batch)
    for row in crops['results']:
        (output/(row['id']+'-nuiak.png')).write_bytes(base64.b64decode(row['png'],validate=True))
    scores.extend(invoke(batch,model)['results'])
peer = ROOT/'reports/work/FOCUS-PARITY-01/replay-03/peer-probe'
peer_identity = json.loads((peer.parent/'report.json').read_text())
assert hashlib.sha256(peer.read_bytes()).hexdigest() == peer_identity['peerBinarySHA256']
assert model_hash == peer_identity['modelSHA256']
result = subprocess.run([str(peer)],input=json.dumps(dict(model=str(model),items=items)),text=True,capture_output=True,
                        timeout=120,env={**os.environ,'TMPDIR':str(ROOT/'.build/native-os-focus/tmp')})
(output/'peer-runtime.log').write_text(result.stderr)
assert result.returncode == 0
peer_rows = json.loads(result.stdout)
assert [r['id'] for r in peer_rows] == [i['id'] for i in items]
rows = []
for a,b in zip(scores,peer_rows,strict=True):
    assert a['id'] == b['id']
    (output/(a['id']+'-ttr.png')).write_bytes(base64.b64decode(b['png'],validate=True))
    rows.append(dict(id=a['id'],nativeFocused=truth[a['id']],nuiakProbability=a['probability'],
                     ttrProbability=b['probability'],ttrConfidence=b['confidence'],
                     ttrFailureSentinel=b['zeroScoreMayHideFailure']))
assert artifact_digest(model) == model_hash
report = dict(version=1,observations=7,uniqueFrames=4,inputs=6,uniqueRows=4,
              sourceKind='tvos_simulator_os',membership='development-only-one-journey',trainingEligible=False,
              modelSHA256=model_hash,runtime=identity(),peerBinarySHA256=peer_identity['peerBinarySHA256'],
              coordinateScale=2,pointViewport=[0,0,1920,1080],pixelDimensions=[3840,2160],
              nativeFocusSequence=[r['before']['focus']['label'] for r in records],
              terminal=terminal,rows=rows,
              scope='Injected native row boxes; model makes scores, native focus only scores truth. Not detector candidate extraction or model-driven navigation. NUA CPU versus TTR all backend.',
              visualReview='Four unique full frames inspected; highlights match native focus, standard Settings labels only. Reviewed development evidence, not independent final test annotations.')
(output/'inputs.json').write_text(json.dumps(items,indent=2))
(output/'report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
