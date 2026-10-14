"""Shared real crop preparation, inference, and reporting. No model acceptance."""
import argparse
import json
import math
from pathlib import Path
import time

import research_queue as q

OUT = None


def checked(ref):
    q.check_pin(ref)
    path = q.local_path(q.ROOT, ref['path'])
    q.require(path.is_file(), 'input_missing:' + ref['path'])
    q.require(q.digest(path) == ref['sha256'], 'input_changed:' + ref['path'])
    return path


def validate_manifest(doc):
    q.require(doc.get('version') == 'prepared-crop-membership-v1', 'membership_version')
    q.require(doc.get('preprocessing') == 'production-crops-rgb256-v1', 'preprocessing_contract')
    rows = doc.get('rows')
    q.require(isinstance(rows, list) and 1 <= len(rows) <= 16, 'membership_count')
    q.require(len({r['id'] for r in rows}) == len(rows), 'duplicate_case')
    for row in rows:
        q.require(row.get('role') == 'development', 'development_only')
        q.require(isinstance(row.get('group'), str) and row['group'], 'group_missing')
        q.require(type(row.get('label')) is int and row['label'] in (0, 1), 'label_invalid')
        q.require(row.get('profile') in ('standard', 'hcf'), 'profile_unknown')
        checked(row['image'])
    return rows


def context():
    spec = q.load(OUT.parents[2] / 'spec.json')
    return spec['templateConfig']


def deps():
    refs = [p for d in q.load(OUT / 'dependencies.json') for p in d['outputs']]
    for ref in refs:
        checked(ref)
    q.save(OUT / 'sources.json', refs)
    return {Path(p['path']).name: checked(p) for p in refs}


def prepare_at(config, output):
    import numpy as np
    from PIL import Image
    manifest = q.load(checked(config['manifest']))
    rows = validate_manifest(manifest)
    checked(config['model'])  # Check identity, never load weights during preparation.
    arrays = []
    for row in rows:
        with Image.open(checked(row['image'])) as image:
            q.require(image.size == (256, 256), 'crop_contract')
            arrays.append(np.array(image.convert('RGB'), copy=True))
    tensor = np.stack(arrays)
    np.save(output / 'tensors.npy', tensor, allow_pickle=False)
    q.save(output / 'prepared.json', dict(version='template-prepared-v1', rows=rows,
        tensorsSHA256=q.digest(output / 'tensors.npy'), preprocessing=manifest['preprocessing'],
        model=config['model'], modelAccepted=False, qualificationOnly=True))


def score_at(config, prepared, tensors, output):
    import numpy as np
    import torch
    from train_focus_ring_detector import load_mobilenetv4_conv_small
    checked(config['manifest'])
    doc = q.load(prepared)
    q.require(doc.get('version') == 'template-prepared-v1', 'prepared_version')
    q.require(doc['model'] == config['model'], 'prepared_model_changed')
    q.require(q.digest(tensors) == doc['tensorsSHA256'], 'tensor_changed')
    rows = validate_manifest(dict(version='prepared-crop-membership-v1', rows=doc['rows'], preprocessing=doc['preprocessing']))
    values = np.load(tensors, allow_pickle=False)
    q.require(values.shape == (len(rows), 256, 256, 3) and values.dtype == np.uint8, 'tensor_contract')
    torch.set_num_threads(2)
    model = load_mobilenetv4_conv_small()(pretrained=False, num_classes=1).eval()
    model.load_state_dict(torch.load(checked(config['model']), map_location='cpu', weights_only=True)['state_dict'], strict=True)
    scores = []
    with torch.no_grad():
        for offset in range(0, len(rows), config['batchSize']):
            batch = torch.from_numpy(values[offset:offset+config['batchSize']].copy()).permute(0, 3, 1, 2).float()/255
            scores.extend(torch.sigmoid(model(batch)).reshape(-1).tolist())
    q.require(len(scores) == len(rows) and all(math.isfinite(v) and 0 <= v <= 1 for v in scores), 'invalid_scores')
    q.save(output / 'predictions.json', dict(version='template-predictions-v1', model=config['model'],
        rows=[dict(**row, score=value) for row, value in zip(rows, scores)],
        modelAccepted=False, qualificationOnly=True))


def report_at(predictions, output):
    doc = q.load(predictions)
    q.require(doc.get('version') == 'template-predictions-v1', 'predictions_version')
    rows = doc['rows']
    q.require(rows and len({r['id'] for r in rows}) == len(rows), 'prediction_membership')
    result = []
    for row in rows:
        value = row['score']
        q.require(type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1, 'invalid_scores')
        q.require(type(row['label']) is int and row['label'] in (0, 1), 'label_invalid')
        decision = 1 if value >= .85 else 0 if value <= .15 else None
        result.append(dict(id=row['id'], profile=row['profile'], group=row['group'], label=row['label'],
                           score=value, decision=decision, correct=decision == row['label']))
    q.save(output / 'report.json', dict(version='template-report-v1', rows=result,
        correct=sum(r['correct'] for r in result), abstentions=sum(r['decision'] is None for r in result),
        count=len(result), groups=len({r['group'] for r in result}), model=doc['model'],
        modelAccepted=False, qualificationOnly=True,
        limitation='Small known-box development crop sample. This tests execution, not deployment accuracy or a model correction.'))


def guarded(step):
    start = time.monotonic()
    try:
        config = context()
        if step == 'prepare':
            prepare_at(config, OUT)
        elif step == 'score':
            inputs = deps()
            score_at(config, inputs['prepared.json'], inputs['tensors.npy'], OUT)
        else:
            inputs = deps()
            report_at(inputs['predictions.json'], OUT)
        q.save(OUT / 'template-result.json', dict(step=step, execution='complete', modelAccepted=False,
              qualificationOnly=True, seconds=time.monotonic()-start))
    except Exception as error:
        q.save(OUT / 'template-result.json', dict(step=step, execution='failed', code=str(error)[:500],
              errorType=type(error).__name__, modelAccepted=False, qualificationOnly=True,
              nextAction='Repair this requirement before an explicit replacement attempt.', seconds=time.monotonic()-start))
        raise


def prepare(): guarded('prepare')
def score(): guarded('score')
def report(): guarded('report')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', choices=['prepare', 'score', 'report'])
    parser.add_argument('config', type=Path)
    parser.add_argument('workspace', type=Path)
    args = parser.parse_args()
    workspace = q.local_path(q.ROOT, q.relative(args.workspace.absolute()))
    output = workspace / args.step
    output.mkdir(parents=True, exist_ok=True)
    config = q.load(args.config)
    # DVC owns replacing its isolated outputs. It never points at original evidence.
    if args.step == 'prepare': prepare_at(config, output)
    elif args.step == 'score': score_at(config, workspace/'prepare/prepared.json', workspace/'prepare/tensors.npy', output)
    else: report_at(workspace/'score/predictions.json', output)


if __name__ == '__main__': main()
