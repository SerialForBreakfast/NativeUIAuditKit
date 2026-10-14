"""Compare the runtime fallback with retained learned decisions on fixed proposals."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
from collections import Counter

import human_annotation_review as h
import artifact_storage
from real_model_scorecard import bounds, score
from real_reference_inventory import iou


def outcome(frame, elements):
    focused = [c for c in frame['controls'] if c['state'] == 'focused']
    selected = [e for e in elements if e['state'].get('isFocused') is True]
    if not frame['complete'] or len(focused) != 1:
        return 'ineligible_incomplete_or_nonunique_truth'
    target = focused[0]['bounds']
    if not any(iou(bounds(e['boundingBoxPixels']), target) >= .5 for e in elements):
        return 'focused_control_not_localized'
    if not selected:
        return 'no_focus_selected'
    if len(selected) > 1:
        return 'multiple_focus_selected'
    box = bounds(selected[0]['boundingBoxPixels'])
    if iou(box, target) < .5:
        return 'wrong_focus_selected'
    return ('correct' if sum(iou(box, c['bounds']) >= .5 for c in frame['controls']) == 1
            else 'ambiguous_selected_geometry')


def validate_reply(request, reply):
    h.require(reply['version'] == 1 and reply['sha256'] == request['sha256'] and
              reply['policy'] == 'legacy-visual-heuristic-v1', 'wrong_reply')
    h.require(type(reply.get('milliseconds')) in (int, float) and
              math.isfinite(reply['milliseconds']) and reply['milliseconds'] >= 0, 'invalid_timing')
    expected, actual = request['observations'], reply['observations']
    h.require(len(actual) == len(expected), 'changed_proposals')
    for a, b in zip(expected, actual):
        for key in ('id', 'elementType', 'boundingBox', 'boundingBoxPixels', 'confidence'):
            h.require(a[key] == b[key], 'changed_proposals')


def run(root, binary, output):
    root, binary, output = map(lambda p: Path(p).resolve(), (root, binary, output))
    h.require(output.is_relative_to(root) and binary.is_relative_to(root), 'outside_root')
    h.require(not output.exists(), 'preserve_existing_attempt')
    report_path = root/'reports/work/REAL-MODEL-SCORECARD-36/scorecard-final/scorecard.json'
    retained = json.loads(report_path.read_text())
    def checked(ref):
        path = (root/ref['path']).resolve()
        h.require(path.is_relative_to(root), 'outside_root')
        path = artifact_storage.resolve_input(path)
        h.require(hashlib.sha256(path.read_bytes()).hexdigest() == ref['sha256'], 'changed_input')
        return path
    frozen = json.loads(checked(retained['inputs']).read_text())
    frames = frozen['frames']
    h.require(0 < len(frames) <= 46 and len(frames) == len(retained['rawPredictions']), 'membership')
    h.require(len({frame['sha256'] for frame in frames}) == len(frames), 'duplicate_frames')
    output.mkdir(parents=True)
    rows = []
    start = time.monotonic()
    for index, (frame, ref) in enumerate(zip(frames, retained['rawPredictions'])):
        raw = json.loads(checked(ref).read_text())
        baseline = score(frame, raw)
        image = checked(frame['image'])
        observations = raw['runtime']['result']['elements']
        # Remove learned focus state before calling the independent fallback.
        clean = json.loads(json.dumps(observations))
        for element in clean:
            for key in ('isFocused', 'focusConfidence', 'focusScore', 'isAmbiguousFocus'):
                element['state'].pop(key, None)
        request = dict(version=1, root=str(image.parent), path=str(image), sha256=frame['sha256'], observations=clean)
        remaining = 800 - (time.monotonic() - start)
        h.require(remaining > 0, 'time_budget')
        process = subprocess.run([str(binary)], input=json.dumps(request), text=True,
                                 capture_output=True, timeout=min(60, remaining))
        (output/f'{index:03d}.stderr').write_text(process.stderr)
        (output/f'{index:03d}.json').write_text(process.stdout)
        (output/f'{index:03d}.receipt.json').write_text(json.dumps(dict(exitCode=process.returncode,
            imageSHA256=frame['sha256'], proposalSource=ref)))
        h.require(process.returncode == 0, 'fallback_failed_preserved')
        reply = json.loads(process.stdout)
        validate_reply(request, reply)
        current = outcome(frame, reply['observations'])
        rows.append(dict(image=frame['sha256'], baseline=baseline['focusOutcome'], fallback=current,
                         complete=baseline['focusEligible'], milliseconds=reply['milliseconds']))
        h.require(sum(p.stat().st_size for p in output.iterdir()) <= 100_000_000, 'output_budget')
    eligible = [r for r in rows if r['complete']]
    result = dict(version='fallback392-v1', role='development', modelAccepted=False,
                  source=retained['inputs'], predictions=retained['rawPredictions'],
                  binarySHA256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                  sourceHashes={p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in (
                      'scripts/fallback392.py', 'scripts/real_model_scorecard.py',
                      'Tools/FocusFallbackTool/main.swift',
                      'Sources/NativeUIAuditKit/Detection/NativeUIDetectionRequest.swift',
                      'Sources/NativeUIAuditKit/Detection/FocusFallbackReplay.swift')},
                  rows=rows, baseline=Counter(r['baseline'] for r in eligible),
                  fallback=Counter(r['fallback'] for r in eligible),
                  gains=[r['image'] for r in eligible if r['baseline'] != 'correct' and r['fallback'] == 'correct'],
                  losses=[r['image'] for r in eligible if r['baseline'] == 'correct' and r['fallback'] != 'correct'],
                  seconds=time.monotonic()-start,
                  limitations=['Only complete reviewed frames support full selection claims.',
                               'Historical OS focus profiles remain unqualified.',
                               'Fixed 0.5 detector proposals cannot measure a lower threshold.'])
    (output/'comparison.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('baseline', 'fallback', 'gains', 'losses', 'seconds')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--binary', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    run(args.root, args.binary, args.output)
