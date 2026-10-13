"""Read-only schema2 action/frame correlation audit; no capture or model calls."""
import argparse
from collections import Counter
import json
import statistics
import re
from pathlib import Path
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
    rows = [];raw_timing=[];generation_pairs=Counter()
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
            generation_pairs[(action.get('connectionGeneration'),frame.get('connectionGeneration'))]+=1
            if t is not None and role!='preInput':
                raw_timing.append(dict(actionID=ident,frameID=frame['frameID'],role=role,
                    afterDispatchMilliseconds=(ft-t)/1e6,
                    afterCompletionMilliseconds=(ft-ticks[-1])/1e6 if ticks[-1] is not None else None,
                    beforeNextDispatch=following is None or ft<following,
                    actionGeneration=action.get('connectionGeneration'),frameGeneration=frame.get('connectionGeneration'),
                    qualified=False))
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
        reportedAssociationTiming=raw_timing,
        generationCounterPairs=[dict(action=a,frame=f,count=n) for (a,f),n in generation_pairs.items()],
        limitations=['Metadata associations, not pixel or native focus qualification.',
            'Completed dispatch does not prove intended UI outcome; repeated bytes do not prove no-op.',
            'Settlement is producer-declared; associations after a subsequent dispatch are excluded.',
            'No human transition labels or training admission.',
            'Reported association timing is unqualified. Different counters may represent different connection domains.'])


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


def analyze_summary(summary, cases, diagram):
    """Audit the sanitized offer without treating command results as focus labels."""
    h.require(type(summary) is dict and type(summary.get('schema')) is int and summary['schema']==1,
              'unsupported_summary_schema')
    h.require(type(summary.get('session')) is str and bool(summary['session']) and
              type(summary.get('source_manifest_sha256')) is str and
              re.fullmatch('[0-9a-f]{64}',summary['source_manifest_sha256']),'summary_identity')
    for key in ('frames','unique_images','commands','commands_with_result','commands_without_result'):
        h.require(type(summary.get(key)) is int and summary[key]>=0,'invalid_summary_count')
    h.require(type(cases) is list and len(cases)<=10000 and len(cases)==summary['frames'],'frame_count')
    ids={}; frame_ids=set();sequences=set();hashes={};roles=Counter()
    for case in cases:
        h.require(type(case) is dict and set(case)=={'case_id','frame_id','sha256','role','sequence'},'case_fields')
        ident=case['case_id'];seq=case['sequence'];digest=case['sha256']
        h.require(type(ident) is str and re.fullmatch(r'F\d+',ident) and ident not in ids,'duplicate_or_invalid_case')
        h.require(type(case['frame_id']) is str and case['frame_id'] and case['frame_id'] not in frame_ids,'duplicate_frame')
        h.require(type(seq) is int and seq>=0 and seq not in sequences,'duplicate_or_invalid_sequence')
        h.require(type(digest) is str and re.fullmatch('[0-9a-f]{64}',digest),'invalid_image_hash')
        h.require(case['role'] in ('standalone','postInputUnverified','postInputSettled','transition','preInput'),'frame_role')
        ids[ident]=case;frame_ids.add(case['frame_id']);sequences.add(seq)
        hashes.setdefault(digest,[]).append(ident);roles[case['role']]+=1
    h.require([c['sequence'] for c in cases]==sorted(sequences),'frame_order')
    h.require(len(hashes)==summary['unique_images'] and dict(roles)==summary['frame_roles'],'summary_disagrees')
    h.require(type(diagram) is str and len(diagram)<=2_000_000,'diagram_limit')
    # Parse the producer's narrow text format. Never execute PlantUML directives.
    commands={};links={};declared={}
    command=re.compile(r'state "(C\d+) ([a-zA-Z0-9_-]+) / receipt (completed|failed)" as (C\d+)')
    frame=re.compile(r'state "(F\d+) / ([a-zA-Z]+)" as (F\d+)')
    edge=re.compile(r'(C\d+) --> (F\d+|Missing\d+) : (postInputUnverified|postInputSettled|no retained endpoint)')
    for line in diagram.splitlines():
        line=line.strip()
        h.require(not line.startswith('!'),'unsafe_diagram_directive')
        match=command.fullmatch(line)
        if match:
            ident,key,outcome,alias=match.groups()
            h.require(ident==alias and ident not in commands,'duplicate_or_invalid_command')
            commands[ident]=dict(commandID=ident,key=key,outcome=outcome);continue
        match=frame.fullmatch(line)
        if match:
            ident,role,alias=match.groups()
            h.require(ident==alias and ident not in declared and ident in ids and ids[ident]['role']==role,'diagram_frame')
            declared[ident]=role;continue
        match=edge.fullmatch(line)
        if match:
            ident,dest,role=match.groups()
            h.require(ident not in links,'duplicate_link')
            links[ident]=(dest,role);continue
        h.require('-->' not in line and not ('/ receipt ' in line),'unsupported_diagram_record')
    h.require(set(declared)==set(ids),'missing_diagram_frame')
    h.require(set(links)==set(commands) and len(commands)==summary['commands'],'command_count')
    review=[];results=[];missing=[];linked_frames=set()
    for ident,cmd in commands.items():
        dest,role=links[ident]
        if dest.startswith('Missing'):
            h.require(role=='no retained endpoint','missing_endpoint_role');missing.append(ident)
            results.append(dict(cmd,caseID=None,role='missing',focusChanged=None));continue
        h.require(dest in ids and ids[dest]['role']==role,'endpoint_role')
        h.require(dest not in linked_frames,'endpoint_reused');linked_frames.add(dest)
        results.append(dict(cmd,caseID=dest,role=role,focusChanged=None))
        review.append(dict(cmd,caseID=dest,imageSHA256=ids[dest]['sha256'],role=role,
            priority=0 if cmd['outcome']=='failed' else 1 if role=='postInputSettled' else 2,
            focusChanged=None,hcf='unknown',labelAuthority='unreviewed',dataRole='development',
            needs=['privacy review','pixels','focus identity review','original command and frame timing']))
    h.require(len(linked_frames)==summary['commands_with_result'] and len(missing)==summary['commands_without_result'],
              'result_count')
    h.require(len(linked_frames)+len(missing)==summary['commands'],'command_total')
    gaps=summary.get('gap_reasons',{})
    h.require(type(gaps) is dict and all(type(v) is int and v>=0 for v in gaps.values()),'invalid_gap_count')
    ordered=sorted(review,key=lambda v:(v['priority'],int(v['caseID'][1:])))
    selected=[]
    for row in ordered:
        if row['priority']<=1:selected.append(row)
    # Fill the bounded review with missing command types, not inferred screen types.
    for key in sorted({r['key'] for r in ordered}):
        if len(selected)>=12:break
        if key not in {r['key'] for r in selected}:
            selected.append(next(r for r in ordered if r['key']==key))
    positions={row['case_id']:i for i,row in enumerate(cases)}
    pair_review=[]
    for row in selected[:12]:
        i=positions[row['caseID']]
        if i==0:continue
        before=cases[i-1];after=cases[i]
        pair_review.append(dict(before=before['case_id'],after=after['case_id'],
            beforeSHA256=before['sha256'],afterSHA256=after['sha256'],
            repeatedImageHash=before['sha256']==after['sha256'],focusChanged=None,
            actionLinked=False,trainingEligible=False,
            purpose='Human review of visual change only. Multiple commands can occur between these frames.'))
    return dict(version='human-recording-summary-audit-v1',**h.FLAGS,sessionID=summary['session'],
        sourceManifestSHA256=summary['source_manifest_sha256'],counts=dict(frames=len(cases),uniqueHashes=len(hashes),
            commands=len(commands),resultFrames=len(linked_frames),missingResults=len(missing)),
        frameRoles=dict(roles),commandOutcomes=dict(Counter(r['outcome'] for r in results)),
        commandKeys=dict(Counter(r['key'] for r in results)),
        failedCommandsWithSettledFrames=[r for r in results if r['outcome']=='failed' and r['role']=='postInputSettled'],
        duplicateImageGroups=[v for v in hashes.values() if len(v)>1],gapReasons=gaps,
        commands=results,review=ordered,proposedFirstReview=[r['caseID'] for r in selected[:12]],
        proposedVisualPairReview=pair_review,
        proposedReviewBasis='Up to 12 cases: failed receipt, declared settlement, then command diversity. Not random evaluation.',
        unavailable=['focus accuracy','localization error','false changes','movement recall','HCF state','capture latency'],
        limitations=['Counts describe producer metadata, not verified pixels or observed UI outcomes.',
            'No fresh before frames are reported. Do not construct command pairs from adjacent frames.',
            'Settlement and command completion do not establish focus truth.',
            'Keep this session and related images together in development. No final evaluation claim.'])


