"""Replayable development scorecard of production CLI predictions against reviewed controls."""
import argparse
from collections import Counter
import json
import math
import os
from pathlib import Path
import subprocess
import time

import human_annotation_review as h
from real_reference_inventory import iou

INVENTORY = h.ROOT / 'reports/work/REAL-REFERENCE-CHALLENGE-31/inventory/inventory.json'


def bounds(value):
    b = [value[k] for k in ('x', 'y', 'width', 'height')]
    h.require(all(type(x) in (int, float) and math.isfinite(x) for x in b)
              and b[2] > 0 and b[3] > 0, 'invalid_prediction_bounds')
    return b


def matching(truth, predictions, threshold):
    """Maximum-cardinality one-to-one matching; deterministic IoU-ordered edges."""
    edges = [[j for j in sorted(range(len(predictions)),
              key=lambda j: (-iou(a, predictions[j]), j))
              if iou(a, predictions[j]) >= threshold] for a in truth]
    owners = {}

    def augment(i, seen):
        for j in edges[i]:
            if j in seen:
                continue
            seen.add(j)
            if j not in owners or augment(owners[j], seen):
                owners[j] = i
                return True
        return False

    for i in range(len(truth)):
        augment(i, set())
    return dict(sorted((i, j) for j, i in owners.items()))


def score(frame, doc):
    h.require(doc['status'] == 'success' and doc['inputSHA256'] == frame['sha256'],
              'failed_or_mismatched_prediction')
    h.require(doc['configuration']['platform'] == 'tvOS' and
              doc['configuration']['ocr'] is False and
              doc['configuration']['minConfidence'] == .5, 'changed_configuration')
    result = doc['runtime']['result']
    execution = result['focusExecution']
    h.require(execution['backend'] == 'coreML' and execution['modelScoringComplete'],
              'incomplete_focus_execution')
    controls, elements = frame['controls'], result['elements']
    boxes = [bounds(e['boundingBoxPixels']) for e in elements]
    matches = matching([c['bounds'] for c in controls], boxes, .5)
    tight = matching([c['bounds'] for c in controls], boxes, .75)
    selected = [i for i, e in enumerate(elements) if e['state'].get('isFocused') is True]
    focused = [i for i, c in enumerate(controls) if c['state'] == 'focused']
    eligible = frame['complete'] and len(focused) == 1
    outcome = 'ineligible_incomplete_or_nonunique_truth'
    if eligible:
        target = focused[0]
        if target not in matches:
            outcome = 'focused_control_not_localized'
        elif not selected:
            outcome = 'no_focus_selected'
        elif len(selected) > 1:
            outcome = 'multiple_focus_selected'
        elif iou(boxes[selected[0]],controls[target]['bounds']) >= .5:
            overlaps=sum(iou(boxes[selected[0]],c['bounds'])>=.5 for c in controls)
            outcome = 'correct' if overlaps==1 else 'ambiguous_selected_geometry'
        else:
            outcome = 'wrong_focus_selected'
    rows = [dict(id=c['id'], role=h.control_label(c), focused=c['state']=='focused',
                 localized=i in matches, tightLocalized=i in tight,
                 predictedRole=elements[matches[i]]['elementType'] if i in matches else None,
                 predictionIndex=matches.get(i)) for i, c in enumerate(controls)]
    return dict(image=frame['sha256'], screen=frame['screen'], controls=rows,
                complete=frame['complete'], focusEligible=eligible, focusOutcome=outcome,
                selectedIndices=selected, predictions=len(elements),
                unmatchedPredictionsUnreviewed=len(elements)-len(matches),
                focusExecution=execution, totalMs=doc['totalMs'])


def load_frames(inventory):
    doc = h.sealed(inventory, 'real-reference-inventory-v1')
    for ref in doc['inputs'].values():
        h.checked(h.ROOT, ref)
    frames = sorted([f for values in doc['groups'].values() for f in values], key=lambda f:f['sha256'])
    h.require(len(frames) == doc['frames'] and len({f['sha256'] for f in frames}) == len(frames),
              'duplicate_or_missing_frame')
    for f in frames:
        h.require(f['sha256'] == f['image']['sha256'], 'image_identity_mismatch')
        size = h.image(h.ROOT, f['image'])
        h.require(len({c['id'] for c in f['controls']}) == len(f['controls']), 'duplicate_control')
        for c in f['controls']:
            b = c['bounds']
            h.require(len(b)==4 and all(math.isfinite(x) for x in b) and min(b[2:])>0,
                      'invalid_truth_bounds')
            h.require(b[0]>=0 and b[1]>=0 and b[0]+b[2]<=size[0]+1 and b[1]+b[3]<=size[1]+1,
                      'truth_outside_image')
    return frames


