"""Select finite diagnostic branches from matched evidence. Never dispatch or promote."""
from collections import Counter
import math

import research_queue as q
from experiment_templates import checked
from proposal_report443 import contrast_reports, SUCCESS, WRONG

OUT = None
METRICS = {'focusedFrames', 'noFocusFrames', 'groups', 'cropLosses', 'newWrong',
           'proposalGains', 'proposalLosses', 'missingProposals', 'scoreFailures'}


def rules_valid(rules):
    q.require(isinstance(rules, dict) and set(rules) == {'geometry', 'supplemental'}, 'selection_rules')
    for limits in rules.values():
        q.require(isinstance(limits, dict) and limits, 'selection_limits')
        for metric, bounds in limits.items():
            q.require(metric in METRICS and isinstance(bounds, dict) and bounds and
                      set(bounds) <= {'min', 'max'}, 'selection_metric')
            q.require(all(type(v) is int and v >= 0 for v in bounds.values()), 'selection_bound')
            q.require(bounds.get('min', 0) <= bounds.get('max', math.inf), 'selection_range')


def select(left, right, contrast, rules):
    rules_valid(rules)
    q.require(contrast == contrast_reports(left, right), 'selection_contrast_changed')
    q.require(left['preservation'] == right['preservation'], 'selection_preservation_changed')
    for report in (left, right):
        q.require(report.get('modelAccepted') is False, 'selection_acceptance')
        for row in report['rows']:
            q.require(row['profile'] in ('standard', 'hcf') and type(row['noFocus']) is bool,
                      'selection_profile')
            q.require(row['baseline'] in SUCCESS | WRONG | {'miss'} and
                      row['candidate'] in SUCCESS | WRONG | {'miss'}, 'selection_outcome')
            q.require(row['gain'] == (row['baseline'] not in SUCCESS and row['candidate'] in SUCCESS) and
                      row['loss'] == (row['baseline'] in SUCCESS and row['candidate'] not in SUCCESS) and
                      row['newWrong'] == (row['baseline'] not in WRONG and row['candidate'] in WRONG), 'selection_counts')
    base = [r for r in left['rows'] if r['profile'] == 'standard' and r['arm'] == 'detector']
    other = [r for r in right['rows'] if r['profile'] == 'standard' and r['arm'] == 'detector']
    changes = [r for r in contrast['rows'] if r['profile'] == 'standard' and r['arm'] == 'detector']
    q.require(base and len(base) == len(other) == len(changes), 'selection_standard_support')
    metrics = dict(focusedFrames=sum(not r['noFocus'] for r in base), noFocusFrames=sum(r['noFocus'] for r in base),
        groups=len({r['group'] for r in base}), cropLosses=sum(r['loss'] for r in base),
        newWrong=sum(r['newWrong'] for r in base), proposalGains=sum(r['gain'] for r in changes),
        proposalLosses=sum(r['loss'] for r in changes),
        missingProposals=sum(not r['noFocus'] and r['focusedProposalPresent'] is False for r in base),
        scoreFailures=sum(r['diagnosis'] in ('below-threshold', 'competing-above-threshold') for r in base))
    # Support is a qualification floor, not a claim of statistical confidence.
    sufficient = metrics['focusedFrames'] > 0 and metrics['noFocusFrames'] > 0 and metrics['groups'] >= 3
    branches = {}
    for name, limits in rules.items():
        matches = all(b.get('min', 0) <= metrics[k] <= b.get('max', math.inf) for k, b in limits.items())
        branches[name] = 'inconclusive' if not sufficient else 'supported' if matches else 'contradicted'
    return dict(version='bounded-selection-v1', metrics=metrics, branches=branches, modelAccepted=False,
        preservation=left['preservation'], standardPrimary=True, hcfRequired=False,
        limit='One finite diagnostic generation. No training, capture, retry, promotion, or invented descendants.')


def context():
    spec = q.load(OUT.parents[2] / 'spec.json')
    deps = q.dependency_inputs(spec, OUT.parents[4])
    q.require(deps == q.load(OUT / 'dependencies.json'), 'selection_dependencies_changed')
    plan = q.load(checked(spec['selectionPlan']))
    q.require(plan['version'] == 'bounded-selection-request-v1', 'selection_plan_version')
    return spec, deps, plan


