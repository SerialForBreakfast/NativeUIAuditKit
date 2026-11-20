"""Evaluate a fixed, stricter HCF observer on retained full-screen proposals."""
from pathlib import Path
from collections import Counter
import math
import research_queue as q
import native343
from experiment_templates import checked
from cached_selection405 import verified_report
from cached_focus_policy import select
from coverage_reports402 import rectangle
from native_selection404 import outcome
OUT = None


def strict_index(scores):
    q.require(all(math.isfinite(s)and 0<=s<=1 for s in scores),'hcf574_invalid_score')
    eligible=[i for i,s in enumerate(scores)if s>=.85]
    if len(eligible)!=1:return None
    i=eligible[0]
    if scores[i]<.95 or any(s>.70 for j,s in enumerate(scores)if j!=i):return None
    return i


def run():
    spec=q.load(OUT.parents[2]/'spec.json');request=q.load(checked(spec['request']))
    q.require(request['version']=='hcf-strict-observer574-v1' and request['minimumScore']==.95 and request['maximumCompetitorScore']==.70,'hcf574_fixed_policy')
    rows=[];models=[]
    for ref in request['reports']:
        report=verified_report(ref)
        q.require(report['version']=='detector-focus-pilot-v1'and report['threshold']==.85,'hcf574_source_kind')
        artifact=q.load(checked(report['inputs']['capture']));capture_path=Path(artifact['path'])
        q.require(capture_path.is_relative_to('/Volumes/training-drive/data/NUIAK/HCF371')and q.digest(capture_path)==artifact['sha256'],'hcf574_capture_changed')
        plan=artifact['plan'];q.require(plan.get('trainingEligible')is False and all(c['role']=='development'for c in plan['cases']),'hcf574_data_role')
        capture=q.load(capture_path);q.require(capture['complete']and capture['cleanup'],'hcf574_capture_incomplete')
        q.require([f['id']for f in capture['frames']]==[r['id']for r in report['rows']],'hcf574_membership')
        for frame,row in zip(capture['frames'],report['rows']):
            if row['profile']!='hcf':continue
            native343.signature(frame['before'],frame['before'],frame['focus']);native343.signature(frame['after'],frame['before'],frame['focus'])
            q.require((frame['sha256'],frame['profile'],frame['case'])==(row['sha256'],row['profile'],row['group']),'hcf574_identity')
            focused=[e for e in frame['before']['scene']['elements']if e['is_focused']];q.require(len(focused)<=1,'hcf574_reference')
            body=rectangle(focused[0]['rendered_body_geometry']['visible_pixel_bounds'])if focused else None
            truth=[body[k]for k in ['x','y','width','height']]if body else None
            baseline=select(row,truth,'abstention-fallback');arm=row['arms']['detector-plus-ring'];scores=arm['models'][baseline['selectedModel']]['scores'];boxes=[c['box']for c in arm['candidates']]
            chosen=strict_index(scores);filtered=[(1. if i==chosen else 0.)for i in range(len(scores))]
            decision=outcome(filtered,boxes,truth)
            q.require(chosen is None or sum(s>=.85 for s in scores)==1,'hcf574_ambiguity_bypass')
            rows.append(dict(id=row['id'],group=row['group'],profile='hcf',noFocus=row['noFocus'],reference=baseline['outcome'],strictOutcome=decision,accepted=chosen is not None,selectedIndex=chosen,selectedScore=scores[chosen]if chosen is not None else None,selectedModel=baseline['selectedModel'],lostCoverage=baseline['outcome']=='correct'and decision!='correct',newWrong=decision in ('wrong','false-selection')and baseline['outcome']not in ('wrong','false-selection')))
        models.append(report['inputs'])
    q.require(rows and len({r['id']for r in rows})==len(rows),'hcf574_duplicate_membership')
    result=dict(version='hcf-strict-observer574-result-v1',minimumScore=.95,maximumCompetitorScore=.70,rows=rows,frames=len(rows),groups=len({r['group']for r in rows}),noFocusFrames=sum(r['noFocus']for r in rows),referenceCounts=dict(Counter(r['reference']for r in rows)),strictCounts=dict(Counter(r['strictOutcome']for r in rows)),accepted=sum(r['accepted']for r in rows),lostCoverage=[r['id']for r in rows if r['lostCoverage']],newWrongSelections=[r['id']for r in rows if r['newWrong']],models=models,metricsStatus='provisional',modelAccepted=False,limitation='Related Fixture development observations. Scores are not calibrated probabilities. No independent real-app accuracy, runtime activation, or model promotion.')
    q.save(OUT/'benchmark_summary.json',result);q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='benchmark_summary.json',sha256=q.digest(OUT/'benchmark_summary.json'))]))