def run_summary(offer_path,output):
    import shared_transfer as transfer
    offer_path=h.local(offer_path);offer=transfer.document(offer_path)
    h.require(offer.get('version')==2 and type(offer.get('files')) is list and len(offer['files'])==3,'summary_offer')
    docs={};refs=[]
    for item in offer['files']:
        name=Path(item['file']).name
        path=offer_path.parent/name
        h.require(path.stat().st_size<=2_000_000,'summary_size')
        transfer.verified(path,item);refs.append(h.ref(path))
        if name.endswith('-evaluation-summary.json'):docs['summary']=transfer.document(path)
        elif name.endswith('-case-index.json'):docs['cases']=transfer.document(path)
        elif name.endswith('-observed-navigation.puml'):docs['diagram']=path.read_text()
        else:raise ValueError('unsupported_summary_member')
    h.require(set(docs)=={'summary','cases','diagram'},'missing_summary_member')
    result=analyze_summary(**docs);result['inputs']=refs+[h.ref(offer_path)]
    for ref in refs:h.checked(h.ROOT,ref)
    h.write(h.fresh(output),result,sealed=True)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('batch'); p.add_argument('output')
    p.add_argument('--sanitized-summary',action='store_true')
    args = p.parse_args()
    result = run_summary(args.batch,args.output) if args.sanitized_summary else run(args.batch, args.output)
    print(json.dumps(dict(counts=result['counts'],issues=len(result.get('issues',[])),timing=result.get('timing'))))
