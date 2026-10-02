"""Audit recorded focus endpoints and minimize pending review; no inferred labels."""
import argparse
from collections import Counter,defaultdict
from itertools import combinations
import json

import human_annotation_review as h
import human_recording_audit as recording
import human_recording_review as review
import focus_artwork_readiness as baseline_reader
import human_regression_review as regression


def reviewed_frames(base, pending_path, revision_path=None, completeness_path=None):
    """Explicit immutable truth; mutable editor files never supply labels."""
    h.require(not completeness_path or revision_path, 'completeness_requires_revision')
    frames={}
    for r in base['samples']:
        if not r.get('image') or r.get('use') not in ('representative-selection','human-static-auxiliary'):
            continue
        h.checked(h.ROOT,r['image'])
        f=frames.setdefault(r['image']['sha256'],dict(image=r['image'],screen=r['screen'],
                           controls=[],complete=False,source='frozen-protocol'))
        h.require(f['screen']==r['screen'], 'conflicting_screen_context')
        c=dict(id=r['id'],bounds=r['bounds'],state=r['state'],**{'class':r['class']})
        if r.get('focusRole'):c['focusRole']=r['focusRole']
        same=[x for x in f['controls'] if x['bounds']==c['bounds']]
        h.require(all(h.control_label(x)==h.control_label(c) and x['state']==c['state'] for x in same),
                  'conflicting_frozen_labels')
        if not same:f['controls'].append(c)
    if revision_path:
        revision=regression.checked_revision(h.local(revision_path))
        h.require(revision['batch']==h.ref(h.local(pending_path)), 'revision_wrong_batch')
        h.require(revision['reviewer']['kind']=='human', 'revision_requires_human')
        originals={f['id']:f for f in h.validate_batch(pending_path)['frames']}
        complete=regression.checked_completeness(h.local(completeness_path),h.local(revision_path)) if completeness_path else set()
        for row in revision['frames']:
            original=originals[row['id']]
            h.require(row['image']==original['image'] and row['screen']==original['screen'], 'revision_frame_binding')
            if row['disposition']!='reviewed':continue
            controls=[c for c in row['controls'] if c['disposition']=='reviewed']
            old=frames.get(row['image']['sha256'])
            if old:
                # A revision may add controls; changing already accepted truth is explicit work.
                for c in old['controls']:
                    matches=[x for x in controls if x['bounds']==c['bounds'] and h.control_label(x)==h.control_label(c)]
                    h.require(len(matches)==1 and matches[0]['state']==c['state'], 'review_conflicts_with_frozen_truth')
            frames[row['image']['sha256']]=dict(image=row['image'],screen=row['screen'],
                controls=controls,complete=row['id'] in complete,source='human-revision',revision=h.ref(h.local(revision_path)))
    return frames


def review_frontier(actions, candidates):
    """Exact small-batch coverage, not a greedy preference for single-endpoint pairs."""
    candidates=sorted(set(candidates));h.require(len(candidates)<=8,'review_frontier_limit')
    needs=[set(a['missingReview']) for a in actions if a['metadataReady']]
    result=[]
    for count in range(len(candidates)+1):
        best=None
        for selected in combinations(candidates,count):
            available=set(selected);unlocked=sum(n<=available for n in needs)
            if best is None or unlocked>best['annotationCompleteActions']:
                best=dict(reviewCount=count,selected=list(selected),annotationCompleteActions=unlocked)
        result.append(best)
    return result


