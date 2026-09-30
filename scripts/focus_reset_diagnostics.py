"""Cached-score diagnostic reset. Never imports a model or changes selection gates."""
import argparse
from collections import Counter, defaultdict
import math
import struct

from PIL import Image
import focus_offline_diagnosis as offline
from focus_dataset_contract import ROOT, digest, pixel_digest, expanded_box
from focus_representative_experiment import selection_metrics
from focus_representative_validation import stratum

VERSION = 'focus-reset-diagnostic-v1'
require = offline.require


def f32(value):
    return struct.unpack('f', struct.pack('f', value))[0]


def frame_scores(rows, predictions, policy):
    require(len({r['id'] for r in rows}) == len(rows), 'duplicate_rows')
    require([r['id'] for r in rows] == [p['id'] for p in predictions], 'prediction_membership')
    for r, p in zip(rows, predictions):
        require(type(r['label']) is int and r['label'] in (0, 1) and type(p['label']) is int and p['label'] == r['label']
                and type(p['probability']) in (int, float) and math.isfinite(p['probability'])
                and 0 <= p['probability'] <= 1, 'invalid_score_or_label')
        require(r['use'] == 'representative-selection' and r['split'] == 'validation'
                and r['population'] == 'candidate' and r['settlement'] == 'settled', 'unsupported_role')
    require(len({f['id'] for f in policy['frames']}) == len(policy['frames']), 'duplicate_frames')
    require(set(r['frameID'] for r in rows) <= {f['id'] for f in policy['frames']}, 'missing_frame')
    require(policy['populations'] == dict(candidate=[r['id'] for r in rows], auxiliary=[], unresolved=[]),
            'changed_candidate_membership')
    scores = {p['id']: p['probability'] for p in predictions}
    by_frame = defaultdict(list)
    for r in rows:
        by_frame[r['frameID']].append(r)
    results = []
    for frame in policy['frames']:
        require(frame['coverage'] in ('complete', 'incomplete', 'unknown')
                and frame['settlement'] in ('settled', 'disputed', 'unknown'), 'invalid_frame_policy')
        subset = by_frame[frame['id']]
        truth = [r for r in subset if r['label']]
        record = dict(id=frame['id'], candidates=len(subset), focusedSupport=len(truth))
        if frame['coverage'] != 'complete' or frame['settlement'] != 'settled' or len(truth) != 1:
            record.update(status='unavailable', reason=frame.get('reason') or 'incomplete_unsettled_or_nonunique_truth')
        else:
            ordered = sorted(subset, key=lambda r: (-scores[r['id']], r['id']))
            target = truth[0]
            highest = scores[ordered[0]['id']]
            winners = [r for r in ordered if scores[r['id']] == highest]
            competitors = [r for r in ordered if not r['label']]
            selected = [r for r in subset if scores[r['id']] >= .85]
            strict = ('no_focus' if not selected else 'multiple_focus' if len(selected) > 1
                      else 'unique_correct' if selected[0]['label'] else 'wrong')
            # Native scorer uses Float; tied winner identity is deliberately not guessed.
            native_highest = max(f32(scores[r['id']]) for r in subset)
            native_winners = [r for r in subset if f32(scores[r['id']]) == native_highest]
            runtime = ('no_focus' if native_highest < f32(.85) else 'tied_unavailable'
                       if len(native_winners) > 1 else 'correct' if native_winners[0]['label'] else 'wrong')
            geometric = sorted(subset, key=lambda r: (r['bounds'][1], r['bounds'][0], r['id']))[0]
            largest = max(r['bounds'][2] * r['bounds'][3] for r in subset)
            area_winners = [r for r in subset if r['bounds'][2] * r['bounds'][3] == largest]
            record.update(status='supported', family=target.get('family', 'unknown'), stratum=stratum(target),
                focusedID=target['id'], highestIDs=[r['id'] for r in winners],
                competitorID=competitors[0]['id'] if competitors else None,
                focusedScore=scores[target['id']], highestScore=highest,
                focusedRank=1+sum(scores[r['id']] > scores[target['id']] for r in subset),
                focusedMargin=scores[target['id']]-scores[competitors[0]['id']] if competitors else None,
                top1ExpectedCorrect=sum(r['label'] for r in winners)/len(winners),
                tiedTop=len(winners) > 1, randomExpectedCorrect=1/len(subset),
                topLeftCorrect=geometric['label'],
                largestAreaExpectedCorrect=sum(r['label'] for r in area_winners)/len(area_winners),
                strictThresholdOutcome=strict, runtimeStyleOutcome=runtime)
        results.append(record)
    supported = [r for r in results if r['status'] == 'supported']
    pos = [scores[r['id']] for r in rows if r['label']]
    neg = [scores[r['id']] for r in rows if not r['label']]
    return dict(frames=results, supported=len(supported), excluded=len(results)-len(supported),
        composition=dict(Counter(r['family'] for r in supported)),
        top1ExpectedCorrect=sum(r['top1ExpectedCorrect'] for r in supported) if supported else None,
        randomExpectedCorrect=sum(r['randomExpectedCorrect'] for r in supported) if supported else None,
        topLeftCorrect=sum(r['topLeftCorrect'] for r in supported) if supported else None,
        largestAreaExpectedCorrect=sum(r['largestAreaExpectedCorrect'] for r in supported) if supported else None,
        runtimeStyleCounts=dict(Counter(r['runtimeStyleOutcome'] for r in supported)),
        strictThresholdCounts=dict(Counter(r['strictThresholdOutcome'] for r in supported)),
        alwaysUnfocusedAccuracy=len(neg)/len(rows) if rows else None,
        cropAUROC=sum((a > b)+.5*(a == b) for a in pos for b in neg)/(len(pos)*len(neg)) if pos and neg else None,
        scoreDistributions={str(label): offline.distribution(pos if label else neg) for label in (0, 1)})


