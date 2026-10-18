"""Measure development box errors. Do not use these offsets for training."""
import math
from collections import Counter
import research_queue as q
from cached_selection405 import verified_report
from template_adapters395 import resolve_inputs
from hcf_compare371 import iou
from coverage_reports402 import rectangle
OUT = None

def audit(report):
    q.require(report.get('version')=='detector-focus-pilot-v1','geometry_version')
    rows=report['rows']; results=[]
    q.require(rows and len({r['id'] for r in rows})==len(rows),'geometry_rows')
    for row in rows:
        known=row['arms']['known-box']; detected=row['arms']['detector']
        q.require(row['profile'] in ('standard','hcf'),'geometry_profile')
        for arm in (known,detected):
            for c in arm['candidates']:
                b=c['box']
                q.require(len(b)==4 and all(math.isfinite(v) for v in b) and min(b[2:])>0,'geometry_box')
            for model in ('baseline','candidate'):
                scores=arm['models'][model]['scores']
                q.require(len(scores)==len(arm['candidates']) and all(math.isfinite(s) and 0<=s<=1 for s in scores),'geometry_scores')
        controls=[]
        for index,control in enumerate(known['candidates']):
            body=control['box']; overlaps=[iou(rectangle(c['box']),rectangle(body)) for c in detected['candidates']]
            best=max(range(len(overlaps)),key=overlaps.__getitem__,default=None); match=None
            if best is not None and overlaps[best]>=.5:
                box=detected['candidates'][best]['box']
                match=dict(index=best,overlap=overlaps[best],widthRatio=box[2]/body[2],heightRatio=box[3]/body[3],
                    centerDx=(box[0]+box[2]/2-body[0]-body[2]/2)/body[2],
                    centerDy=(box[1]+box[3]/2-body[1]-body[3]/2)/body[3],
                    scoreDelta={m:detected['models'][m]['scores'][best]-known['models'][m]['scores'][index] for m in ('baseline','candidate')})
            controls.append(dict(index=index,body=body,bestOverlap=max(overlaps,default=0),match=match))
        counts=Counter(c['match']['index'] for c in controls if c['match'])
        results.append(dict(id=row['id'],group=row['group'],profile=row['profile'],noFocus=row['noFocus'],controls=controls,
            ambiguousMatches=[i for i,n in counts.items() if n>1],knownOutcome=known['models']['candidate']['outcome'],
            detectorOutcome=detected['models']['candidate']['outcome']))
    return dict(version='proposal-geometry-audit-v1',rows=results,modelAccepted=False,
        matchedControls=sum(c['match'] is not None for r in results for c in r['controls']),
        missingControls=sum(c['match'] is None for r in results for c in r['controls']),
        limitation='Development diagnosis only. Matches can be ambiguous. Do not train on these offsets.')

def run():
    cfg=q.load(OUT.parents[2]/'spec.json')['template']
    q.require(cfg['parameters']=={},'geometry_parameters')
    refs=resolve_inputs(cfg,OUT)
    result=audit(verified_report(dict(report=refs['report'],result=refs['receipt'])))
    result['inputs']=refs; q.save(OUT/'benchmark_summary.json',result)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
