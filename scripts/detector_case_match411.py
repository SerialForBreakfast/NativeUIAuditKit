"""T42 detector-case-match: match cached detector predictions to labels per object. No new inference.

The adapter compares a baseline and a candidate prediction file on the same labelled images.
Each label gets 1 outcome per model. A lost prior success is a label that the baseline detects and the candidate does not.
Labels, predictions, and thresholds stay unchanged. Label review status is reported, not assumed.
"""
from collections import Counter, defaultdict
from pathlib import Path
import research_queue as q
from template_inputs398 import checked
from template_adapters395 import document, resolve_inputs

OUT = None
IOU = .5
# Below this overlap a same-class prediction does not count as a localization attempt.
NEAR = .1
FORMATS = ('prediction-artifact-v1', 'real-model-scorecard-v1')
ROLES = ('development', 'withheld-diagnostic')
SLICES = ('class', 'geometry', 'position', 'screen', 'state', 'edge')
# class-aware-suppressed: the candidate arm gets 1 fixed cross-class suppression before class-aware matching.
# The baseline arm stays unchanged, so lost prior successes are the labels that the suppression removes.
MATCHING = ('class-aware', 'class-agnostic', 'class-aware-suppressed')
SUPPRESS_IOU = .5
# A label or box within this many pixels of the image border counts as an edge object. It is a geometric proxy, not clipping review.
EDGE = 2.0
# Fit of the nearest box to a missed label: larger contains the label, smaller lies inside it.
CONTAIN = .8
AREA = 1.5
SUCCESS = 'detected'
STATUSES = ('detected', 'wrong-class', 'mislocalized', 'missed')


def parameters(value):
    """Return (slice, classes, groups, matching) or raise. Groups merge label and prediction classes before matching."""
    q.require(isinstance(value, dict) and set(value) == {'slice', 'classes', 'groups', 'matching'}, 'case_parameters')
    q.require(value['slice'] in SLICES, 'case_slice')
    q.require(value['matching'] in MATCHING, 'case_matching')
    classes = value['classes']
    q.require(classes is None or (isinstance(classes, list) and classes and len(classes) == len(set(classes)) and
              all(isinstance(c, str) and c for c in classes)), 'case_classes')
    groups = value['groups']
    q.require(isinstance(groups, dict) and all(isinstance(k, str) and isinstance(v, str) and k and v
              for k, v in groups.items()), 'case_groups')
    q.require(not (groups and value['matching'] == 'class-agnostic'), 'case_groups_unused')
    return value['slice'], classes, groups, value['matching']


def iou(a, b):
    """IoU of 2 top-left pixel [x1, y1, x2, y2] boxes."""
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    if w <= 0 or h <= 0:
        return 0.0
    inter = w * h
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def contained(inner, outer):
    """Fraction of the inner box area inside the outer box."""
    w = min(inner[2], outer[2]) - max(inner[0], outer[0])
    h = min(inner[3], outer[3]) - max(inner[1], outer[1])
    area = (inner[2] - inner[0]) * (inner[3] - inner[1])
    return w * h / area if w > 0 and h > 0 and area > 0 else 0.0


def fit(label, box):
    """Relation of 1 box to a label: larger, smaller, offset, or None without overlap. Fixed before results are read."""
    if contained(label, box) <= 0:
        return None
    area = lambda b: (b[2] - b[0]) * (b[3] - b[1])
    if contained(label, box) >= CONTAIN and area(box) >= AREA * area(label):
        return 'larger'
    if contained(box, label) >= CONTAIN and area(label) >= AREA * area(box):
        return 'smaller'
    return 'offset'


def suppress(found):
    """1 fixed cross-class suppression: keep a box unless a kept box with a higher or equal score overlaps it at SUPPRESS_IOU."""
    kept = []
    for item in sorted(found, key=lambda p: -p[1]):
        if all(iou(item[2], k[2]) < SUPPRESS_IOU for k in kept):
            kept.append(item)
    return kept


