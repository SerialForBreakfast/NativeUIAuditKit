"""Retrospective development diagnostics on reviewed recorded endpoints."""
import argparse
import base64
from collections import Counter
import io
import json
from PIL import Image

import human_annotation_review as h
import focus_recorded_readiness as readiness
import focus_transition_verifier as visual
import focus_runtime as native

POLICY=dict(minCorrespondenceIoU=.5,maxActions=32,maxControls=256)


def iou(a,b):
    ax,ay,aw,ah=a;bx,by,bw,bh=b
    area=max(0,min(ax+aw,bx+bw)-max(ax,bx))*max(0,min(ay+ah,by+bh)-max(ay,by))
    return area/(aw*ah+bw*bh-area)


def predict(before_ref,after_ref,controls,*,tracker='template'):
    """No state, after geometry, class, or after identity enters the predictor."""
    h.require(0<len(controls)<=POLICY['maxControls'],'control_limit')
    h.require(all(set(c)=={'id','bounds'} for c in controls),'prediction_truth_fields')
    h.require(len({c['id'] for c in controls})==len(controls),'duplicate_prediction_id')
    paths=[h.checked(h.ROOT,r) for r in (before_ref,after_ref)]
    images=[]
    for path in paths:
        with Image.open(path) as im:
            h.require(im.width*im.height<=40_000_000,'image_pixel_limit')
            images.append(im.convert('RGB'))
    rows=[];items=[]
    for n,c in enumerate(controls):
        t=visual.track(*images,c['bounds'],common=True,tracker=tracker)
        row=dict(id=c['id'],tracking=t,decision='unavailable');rows.append(row)
        if t['status']=='identical':row['decision']='unchanged'
        if t['status']!='matched':continue
        windows=[t.get('beforeCropBounds',c['bounds']),t.get('afterCropBounds',t['afterBounds'])]
        for k,(path,ref,bounds) in enumerate(zip(paths,(before_ref,after_ref),windows)):
            items.append(dict(id=f'{n}:{k}',path=str(path),sha256=ref['sha256'],bounds=bounds))
    runtime=native.identity() if items else None
    crops={}
    for block in native.bounded_batches(items):
        result=native.invoke(block)['results']
        h.require([r['id'] for r in result]==[r['id'] for r in block],'crop_response_membership')
        for r in result:crops[r['id']]=Image.open(io.BytesIO(base64.b64decode(r['png'],validate=True))).convert('RGB')
    if items:h.require(native.identity()==runtime,'runtime_changed')
    for n,(c,row) in enumerate(zip(controls,rows)):
        if row['tracking']['status']=='matched':
            row.update(visual.compare_crops(crops[f'{n}:0'],crops[f'{n}:1'],
                clipped=any(visual.footprint(c['bounds'],images[0].size))))
    return rows,runtime


def score(predictions,before,after):
    """After truth is accessed only here; geometry correspondence is a proxy."""
    h.require(len(after)<=POLICY['maxControls'],'control_limit')
    by={c['id']:c for c in before}; matches={}
    for p in predictions:
        bounds=p['tracking'].get('afterBounds')
        matches[p['id']]=[n for n,c in enumerate(after) if bounds and
            h.control_label(c)==h.control_label(by[p['id']]) and iou(bounds,c['bounds'])>=POLICY['minCorrespondenceIoU']]
    owners=Counter(n for values in matches.values() for n in values)
    rows=[]
    for p in predictions:
        candidates=matches[p['id']];r=dict(p,scorable=False,correct=None,expected=None)
        rows.append(r)
        if not candidates:r['scoreReason']='no_geometric_correspondence';continue
        if len(candidates)!=1 or owners[candidates[0]]!=1:
            r['scoreReason']='ambiguous_geometric_correspondence';continue
        c=by[p['id']];a=after[candidates[0]]
        h.require(c['state'] in ('focused','unfocused') and a['state'] in ('focused','unfocused'),'unknown_truth')
        expected='unchanged' if c['state']==a['state'] else 'arrival' if a['state']=='focused' else 'departure'
        r.update(scorable=True,afterControl=a['id'],expected=expected,
                 correct=p['decision']==expected,scoreReason='unique_geometric_proxy')
    return rows


