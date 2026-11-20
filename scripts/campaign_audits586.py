"""Prepare bounded failure and eligibility reports from existing evidence."""
from collections import Counter
from pathlib import Path
import research_queue as q
from template_inputs398 import checked
from sdk_episode_labels530 import normalize

OUT=None


def receipt(names):
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=n,sha256=q.digest(OUT/n)) for n in names]))


def focus():
    spec=q.load(OUT.parents[2]/'spec.json');sources=spec['focusSources']
    q.require(0<len(sources)<=8,'focus_audit_source_limit')
    frames=[];occurrences=[];rows=[]
    for source in sources:
        request=q.load(checked(source['request']));retained=q.load(checked(source['labels']))
        current=normalize(request)
        q.require(current==retained,'focus_audit_labels_changed')
        q.require(current['trainingEligible'] is False and current['modelAccepted'] is False,'focus_audit_role')
        for f in current['frames']:
            checked(f['image']);checked(f['evidence'])
            q.require(f['role']=='review_only' and f['trainingEligible'] is False,'focus_audit_frame_role')
            frames.append(f)
        occurrences+=current['occurrences']
        rows.append(dict(request=source['request'],labels=source['labels'],frames=len(current['frames']),
            occurrences=len(current['occurrences']),excluded=current['excluded'],emptyFrames=len(current['emptyFrames']),
            profiles=dict(Counter(f['profile'] for f in current['frames'])),requirements=current['requirements']))
    groups=sorted({f['group'] for f in frames});pixels={f['sha256'] for f in frames}
    requirement_rows=[dict(id='observed-profile',owner='Maximum-mini-NUIAK',
        requirement='Native crop sources lack qualified observed profile continuity.',
        resumeWhen='A qualified producer supplies observed profile continuity for eligible native groups.'),
        dict(id='training-groups',owner='Maximum-mini-NUIAK',
        requirement='Current crop roles are review_only. They are not admitted training data.',
        resumeWhen='Prepare independently eligible training groups without changing existing evaluation roles.')]
    result=dict(version='focus-eligibility-audit586-v1',sources=rows,retainedFrames=len(frames),
        sourceOccurrences=len(occurrences),distinctSourcePixels=len(pixels),constructionGroups=groups,
        profileCounts=dict(Counter(f['profile'] for f in frames)),trainingEligible=False,
        observedProfilesQualified=False,missingRequirements=requirement_rows,modelAccepted=False,resultsProvisional=True,
        nextAction='Acquire the missing profile and eligible groups. Reuse valid review evidence without another classifier fit.',
        limitation='Normalized SDK review evidence only. Distinct pixels are not independent scenes. No training role changes or model accuracy claims.')
    q.save(OUT/'benchmark_summary.json',result)
    receipt(['benchmark_summary.json'])


def ios():
    spec=q.load(OUT.parents[2]/'spec.json');deps=q.dependency_inputs(spec,OUT.parents[4])
    q.require(0<len(deps)<=8,'ios_audit_count')
    rows=[];sources=[]
    for dep in deps:
        outputs={Path(r['path']).name:r for r in dep['outputs']}
        report=q.load(checked(outputs['benchmark_summary.json']));cases=q.load(checked(outputs['cases.json']))
        q.require(report['version']=='detector-case-match-v1' and report['slice']=='geometry' and
                  report['matching']=='class-aware' and report['confidence']==.5 and
                  report['modelAccepted'] is False,'ios_audit_report')
        q.require(cases['version']=='detector-case-rows-v1','ios_audit_cases')
        indexed={r['id']:r for r in cases['rows']}
        q.require(len(indexed)==len(cases['rows']) and set(report['lostPriorSuccesses'])<=indexed.keys(),'ios_audit_membership')
        for ident in report['lostPriorSuccesses']:
            r=indexed[ident]
            q.require(r['baseline']['status']=='detected' and r['candidate']['status']!='detected','ios_audit_loss')
            rows.append(dict(condition=dep['job'],id=ident,image=r['image'],className=r['labelClass'],
                geometry=r['slice'],status=r['candidate']['status'],fit=r['candidate']['fit']))
        sources.append(dict(job=dep['job'],report=outputs['benchmark_summary.json'],cases=outputs['cases.json']))
    counts=Counter((r['className'],r['geometry'],r['status']) for r in rows)
    priorities=[dict(className=k[0],geometry=k[1],status=k[2],occurrences=n,
                    distinctCases=len({r['id'] for r in rows if (r['className'],r['geometry'],r['status'])==k}))
                for k,n in sorted(counts.items(),key=lambda item:(-item[1],item[0]))]
    result=dict(version='ios-spatial-loss-audit586-v1',sources=sources,rows=rows,priorities=priorities,
        lossOccurrences=len(rows),distinctCases=len({r['id'] for r in rows}),distinctImages=len({r['image'] for r in rows}),
        confidence=.5,matchingIoU=.5,modelAccepted=False,resultsProvisional=True,trainingRepeated=False,inferenceRepeated=False,
        nextAction='Use frequent class and size failures to define one distinct correction. Preserve matched-control and Run013 retention gates.',
        limitation='Matched-control development losses only. Repeated conditions are not independent cases. Unmatched predictions are not reviewed false positives.')
    q.save(OUT/'benchmark_summary.json',result);receipt(['benchmark_summary.json'])