def match(labels, predictions, agnostic):
    """Greedy one-to-one matching in score order, as in eval_run013.score.

    labels: [(class, box)]. predictions: [(class, score, box)] above the operating confidence.
    Return (matched label index per prediction or None, outcome per label).
    """
    taken, owner = set(), []
    for cls, _, box in sorted(predictions, key=lambda p: -p[1]):
        choices = [(iou(box, b), j) for j, (c, b) in enumerate(labels)
                   if j not in taken and (agnostic or c == cls)]
        overlap, j = max(choices, default=(0.0, -1))
        if overlap >= IOU:
            taken.add(j); owner.append(j)
        else:
            owner.append(None)
    order = sorted(range(len(predictions)), key=lambda i: -predictions[i][1])
    matched = {j: order[k] for k, j in enumerate(owner) if j is not None}
    outcomes = []
    for j, (cls, box) in enumerate(labels):
        if j in matched:
            p = predictions[matched[j]]
            outcomes.append(dict(status=SUCCESS, predictedClass=p[0], iou=iou(box, p[2]), score=p[1], fit=None))
            continue
        # Diagnose the miss. Class confusion needs a well-placed box of another class.
        other = max(((iou(box, p[2]), p) for p in predictions if p[0] != cls),
                    default=(0.0, None), key=lambda v: v[0])
        eligible = [p for p in predictions if agnostic or p[0] == cls]
        near = max((iou(box, p[2]) for p in eligible), default=0.0)
        if not agnostic and other[0] >= IOU:
            outcomes.append(dict(status='wrong-class', predictedClass=other[1][0], iou=other[0], score=other[1][1],
                                 fit=fit(box, other[1][2])))
            continue
        # The fit uses the eligible box that covers most of the label. A wide group box can have IoU below 0.1.
        cover = max(eligible, key=lambda p: (contained(box, p[2]), iou(box, p[2])), default=None)
        shape = fit(box, cover[2]) if cover is not None else None
        if near >= NEAR:
            # A same-class box exists but overlaps too little, or a better box went to another label.
            outcomes.append(dict(status='mislocalized', predictedClass=None, iou=near, score=None, fit=shape))
        else:
            outcomes.append(dict(status='missed', predictedClass=None, iou=None, score=None, fit=shape))
    unmatched = [order[k] for k, j in enumerate(owner) if j is None]
    return unmatched, outcomes


def extra_kind(found, i, kept, boxes):
    """Label 1 unmatched prediction. The rule is fixed before results are read; it does not review the box.

    duplicate: it overlaps a matched prediction of the same class with a higher or equal score at the matching IoU.
    near-label: otherwise it overlaps some label at the near IoU. no-label: neither.
    """
    cls, score, box = found[i]
    if any(found[k][0] == cls and found[k][1] >= score and iou(found[k][2], box) >= IOU for k in kept):
        return 'duplicate'
    return 'near-label' if any(iou(box, b) >= NEAR for b in boxes) else 'no-label'


def bin_of(box, width, height, kind, screen):
    """Slice key of 1 [x1, y1, x2, y2] box. Bins are fixed before any result is read."""
    if kind == 'screen':
        return screen or 'unknown'
    if kind == 'state':
        # Only labels carry a focus state. Unmatched boxes share 1 bin.
        return 'prediction'
    if kind == 'edge':
        return 'edge' if min(box[0], box[1], width - box[2], height - box[3]) <= EDGE else 'interior'
    w, h = box[2] - box[0], box[3] - box[1]
    if kind == 'geometry':
        size = next(name for limit, name in ((16, 'h<16'), (32, 'h16-32'), (64, 'h32-64'), (128, 'h64-128'),
                                             (float('inf'), 'h>=128')) if h < limit)
        span = w / width
        return size + '/' + ('w<0.5' if span < .5 else 'w0.5-0.9' if span < .9 else 'w>=0.9')
    cy, cx = (box[1] + box[3]) / 2 / height, (box[0] + box[2]) / 2 / width
    vertical = 'top' if cy < .1 else 'bottom' if cy >= .9 else 'middle'
    return vertical + '-' + ('left' if cx < 1 / 3 else 'right' if cx >= 2 / 3 else 'center')


