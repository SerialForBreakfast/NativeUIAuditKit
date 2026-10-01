"""Offline random/exception review in isolated existing Labelme workspaces.

No capture, model loading, inferred labels, automatic approval or training admission.
"""
import argparse
import copy
import json
import random

import human_annotation_review as h
import human_regression_review as regression
from human_review_audit import overlap

PLAN = 'human-intake-audit-plan-v1'
QUEUE = 'human-intake-audit-queue-v1'


def source_documents(batch_path, revision_path=None):
    batch_path = h.local(batch_path)
    batch = h.validate_batch(batch_path)
    ids = [h.identifier(f['id']) for f in batch['frames']]
    h.require(len(ids) == len(set(ids)), 'duplicate_frame_identity')
    stems = [h.identifier(f['editorStem']) for f in batch['frames']]
    h.require(len(stems) == len(set(stems)), 'duplicate_editor_identity')
    snapshots = {}
    if revision_path:
        revision = regression.checked_revision(h.local(revision_path))
        h.require(revision['batch'] == h.ref(batch_path), 'revision_wrong_batch')
        snapshots = {h.checked(h.ROOT, r).stem: h.checked(h.ROOT, r)
                     for r in revision['editorSnapshots']}
    docs = {}
    for frame in batch['frames']:
        if frame['disposition'] != 'imported':
            continue
        h.require(h.pixel_digest(h.ROOT, frame['image']) == frame['pixelSHA256'], 'pixels_changed')
        # Never read mutable source editor annotations; unsaved/current work is irrelevant.
        if revision_path:
            doc = h.read(snapshots[frame['editorStem']])
            h.parse_editor_document(batch, frame, snapshots[frame['editorStem']], doc)
        else:
            doc = h.editor_document(batch['id'], frame)
            h.require(len(frame['proposals']) <= 100, 'control_limit')
            proposal_ids = [h.identifier(p['id']) for p in frame['proposals']]
            h.require(len(proposal_ids) == len(set(proposal_ids)), 'duplicate_control_identity')
            for p in frame['proposals']:
                h.box(p['bounds'], frame['size'])
                h.require(p['class'] in h.review_labels() and
                          p['state'] in ('focused', 'unfocused', 'unknown'), 'invalid_proposal')
        docs[frame['id']] = doc
    return batch, docs


def findings(doc):
    """Conservative structural flags, not diagnoses; never alter a rectangle."""
    reasons = []
    active = [s for s in doc['shapes'] if not s['flags'].get('rejected')]
    if not active:
        reasons.append('no_active_boxes')
    if sum(s['flags'].get('focused', False) for s in active) > 1:
        reasons.append('multiple_focused_controls')
    for shape in active:
        flags = shape['flags']
        if not flags.get('focused') and not flags.get('unfocused'):
            reasons.append('unknown_focus')
        if flags.get('focused') and flags.get('unfocused'):
            reasons.append('conflicting_focus')
        if flags.get('flagged'):
            reasons.append('reviewer_flagged')
    def bounds(s):
        (x, y), (xx, yy) = s['points']
        return [min(x, xx), min(y, yy), abs(xx-x), abs(yy-y)]
    boxes = [bounds(s) for s in active]
    if any(overlap(a, b) / min(a[2]*a[3], b[2]*b[3]) > .8
           for n, a in enumerate(boxes) for b in boxes[n+1:]):
        reasons.append('overlapping_boxes_may_be_legitimate')
    return sorted(set(reasons))


