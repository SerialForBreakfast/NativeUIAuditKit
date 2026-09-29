"""Read-only schema2 action/frame correlation audit; no capture or model calls."""
import argparse
from collections import Counter
import json
import statistics
import human_annotation_review as h


def analyze(manifest, events):
    h.require(manifest.get('schemaVersion') == 2, 'unsupported_recording_schema')
    target = manifest['targetDeviceID']
    kinds = Counter()
    actions, frames, dispatches, links, gaps, issues = {}, {}, {}, [], [], []
    for number, event in enumerate(events):
        h.require(isinstance(event, dict) and len(event) == 1, 'invalid_event_envelope')
        kind, value = next(iter(event.items())); kinds[kind] += 1
        if kind in ('action', 'frame', 'gap'): value = value['_0']
        if kind in ('action', 'frame', 'dispatch'):
            field = 'frameID' if kind == 'frame' else 'actionID'
            table = frames if kind == 'frame' else actions if kind == 'action' else dispatches
            h.require(value[field] not in table, 'duplicate_'+kind)
            table[value[field]] = value
            t = value.get('sourceDeviceID') if kind == 'frame' else value.get('targetDeviceID') if kind == 'action' else value.get('target')
            h.require(t == target, 'wrong_target')
        elif kind == 'association': links.append(value)
        elif kind == 'gap': gaps.append(value)
        elif kind != 'ocr': issues.append(dict(event=number, reason='unknown_event_kind', kind=kind))
    linked = {a: [] for a in actions}
    seen = set()
    for link in links:
        key = (link['actionID'], link['frameID'], link['role'])
        reason = None
        if key in seen: reason = 'duplicate_association'
        elif link['actionID'] not in actions: reason = 'unknown_action'
        elif link['frameID'] not in frames: reason = 'unknown_frame'
        elif link['sha256'] != frames[link['frameID']]['sha256']: reason = 'association_hash_mismatch'
        elif link['role'] not in ('preInput','transition','postInputUnverified','postInputSettled'):
            reason = 'unsupported_association_role'
        seen.add(key)
        if reason: issues.append(dict(association=link, reason=reason))
        else: linked[link['actionID']].append(link)
    for ident in set(dispatches)-set(actions): issues.append(dict(actionID=ident, reason='dispatch_without_action_result'))
    def ns(value):
        h.require(type(value) is int and value >= 0, 'invalid_monotonic_time')
        return value
    times = sorted(ns(d['monotonicNanoseconds']) for d in dispatches.values())
    rows = []
    for ident, action in actions.items():
        reasons = []
        if any(i.get('association', {}).get('actionID') == ident for i in issues):
            reasons.append('invalid_association')
        d = dispatches.get(ident)
        t = ns(d['monotonicNanoseconds']) if d else None
        if not d: reasons.append('missing_dispatch')
        elif d['command'] != action['command']: reasons.append('command_mismatch')
        following = next((v for v in times if t is not None and v > t), None)
        timing = action.get('commandTiming', {})
        ticks = [timing.get(k, {}).get('monotonic', {}).get('nanoseconds') for k in ('enqueued','transmitted','completed')]
        if any(v is None for v in ticks): reasons.append('incomplete_command_timing')
        else:
            ticks = [ns(v) for v in ticks]
            if ticks != sorted(ticks) or (t is not None and ticks[0] < t): reasons.append('command_time_order')
        pre, post, settled = [], [], []
        for link in linked[ident]:
            frame = frames[link['frameID']]; ft = ns(frame['capturedMonotonicNanoseconds'])
            role = link['role']
            if frame.get('connectionGeneration') != action.get('connectionGeneration'):
                reasons.append('generation_mismatch'); continue
            if t is None: continue
            if role == 'preInput':
                if ft > t: reasons.append('pre_frame_after_dispatch')
                else: pre.append(frame)
            else:
                if ft < t: reasons.append('post_frame_before_dispatch'); continue
                if ticks[-1] is not None and ft < ticks[-1]:
                    reasons.append('post_frame_before_command_completion'); continue
                if following is not None and ft >= following:
                    reasons.append('post_frame_after_next_dispatch'); continue
                post.append(frame)
                if role == 'postInputSettled': settled.append(frame)
        if not pre: reasons.append('no_pre_frame')
        if not post: reasons.append('no_post_frame_before_next_input')
        if not settled: reasons.append('no_declared_settled_post')
        if action['outcome'] != 'completed': reasons.append('dispatch_not_completed')
        if action.get('preFrameHash') and action['preFrameHash'] not in {f['sha256'] for f in pre}:
            reasons.append('pre_hash_unmatched')
        # Exact byte repetition is evidence only, not a no-op label.
        pre_hashes = {f['sha256'] for f in pre}
        rows.append(dict(actionID=ident, command=action['command'], outcome=action['outcome'],
            preFrames=[f['frameID'] for f in pre], postFrames=[f['frameID'] for f in post],
            settledFrames=[f['frameID'] for f in settled], reasons=sorted(set(reasons)),
            firstPostMilliseconds=(min(f['capturedMonotonicNanoseconds'] for f in post)-t)/1e6 if post else None,
            preAgeMilliseconds=(t-max(f['capturedMonotonicNanoseconds'] for f in pre))/1e6 if pre and t is not None else None,
            firstDeclaredSettledMilliseconds=(min(f['capturedMonotonicNanoseconds'] for f in settled)-t)/1e6 if settled else None,
            repeatedPrePostBytes=bool(pre_hashes & {f['sha256'] for f in post}),
            associationReady=not reasons, trainingEligible=False))
    def stats(key):
        values = sorted(r[key] for r in rows if r[key] is not None)
        return dict(n=len(values), minimum=min(values), median=statistics.median(values), maximum=max(values)) if values else dict(n=0)
    return dict(version='human-recording-audit-v1', **h.FLAGS, sessionID=manifest['sessionID'],
        eventCounts=dict(kinds), outcomes=dict(Counter(r['outcome'] for r in rows)),
        frameRoles=dict(Counter(f['role'] for f in frames.values())),
        gapReasons=dict(Counter(g['reason'] for g in gaps)), issues=issues, actions=rows,
        counts=dict(actions=len(rows), associatedReady=sum(r['associationReady'] for r in rows),
            repeatedPrePostBytes=sum(r['repeatedPrePostBytes'] for r in rows),
            frames=len(frames), distinctFrameHashes=len({f['sha256'] for f in frames.values()})),
        timing={k:stats(k) for k in ('firstPostMilliseconds','preAgeMilliseconds','firstDeclaredSettledMilliseconds')},
        limitations=['Metadata associations, not pixel or native focus qualification.',
            'Completed dispatch does not prove intended UI outcome; repeated bytes do not prove no-op.',
            'Settlement is producer-declared; associations after a subsequent dispatch are excluded.',
            'No human transition labels or training admission.'])


def run(batch_path, output):
    # Validate only retained metadata here, not the mutable annotation editor.
    batch = h.sealed(batch_path, 'human-recording-review-batch-v1')
    manifest_path = h.checked(h.ROOT, batch['manifest'])
    events_path = h.checked(h.ROOT, batch['events'])
    manifest = h.read(manifest_path)
    h.require(manifest['sessionID'] == batch['sessionID'] and
              manifest['targetDeviceID'] == batch['sourceDeviceID'], 'wrong_recording_binding')
    h.require(events_path.stat().st_size <= 64*1024*1024, 'event_size_limit')
    result = analyze(manifest, [json.loads(line) for line in events_path.read_text().splitlines() if line])
    result['inputs'] = dict(batch=h.ref(h.local(batch_path)), manifest=h.ref(manifest_path), events=h.ref(events_path))
    for ref in result['inputs'].values(): h.checked(h.ROOT, ref)
    h.write(h.fresh(output), result, sealed=True)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('batch'); p.add_argument('output')
    args = p.parse_args()
    result = run(args.batch, args.output)
    print(json.dumps(dict(counts=result['counts'], issues=len(result['issues']), timing=result['timing'])))
