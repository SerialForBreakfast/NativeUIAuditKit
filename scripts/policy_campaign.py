"""Summarize fixed T60 policies and emit a bounded diagnostic condition."""
import research_queue as q
import cached_focus_policy as policy
from cached_selection405 import verified_report, OUTCOMES
from experiment_templates import checked

OUT = None


def assess(documents, expected, minimum_gain):
    """Use Standard evidence for branch selection. HCF cannot unlock a branch."""
    q.require(type(minimum_gain) is int and minimum_gain >= 0, 'policy_gate_gain')
    rows = []
    for doc in documents:
        q.require(doc.get('version') == 'cached-focus-policy-v1' and
                  doc.get('policy') == 'abstention-fallback' and
                  doc.get('threshold') == .85 and doc.get('modelAccepted') is False,
                  'policy_gate_report')
        rows.extend(doc['rows'])
    actual = [(r['id'], r['group'], r['profile']) for r in rows]
    q.require(actual and len(actual) == len(set(actual)) and sorted(actual) == sorted(expected),
              'policy_gate_membership')
    for row in rows:
        q.require(type(row['noFocus']) is bool and row['profile'] in ('standard', 'hcf') and
                  all(row[k] in OUTCOMES for k in ('reference', 'baseline', 'outcome')),
                  'policy_gate_outcome')
        allowed = {'correct-abstention', 'false-selection'} if row['noFocus'] else {'correct', 'miss', 'wrong'}
        q.require(all(row[k] in allowed for k in ('reference', 'baseline', 'outcome')), 'policy_gate_focus')
        q.require(row['loss'] == (row['reference'] in policy.SUCCESS and row['outcome'] not in policy.SUCCESS) and
                  row['baselineLoss'] == (row['baseline'] in policy.SUCCESS and row['outcome'] not in policy.SUCCESS),
                  'policy_gate_counts')
    standard = [r for r in rows if r['profile'] == 'standard']
    q.require(standard, 'policy_gate_standard_missing')
    wrong = {'wrong', 'false-selection'}
    losses = [r['id'] for r in standard if r['loss'] or r['baselineLoss']]
    new_wrong = [r['id'] for r in standard if r['outcome'] in wrong and
                 (r['baseline'] not in wrong or r['reference'] not in wrong)]
    gains = [r['id'] for r in standard if r['baseline'] not in policy.SUCCESS and r['outcome'] in policy.SUCCESS]
    no_focus = sum(r['noFocus'] for r in standard)
    groups = len({r['group'] for r in standard})
    outcome = ('contradicted' if losses or new_wrong else
               'inconclusive' if no_focus == 0 or groups < 3 or len(gains) < minimum_gain else 'supported')
    return dict(version='policy-campaign-decision-v1', outcome=outcome, rows=rows,
                gains=gains, losses=losses, newWrong=new_wrong, noFocus=no_focus,
                frames=len(standard), groups=groups, modelAccepted=False,
                nextAction=('Run only the approved downstream diagnostics.' if outcome == 'supported' else
                            'Stop this branch. Preserve the cases and review the unmet condition.'),
                limitation='Inspected development evidence. Group identifiers do not prove independence. Prior delivery failures remain open.')


def run():
    spec = q.load(OUT.parents[2]/'spec.json')
    deps = q.dependency_inputs(spec, OUT.parents[4])
    q.require(deps == q.load(OUT/'dependencies.json'), 'policy_gate_dependencies')
    expected = q.load(checked(spec['expectedMembership']))
    docs = []
    models = None
    evidence = []
    for dep in deps:
        for ref in dep['outputs']:
            doc = q.load(checked(ref))
            if doc.get('version') == 'research-condition-v1':
                # The queue verifies this condition before dispatch.
                q.require(doc['outcome'] == 'supported', 'policy_gate_parent_closed')
                continue
            if doc.get('version') == 'policy-campaign-decision-v1':
                docs.append(dict(version='cached-focus-policy-v1', policy='abstention-fallback',
                                 threshold=.85, modelAccepted=False, rows=doc['rows']))
                identity = doc['models']
            elif doc.get('version') == 'cached-focus-policy-v1':
                source = verified_report(dict(report=doc['inputs']['report'], result=doc['inputs']['receipt']))
                identity = {k: source['inputs'][k] for k in ('baseline', 'candidate', 'tool', 'mapping')}
                q.require(sorted(r['id'] for r in source['rows']) == sorted(r['id'] for r in doc['rows']),
                          'policy_gate_source_membership')
                docs.append(doc)
            else:
                raise ValueError('policy_gate_output')
            if models is None:
                models = identity
            q.require(identity == models, 'policy_gate_model_drift')
            evidence.append(ref)
    result = assess(docs, [tuple(r) for r in expected], spec['minimumGain'])
    result['models'] = models
    result['retainedFailures'] = spec['retainedFailures']
    for ref in result['retainedFailures']:
        checked(ref)
    q.save(OUT/'decision.json', result)
    q.save(OUT/'gate.json', dict(version='research-condition-v1', outcome=result['outcome'],
                               reason=result['nextAction'], evidence=evidence))
    q.save(OUT/'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[
        dict(path=name, sha256=q.digest(OUT/name)) for name in ('decision.json', 'gate.json')]))