def load(protocol_path, result_path):
    protocol = offline.read(protocol_path)
    content = dict(protocol)
    seal = content.pop('protocolSHA256', None)
    require(protocol.get('version') in ('focus-sampler-experiment-v1', 'focus-representative-experiment-v1',
                                       'focus-pretrained-experiment-v1', 'focus-paired-experiment-v1')
            and seal == digest(content), 'incompatible_or_changed_protocol')
    require(all((r['split'], r['use']) in (('train', 'train-candidate'), ('validation', 'retention-validation'),
                ('validation', 'representative-selection')) for r in protocol['samples']), 'protected_or_unknown_role')
    result = offline.read(result_path)
    require(result['protocolSHA256'] == seal and result.get('selection', protocol['selection']) == protocol['selection']
            and result['status'] in ('completed', 'failed_no_eligible_checkpoint'), 'incompatible_result')
    require([h['epoch'] for h in result['history']] == list(range(1, protocol['configuration']['epochs']+1)),
            'incomplete_or_duplicate_epochs')
    # Stored predictions bind historical trainer identity; replay only executes
    # the metric code. An additive trainer change must not prevent old-score analysis.
    metric_files = {'focus_representative_experiment.py', 'focus_representative_validation.py',
                    'human_focus_evaluation.py', 'human_focus_roles.py'}
    for ref in protocol.get('runtime', {}).get('code', []):
        if ref['path'].rsplit('/', 1)[-1] in metric_files: offline.checked(ref)
    rows = [r for r in protocol['samples'] if r['split'] == 'validation']
    for h in [dict(epoch=0, validation=result['initial'])] + result['history']:
        actual = selection_metrics(h['validation']['predictions'], rows, protocol['selection'])
        require(all(h['validation'][k] == v for k, v in actual.items()), 'changed_published_metrics')
    return protocol, result


