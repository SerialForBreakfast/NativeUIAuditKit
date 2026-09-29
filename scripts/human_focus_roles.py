"""Explicit role/coverage admission for development only; never infers labels."""
from collections import Counter
import human_annotation_review as h
import human_regression_review as review

VERSION = 'human-focus-role-admission-v1'


def partition(report, doc, complete):
    """Validate exhaustive sample/frame decisions independently of model execution."""
    h.require(doc.get('approved') is True and doc.get('reviewer') and
              doc.get('authorizationReference') and doc.get('role') == 'development-regression',
              'unapproved_role_admission')
    samples = {s['id']: s for s in report['samples']}
    h.require(len(samples) == len(report['samples']), 'duplicate_sample')
    populations = doc['populations']
    h.require(set(populations) == {'candidate', 'auxiliary', 'unresolved'}, 'invalid_populations')
    members = [i for ids in populations.values() for i in ids]
    h.require(len(members) == len(set(members)) and set(members) == set(samples), 'role_membership')
    h.require(all(samples[i]['state'] == 'unfocused' for i in populations['auxiliary']),
              'focused_auxiliary_requires_resolution')
    frames = doc['frames']
    h.require(len(frames) == len({f['id'] for f in frames}) and
              {f['id'] for f in frames} == {f['id'] for f in report['frames']}, 'frame_membership')
    for frame in frames:
        h.require(frame['settlement'] in ('settled', 'disputed', 'unknown') and
                  frame['coverage'] in ('complete', 'incomplete', 'unknown'), 'invalid_frame_policy')
        if frame['coverage'] == 'complete':
            h.require(frame['id'] in complete and not any(samples[i]['frameID'] == frame['id']
                      for i in populations['unresolved']), 'unproven_complete_frame')
        if frame['coverage'] != 'complete' or frame['settlement'] != 'settled':
            h.require(isinstance(frame.get('reason'), str) and bool(frame['reason'].strip()),
                      'missing_frame_exclusion_reason')
    pair_ids = doc.get('pairIDs', [])
    available = {p['id']: p for p in report.get('pairs', [])}
    h.require(len(pair_ids) == len(set(pair_ids)) and set(pair_ids) <= set(available), 'invalid_admitted_pairs')
    settled = {f['id'] for f in frames if f['settlement'] == 'settled'}
    for ident in pair_ids:
        pair = available[ident]
        h.require(set(pair['frames']) <= settled and all(f+':'+pair['controlID'] in populations['candidate']
                  for f in pair['frames']), 'unsupported_pair_population')
    return dict(populations=populations, frames=frames, pairIDs=pair_ids)


def admit(path, report, revision, crops):
    doc = h.sealed(path, VERSION)
    h.require(doc['revision'] == h.ref(h.local(revision)) and doc['crops'] == h.ref(h.local(crops)),
              'wrong_role_source')
    review.checked_revision(revision)
    complete = (review.checked_completeness(h.checked(h.ROOT, doc['completeness']), revision)
                if doc.get('completeness') else set())
    return partition(report, doc, complete)


def metrics(rows, predictions, policy, summarize):
    """Caller validates complete, finite predictions before invoking this function."""
    values = {p['id']: p['probability'] for p in predictions}
    by_id = {r['id']: r for r in rows}
    candidates = [by_id[i] for i in policy['populations']['candidate']]
    auxiliary = [by_id[i] for i in policy['populations']['auxiliary']]
    frame_results = []
    for frame in policy['frames']:
        subset = [r for r in candidates if r['frameID'] == frame['id']]
        truth = [r['id'] for r in subset if r['label']]
        reason = frame.get('reason', '')
        if frame['settlement'] != 'settled' or frame['coverage'] != 'complete':
            outcome = 'unavailable'
        elif len(truth) != 1:
            outcome, reason = 'unavailable', 'requires_one_true_focused_candidate'
        else:
            selected = [r['id'] for r in subset if values[r['id']] >= .85]
            outcome = ('no_focus' if not selected else 'multiple_focus' if len(selected) > 1
                       else 'unique_correct' if selected == truth else 'wrong')
        frame_results.append(dict(id=frame['id'], outcome=outcome, reason=reason,
                                  candidates=len(subset), focusedSupport=len(truth)))
    # Disputed settlement is accounted but excluded from settled crop metrics too.
    settled = {f['id'] for f in policy['frames'] if f['settlement'] == 'settled'}
    supported = [r for r in candidates if r['frameID'] in settled]
    unique = {r['pixelSHA256']:r for r in reversed(supported)}
    counts = Counter(f['outcome'] for f in frame_results)
    denominator = sum(v for k, v in counts.items() if k != 'unavailable')
    return dict(candidate=summarize(supported), candidateDuplicateSensitivity=summarize(list(unique.values())),
                auxiliary=summarize([r for r in auxiliary if r['frameID'] in settled]),
                excludedCandidates=[r['id'] for r in candidates if r['frameID'] not in settled],
                unresolved=policy['populations']['unresolved'],
                completeFrameSelection=dict(status='available' if denominator else 'unavailable',
                    supported=denominator, total=len(frame_results), counts=dict(counts), frames=frame_results))