def summarize(frames):
    roles = {}
    for f in frames:
        for c in f['controls']:
            row = roles.setdefault(c['role'], Counter())
            row['reviewed'] += 1
            row['localized50'] += c['localized']
            row['localized75'] += c['tightLocalized']
            row['exactRoleOnLocalized'] += c['localized'] and c['role']==c['predictedRole']
            row['focusedTruth'] += c['focused']
            row['focusedLocalized50'] += c['focused'] and c['localized']
    return dict(frames=len(frames), roles=roles,
                completeFocusOutcomes=Counter(f['focusOutcome'] for f in frames if f['focusEligible']),
                focusEligible=sum(f['focusEligible'] for f in frames),
                unreviewedPredictions=sum(f['unmatchedPredictionsUnreviewed'] for f in frames))


def run(output, replay=False, report_output=None):
    out = h.local(output)
    h.require(report_output is None or replay, 'new_report_requires_replay')
    frames = load_frames(INVENTORY)
    h.require(len(frames)<=46, 'image_budget')
    binary = h.ROOT / '.build/debug/nativeui-audit'
    if not replay:
        h.fresh(out); out.mkdir(parents=True)
        h.write(out/'inputs.json', dict(inventory=h.ref(INVENTORY), binary=h.ref(binary),
                                      frames=frames, configuration=dict(platform='tvOS', ocr=False, minConfidence=.5)))
        start=time.monotonic()
        for i, f in enumerate(frames):
            remaining=300-(time.monotonic()-start)
            h.require(remaining>0, 'inference_budget_exhausted')
            command=[str(binary),'scan',str(h.checked(h.ROOT,f['image'])), '--platform','tvOS',
                     '--min-confidence','0.5','--no-ocr','--strict','--root',str(h.ROOT)]
            proc=subprocess.run(command,cwd=h.ROOT,capture_output=True,text=True,timeout=min(90,remaining),
                env={**os.environ,'TMPDIR':str(h.ROOT/'.build/debug-output/focus-launch/tmp')})
            (out/f'{i:03d}.json').write_text(proc.stdout)
            (out/f'{i:03d}.stderr').write_text(proc.stderr)
            h.write(out/f'{i:03d}.receipt.json',dict(command=command,exitCode=proc.returncode,
                    elapsedSeconds=time.monotonic()-start,sha256=f['sha256']))
            h.require(proc.returncode==0, 'runtime_failure_retained')
            print(f'{i+1}/{len(frames)} {time.monotonic()-start:.1f}s',flush=True)
        h.write(out/'execution.json',dict(seconds=time.monotonic()-start,pid=os.getpid(),images=len(frames)))
    frozen=h.read(out/'inputs.json')
    h.require(frozen['frames']==frames and frozen['inventory']==h.ref(INVENTORY), 'changed_replay_inputs')
    results=[]; identities=[]
    for i,f in enumerate(frames):
        d=h.read(out/f'{i:03d}.json')
        results.append(score(f,d))
        e=d['runtime']['result']['focusExecution']
        identities.append(dict(detector=d['runtime']['detector'],focusDigest=e.get('modelDigest'),
                               focusPolicy=e['policy'],threshold=e.get('threshold')))
    h.require(all(x==identities[0] for x in identities), 'model_changed_during_batch')
    report=dict(version='real-model-scorecard-v1',**h.FLAGS,inputs=h.ref(out/'inputs.json'),
                rawPredictions=[h.ref(out/f'{i:03d}.json') for i in range(len(frames))],
                implementation=h.ref(__file__),identity=identities[0],summary=summarize(results),frames=results)
    destination=h.local(report_output) if report_output else out
    if report_output and not destination.exists():
        h.fresh(report_output)
        destination.mkdir(parents=True)
    if replay and (destination/'scorecard.json').exists():
        prior=h.sealed(destination/'scorecard.json','real-model-scorecard-v1')
        h.require(all(prior[k]==report[k] for k in ('inputs','identity','summary','frames')),
                  'replay_differs_from_retained_scorecard')
        if prior.get('rawPredictions'):
            h.require(prior['rawPredictions']==report['rawPredictions'],'changed_raw_predictions')
        print('Replay matches retained scorecard (no inference).')
        return
    h.write(destination/'scorecard.json',report,sealed=True)
    lines=['# Real-screen production baseline','',
      'Development evidence, not an independent benchmark. Unmatched predictions remain unreviewed, not false positives.',
      '', '| Reviewed role | Controls | Located IoU .50 | Located IoU .75 | Exact role among located |',
      '|---|---:|---:|---:|---:|']
    for role,r in sorted(report['summary']['roles'].items()):
        lines.append(f"| {role} | {r['reviewed']} | {r['localized50']} | {r['localized75']} | {r['exactRoleOnLocalized']}/{r['localized50']} |")
    lines += ['',f"Complete-frame focus outcomes: `{dict(report['summary']['completeFocusOutcomes'])}`.",
              '', 'Focus-only roles have no equivalent detector class; exact role comparison is not a new taxonomy mapping.',
              '', 'The bundled production focus model is not FDR021 or the paired-input FDR036.']
    (destination/'scorecard.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(report['summary'],indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True);p.add_argument('--replay',action='store_true')
    p.add_argument('--report-output',help='Separate replay report; existing reports are verified without overwrite.')
    a=p.parse_args();run(a.output,a.replay,a.report_output)