def run(protocol_path, result_path, output):
    output = offline.local(output)
    require(not output.exists(), 'output_exists')
    protocol_path, result_path = map(offline.local, (protocol_path, result_path))
    inputs = [offline.ref(p) for p in (protocol_path, result_path)]
    p, result = load(protocol_path, result_path)
    rows = [r for r in p['samples'] if r['use'] == 'representative-selection']
    require(rows, 'empty_supported_population')
    cache = {}
    for row in rows:
        require(len(row['bounds']) == 4 and all(type(v) in (int, float) and math.isfinite(v) for v in row['bounds']),
                'invalid_bounds')
        for kind in ('image', 'crop'):
            ref = row[kind]
            key = (ref['path'], ref['sha256'])
            if key not in cache:
                path = offline.checked(ref)
                with Image.open(path) as im:
                    require(im.width * im.height <= 40_000_000, 'oversize_image')
                    im.load()
                    if kind == 'crop': require(im.size == (256, 256), 'wrong_crop_size')
                    cache[key] = im.size
        expanded_box(row['bounds'], cache[(row['image']['path'], row['image']['sha256'])])
        require(pixel_digest(ROOT, row['crop']) == row['pixelSHA256'], 'changed_crop_pixels')
    epochs = []
    for h in [dict(epoch=0, validation=result['initial'])] + result['history']:
        values = {v['id']: v for v in h['validation']['predictions']}
        epochs.append(dict(epoch=h['epoch'], selectionLoss=h['validation']['selectionLoss'],
            checkpointEligible=h['validation']['checkpointEligible'],
            **frame_scores(rows, [values[r['id']] for r in rows], p['selection']['framePolicy'])))
    # Fixed snapshots, not post-hoc checkpoint selection: initialization, first, last.
    by_id = {r['id']: r for r in rows}
    panel = []
    for lane in ('buttons', 'tabs', 'artwork', 'rows'):
        targets = sorted([r for r in rows if r['label'] and stratum(r) == lane], key=lambda r: r['id'])
        for target in targets[:2]:
            same_frame = [r for r in rows if r['frameID'] == target['frameID'] and not r['label']]
            last_scores = {x['id']: x['probability'] for x in result['history'][-1]['validation']['predictions']}
            competitor = sorted(same_frame, key=lambda r: (-last_scores[r['id']], r['id']))[0] if same_frame else None
            panel.append(dict(stratum=lane, target=target['id'], competitor=competitor['id'] if competitor else None,
                              frameID=target['frameID']))
    output.mkdir(parents=True)
    for i, item in enumerate(panel, 1):
        target = by_id[item['target']]
        item['page'] = offline.page(output, i, {**target, 'frame': target['image']},
            item['stratum']+' / human-reviewed target', 'Existing production crops; not new labels',
            by_id.get(item['competitor']))
    for ref in inputs: offline.checked(ref)
    report = dict(version=VERSION, inputs=inputs,
        implementation=[offline.ref(ROOT/path) for path in ('scripts/focus_reset_diagnostics.py',
            'scripts/focus_offline_diagnosis.py', 'scripts/focus_representative_experiment.py',
            'scripts/human_focus_roles.py', 'Sources/NativeUIAuditKit/Detection/NativeUIDetectionRequest.swift')],
        modelExecution=False, trainingEligible=False, finalChallengeScored=False,
        independentEvaluationEligible=False, releaseGateChanged=False,
        verifiedImageFiles=len(cache), verifiedPredictions=len(result['initial']['predictions'])*(len(result['history'])+1),
        epochs=epochs, panel=panel,
        limitations=['human/native candidate boxes, not detector recall', 'cached MPS scores, not CoreML parity',
                    'tied native winners unavailable', 'reused development data; no calibration fitted'])
    offline.write(output/'report.json', report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', required=True)
    parser.add_argument('--result', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    report = run(args.protocol, args.result, args.output)
    print(f"Verified {report['verifiedPredictions']} cached predictions; {len(report['panel'])} evidence pages. No inference.")


if __name__ == '__main__':
    main()