def endpoints(audit, events, reviewed, pending):
    frames={e['frame']['_0']['frameID']:e['frame']['_0'] for e in events if 'frame' in e}
    gaps=defaultdict(list);unattributed=[]
    for e in events:
        if 'gap' not in e:continue
        g=e['gap']['_0'];reason=g.get('reason','unknown')
        if reason=='advisorySkipped':continue  # optional OCR is not focus truth
        if g.get('precedingActionID'):gaps[g['precedingActionID']].append(reason)
        else:unattributed.append(reason)
    rows=[]
    for action in audit['actions']:
        reasons=list(action['reasons'])+['recorded_gap:'+r for r in gaps[action['actionID']]]
        choices={}
        for name,key in [('before','preFrames'),('after','settledFrames')]:
            eligible=[frames[f] for f in action[key]]
            # Closest pre-input and first producer-declared settled post-input.
            eligible.sort(key=lambda f:(f['capturedMonotonicNanoseconds'],f['frameID']),reverse=name=='before')
            if eligible:choices[name]=eligible[0]
        missing=sorted({f['sha256'] for f in choices.values() if f['sha256'] not in reviewed})
        rows.append(dict(actionID=action['actionID'],command=action['command'],
            metadataReady=action['associationReady'] and not reasons,
            endpoints={k:dict(frameID=f['frameID'],sequence=f['sequenceNumber'],sha256=f['sha256'],
                reviewed=f['sha256'] in reviewed,prepared=f['sha256'] in pending) for k,f in choices.items()},
            missingReview=missing,reasons=sorted(set(reasons)),
            annotationsComplete=len(choices)==2 and not missing,
            runtimeContextVerified=False,persistentIdentityVerified=False))
    return rows,dict(Counter(unattributed))


def run(batch_path, baseline_path, pending_path, revision_path=None, completeness_path=None):
    batch_path,baseline_path,pending_path=map(h.local,(batch_path,baseline_path,pending_path))
    batch=review.validate(batch_path);pending_batch=h.validate_batch(pending_path)
    h.require(batch['sessionID']==pending_batch['sessionID'] and
              batch['events']['sha256']==pending_batch['events']['sha256'],'different_recording')
    manifest=h.read(h.checked(h.ROOT,batch['manifest']));eventpath=h.checked(h.ROOT,batch['events'])
    h.require(eventpath.stat().st_size<=64*1024**2,'event_size_limit')
    events=review.events(eventpath);audit=recording.analyze(manifest,events)
    base=baseline_reader.baseline(baseline_path)
    reviewed=reviewed_frames(base,pending_path,revision_path,completeness_path)
    pending={f['image']['sha256']:f for f in pending_batch['frames']}
    h.require(len(pending)==len(pending_batch['frames']),'duplicate_pending_image')
    # Mutable editor contents never become truth without a saved reviewed revision.
    rows,unattributed=endpoints(audit,events,reviewed,pending)
    frontier=review_frontier(rows,pending)
    for item in frontier:
        item['frames']=[dict(id=pending[s]['id'],image=pending[s]['image'],screen=pending[s]['screen']) for s in item['selected']]
    refs=dict(batch=h.ref(batch_path),baseline=h.ref(baseline_path),pending=h.ref(pending_path),events=h.ref(eventpath))
    if revision_path:refs['revision']=h.ref(h.local(revision_path))
    if completeness_path:refs['completeness']=h.ref(h.local(completeness_path))
    return dict(version='focus-recorded-readiness-v1',**h.FLAGS,inputs=refs,actions=rows,
        implementation=[h.ref(h.ROOT/'scripts'/name) for name in
                        ('focus_recorded_readiness.py','human_recording_audit.py','human_recording_review.py')],
        counts=dict(actions=len(rows),originalTimingReady=audit['counts']['associatedReady'],
                    metadataReady=sum(r['metadataReady'] for r in rows),
                    annotatedMetadataReady=sum(r['metadataReady'] and r['annotationsComplete'] for r in rows),
                    preparedFrames=len(pending),reviewedImageHashes=len(reviewed)),
        reviewFrontier=frontier,unattributedGaps=unattributed,
        qualifiedTransitionAccuracy=None,
        remaining=['Saved human endpoint review','Same-screen/Settings context evidence',
                   'Persistent control correspondence','Unattributed gap reconciliation'],
        warning='Review frontier counts endpoint annotation opportunities only, not qualified transitions or independent journeys.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('batch','baseline','pending','output'):p.add_argument('--'+name,required=True)
    p.add_argument('--revision');p.add_argument('--completeness')
    a=p.parse_args()
    try:
        out=h.fresh(a.output);r=run(a.batch,a.baseline,a.pending,a.revision,a.completeness);h.write(out,r,sealed=True)
        print(json.dumps(dict(counts=r['counts'],frontier=[{k:v for k,v in f.items() if k not in ('selected','frames')} for f in r['reviewFrontier']])));return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print('Recorded readiness blocked: '+str(e));return 2


if __name__=='__main__':raise SystemExit(main())