def plan(batch_path, revision_path=None, *, seed=42, count=8, exception_limit=8, focus_element=None):
    h.require(type(seed) is int and type(count) is int and 1 <= count <= 256 and
              type(exception_limit) is int and 0 <= exception_limit <= 256, 'invalid_sampling_limits')
    batch_path = h.local(batch_path)
    batch, docs = source_documents(batch_path, revision_path)
    rows = []
    for frame in sorted(batch['frames'], key=lambda f: f['id']):
        native_findings=frame.get('reviewFindings',[])
        h.require(isinstance(native_findings,list) and len(native_findings)<=32 and
                  all(isinstance(v,str) and 0<len(v)<=128 for v in native_findings),'invalid_review_findings')
        excluded = list(frame['reasons']) if frame['disposition'] != 'imported' else []
        if frame['disposition'] != 'imported':
            excluded.append('not_imported')
        if frame.get('nativeUnresolved'):
            excluded.append('unresolved_native_observation')
        if frame.get('duplicateOf'):
            excluded.append('existing_exact_duplicate_alias')
        rows.append(dict(id=frame['id'], screen=frame['screen'], excluded=sorted(set(excluded)),
                         duplicateOf=frame.get('duplicateOf'),
                         findings=sorted(set(findings(docs[frame['id']])+native_findings)) if frame['id'] in docs else native_findings))
    population = [r['id'] for r in rows if not r['excluded']]
    selected = sorted(random.Random(seed).sample(population, min(count, len(population))))
    stratified=None
    if focus_element is not None:
        h.require(isinstance(focus_element,str) and focus_element and count>=2 and count%2==0,'invalid_focus_stratification')
        groups={'focused':[],'unfocused':[]};by_id={f['id']:f for f in batch['frames']}
        for fid in population:
            target=[p for p in by_id[fid]['proposals'] if p.get('sourceElementID')==focus_element]
            h.require(len(target)==1 and target[0]['state'] in groups,'unknown_sampling_target')
            groups[target[0]['state']].append(fid)
        rng=random.Random(seed);stratified={};selected=[]
        for state,members in groups.items():
            chosen=sorted(rng.sample(members,min(count//2,len(members))))
            stratified[state]=dict(population=members,selected=chosen,denominator=len(members),
                                  inclusionProbability=len(chosen)/len(members) if members else None)
            selected.extend(chosen)
        selected.sort()
    flagged = [r['id'] for r in rows if not r['excluded'] and r['findings']]
    exceptions = flagged[:exception_limit]
    union = selected + [i for i in exceptions if i not in selected]
    result=dict(version=PLAN, **h.FLAGS, sourceBatch=h.ref(batch_path),
                sourceRevision=h.ref(h.local(revision_path)) if revision_path else None,
                seed=seed, requestedCount=count, exceptionLimit=exception_limit,
                sampling=dict(method='simple-random-without-replacement', unit='eligible-frame',
                              population=population, denominator=len(population), selected=selected,
                              inclusionProbability=len(selected)/len(population) if population else None),
                exceptions=dict(selected=exceptions, deferred=flagged[exception_limit:],
                                overlap=sorted(set(selected) & set(exceptions))),
                selectedFrames=union, batches=[union[n:n+8] for n in range(0, len(union), 8)],
                frames=rows, counts=dict(total=len(rows), eligible=len(population),
                                        excluded=len(rows)-len(population), random=len(selected),
                                        flagged=len(flagged), uniqueReview=len(union)),
                limitations=['Eligible subset only; original duplicate aliases/exclusions remain accounted.',
                             'Related frames are not independent source groups; no confidence-bound claim.',
                             'Exception yield is not a random-sample defect estimate.',
                             'No Vision execution or OCR-derived control/focus truth.'])
    if stratified is not None:
        result['focusElement']=focus_element
        result['sampling'].update(method='stratified-random-without-replacement',strata=stratified,inclusionProbability=None)
    return result


def validate_plan(path):
    doc = h.sealed(h.local(path), PLAN)
    expected = plan(h.checked(h.ROOT, doc['sourceBatch']),
                    h.checked(h.ROOT, doc['sourceRevision']) if doc['sourceRevision'] else None,
                    seed=doc['seed'], count=doc['requestedCount'], exception_limit=doc['exceptionLimit'],
                    focus_element=doc.get('focusElement'))
    h.require(h.digest(expected) == doc['seal'], 'audit_population_or_selection_changed')
    return doc


def prepare(batch_path, output, revision_path=None, **options):
    """Freeze population and clone prefilled review work, preserving all original bytes."""
    output = h.fresh(output)
    report = plan(batch_path, revision_path, **options)
    batch, docs = source_documents(batch_path, revision_path)
    output.mkdir(parents=True)
    h.write(output/'plan.json', report, sealed=True)
    work = output/'review'
    (work/'editor').mkdir(parents=True)
    (output/'baseline').mkdir()
    h.copy_ref(h.ref(h.local(batch_path)), work/'batch.json')
    baseline = []
    for frame in batch['frames']:
        if frame['id'] not in docs:
            continue
        doc = copy.deepcopy(docs[frame['id']])
        stem = frame['editorStem']
        h.write(output/'baseline'/(stem+'.json'), doc)
        baseline.append(dict(id=frame['id'], document=h.ref(output/'baseline'/(stem+'.json'))))
        doc['flags'] = {k: False for k in h.FRAME_FLAGS}
        for shape in doc['shapes']:
            shape['flags']['confirmed'] = False
        h.write(work/'editor'/(stem+'.json'), doc)
        h.copy_ref(frame['image'], work/'editor'/(stem+'.png'))
    for lane, ids in (('combined', report['selectedFrames']),
                      ('random', report['sampling']['selected']),
                      ('exceptions', report['exceptions']['selected'])):
        queue = dict(version=QUEUE, **h.FLAGS, plan=h.ref(output/'plan.json'),
                     batch=h.ref(work/'batch.json'), baseline=baseline, lane=lane,
                     selectedFrames=ids, batches=[ids[n:n+8] for n in range(0, len(ids), 8)])
        h.write(output/(lane+'-queue.json'), queue, sealed=True)
        validate_queue(output/(lane+'-queue.json'))
    return report


def validate_queue(path):
    queue = h.sealed(h.local(path), QUEUE)
    report = validate_plan(h.checked(h.ROOT, queue['plan']))
    work_batch_path = h.checked(h.ROOT, queue['batch'])
    h.require(queue['batch']['sha256'] == report['sourceBatch']['sha256'], 'fork_batch_changed')
    batch, docs = source_documents(h.checked(h.ROOT, report['sourceBatch']),
                                  h.checked(h.ROOT, report['sourceRevision']) if report['sourceRevision'] else None)
    baseline = queue['baseline']
    h.require([r['id'] for r in baseline] == [f['id'] for f in batch['frames'] if f['id'] in docs],
              'baseline_membership_changed')
    for row in baseline:
        h.require(h.read(h.checked(h.ROOT, row['document'])) == docs[row['id']], 'baseline_annotations_changed')
    lanes = dict(combined=report['selectedFrames'], random=report['sampling']['selected'],
                 exceptions=report['exceptions']['selected'])
    h.require(queue['lane'] in lanes, 'unsupported_audit_lane')
    ids = lanes[queue['lane']]
    h.require(queue['selectedFrames'] == ids and queue['batches'] == [ids[n:n+8] for n in range(0, len(ids), 8)],
              'audit_queue_changed')
    h.validate_batch(work_batch_path)
    return queue


def summarize(queue_path, revision_path):
    queue = validate_queue(queue_path)
    report = validate_plan(h.checked(h.ROOT, queue['plan']))
    revision = regression.checked_revision(h.local(revision_path))
    h.require(revision['batch'] == queue['batch'], 'revision_wrong_batch')
    snapshots = {h.checked(h.ROOT, r).stem: h.checked(h.ROOT, r) for r in revision['editorSnapshots']}
    batch = h.validate_batch(h.checked(h.ROOT, queue['batch']))
    baseline = {r['id']: h.read(h.checked(h.ROOT, r['document'])) for r in queue['baseline']}
    by_id = {r['id']: r for r in revision['frames']}
    def signature(doc):
        # Ignore approval bookkeeping, label descriptions, and list order.
        return sorted([dict(id=s['group_id'], label=s['label'], points=s['points'],
                            state={k: s['flags'].get(k, False) for k in ('focused', 'unfocused', 'rejected')})
                       for s in doc['shapes']], key=lambda s: s['id'])
    rows = []
    for f in batch['frames']:
        if f['id'] not in report['selectedFrames']:
            continue
        current = h.read(snapshots[f['editorStem']])
        completed = revision['reviewer']['kind'] == 'human' and by_id[f['id']]['disposition'] == 'reviewed'
        rows.append(dict(id=f['id'], completed=completed,
                         annotationsChanged=signature(baseline[f['id']]) != signature(current)))
    by_id = {r['id']: r for r in rows}
    lanes = {}
    for name, ids in (('random', report['sampling']['selected']), ('exceptions', report['exceptions']['selected'])):
        done = [by_id[i] for i in ids if by_id[i]['completed']]
        lanes[name] = dict(selected=len(ids), completed=len(done), pending=len(ids)-len(done),
                           changedAmongCompleted=sum(r['annotationsChanged'] for r in done))
    return dict(version='human-intake-audit-summary-v1', **h.FLAGS, plan=queue['plan'],
                revision=h.ref(h.local(revision_path)), lanes=lanes, frames=rows,
                note='Changes are reviewer corrections, not automatically adjudicated defects. No quality gate or confidence interval.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('batch'); prep.add_argument('output'); prep.add_argument('--revision')
    prep.add_argument('--seed', type=int, default=42); prep.add_argument('--count', type=int, default=8)
    prep.add_argument('--exception-limit', type=int, default=8)
    prep.add_argument('--focus-element',help='Balance random review across this native target’s two focus states')
    summary = sub.add_parser('summary')
    summary.add_argument('queue'); summary.add_argument('revision'); summary.add_argument('output')
    args = p.parse_args()
    try:
        if args.command == 'prepare':
            result = prepare(args.batch, args.output, args.revision, seed=args.seed, count=args.count,
                             exception_limit=args.exception_limit,focus_element=args.focus_element)
            print(json.dumps(result['counts'], sort_keys=True))
        else:
            result = summarize(args.queue, args.revision)
            h.write(h.local(args.output), result, sealed=True)
            print(json.dumps(result['lanes'], sort_keys=True))
    except (ValueError, OSError, KeyError, TypeError) as error:
        p.exit(2, f'Audit blocked: {error}\n')


if __name__ == '__main__':
    main()