def load_ios(bundle):
    """Return images [(id, width, height, screen, labels)] and per-model predictions for YOLO text labels."""
    names = [c['name'] for c in sorted(document(bundle['categoryMap'])['categories'], key=lambda c: c['id'])]
    category = bundle['categoryMap']['sha256']
    manifest = document(bundle['labels'])
    q.require(manifest.get('formatVersion') == 'prediction-input-manifest-v1', 'labels_format')
    root = bundle['labelRoot']
    q.require(isinstance(root, str), 'label_root')
    models = {}
    for arm in ('baseline', 'candidate'):
        doc = document(bundle[arm])
        q.require(doc.get('formatVersion') == 'prediction-artifact-v1' and doc['completeness']['complete'], 'prediction_format')
        q.require(doc['categoryMap']['sha256'] == category, 'category_map_changed')
        q.require(doc['settings']['coordinateSpace'] == 'original-image-top-left-pixel-xyxy', 'coordinate_space')
        q.require(doc['settings']['confidence'] <= bundle['confidence'], 'prediction_floor')
        models[arm] = doc
    for item in bundle.get('provenance', []):
        # A receipt may name a path from another checkout. Use the local copy only when its hash matches.
        receipt = document(item['receipt'])
        q.require(receipt['sha256'] == item['local']['sha256'], 'provenance_receipt_hash')
        local = document(item['local'])
        scored = models[item['model']]
        q.require(local['model']['checkpointSHA256'] == scored['model']['checkpointSHA256'], 'provenance_model')
        source = {r['imageID']: r['detections'] for r in local['results']}
        q.require(all(source.get(r['imageID']) == r['detections'] for r in scored['results']), 'provenance_predictions')
    rows = {arm: {r['imageID']: r for r in doc['results']} for arm, doc in models.items()}
    images, predictions = [], {arm: {} for arm in models}
    for entry in manifest['images']:
        ident = entry['imageID']
        found = [rows[arm].get(ident) for arm in models]
        q.require(all(found), 'prediction_membership')
        q.require(all(r['imageSHA256'] == entry['imageSHA256'] and r['labelSHA256'] == entry['labelSHA256'] and
                      r['status'] == 'ok' for r in found), 'prediction_identity')
        width, height = found[0]['width'], found[0]['height']
        q.require(all([r['width'], r['height']] == [width, height] for r in found), 'image_size')
        relative = entry['labelPath'].removeprefix('inputs/')
        path = q.local_path(q.ROOT, root + '/' + relative)
        q.require(q.digest(path) == entry['labelSHA256'], 'label_changed')
        labels = []
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            c, cx, cy, w, h = map(float, line.split())
            labels.append((names[int(c)], ((cx - w / 2) * width, (cy - h / 2) * height,
                                           (cx + w / 2) * width, (cy + h / 2) * height)))
        images.append((ident, width, height, None, labels))
        for arm, row in zip(models, found):
            predictions[arm][ident] = [(names[d['classID']], d['score'], tuple(d['xyxyPixels'])) for d in row['detections']]
    identity = {arm: doc['model'] for arm, doc in models.items()}
    q.require(len({r['imageID'] for r in manifest['images']}) == len(manifest['images']) == len(images), 'label_membership')
    return images, predictions, identity


def load_tvos(bundle):
    """Return the same structures for a real-model scorecard and its reviewed control bounds."""
    labels_doc = document(bundle['labels'])
    models, identity = {}, {}
    for arm in ('baseline', 'candidate'):
        card = document(bundle[arm])
        q.require(card.get('version') == 'real-model-scorecard-v1', 'prediction_format')
        q.require(card['inputs'] == bundle['labels'], 'scorecard_labels_changed')
        q.require(card['partition'] == 'development' and card['trainingEligible'] is False, 'scorecard_role')
        raw = [document(ref) for ref in card['rawPredictions']]
        q.require(len(raw) == len(card['frames']) == len(labels_doc['frames']), 'scorecard_membership')
        models[arm] = raw
        identity[arm] = card['identity']['detector']
    images, predictions = [], {arm: {} for arm in models}
    for index, frame in enumerate(labels_doc['frames']):
        ident = frame['sha256'][:12]
        raws = [models[arm][index] for arm in models]
        q.require(all(r['inputSHA256'] == frame['sha256'] == frame['image']['sha256'] for r in raws), 'prediction_identity')
        q.require(all('boundingBoxPixels: pixels top-left' in r['coordinates'] for r in raws), 'coordinate_space')
        width, height = raws[0]['width'], raws[0]['height']
        labels = []
        for control in frame['controls']:
            x, y, w, h = control['bounds']
            # Focus-only roles have no detector class. Keep the scorecard name for them.
            name = control['class'] or 'focus:' + control['focusRole']
            labels.append((name, (x, y, x + w, y + h), control['id'], control.get('state') or 'unknown'))
        images.append((ident, width, height, frame['screen'], labels))
        for arm, raw in zip(models, raws):
            elements = raw['runtime']['result']['elements']
            predictions[arm][ident] = [(e['elementType'], e['confidence'],
                (e['boundingBoxPixels']['x'], e['boundingBoxPixels']['y'],
                 e['boundingBoxPixels']['x'] + e['boundingBoxPixels']['width'],
                 e['boundingBoxPixels']['y'] + e['boundingBoxPixels']['height'])) for e in elements]
    return images, predictions, identity


