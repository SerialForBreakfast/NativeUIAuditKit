"""Cached two-model geometry diagnostic. Never exports an inference artifact."""
import collections
import copy
import time
import crossover189 as c

h, p, e = c.h, c.p, c.e
OUT = h.ROOT / 'reports/work/IOS-REFINE-190/attempt02/artifacts'
RULE = dict(className='pageControl', minimumIoU=.25, donorConfidence=.25,
            association='mutual-degree-one', originalConfidenceFilter=None)


def derive(original, donor, cid):
    a, b = original['results'], donor['results']
    ids = [r['imageID'] for r in a]
    h.require(len(ids) == len(set(ids)) and ids == [r['imageID'] for r in b], 'ordered_membership')
    results, audit = [], []
    for left, right in zip(a, b):
        for key in ('imageID', 'imageSHA256', 'labelSHA256', 'width', 'height'):
            h.require(left[key] == right[key], 'image_identity_' + key)
        h.require(left['status'] in ('ok', 'empty') and right['status'] in ('ok', 'empty'), 'unsuccessful_input')
        row = copy.deepcopy(left)
        edges = collections.defaultdict(list)
        reverse = collections.Counter()
        for i, detection in enumerate(left['detections']):
            if detection['classID'] != cid:
                continue
            for j, proposal in enumerate(right['detections']):
                if proposal['classID'] == cid and proposal['score'] >= RULE['donorConfidence']:
                    if e.iou_xyxy(detection['xyxyPixels'], proposal['xyxyPixels']) >= RULE['minimumIoU']:
                        edges[i].append(j)
                        reverse[j] += 1
        for i, detection in enumerate(left['detections']):
            candidates = edges[i]
            chosen = candidates[0] if len(candidates) == 1 and reverse[candidates[0]] == 1 else None
            reason = ('non_page' if detection['classID'] != cid else
                      'no_match' if not candidates else 'ambiguous' if chosen is None else 'matched')
            if chosen is not None:
                row['detections'][i]['xyxyPixels'] = copy.deepcopy(right['detections'][chosen]['xyxyPixels'])
            audit.append(dict(imageID=left['imageID'], predictionIndex=i, reason=reason,
                              donorIndices=candidates, selectedDonor=chosen))
        results.append(row)
    return dict(formatVersion='geometry-refinement-v1', rule=copy.deepcopy(RULE),
                results=results, audit=audit, productionEligible=False)


def validate_derived(document, original, donor, cid):
    """Call only after strict validation of both source inference artifacts."""
    expected = derive(original, donor, cid)
    h.require(document == expected, 'invalid_derivation')
    return document


def run():
    h.require(not OUT.exists(), 'output_collision')
    started = time.monotonic()
    protocol = c.inputs()  # Reuse sealed input/model/export/source pins; no inference.
    names = e.load_names()
    cid = names.index(RULE['className'])
    paths = {kind: {arm: h.checked(h.ROOT, protocol['reused'][arm][kind], 256*1024**2)
                   for arm in ('022', '024')} for kind in protocol['manifests']}
    requests, sources = {}, {}
    for kind, ref in protocol['manifests'].items():
        req = e.load_request(h.checked(h.ROOT, ref), 41)
        sources[kind] = {}
        for arm, size in (('022', 640), ('024', 1280)):
            doc = h.read(paths[kind][arm], 256*1024**2)
            e.validated_artifact(doc, req, protocol['checkpoints'][arm]['sha256'],
                                 expected_settings=dict(c.SETTINGS, imgsz=size))
            sources[kind][arm] = doc
        requests[kind] = req
    h.require({k: len(v.images) for k, v in requests.items()} == dict(fit=216, page=96, combined=2400), 'population_counts')
    OUT.mkdir(parents=True)
    h.write(OUT/'protocol.json', dict(rule=RULE, parent=h.ref(c.OUT/'protocol.json'),
        source=h.ref(__file__), scorer=h.ref(e.__file__), manifests=protocol['manifests'],
        inputs={k: {a: h.ref(v) for a, v in arms.items()} for k, arms in paths.items()},
        budgetBytes=128*1024**2, productionEligible=False), sealed=True)
    scores, accounting = {}, {}
    control = p.sealed(c.g.CONTROL/'evaluation.json')
    metadata = p.sealed(c.g.CONTROL/'protocol.json')['metadata']
    for kind, req in requests.items():
        left, right = sources[kind]['022'], sources[kind]['024']
        derived = derive(left, right, cid)
        path = OUT/(kind+'-derived.json')
        h.write(path, derived, sealed=True)
        retained = p.sealed(path)
        retained.pop('seal')
        validate_derived(retained, left, right, cid)
        scores[kind] = e.score(retained, req, names)
        # Verify unaffected class metrics too, not just preserved predictions.
        for before, after in zip(control['results'][kind]['perClass'], scores[kind]['perClass']):
            if before['class'] != RULE['className']:
                h.require(before == after, 'non_page_metric_changed')
        accounting[kind] = dict(collections.Counter(x['reason'] for x in retained['audit']))
        if kind == 'fit':
            cases = c.g.r.f.d.pages(req, retained, cid, metadata)
    strata = {s: dict(collections.Counter(x['disposition'] for x in cases if x['metadata']['placement'] == s))
              for s in ('leading', 'center', 'trailing')}
    reference = p.sealed(c.g.r.f.OUT/'evaluation.json')
    h.write(OUT/'evaluation.json', dict(results=scores, strata=strata, accounting=accounting,
        fitCases=cases, transitions=c.transitions(control['fitCases'], cases),
        assessment=c.g.r.assess(scores, strata, reference), protocol=h.ref(OUT/'protocol.json'),
        derived={k: h.ref(OUT/(k+'-derived.json')) for k in requests},
        seconds=time.monotonic()-started, inferenceLaunched=False, trainingLaunched=False,
        independentEvaluation=False, productionEligible=False,
        costScope='Requires both original inference paths; cached diagnostic runtime is not deployment latency.'), sealed=True)
    h.require(sum(x.stat().st_size for x in OUT.iterdir()) <= 128*1024**2, 'output_budget')
    print('190 complete: all2712records, fixed rule, no promotion', flush=True)


if __name__ == '__main__':
    run()
