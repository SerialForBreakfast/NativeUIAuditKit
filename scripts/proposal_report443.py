"""Explain fixed proposal comparisons and preserve previously observed regressions."""
from collections import Counter
import math
import research_queue as q
from experiment_templates import checked

OUT=None
SUCCESS={'correct','correct-abstention'}
WRONG={'wrong','false-selection'}
OUTCOMES=SUCCESS|WRONG|{'miss'}


def analyze(reports,preservation):
    q.require(preservation.get('version')=='model-batch-decision-v1' and preservation.get('modelAccepted') is False,
              'proposal_preservation_version')
    q.require(reports and len(reports)<=32,'proposal_report_count')
    rows=[];seen=set();models=None
    for job,report in reports:
        q.require(report.get('version')=='detector-focus-pilot-v1' and report.get('threshold')==.85 and
                  report.get('modelAccepted') is False,'proposal_report_version')
        q.require(isinstance(report.get('rows'),list) and bool(report['rows']),'proposal_report_empty')
        identity={name:report['inputs'][name] for name in ('baseline','candidate','tool','mapping')}
        if models is None:models=identity
        q.require(identity==models,'proposal_model_drift')
        for row in report['rows']:
            q.require(row['profile'] in ('standard','hcf') and type(row['noFocus']) is bool,'proposal_profile')
            q.require((job,row['id']) not in seen,'proposal_duplicate_case');seen.add((job,row['id']))
            q.require(set(row['arms'])=={'known-box','detector','detector-plus-ring'},'proposal_arms')
            if row['profile']=='standard':
                q.require(row['arms']['detector']['candidates']==row['arms']['detector-plus-ring']['candidates'] and
                          row['arms']['detector']['models']==row['arms']['detector-plus-ring']['models'],'proposal_standard_changed')
            for arm,value in row['arms'].items():
                counts={};gaps={};outcomes={}
                for model in ('baseline','candidate'):
                    result=value['models'][model];scores=result['scores']
                    q.require(len(scores)==len(value['candidates']) and all(type(s) in (int,float) and math.isfinite(s)
                              and 0<=s<=1 for s in scores),'proposal_scores')
                    outcome=result['outcome'];q.require(outcome in OUTCOMES,'proposal_outcome')
                    counts[model]=sum(s>=.85 for s in scores)
                    if row['noFocus']:
                        q.require(outcome==('false-selection' if counts[model]==1 else 'correct-abstention'),'proposal_nofocus_outcome')
                    else:
                        q.require(outcome in {'correct','wrong','miss'} and (outcome=='miss')==(counts[model]!=1),'proposal_focus_outcome')
                    ordered=sorted(scores,reverse=True)
                    gaps[model]=ordered[0]-ordered[1] if len(ordered)>1 else None
                    outcomes[model]=outcome
                old,new=outcomes['baseline'],outcomes['candidate']
                reason=('correct' if new in SUCCESS else 'no-proposals' if not value['candidates'] else
                        'missing-focused-proposal' if value.get('focusedProposalPresent') is False else
                        'competing-above-threshold' if counts['candidate']>1 else
                        'below-threshold' if counts['candidate']==0 else 'wrong-selection')
                rows.append(dict(job=job,id=row['id'],sha256=row['sha256'],group=row['group'],profile=row['profile'],arm=arm,noFocus=row['noFocus'],
                    baseline=old,candidate=new,gain=old not in SUCCESS and new in SUCCESS,loss=old in SUCCESS and new not in SUCCESS,
                    newWrong=old not in WRONG and new in WRONG,proposals=len(value['candidates']),
                    focusedProposalPresent=value.get('focusedProposalPresent'),aboveThreshold=counts,topTwoGap=gaps,diagnosis=reason))
    q.require(rows and models is not None,'proposal_empty')
    q.require(preservation['models']['candidate']==[models['candidate']['sha256']] and
              preservation['models']['baseline']==[models['baseline']['sha256']],'proposal_preservation_model')
    target=[r for r in rows if r['profile']=='standard' and r['arm']=='detector']
    q.require(target,'proposal_standard_support')
    lost=[r for r in rows if r['loss']];wrong=[r for r in rows if r['newWrong']]
    outcome='contradicted' if lost or wrong or preservation['losses'] or preservation['newWrongSelections'] else (
        'supported' if any(r['gain'] for r in target) else 'inconclusive')
    slices=[]
    for profile,arm in sorted({(r['profile'],r['arm']) for r in rows},key=lambda k:(k[0]!='standard',k)):
        subset=[r for r in rows if (r['profile'],r['arm'])==(profile,arm)]
        slices.append(dict(profile=profile,arm=arm,observations=len(subset),groups=len({r['group'] for r in subset}),
            noFocus=sum(r['noFocus'] for r in subset),gains=sum(r['gain'] for r in subset),losses=sum(r['loss'] for r in subset),
            newWrong=sum(r['newWrong'] for r in subset),diagnoses=dict(Counter(r['diagnosis'] for r in subset))))
    return dict(version='proposal-campaign-decision-v1',outcome=outcome,modelAccepted=False,rows=rows,slices=slices,models=models,
                preservation=dict(losses=preservation['losses'],newWrongSelections=preservation['newWrongSelections']),
                limitation='Inspected development evidence. Arms and repeated detector conditions share groups. No model promotion.')