def evaluate(images, predictions, settings, confidence):
    """Return per-object rows and unmatched predictions for both models."""
    kind, classes, groups, matching = settings
    agnostic = matching == 'class-agnostic'
    suppressed = matching == 'class-aware-suppressed'
    rename = lambda c: groups.get(c, c)
    keep = lambda c: classes is None or c in classes
    rows, unmatched = [], []
    for ident, width, height, screen, labels in images:
        names = [rename(item[0]) for item in labels]
        boxes = [item[1] for item in labels]
        result = {}
        for arm, by_image in predictions.items():
            found = [(rename(c), s, b) for c, s, b in by_image[ident] if s >= confidence]
            if suppressed and arm == 'candidate':
                found = suppress(found)
            extra, result[arm] = match(list(zip(names, boxes)), found, agnostic)
            kept = [i for i in range(len(found)) if i not in set(extra)]
            unmatched += [dict(model=arm, image=ident, predictedClass=found[i][0], kind=extra_kind(found, i, kept, boxes),
                               slice=found[i][0] if kind == 'class' else bin_of(found[i][2], width, height, kind, screen))
                          for i in extra if keep(found[i][0])]
        for j, item in enumerate(labels):
            if not keep(names[j]) and not keep(item[0]):
                continue
            # tvOS ids repeat between frames, so the image prefix makes them unique.
            local = item[2] if len(item) > 2 else str(j)
            state = item[3] if len(item) > 3 else 'unknown'
            label_bin = (names[j] if kind == 'class' else state if kind == 'state'
                         else bin_of(boxes[j], width, height, kind, screen))
            rows.append(dict(id=ident + '#' + local, image=ident, labelClass=names[j], state=state, slice=label_bin,
                             box=[round(v, 3) for v in boxes[j]], baseline=result['baseline'][j],
                             candidate=result['candidate'][j]))
    return rows, unmatched


def summarize(rows, unmatched, settings, meta):
    """Build the reviewable summary. Per-object rows stay in cases.json."""
    # A slice may hold only unmatched predictions, for example a class without labels.
    q.require(rows or unmatched, 'empty_comparison')
    kind = settings[0]
    gains, lost, slices = [], [], {}
    for row in rows:
        before, after = row['baseline']['status'] == SUCCESS, row['candidate']['status'] == SUCCESS
        row['change'] = 'kept' if before and after else 'lost' if before else 'gained' if after else 'neither'
        if row['change'] == 'lost':
            lost.append(row['id'])
        if row['change'] == 'gained':
            gains.append(row['id'])
    groups = defaultdict(list)
    for row in rows:
        groups[row['slice']].append(row)
    extra = Counter((u['slice'], u['model']) for u in unmatched)
    for name in sorted(set(groups) | {s for s, _ in extra}):
        subset = groups.get(name, [])
        outcomes = Counter(r['change'] for r in subset)
        slices[name] = dict(
            labels=len(subset), outcomes={k: outcomes.get(k, 0) for k in ('kept', 'gained', 'lost', 'neither')},
            baseline={s: sum(r['baseline']['status'] == s for r in subset) for s in STATUSES},
            candidate={s: sum(r['candidate']['status'] == s for r in subset) for s in STATUSES},
            candidateConfusion=dict(Counter(r['candidate']['predictedClass'] for r in subset
                                            if r['candidate']['status'] == 'wrong-class').most_common()),
            unmatchedPredictions=dict(baseline=extra.get((name, 'baseline'), 0), candidate=extra.get((name, 'candidate'), 0)),
            candidateUnmatchedClasses=dict(Counter(u['predictedClass'] for u in unmatched
                                                   if u['slice'] == name and u['model'] == 'candidate').most_common()),
            missFit={arm: dict(Counter(str(r[arm]['fit']) for r in subset if r[arm]['status'] != SUCCESS))
                     for arm in ('baseline', 'candidate')},
            unmatchedKinds={arm: dict(Counter(u['kind'] for u in unmatched if u['slice'] == name and u['model'] == arm))
                            for arm in ('baseline', 'candidate')})
    single = meta['singleModel']
    ranked = sorted(slices.items(), key=lambda kv: (-(kv[1]['labels'] - kv[1]['candidate'][SUCCESS]) if single
                                                    else -kv[1]['outcomes']['lost'], kv[0]))
    decisions = [dict(slice=name, labels=value['labels'], lost=value['outcomes']['lost'], gained=value['outcomes']['gained'],
                      net=value['outcomes']['gained'] - value['outcomes']['lost'],
                      candidateMisses=value['labels'] - value['candidate'][SUCCESS],
                      wrongClass=value['candidate']['wrong-class'], mislocalized=value['candidate']['mislocalized'],
                      unmatchedPredictions=value['unmatchedPredictions']['candidate'])
                 for name, value in ranked if value['labels'] or value['unmatchedPredictions']['candidate']]
    return dict(version='detector-case-match-v1', slice=kind, classes=settings[1], groups=settings[2], matching=settings[3],
                matchingIoU=IOU, nearIoU=NEAR, **meta, labels=len(rows), images=len({r['image'] for r in rows}),
                totals=dict(baseline={s: sum(r['baseline']['status'] == s for r in rows) for s in STATUSES},
                            candidate={s: sum(r['candidate']['status'] == s for r in rows) for s in STATUSES},
                            unmatchedPredictions=dict(Counter(u['model'] for u in unmatched))),
                gains=gains, lostPriorSuccesses=lost, slices=slices, decisions=decisions, modelAccepted=False,
                limitation='Cached predictions only. Unmatched predictions are not reviewed false positives. '
                           'Single-model runs report no gains or losses. No model is accepted from this report.')


