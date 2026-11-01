"""FOCUS556 S1: score retained FocusRing checkpoints on the real-app focus development set. No training.

Crops come from the production path (`FocusRingTool` crop mode, `FocusRingClassifier.makeCrop`).
A PyTorch parity check against the shipped Core ML model runs first. Checkpoints that do not load
into the single-crop MobileNetV4 architecture are listed as skipped.
Development frames only. The pilot holdout is not read. No threshold is chosen.
Usage: focus_candidates556.py --out NEW_JSON
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import research_queue as q
import focus_runtime as fr
import focus_diagnosis554 as fd
from perception_benchmark import _iou

R = q.ROOT/'reports/work/REALAPP554'
RUNS = q.ROOT/'NativeUITrainer/focus_ring_runs'
CROPS = q.ROOT/'.build/debug-output/focus556/crops'
DEV = dict(labels=R/'review-dev/labels', replays=R/'replays-dev/replays.json',
           sessions=[R/'capture-newstv-dev/session.json', R/'capture-photo-dev/session.json'])
T = fd.THRESHOLD


def items():
    rows, batch = [], []
    for case_id, record, export in fd.frames(DEV['replays'], DEV['sessions']):
        label = q.load(DEV['labels']/f'{case_id}.json')
        q.require(label['review']['status'] == 'accepted' and label['focus']['state'] == 'focused', 'dev_label:'+case_id)
        elements = [e for e in q.load(export/'result.json')['receipt']['provider']['elements'] if e['role'] != 'label']
        frame = dict(id=case_id, truth=label['focus']['box'], candidates=[])
        for e in elements:
            key = f"{case_id}|{e['id']}"
            frame['candidates'].append(dict(key=key, role=e['role'], iou=_iou(e['pixels'], label['focus']['box'])))
            batch.append(dict(id=key, path=record['image'], sha256=record['sha256'], bounds=list(e['pixels'])))
        frame['truthKey'] = f'{case_id}|truth'
        batch.append(dict(id=frame['truthKey'], path=record['image'], sha256=record['sha256'], bounds=label['focus']['box']))
        rows.append(frame)
    return rows, batch


def crops(batch):
    CROPS.mkdir(parents=True, exist_ok=True)
    paths = {}
    for part in fr.bounded_batches(batch, shared_images=True):  # The helper has a decoded-pixel budget.
        for r in fr.invoke(part)['results']:
            raw = base64.b64decode(r['png'])
            path = CROPS/(hashlib.sha256(r['id'].encode()).hexdigest()+'.png')
            if not path.exists():
                path.write_bytes(raw)
            q.require(path.read_bytes() == raw, 'crop_changed')
            paths[r['id']] = path
    return paths


def measure(rows, score):
    """D1: truth box >= T. D2: frames with >= 2 candidates >= T. D3: exactly 1 candidate >= T and it covers the truth."""
    d1 = sum(score[f['truthKey']] >= T for f in rows)
    pills = sum(score[f['truthKey']] > 0.01 for f in rows if f['id'].startswith('newstv-'))
    d2 = sum(sum(score[c['key']] >= T for c in f['candidates']) >= 2 for f in rows)
    d3 = 0
    for f in rows:
        high = [c for c in f['candidates'] if score[c['key']] >= T]
        d3 += len(high) == 1 and high[0]['iou'] >= .5
    false_high = sum(score[c['key']] >= T for f in rows for c in f['candidates'] if c['iou'] < .5)
    negatives = sum(c['iou'] < .5 for f in rows for c in f['candidates'])
    return dict(D1=d1, newstvPillsAbove001=pills, D2=d2, D3=d3, falseHigh=false_high, negatives=negatives)


def checkpoints():
    found = []
    for run in sorted(RUNS.iterdir()):
        for name in ('last.pt', 'best.pt'):
            path = run/'weights'/name
            if path.is_file():
                found.append(path); break
    return found


def build(out):
    import torch
    from eval_focus_ring_detector import predict_torch
    torch.set_num_threads(4)
    rows, batch = items()
    paths = crops(batch)
    keys = [b['id'] for b in batch]
    coreml = {}
    for part in fr.bounded_batches(batch, shared_images=True):
        coreml.update({r['id']: float(r['probability']) for r in fr.invoke(part, fd.MODEL)['results']})
    shipped = RUNS/'fdr001/weights/best.pt'
    reference = dict(zip(keys, predict_torch(shipped, [dict(path=paths[k]) for k in keys])))
    diff = max(abs(reference[k]-coreml[k]) for k in keys)
    agree = sum((reference[k] >= T) == (coreml[k] >= T) for k in keys)
    results, skipped = [], []
    for path in checkpoints():
        try:
            scores = reference if path == shipped else dict(zip(keys, predict_torch(path, [dict(path=paths[k]) for k in keys])))
        except (RuntimeError, KeyError, ValueError) as error:
            skipped.append(dict(checkpoint=str(path.relative_to(q.ROOT)), reason=str(error).splitlines()[0][:160])); continue
        results.append(dict(checkpoint=str(path.relative_to(q.ROOT)), sha256=q.digest(path), **measure(rows, scores)))
    results.sort(key=lambda r: (-r['D3'], -r['D1'], r['D2'], r['falseHigh']))
    doc = dict(version='focus556-s1-v1', frames=len(rows), crops=len(keys), threshold=T,
               parity=dict(coreml=fd.MODEL.relative_to(q.ROOT).as_posix(), torch=str(shipped.relative_to(q.ROOT)), maxAbsDiff=diff,
                           decisionAgreement=f'{agree}/{len(keys)}', coremlBaseline=measure(rows, coreml)),
               baseline=measure(rows, reference), candidates=results, skipped=skipped,
               limitations=['D3 approximates the runtime: it uses all non-text proposals; the runtime filter is not exported.',
                            'Retention (R1) is not measured here. Use each run\'s recorded result before any choice.'])
    q.save(out, doc)
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, required=True)
    doc = build(parser.parse_args().out)
    print(json.dumps(dict(parity=doc['parity'], baseline=doc['baseline'], scored=len(doc['candidates']), skipped=len(doc['skipped'])), indent=1))
    for r in doc['candidates'][:15]:
        print(r['checkpoint'].split('/')[2], {k: r[k] for k in ('D1', 'newstvPillsAbove001', 'D2', 'D3', 'falseHigh')})


if __name__ == '__main__':
    main()