def summarize(rows):
    scored=[r for r in rows if r['scorable']]
    decided=[r for r in scored if r['decision'] not in ('unknown','unavailable')]
    correct=sum(r['correct'] for r in scored)
    return dict(controls=len(rows),scorable=len(scored),decided=len(decided),correct=correct,
                wrong=sum(not r['correct'] for r in decided),abstained=len(scored)-len(decided),
                unmatched=len(rows)-len(scored),
                unscoredReasons=dict(Counter(r.get('scoreReason','unspecified') for r in rows if not r['scorable'])),
                coverage=len(decided)/len(rows) if rows else None,
                correctnessIncludingAbstentions=correct/len(scored) if scored else None,
                correctnessWhenDecided=correct/len(decided) if decided else None,
                confusion=dict(Counter(r['expected']+'->'+r['decision'] for r in scored)))


def run(batch,baseline,pending,revision=None,completeness=None,observe_pending=False):
    implementation=[h.ref(h.ROOT/'scripts'/s) for s in ('focus_recorded_transition_eval.py',
        'focus_recorded_readiness.py','focus_transition_verifier.py','focus_paired_growth.py','focus_runtime.py')]
    audit=readiness.run(batch,baseline,pending,revision,completeness)
    base=readiness.baseline_reader.baseline(h.local(baseline))
    truth=readiness.reviewed_frames(base,pending,revision,completeness)
    pending_frames={f['image']['sha256']:f for f in h.validate_batch(pending)['frames']}
    selected=[a for a in audit['actions'] if a['metadataReady'] and
        (a['annotationsComplete'] or (observe_pending and
         a['endpoints']['before']['sha256'] in truth and a['endpoints']['after']['sha256'] in pending_frames))]
    h.require(len(selected)<=POLICY['maxActions'],'action_limit_requires_explicit_subset')
    actions=[];runtime=[]
    for action in selected:
        b=truth[action['endpoints']['before']['sha256']]
        a=truth.get(action['endpoints']['after']['sha256'])
        pixel_only=a is None
        if pixel_only:a=pending_frames[action['endpoints']['after']['sha256']]
        row=dict(actionID=action['actionID'],command=action['command'],endpoints=action['endpoints'],controls=[])
        row['annotationScreenLabels']=dict(before=b['screen'],after=a['screen'])
        actions.append(row)
        if b['screen']!=a['screen'] and not pixel_only:
            row.update(status='excluded',reason='screen_label_changed');continue
        predicted,identity=predict(b['image'],a['image'],[dict(id=c['id'],bounds=c['bounds']) for c in b['controls']])
        if identity and identity not in runtime:runtime.append(identity)
        scores=([dict(p,scorable=False,correct=None,expected=None,scoreReason='pending_human_after_review')
                 for p in predicted] if pixel_only else score(predicted,b['controls'],a['controls']))
        row.update(status='pixel-only' if pixel_only else 'diagnostic',controls=scores,
                   completeEndpoints=b['complete'] and a.get('complete',False),screen=b['screen'])
        row['summary']=summarize(row['controls'])
    h.require(len(runtime)<=1,'runtime_changed_between_actions')
    for ref in list(audit['inputs'].values())+implementation:
        h.checked(h.ROOT,ref)
    for frame in list(truth.values())+list(pending_frames.values()):h.checked(h.ROOT,frame['image'])
    return dict(version='focus-recorded-transition-eval-v1',**h.FLAGS,inputs=audit['inputs'],
        readinessCounts=audit['counts'],actions=actions,observePendingEnabled=observe_pending,
        observedDecisions=dict(Counter(r['decision'] for a in actions for r in a['controls'])),
        summary=summarize([r for a in actions for r in a['controls']]),
        policies=dict(scoring=POLICY,tracking=visual.POLICY),runtime=runtime,
        implementation=implementation,
        qualifiedTransitionAccuracy=None,unattributedGaps=audit['unattributedGaps'],
        interpretation='Retrospective development diagnostic; geometric correspondence and equal screen labels are proxies, not runtime identity/context proof.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('batch','baseline','pending','output'):p.add_argument('--'+name,required=True)
    p.add_argument('--revision');p.add_argument('--completeness')
    p.add_argument('--observe-pending',action='store_true',help='Unscored pixel diagnostics using accepted before-bounds and verified pending after-images')
    a=p.parse_args()
    try:
        out=h.fresh(a.output);result=run(a.batch,a.baseline,a.pending,a.revision,a.completeness,a.observe_pending)
        h.write(out,result,sealed=True);print(json.dumps(result['summary']));return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print('Transition evaluation blocked: '+str(e));return 2


if __name__=='__main__':raise SystemExit(main())