def load_bundle(bundle):
    q.require(isinstance(bundle, dict) and bundle.get('version') == 'detector-case-inputs-v1', 'bundle_version')
    allowed = {'version', 'role', 'platform', 'format', 'confidence', 'labelReview', 'baseline', 'candidate', 'labels',
               'labelRoot', 'categoryMap', 'provenance'}
    q.require(set(bundle) <= allowed, 'bundle_fields')
    # Final audit and training data are not diagnostic inputs. Reject them before any output.
    q.require(bundle.get('role') in ROLES, 'bundle_role')
    q.require(bundle.get('format') in FORMATS, 'bundle_format')
    q.require(bundle.get('labelReview') in ('unknown', 'reviewed'), 'bundle_label_review')
    q.require(type(bundle.get('confidence')) in (int, float) and 0 < bundle['confidence'] < 1, 'bundle_confidence')
    for key in ('baseline', 'candidate', 'labels') + (('categoryMap',) if bundle['format'] == FORMATS[0] else ()):
        checked(bundle[key])
    for item in bundle.get('provenance', []):
        q.require(set(item) == {'model', 'receipt', 'local'} and item['model'] in ('baseline', 'candidate'), 'provenance_fields')
    images, predictions, identity = (load_ios if bundle['format'] == FORMATS[0] else load_tvos)(bundle)
    meta = dict(platform=bundle['platform'], role=bundle['role'], format=bundle['format'],
                confidence=bundle['confidence'], labelReview=bundle['labelReview'],
                singleModel=bundle['baseline'] == bundle['candidate'],
                baselineModel=identity['baseline'], candidateModel=identity['candidate'])
    return images, predictions, meta


def run():
    cfg = q.load(OUT.parents[2] / 'spec.json')['template']
    settings = parameters(cfg['parameters'])
    refs = resolve_inputs(cfg, OUT)
    images, predictions, meta = load_bundle(document(refs['bundle']))
    if settings[3] == 'class-aware-suppressed':
        # Both arms read the same predictions. Only the candidate arm is suppressed, so changes are real comparisons.
        meta.update(singleModel=False, comparison='unsuppressed baseline versus suppressed candidate')
    rows, unmatched = evaluate(images, predictions, settings, meta['confidence'])
    report = summarize(rows, unmatched, settings, meta)
    report['bundle'] = refs['bundle']
    q.save(OUT / 'benchmark_summary.json', report)
    q.save(OUT / 'cases.json', dict(version='detector-case-rows-v1', rows=rows, unmatchedPredictions=unmatched))
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=name, sha256=q.digest(OUT / name)) for name in ('benchmark_summary.json', 'cases.json')]))
