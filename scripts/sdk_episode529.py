"""Join exact SDK frames and bounded native history. No invented timing or training roles."""
from collections import Counter
from pathlib import Path
import research_queue as q
from experiment_templates import checked,pin
from sdk_packet502 import review
from sdk_semantics529 import semantics,transition
OUT=None


def uint(value,name):
    q.require(type(value) is int and 0<=value<2**64,'sdk529_'+name)
    return value


def timeline(snapshot):
    t=snapshot.get('timeline')
    if t is None:return None
    q.require(t.get('schemaVersion')==1,'sdk529_timeline_version')
    q.require(all(t[k]==snapshot[k] for k in ('processID','runID')),'sdk529_timeline_identity')
    for key in ('highestSequence','producerDroppedEvents','omittedEvents'):uint(t[key],key)
    q.require(t.get('producerHistoryEvictedEvents') is None or type(t['producerHistoryEvictedEvents']) is int and
              0<=t['producerHistoryEvictedEvents']<=t['producerDroppedEvents'],'sdk529_eviction')
    q.require(t.get('producerQueueGap') is None or type(t['producerQueueGap']) is bool,'sdk529_queue_gap')
    q.require(isinstance(t['events'],list) and len(t['events'])<=256,'sdk529_event_limit')
    previous=0
    for e in t['events']:
        q.require(e.get('schemaVersion')==1 and all(e[k]==t[k] for k in ('processID','runID')),'sdk529_event_identity')
        seq=uint(e['sequence'],'event_sequence');time=uint(e['monotonicNanoseconds'],'event_time')
        q.require(previous<seq<=t['highestSequence'],'sdk529_event_order');previous=seq
        # Sequence is recorder order. Buffered callback timestamps can precede a health marker.
        q.require(e['source'] in ('appDeclared','nativeCallback','swiftUIBinding','sdkHealth') and
                  isinstance(e['name'],str) and isinstance(e['fields'],dict) and len(e['fields'])<=64 and
                  all(isinstance(k,str) and isinstance(v,str) and len(v.encode())<=2048 for k,v in e['fields'].items()),'sdk529_event_fields')
    b=t.get('clockBracket')
    if b is not None:
        for key in ('hostRequestStartNS','hostResponseEndNS','producerSampleNS'):uint(b[key],key)
        q.require(0<=b['hostResponseEndNS']-b['hostRequestStartNS']<10**9,'sdk529_clock_bracket')
    return t


def frame(ref):
    q.require(set(ref)=={'image','evidence'},'sdk529_frame_fields')
    e=q.load(checked(ref['evidence']));r=review(e,checked(ref['image']))
    controls=[]
    for raw,normalized in zip(e['after']['elements'],r['elements']):
        controls.append(dict(normalized,**{k:v for k,v in semantics(raw).items() if k not in normalized}))
    a,b=timeline(e['before']),timeline(e['after']);gaps=[];interval=None
    if any(e['before'].get(k)!=e['after'].get(k) for k in ('appID','processID','runID')):
        gaps.append('producer_changed_during_capture')
    if any(e[side].get('sourceKind')!='authenticated_sdk_challenge' for side in ('before','after')):
        gaps.append('unauthenticated_observation')
    if a is None or b is None:gaps.append('timeline_unavailable')
    elif a.get('clockBracket') is None or b.get('clockBracket') is None:gaps.append('clock_mapping_unavailable')
    else:
        offsets=[(t['clockBracket']['producerSampleNS']-t['clockBracket']['hostResponseEndNS'],
                  t['clockBracket']['producerSampleNS']-t['clockBracket']['hostRequestStartNS']) for t in (a,b)]
        lo=max(o[0] for o in offsets);hi=min(o[1] for o in offsets)
        if lo>hi:gaps.append('clock_mapping_conflict')
        else:interval=[e['captureStartNS']+lo,e['captureEndNS']+hi]
    return dict(image=ref['image'],evidence=ref['evidence'],captureID=e['captureID'],sourceID=e['sourceID'],
        appID=e['after'].get('appID'),processID=e['after'].get('processID'),runID=e['after'].get('runID'),
        focusID=r['reportedFocusID'],frameFocusState=r['focusState'],
        focusState=('unknown' if not e['after']['focusKnown'] or e['after']['interrupted'] or
                    e['after'].get('sourceKind')!='authenticated_sdk_challenge' else
                    'no_focus' if r['reportedFocusID'] is None else 'focused'),controls=controls,
        frameReviewable=r['reviewable'],frameIssues=r['reasons'],timelines=[a,b],
        producerIntervalNS=interval,timingIssues=gaps,bytes=e['imageBytes'])