def receipt():
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=p.name, sha256=q.digest(p)) for p in sorted(OUT.iterdir())
        if p.is_file() and p.name != 'artifact-receipt.json']))


def gate():
    _, deps, plan = context()
    q.require(len(deps) == 3, 'selection_dependencies')
    result = select(*(q.load(checked(d['outputs'][0])) for d in deps), plan['rules'])
    q.save(OUT/'selection.json', result)
    for name, outcome in result['branches'].items():
        q.save(OUT/(name+'-gate.json'), dict(version='research-condition-v1', outcome=outcome,
            reason='Frozen Standard evidence selects this diagnostic branch. HCF does not affect selection.',
            evidence=[d['result'] for d in deps]))
    receipt()


def verify_branch():
    """Recheck the typed condition inside an adapter that otherwise reads only static inputs."""
    spec, _, _ = context()
    q.require(len(spec.get('conditions', [])) == 1 and
              spec['conditions'][0]['outcome'] == 'supported', 'selection_branch_condition')


def summarize(documents, branch, selection):
    q.require(branch in ('geometry', 'supplemental') and documents, 'selection_summary_branch')
    seen = set(); rows = []; optional = []
    for job, doc in documents:
        expected = 'proposal-geometry-audit-v1' if branch == 'geometry' else 'supplemental-proposal-comparison-v1'
        q.require(doc.get('version') == expected and doc.get('modelAccepted') is False, 'selection_summary_version')
        q.require(doc['rows'], 'selection_summary_empty')
        for row in doc['rows']:
            q.require(row['profile'] in ('standard', 'hcf'), 'selection_summary_profile')
            key = (job, row['id'], row.get('arm'), row.get('model'))
            q.require(key not in seen, 'selection_summary_duplicate'); seen.add(key)
            value = dict(row, job=job)
            (rows if row['profile'] == 'standard' else optional).append(value)
    q.require(rows, 'selection_summary_standard_missing')
    if branch == 'supplemental':
        slices = {}
        for model in ('baseline', 'candidate'):
            subset = [r for r in rows if r['arm'] == 'detector' and r['model'] == model]
            q.require(subset, 'selection_summary_model_missing')
            counts = dict(gains=sum(r['gain'] for r in subset), losses=sum(r['loss'] for r in subset),
                          newWrong=sum(r['newWrong'] for r in subset),
                          noFocus=sum(r['noFocus'] for r in subset), groups=len({r['group'] for r in subset}))
            counts['outcome'] = ('contradicted' if counts['losses'] or counts['newWrong'] else
                                 'supported' if counts['gains'] and counts['noFocus'] and counts['groups'] >= 3 else 'inconclusive')
            slices[model] = counts
        action = ('Prepare independent verification only for a supported fixed policy. '
                  'Reject policies with new wrong selections. Existing crop regressions still block candidate replacement.')
    else:
        slices = dict(observations=len(rows), groups=len({r['group'] for r in rows}),
            knownCorrectDetectorFailed=sum(r['knownOutcome'] == 'correct' and r['detectorOutcome'] != 'correct' for r in rows),
            ambiguousFrames=sum(bool(r['ambiguousMatches']) for r in rows),
            missingControls=sum(c['match'] is None for r in rows for c in r['controls']))
        action = ('Use case-linked geometry and score differences to scope a training-only producer. '
                  'Do not use inspected development offsets or labels as training examples.')
    return dict(version='bounded-selection-followup-v1', branch=branch, standard=slices, rows=rows,
        optionalHCF=optional, preservation=selection['preservation'], nextAction=action,
        modelAccepted=False, trainingAuthorized=False, captureAuthorized=False, terminal=True)


def finish():
    spec, deps, _ = context()
    branch = spec['selectionBranch']; selection = q.load(checked(deps[0]['outputs'][0]))
    q.require(selection['branches'][branch] == 'supported', 'selection_branch_not_selected')
    result = summarize([(d['job'], q.load(checked(d['outputs'][0]))) for d in deps[1:]], branch, selection)
    q.save(OUT/'decision.json', result)
    (OUT/'report.md').write_text('# Bounded selection: '+branch+'\n\n'+result['nextAction']+
        '\n\nStandard counts: '+str(result['standard'])+'\n\nNo model promotion. This branch ends here.\n')
    receipt()
