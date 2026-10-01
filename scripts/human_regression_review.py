"""Offline diagnostic review queues and coverage; never capture, infer or train."""
import argparse
from collections import Counter, defaultdict
import json

import human_annotation_review as h

QUEUE = 'human-regression-queue-v1'
META = 'human-regression-coverage-metadata-v1'
COMPLETE = 'human-review-completeness-v1'
FAMILIES = ('artwork-grid', 'shelf-card', 'native-list', 'button-detail',
            'navigation-toolbar', 'overlay-search-player', 'unknown')


def prepare(batch_path, metadata_path=None, *, limit=72, per_layout=3):
    """Deterministic family/layout rotation, exact pixels only, complete accounting."""
    h.require(type(limit) is int and 1 <= limit <= 1000 and
              type(per_layout) is int and 1 <= per_layout <= 1000, 'invalid_queue_limits')
    batch_path = h.local(batch_path)
    batch = h.validate_batch(batch_path)
    metadata = h.sealed(metadata_path, META) if metadata_path else {'screens': {}}
    h.require(set(metadata['screens']) <= {f['screen'] for f in batch['frames']}, 'unknown_metadata_screen')
    rows, groups = [], defaultdict(list)
    for frame in batch['frames']:
        info = metadata['screens'].get(frame['screen'], {})
        app, layout, family = (info.get(k, 'unknown') for k in ('app', 'layout', 'family'))
        for value in (app, layout, family):
            h.text(value)
            h.require(bool(value.strip()), 'empty_coverage_value')
        h.require(family in FAMILIES, 'unsupported_family')
        row = dict(id=frame['id'], screen=frame['screen'], app=app, layout=layout, family=family,
                   disposition='blocked', reasons=list(frame['reasons']))
        if 'focusTreatment' in info:
            h.text(info['focusTreatment'])
            h.require(bool(info['focusTreatment'].strip()), 'empty_focus_treatment')
            row['focusTreatment'] = info['focusTreatment']
        rows.append(row)
        if frame['disposition'] != 'imported':
            row['reasons'].append('not_imported')
            continue
        pixels = h.pixel_digest(h.ROOT, frame['image'])
        h.require(pixels == frame['pixelSHA256'], 'pixel_hash_changed')
        # Unresolved native observations cannot be cured by deduplication.
        if frame.get('nativeUnresolved'):
            row['reasons'].append('unresolved_native_observation')
            continue
        row['pixelSHA256'] = pixels
        key = (frame['screen'], h.digest(frame.get('context')), pixels)
        groups[key].append((row, frame))
    eligible = []
    for members in groups.values():
        if len({h.digest(f['proposals']) for _, f in members}) != 1:
            for row, _ in members:
                row['reasons'].append('conflicting_exact_duplicate_proposals')
            continue
        canonical, original = members[0]
        # v1 duplicate pointers are not rewritten; a cross-context alias cannot
        # become independently reviewable by hiding its existing provenance.
        if original.get('duplicateOf'):
            for row, _ in members:
                row['reasons'].append('duplicate_outside_compatible_group')
            continue
        canonical.update(disposition='eligible', reasons=[])
        eligible.append(canonical)
        for row, _ in members[1:]:
            row.update(disposition='exact-duplicate', canonical=canonical['id'],
                       reasons=['same_pixels_and_context_no_repeat_annotation'])
    buckets = defaultdict(lambda: defaultdict(list))
    for row in eligible:
        # Unknown layouts remain distinct screens, not invented independence.
        key = (row['app'], row['layout'] if row['layout'] != 'unknown' else row['screen'])
        buckets[row['family']][key].append(row)
    family_orders = {}
    for family in sorted(buckets):
        layouts = buckets[family]
        family_orders[family] = [group[n] for n in range(per_layout)
                                 for _, group in sorted(layouts.items()) if n < len(group)]
    selected = []
    for n in range(max((len(v) for v in family_orders.values()), default=0)):
        for family in sorted(family_orders):
            if n < len(family_orders[family]) and len(selected) < limit:
                selected.append(family_orders[family][n]['id'])
    for row in eligible:
        row['disposition'] = 'selected' if row['id'] in selected else 'deferred'
        row['reasons'] = [] if row['id'] in selected else ['collection_target_or_layout_cap']
    return dict(version=QUEUE, **h.FLAGS, batch=h.ref(batch_path),
                metadata=h.ref(h.local(metadata_path)) if metadata_path else None,
                limit=limit, perLayout=per_layout, selectedFrames=selected,
                batches=[selected[n:n+8] for n in range(0, len(selected), 8)], frames=rows,
                counts=dict(Counter(r['disposition'] for r in rows)),
                independence='unassessed', role='development-regression')


def validate_queue(path):
    if h.read(path).get('version') == 'human-intake-audit-queue-v1':
        from human_intake_audit import validate_queue as validate_intake_queue
        return validate_intake_queue(path)
    queue = h.sealed(path, QUEUE)
    expected = prepare(h.checked(h.ROOT, queue['batch']),
                       h.checked(h.ROOT, queue['metadata']) if queue['metadata'] else None,
                       limit=queue['limit'], per_layout=queue['perLayout'])
    h.require(h.digest(expected) == queue['seal'], 'queue_membership_or_selection_changed')
    return queue


def queue_scope(path, batch_path, batch_index=None):
    queue = validate_queue(path)
    h.require(queue['batch'] == h.ref(h.local(batch_path)), 'queue_wrong_batch')
    if batch_index is None:
        return queue['selectedFrames']
    h.require(type(batch_index) is int and 1 <= batch_index <= len(queue['batches']), 'invalid_batch_index')
    return queue['batches'][batch_index-1]