def episode(row):
    q.require(set(row)=={'id','scenario','group','role','frames'} and q.ID.fullmatch(row['id']),'sdk529_episode_fields')
    q.require(row['role'] in ('review_only','train','development','evaluation'),'sdk529_episode_role')
    q.require(row['group'] and row['scenario'] and 2<=len(row['frames'])<=128,'sdk529_episode_scope')
    frames=[frame(r) for r in row['frames']]
    q.require(len({f['captureID'] for f in frames})==len(frames),'sdk529_duplicate_capture')
    identities={(f['sourceID'],f['appID'],f['processID'],f['runID']) for f in frames}
    reasons=[]
    if len(identities)!=1:reasons.append('producer_changed')
    reasons.extend(x for f in frames for x in f['timingIssues'])
    # Unsettled frames remain temporal evidence. They do not become aligned image labels.
    events={};history=Counter();all_timelines=[t for f in frames for t in f['timelines'] if t]
    for t in all_timelines:
        history['retentionOmissions']=max(history['retentionOmissions'],t['omittedEvents'])
        history['evicted']=max(history['evicted'],t.get('producerHistoryEvictedEvents') or 0)
        history['historicalQueueGap']=bool(history.get('historicalQueueGap') or t.get('producerQueueGap'))
        for e in t['events']:
            key=(e['processID'],e['runID'],e['sequence']);prior=events.setdefault(key,e)
            q.require(prior==e,'sdk529_event_conflict')
    selected=[];range_=None
    if len(identities)==1 and all(f['timelines'][0] and f['timelines'][1] for f in frames):
        start=frames[0]['timelines'][0]['highestSequence'];end=frames[-1]['timelines'][1]['highestSequence'];range_=[start,end]
        if end<start or end-start>32768:reasons.append('episode_sequence_range')
        else:
            selected=sorted((e for e in events.values() if start<e['sequence']<=end),key=lambda e:e['sequence'])
            if [e['sequence'] for e in selected]!=list(range(start+1,end+1)):reasons.append('episode_event_gap')
            if any(e['name']=='ui.queue.gap' for e in selected):reasons.append('producer_event_loss')
            first,last=frames[0]['timelines'][0],frames[-1]['timelines'][1]
            lost=lambda t:t['producerDroppedEvents']-(t.get('producerHistoryEvictedEvents') or 0)
            if lost(last)>lost(first):reasons.append('producer_event_loss')
            if last.get('producerQueueGap') is True and first.get('producerQueueGap') is not True:reasons.append('producer_event_loss')
    transitions=[dict(beforeFrame=i,afterFrame=i+1,**transition(a,b)) for i,(a,b) in enumerate(zip(frames,frames[1:]))]
    if any(not t['eligible'] for t in transitions):reasons.append('focus_identity_unavailable')
    intervals=[f['producerIntervalNS'] for f in frames]
    if all(v is not None for v in intervals) and any(a[0]>b[0] for a,b in zip(intervals,intervals[1:])):reasons.append('frame_time_order')
    # Input correlation is recorded as caller-asserted. Timestamp proximity never creates a causal link.
    linked=[e for e in selected if e['fields'].get('correlation')=='caller_asserted' and e['fields'].get('input_id')]
    reasons=sorted(set(reasons))
    return dict(id=row['id'],scenario=row['scenario'],group=row['group'],role=row['role'],frames=frames,
        transitions=transitions,events=selected,eventSequenceRange=range_,history=dict(history),
        callerAssertedInputIDs=sorted({e['fields']['input_id'] for e in linked}),
        eligibility=dict(staticDiagnostics=any(f['frameReviewable'] for f in frames),temporalReview=not reasons,
                         allFramesAligned=all(f['frameReviewable'] for f in frames),
                         detectorTraining=False,focusTraining=False),reasons=reasons,
        trainingAdmitted=False,modelAccepted=False)


def intake(request):
    q.require(set(request)=={'version','id','episodes'} and request['version']=='sdk-episode-request-v1' and q.ID.fullmatch(request['id']),'sdk529_request')
    q.require(0<len(request['episodes'])<=32,'sdk529_episode_count')
    rows=[episode(r) for r in request['episodes']];groups={};pixels={}
    q.require(len({r['id'] for r in rows})==len(rows),'sdk529_duplicate_episode')
    for r in rows:
        q.require(groups.setdefault(r['group'],r['role'])==r['role'],'sdk529_group_split')
        for f in r['frames']:q.require(pixels.setdefault(f['image']['sha256'],r['role'])==r['role'],'sdk529_pixel_split')
    return dict(version='sdk-episode-intake-v1',episodes=rows,trainingAdmitted=False,modelAccepted=False,
                limitation='Native observations supervise diagnostics. No model uses privileged SDK metadata as image features.')


def build(path):
    r=q.load(path);intake(r)
    refs=[pin(path)]+[ref for e in r['episodes'] for f in e['frames'] for ref in f.values()]
    refs=list({v['path']:v for v in refs}.values())
    return dict(version='research-spec-v2',id=r['id'],task='SDK529',owner='Maximum-mini-NUIAK',kind='screen',jobKind='artifact',authority='diagnostic',
        dependencies=[],inputs=refs+[pin(Path(__file__))],adapter=dict(type='python-callable',steps=['sdk_episode529.run'],outputAttributes=['sdk_episode529.OUT']),
        limits=dict(timeoutSeconds=800,maxOutputBytes=100000000,maxAttempts=1),evidence=dict(reads=[x['path'] for x in refs],artifactReceipt='artifact-receipt.json'),
        question='Which native UI and temporal products have sufficient observed evidence?',hypothesis='Episode-specific eligibility keeps independent static work available when history is incomplete.',
        controlledComparison='Preserve all image bytes, native observations, source references, and episode groups.',decisionRule='Do not infer unknown focus, clock alignment, taxonomy, or event completeness.',
        nextActionByOutcome=dict(supported='Run matched timing and transition diagnostics on qualified episodes.',contradicted='Keep eligible static diagnostics and report the exact missing temporal evidence.'))


def run():
    spec=q.load(OUT.parents[2]/'spec.json');result=intake(q.load(checked(spec['inputs'][0])))
    q.save(OUT/'benchmark_summary.json',result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