def context():
    spec=q.load(OUT.parents[2]/'spec.json');deps=q.dependency_inputs(spec,OUT.parents[4])
    q.require(deps==q.load(OUT/'dependencies.json'),'proposal_dependencies_changed')
    q.load(checked(spec['proposalPlan']))
    return spec,deps


def receipt():
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[
        dict(path=p.name,sha256=q.digest(p)) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='artifact-receipt.json']))


def run():
    spec,deps=context();reports=[];preservation=[]
    for original,dep in zip(spec['dependencies'],deps):
        for name,ref in zip(original['outputs'],dep['outputs']):
            doc=q.load(checked(ref))
            if name=='decision.json':preservation.append(doc)
            elif name=='benchmark_summary.json':reports.append((dep['job'],doc))
            else:raise ValueError('proposal_output_unknown')
    q.require(len(preservation)==1,'proposal_preservation_count')
    report=analyze(reports,preservation[0]);q.save(OUT/'decision.json',report)
    q.save(OUT/'gate.json',dict(version='research-condition-v1',outcome=report['outcome'],
        reason='Matched Standard proposal comparison with retained success checks.',evidence=[d['result'] for d in deps]))
    lines=['# Fixed detector-to-crop comparison','', 'Outcome: '+report['outcome']+'. Model acceptance: not granted.','',
           '| Profile | Arm | Observations | Groups | Gains | Losses | New wrong |',
           '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for s in report['slices']:lines.append('| '+' | '.join(str(s[k]) for k in ('profile','arm','observations','groups','gains','losses','newWrong'))+' |')
    lines+=['',report['limitation'],'','Retained regressions remain in decision.json even when this subset improves.']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n');receipt()


def followup():
    _,deps=context();q.require(len(deps)==1,'proposal_followup_dependencies')
    report=q.load(checked(deps[0]['outputs'][0]))
    q.require(report['version']=='proposal-campaign-decision-v1','proposal_followup_version')
    cases=[r for r in report['rows'] if r['loss'] or r['newWrong'] or r['diagnosis'] not in ('correct',)]
    action='Qualify independent groups without promotion.' if report['outcome']=='supported' else (
        'Prioritize missing proposals separately from competing scores. Preserve retained consumer failures before another training correction.')
    q.save(OUT/'followup.json',dict(outcome=report['outcome'],action=action,cases=cases,preservation=report['preservation'],
        modelAccepted=False,newTrainingAuthorized=False));receipt()


def contrast_reports(left,right):
    q.require(left.get('version')==right.get('version')=='proposal-campaign-decision-v1','proposal_contrast_version')
    q.require(left['models']==right['models'],'proposal_contrast_models')
    def index(doc):
        keys=[(r['id'],r['profile'],r['arm']) for r in doc['rows']]
        q.require(len(keys)==len(set(keys)),'proposal_contrast_duplicates')
        return dict(zip(keys,doc['rows']))
    a,b=index(left),index(right);q.require(a and a.keys()==b.keys(),'proposal_contrast_membership')
    cases=[]
    for key,old in a.items():
        new=b[key]
        q.require(all(old[k]==new[k] for k in ('sha256','group','noFocus')),'proposal_contrast_identity')
        if old['arm']=='known-box':
            q.require(all(old[k]==new[k] for k in ('baseline','candidate','aboveThreshold','topTwoGap')),'proposal_contrast_known_box')
        cases.append(dict(id=old['id'],profile=old['profile'],arm=old['arm'],group=old['group'],noFocus=old['noFocus'],
            baseline=old['candidate'],candidate=new['candidate'],gain=old['candidate'] not in SUCCESS and new['candidate'] in SUCCESS,
            loss=old['candidate'] in SUCCESS and new['candidate'] not in SUCCESS,
            newWrong=old['candidate'] not in WRONG and new['candidate'] in WRONG,
            focusedProposalRecovered=old['focusedProposalPresent'] is False and new['focusedProposalPresent'] is True,
            focusedProposalLost=old['focusedProposalPresent'] is True and new['focusedProposalPresent'] is False))
    return dict(version='proposal-source-contrast-v1',rows=cases,modelAccepted=False,
                limitation='Only the detector source changes. Repeated arms share groups. Retained crop regressions still prevent replacement.')


def contrast():
    _,deps=context();q.require(len(deps)==2,'proposal_contrast_dependencies')
    result=contrast_reports(*(q.load(checked(d['outputs'][0])) for d in deps))
    q.save(OUT/'contrast.json',result);receipt()
