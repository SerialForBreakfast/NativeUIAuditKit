"""Separate absent proposals from observed decision regressions using retained evidence."""
from collections import Counter
import research_queue as q
from experiment_templates import checked

OUT = None


def analyze(doc):
    q.require(doc.get('version') == 'model-batch-decision-v1' and doc.get('modelAccepted') is False, 'audit_decision_version')
    rows = doc['rows']
    q.require(isinstance(rows, list) and rows, 'audit_rows')
    keys = [(r['profile'],r['arm'],r['id']) for r in rows]
    q.require(len(keys) == len(set(keys)), 'audit_duplicate_case')
    summaries = []
    cases = []
    for profile, arm in sorted({(r['profile'],r['arm']) for r in rows}, key=lambda k:(k[0]!='standard',k)):
        subset = [r for r in rows if (r['profile'],r['arm']) == (profile,arm)]
        missing = [r for r in subset if not r['noFocus'] and r.get('candidateProposals') == 0]
        failures = [r for r in subset if r['loss'] or r['newWrong']]
        margins = [r for r in failures if r.get('candidateMargin') is not None and r['candidateMargin'] >= 0]
        summaries.append(dict(profile=profile, arm=arm, observations=len(subset), groups=len({r['group'] for r in subset}),
                              absentProposals=len(missing), lostSuccesses=sum(r['loss'] for r in subset),
                              newWrong=sum(r['newWrong'] for r in subset), regressionsWithPositiveMaximumMargin=len(margins),
                              unknownProposalCount=sum('candidateProposals' not in r for r in subset)))
        for r in failures + [r for r in missing if r not in failures]:
            cases.append(dict(r, diagnosis='no_candidate_proposal' if r in missing else
                              'regression_despite_positive_maximum_margin' if r in margins else 'decision_regression'))
    return dict(version='workflow-loss-audit-v1', slices=summaries, cases=cases, modelAccepted=False,
                nextActions=['Test compatible detector proposals where proposal counts are zero.',
                             'Inspect competing scores before changing thresholds for positive-margin regressions.',
                             'Keep retained consumer successes in every subsequent comparison.'],
                limitation='Maximum margin is not the winner-to-runner-up gap. These findings do not establish a causal training correction.')


def run():
    spec=q.load(OUT.parents[2]/'spec.json');queue=OUT.parents[4]
    resolved=q.dependency_inputs(spec,queue)
    q.require(resolved==q.load(OUT/'dependencies.json'),'audit_dependency_changed')
    dep=resolved[0]
    original=spec['dependencies'][0]
    ref=dep['outputs'][original['outputs'].index('decision.json')]
    doc=q.load(checked(ref))
    report=analyze(doc)
    report['source']=ref
    q.save(OUT/'audit.json',report)
    q.save(OUT/'artifact-receipt.json',dict(version='research-artifact-v1',outputs=[dict(path='audit.json',sha256=q.digest(OUT/'audit.json'))]))
