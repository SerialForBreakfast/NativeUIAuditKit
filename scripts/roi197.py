"""Training-only proposal support audit. No model execution or pixel materialization."""
import collections
import math
import time
import roi193 as r

h, p, e = r.h, r.p, r.e
OUT = h.ROOT / 'reports/work/IOS-PROPOSAL-197/artifacts/support02'


def candidate(row, cid):
    h.require(row['status'] in ('ok', 'empty'), 'failed_inference')
    low = [(i, d) for i, d in enumerate(row['detections'])
           if d['classID'] == cid and .001 <= d['score'] < .25]
    if not low:
        return None, 'absent'
    index, chosen = min(low, key=lambda v: (-v[1]['score'], v[0]))
    if any(e.iou_xyxy(chosen['xyxyPixels'], d['xyxyPixels']) >= .5
           for _, d in r.proposals(row, cid)):
        return None, 'duplicate_operating'
    return (index, chosen), 'selected'


def windows(width, height):
    h.require(type(width) is int and type(height) is int and
              2 <= width <= height <= 16384, 'portrait_dimensions')
    side = math.floor(width / 2 + .5)
    stride = max(1, side // 2)
    def starts(length):
        return sorted(set(range(0, length-side+1, stride)) | {length-side})
    result = [[x, y, x+side, y+side] for y in starts(height) for x in starts(width)]
    h.require(len(result) <= 256, 'window_budget')
    return result


def contained(box, window):
    return window[0] <= box[0] and window[1] <= box[1] and window[2] >= box[2] and window[3] >= box[3]


def run():
    h.require(not OUT.exists(), 'output_collision')
    start = time.monotonic()
    parent = r.c.inputs()
    manifest = h.checked(h.ROOT, parent['manifests']['fit'])
    req = e.load_request(manifest, 41)
    membership = p.sealed(h.checked(h.ROOT, r.r.f.d.inputs()['membership']))
    roles = {v['id']: v['split'] for v in membership['rows']}
    h.require(all(roles.get(im.image_id) == 'train' for im in req.images), 'training_membership')
    path = h.checked(h.ROOT, parent['reused']['022']['fit'], 256*1024**2)
    doc = e.validated_artifact(h.read(path, 256*1024**2), req,
        parent['checkpoints']['022']['sha256'], expected_settings=r.c.SETTINGS)
    predictions = {v['imageID']: v for v in doc['results']}
    cid = e.load_names().index('pageControl')
    rows = []
    for im in req.images:
        row = predictions[im.image_id]
        truths = r.c.g.r.f.d.prior.truth(im, cid)
        base = [d['xyxyPixels'] for _, d in r.proposals(row, cid)]
        missing = [i for i, t in enumerate(truths)
                   if not any(e.iou_xyxy(t, b) >= .5 for b in base)]
        chosen, reason = candidate(row, cid)
        roi = r.window(im.width, im.height, chosen[1]['xyxyPixels']) if chosen else None
        _, candidate_audit = r.labels(im, roi) if roi else ('', [])
        candidate_page = [a for a in candidate_audit if a['classID'] == cid]
        tiled = windows(im.width, im.height)
        dispositions = collections.Counter()
        negatives = 0
        for w in tiled:
            _, audit = r.labels(im, w)
            page = [a for a in audit if a['classID'] == cid]
            dispositions.update(a['disposition'] for a in page)
            negatives += not any(a['disposition'] in ('retained', 'clipped') for a in page)
        rows.append(dict(imageID=im.image_id, truthCount=len(truths),
            operatingCovered=len(truths)-len(missing), missingTruthIndices=missing,
            candidateReason=reason, candidateIndex=chosen[0] if chosen else None,
            candidateWindow=roi, candidateScore=chosen[1]['score'] if chosen else None,
            candidateContainsMissing=sum(contained(truths[i], roi) for i in missing) if roi else 0,
            candidateContainsAny=sum(contained(t, roi) for t in truths) if roi else 0,
            candidatePageDispositions=dict(collections.Counter(a['disposition'] for a in candidate_page)),
            candidateHasVisiblePage=any(a['disposition'] in ('retained','clipped') for a in candidate_page),
            fixedWindows=tiled, fixedFullyCovered=sum(any(contained(t,w) for w in tiled) for t in truths),
            fixedNegativeCrops=negatives, fixedPageDispositions=dict(dispositions)))
    summary = dict(images=len(rows), truths=sum(v['truthCount'] for v in rows),
        operatingCovered=sum(v['operatingCovered'] for v in rows),
        candidateReasons=dict(collections.Counter(v['candidateReason'] for v in rows)),
        candidateContainsMissing=sum(v['candidateContainsMissing'] for v in rows),
        candidateWithoutCompleteTarget=sum(v['candidateWindow'] is not None and v['candidateContainsAny']==0 for v in rows),
        candidateNegativeCrops=sum(v['candidateWindow'] is not None and not v['candidateHasVisiblePage'] for v in rows),
        fixedCrops=sum(len(v['fixedWindows']) for v in rows),
        fixedMaxCrops=max(len(v['fixedWindows']) for v in rows),
        fixedFullyCovered=sum(v['fixedFullyCovered'] for v in rows),
        fixedNegativeCrops=sum(v['fixedNegativeCrops'] for v in rows),
        fixedPageDispositions=dict(sum((collections.Counter(v['fixedPageDispositions']) for v in rows), collections.Counter())))
    OUT.mkdir(parents=True)
    h.write(OUT/'support.json', dict(summary=summary, rows=rows,
        sources=[h.ref(manifest),h.ref(path),parent['checkpoints']['022'],h.ref(__file__),h.ref(r.__file__)],
        seconds=time.monotonic()-start, trainingLaunched=False, inferenceLaunched=False,
        scope='Training fit only. Coverage is containment, not detector recall; no truth-selected windows. No crops admitted or scored.'), sealed=True)
    print(summary, flush=True)


if __name__ == '__main__':
    run()