def checked_revision(path):
    revision = h.read_revision(path)
    batch = h.validate_batch(h.checked(h.ROOT, revision['batch']))
    h.require([f['id'] for f in revision['frames']] == [f['id'] for f in batch['frames']],
              'revision_membership_changed')
    snapshots = {h.checked(h.ROOT, r).stem: h.checked(h.ROOT, r) for r in revision['editorSnapshots']}
    h.require(len(snapshots) == len(revision['editorSnapshots']), 'duplicate_snapshot')
    h.require(set(snapshots) == {f['editorStem'] for f in batch['frames'] if f['disposition'] == 'imported'},
              'snapshot_membership_changed')
    for original, row in zip(batch['frames'], revision['frames']):
        if original['disposition'] != 'imported':
            continue
        if row['disposition'] == 'reviewed':
            controls = h.parse_editor(batch, original, snapshots[original['editorStem']])
            h.require(controls == row['controls'] and bool(controls) and
                      all(c['disposition'] in ('reviewed', 'rejected') for c in controls), 'revision_controls_changed')
    return revision


def attest_completeness(revision_path, frame_ids, output):
    """Internal Finish-review callback; caller has obtained explicit human consent."""
    revision = checked_revision(revision_path)
    h.require(revision['reviewer']['kind'] == 'human', 'completeness_requires_human')
    h.require(bool(frame_ids) and len(frame_ids) == len(set(frame_ids)) and set(frame_ids) <=
              {f['id'] for f in revision['frames'] if f['disposition'] == 'reviewed'}, 'invalid_complete_membership')
    receipt = dict(version=COMPLETE, **h.FLAGS, revision=h.ref(h.local(revision_path)),
                   reviewer=revision['reviewer'], frames=list(frame_ids),
                   assertion='all_visible_focusable_controls_included', attested=True)
    h.write(output, receipt, sealed=True)
    return receipt


def checked_completeness(path, revision_path):
    receipt = h.sealed(path, COMPLETE)
    revision = checked_revision(revision_path)
    h.require(receipt['revision'] == h.ref(h.local(revision_path)) and
              receipt['reviewer'] == revision['reviewer'] and revision['reviewer']['kind'] == 'human' and
              receipt['attested'] is True and receipt['assertion'] == 'all_visible_focusable_controls_included',
              'invalid_completeness_binding')
    ids = receipt['frames']
    h.require(bool(ids) and len(ids) == len(set(ids)) and set(ids) <=
              {f['id'] for f in revision['frames'] if f['disposition'] == 'reviewed'}, 'invalid_complete_membership')
    return set(ids)


def coverage(queue_path, revision_path=None, completeness_path=None):
    queue = validate_queue(queue_path)
    h.require(queue['version'] != 'human-intake-audit-queue-v1', 'use_intake_audit_summary_for_audit_queue')
    h.require(not completeness_path or revision_path, 'completeness_requires_revision')
    revision = checked_revision(revision_path) if revision_path else None
    if revision:
        h.require(revision['batch'] == queue['batch'], 'revision_wrong_batch')
    reviewed = {f['id']: f for f in revision['frames']} if revision else {}
    complete = checked_completeness(completeness_path, revision_path) if completeness_path else set()
    families, support = {}, Counter()
    for family in FAMILIES:
        rows = [r for r in queue['frames'] if r['family'] == family]
        selected = [r for r in rows if r['disposition'] == 'selected']
        confirmed = [r for r in selected if reviewed.get(r['id'], {}).get('disposition') == 'reviewed']
        families[family] = dict(available=len(rows), selected=len(selected), reviewed=len(confirmed),
                                pending=len(selected)-len(confirmed),
                                knownLayouts=len({(r['app'], r['layout']) for r in selected if r['layout'] != 'unknown'}),
                                unknownLayoutFrames=sum(r['layout'] == 'unknown' for r in selected),
                                complete=sum(r['id'] in complete for r in confirmed),
                                blocked=sum(r['disposition'] == 'blocked' for r in rows),
                                status='represented' if selected else 'unrepresented')
        for row in confirmed:
            for control in reviewed[row['id']]['controls']:
                if control['disposition'] == 'reviewed':
                    support[(family, h.control_label(control), control['state'], row.get('focusTreatment', 'unknown'))] += 1
    return dict(version='human-regression-coverage-v1', **h.FLAGS, queue=h.ref(h.local(queue_path)),
                revision=h.ref(h.local(revision_path)) if revision_path else None,
                completeness=h.ref(h.local(completeness_path)) if completeness_path else None,
                families=families, frames=queue['frames'], counts=queue['counts'],
                controlSupport=[dict(family=k[0], category=k[1], state=k[2], focusTreatment=k[3], count=v)
                                for k,v in sorted(support.items())],
                independence='unassessed', modelGate='unassessed', metricsAdmission='separate_assignment_required')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('batch'); prep.add_argument('output'); prep.add_argument('--metadata')
    prep.add_argument('--limit', type=int, default=72); prep.add_argument('--per-layout', type=int, default=3)
    report = sub.add_parser('coverage')
    report.add_argument('queue'); report.add_argument('output')
    report.add_argument('--revision'); report.add_argument('--completeness')
    args = parser.parse_args()
    result = (prepare(args.batch, args.metadata, limit=args.limit, per_layout=args.per_layout)
              if args.command == 'prepare' else coverage(args.queue, args.revision, args.completeness))
    h.write(h.local(args.output), result, sealed=True)
    print(json.dumps(dict(output=str(h.local(args.output)), counts=result['counts']), sort_keys=True))


if __name__ == '__main__':
    main()
