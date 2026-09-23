"""Development-only source-bound TTR/NUIAK crop replay; no navigation or training."""
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from PIL import Image, ImageDraw, ImageChops, ImageStat
from focus_runtime import ROOT, invoke, identity
from focus_ring_baseline import artifact_digest


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_block(text, marker):
    """Mechanical extraction for these pinned Swift declarations; fail if ambiguous."""
    if text.count(marker) != 1:
        raise ValueError('ambiguous_source_marker')
    start = text.index(marker)
    opening = text.index('{', start)
    depth = 1
    for pos in range(opening + 1, len(text)):
        depth += (text[pos] == '{') - (text[pos] == '}')
        if depth == 0:
            return text[start:pos + 1]
    raise ValueError('incomplete_source_block')


def run(peer, output):
    peer = peer.resolve()
    output = output.resolve()
    if not output.is_relative_to(ROOT) or output == ROOT or output.exists():
        raise ValueError('output_collision_or_outside_project')
    output.mkdir(parents=True)
    tmp = output / 'tmp'; tmp.mkdir()
    env = {**os.environ, 'TMPDIR': str(tmp), 'CLANG_MODULE_CACHE_PATH': str(output / 'module-cache'),
           'SWIFT_MODULECACHE_PATH': str(output / 'module-cache')}
    src = peer / 'TVTestRig/TVTestRig'
    paths = [src / 'Services/FocusDetectorService.swift', src / 'Observation/FocusScoring.swift',
             src / 'Observation/LocalVisionOCRService.swift', src / 'Domain/AutomationRecords.swift']
    hashes = {str(p.relative_to(peer)): sha(p) for p in paths}
    # Isolated generated adapter: exact crop/rectangle declarations, only error type stubbed.
    crop = extract_block(paths[2].read_text(), 'nonisolated static func crop(')
    rect = extract_block(paths[3].read_text(), 'nonisolated struct NormalizedRectangle:')
    dependency = output / 'ProbeDependencies.swift'
    dependency.write_text('import Foundation\nimport CoreGraphics\nenum TVTestRigError: Error { case invalidArgument }\n'
                          + rect + '\nenum LocalVisionOCRService {\n' + crop + '\n}\n')
    executable = output / 'peer-probe'
    # Producer project uses Swift 5 language mode; do not rewrite its actor code.
    command = ['xcrun', 'swiftc', '-parse-as-library', '-swift-version', '5',
               '-module-cache-path', str(output / 'module-cache'), str(dependency),
               str(paths[0]), str(paths[1]), str(ROOT / 'scripts/focus_peer_probe.swift'), '-o', str(executable)]
    start = time.monotonic()
    built = subprocess.run(command, env=env, capture_output=True, text=True, timeout=180)
    (output / 'build.log').write_text(built.stdout + built.stderr)
    if built.returncode:
        raise ValueError('peer_probe_compile_failed')
    model = ROOT / 'NativeUIAuditKitModels/Sources/NativeUIAuditKitModels/Resources/FocusRingDetector.mlmodelc'
    model_hash = artifact_digest(model)
    manifest = peer / 'Scripts/native-ui-audit-samples.json'
    cases = json.loads(manifest.read_text())
    items = []
    for case in cases:
        source = (peer / case['path']).resolve()
        if not source.is_relative_to(peer) or sha(source) != case['sha256']:
            raise ValueError('historical_member_hash_mismatch')
        dest = output / (case['id'] + '-source.png')
        shutil.copyfile(source, dest)
        items.append(dict(id=case['id'], path=str(dest), sha256=sha(dest), bounds=case['box']))
    # Spatially asymmetric synthetic calibration image, not training evidence.
    im = Image.new('RGB', (640, 480), 'black'); draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, 639, 239), fill='red')
    draw.rectangle((0, 240, 639, 479), fill='blue')
    draw.rectangle((180, 60, 300, 140), fill='green')
    synthetic = output / 'synthetic-source.png'; im.save(synthetic)
    for name, box in calibration_boxes():
        items.append(dict(id='synthetic-' + name, path=str(synthetic), sha256=sha(synthetic), bounds=box))
    (output / 'inputs.json').write_text(json.dumps(items, indent=2))
    nua_crops = invoke(items)
    nua_scores = invoke(items, model)
    result = subprocess.run([str(executable)], input=json.dumps({'model': str(model), 'items': items}),
                            capture_output=True, text=True, env=env, timeout=120)
    (output / 'peer-runtime.log').write_text(result.stderr)
    if result.returncode:
        raise ValueError('peer_inference_failed')
    rows = json.loads(result.stdout)
    if [r['id'] for r in rows] != [i['id'] for i in items]:
        raise ValueError('peer_membership_mismatch')
    comparisons = []
    controlled_items = []
    for item, nc, ns, tr in zip(items, nua_crops['results'], nua_scores['results'], rows, strict=True):
        crops = []
        for label, encoded in [('nuiak', nc['png']), ('ttr', tr['png'])]:
            raw = base64.b64decode(encoded, validate=True)
            (output / (item['id'] + '-' + label + '.png')).write_bytes(raw)
            image = Image.open(io.BytesIO(raw)).convert('RGB')
            if image.size != (256, 256): raise ValueError('bad_crop_dimensions')
            crops.append(image)
            path = output / (item['id'] + '-' + label + '.png')
            controlled_items.append(dict(id=item['id'] + ':' + label, path=str(path),
                                         sha256=sha(path), bounds=[0, 0, 256, 256]))
        diff = ImageChops.difference(*crops)
        comparisons.append({'id': item['id'], 'pixelsEqual': diff.getbbox() is None,
                            'meanAbsoluteRGBDifference': sum(ImageStat.Stat(diff).mean) / 3,
                            'nuiakProbability': ns['probability'],
                            'ttrProbability': tr['probability'], 'ttrConfidence': tr['confidence'],
                            'ttrRepeatProbability': tr['secondProbability'],
                            'ttrZeroScoreMayHideFailure': tr['zeroScoreMayHideFailure'],
                            'ttrPreprocessingVersion': tr['preprocessingVersion']})
    # Full-image bounds clamp expansion to the entire already-generated crop.
    # Verify this wrapper is pixel-preserving before interpreting controlled scores.
    recrops = invoke(controlled_items)
    for item, row in zip(controlled_items, recrops['results'], strict=True):
        original = Image.open(item['path']).convert('RGB')
        recropped = Image.open(io.BytesIO(base64.b64decode(row['png'], validate=True))).convert('RGB')
        if ImageChops.difference(original, recropped).getbbox() is not None:
            raise ValueError('controlled_recrop_changed_pixels')
    controlled = invoke(controlled_items, model)
    score_by_id = {r['id']: r['probability'] for r in controlled['results']}
    for row in comparisons:
        row['sameCPUClassifierOnNUACrop'] = score_by_id[row['id'] + ':nuiak']
        row['sameCPUClassifierOnTTRCrop'] = score_by_id[row['id'] + ':ttr']
    if hashes != {str(p.relative_to(peer)): sha(p) for p in paths} or artifact_digest(model) != model_hash:
        raise ValueError('changed_source_or_model')
    report = {'version': 1, 'purpose': 'development-only crop parity, not accuracy or navigation qualification',
              'peerSourceHashes': hashes, 'peerRevision': subprocess.check_output(['git', '-C', str(peer), 'rev-parse', 'HEAD'], text=True).strip(),
              'sampleManifestSHA256': sha(manifest), 'modelSHA256': model_hash, 'nuiakRuntime': identity(),
              'peerHarnessSHA256': sha(ROOT / 'scripts/focus_peer_probe.swift'), 'peerBinarySHA256': sha(executable),
              'generatedDependencySHA256': sha(dependency), 'compute': {'nuiak': 'cpuOnly', 'ttr': 'all'},
              'scope': 'Actual TTR scoring source; extracted exact crop/rectangle dependencies; injected identical boxes/model. No OCR candidate generation, app IPC or live controller.',
              'buildScope': 'Standalone Swift 5 matching producer language mode; not its app target or default MainActor isolation configuration',
              'trainingEligible': False, 'modelGatePassed': False, 'comparisons': comparisons,
              'controlledComparison': 'Both retained crops scored by NUIAK CPU classifier; wrapper recrop verified decoded-pixel identical',
              'elapsedSeconds': time.monotonic() - start}
    (output / 'report.json').write_text(json.dumps(report, indent=2))
    print(json.dumps({'cases': len(items), 'equalCrops': sum(r['pixelsEqual'] for r in comparisons),
                      'report': str(output / 'report.json')}))


def calibration_boxes():
    return [('upper', [190, 70, 100, 60]), ('edge', [0, 0, 80, 50]),
            ('lower', [90, 350, 120, 70]), ('fractional', [174.5, 58.25, 132.5, 88.75]),
            ('bottom-right', [597.25, 432.5, 42.75, 47.5]),
            ('cross-color-boundary', [150.25, 204.75, 170.5, 78.25])]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--peer', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    run(args.peer, args.output)
