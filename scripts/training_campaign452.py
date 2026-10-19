"""Author bounded crop training graphs with resident preparation and scoring adapters.

Compilation does not register, approve, train, or promote a model.
"""
import argparse
import copy
import json
from pathlib import Path

import research_queue as q
import hcf_templates395 as templates
import experiment_batch402 as batches
import model_decision_batch434 as decisions
import workflow_campaign439 as campaigns
from experiment_templates import checked, pin


def frozen_membership(reference, excluded):
    document = q.load(checked(reference))
    rows = document.get('rows', [])
    q.require(rows and len({r['id'] for r in rows}) == len(rows), 'training_graph_duplicate_membership')
    groups = {}
    for row in rows:
        q.require(row.get('role') in ('train', 'development') and row.get('profile') in ('standard', 'hcf') and
                  isinstance(row.get('id'), str) and row['id'] and
                  type(row.get('label')) is int and row['label'] in (0, 1) and
                  isinstance(row.get('group'), str) and row['group'], 'training_graph_membership_fields')
        q.require(groups.setdefault(row['group'], row['role']) == row['role'], 'training_graph_group_leak')
    q.require({r['role'] for r in rows} == {'train', 'development'}, 'training_graph_roles')
    train = [r for r in rows if r['role'] == 'train']
    q.require({r['label'] for r in train} == {0, 1} and any(r['profile'] == 'standard' for r in train),
              'training_graph_standard_support')
    q.require(not {r['group'] for r in train} & set(excluded), 'training_graph_evaluation_leak')
    q.require({r['group'] for r in rows if r['role'] == 'development'} <= set(excluded),
              'training_graph_missing_exclusions')
    return rows


def compile_request(source, destination, queue=q.QUEUE):
    request = q.load(source)
    required = {'version', 'id', 'question', 'controlledComparison', 'training', 'suite', 'budget', 'followups'}
    q.require(required <= set(request) <= required | {'reuseScores'}, 'training_graph_fields')
    q.require(request['version'] == 'training-campaign-v1' and q.ID.fullmatch(request['id']), 'training_graph_version')
    if (destination/'compiled.json').exists():
        q.require(q.load(destination/'request.json') == request, 'training_graph_immutable_request')
        manifest = q.load(destination/'compiled.json')
        checked(manifest['plan'])
        checked(request['suite'])
        for row in manifest['jobs']:
            spec = q.load(checked(row['spec']))
            q.require(q.text_digest(spec) == row['specSHA256'], 'training_graph_spec_changed')
            q.verify_pins(spec)
            current = queue/'jobs'/row['job']/'spec.json'
            q.require(not current.exists() or q.load(current) == spec, 'training_graph_registration_conflict')
        for row in manifest['existing']:
            q.require(q.text_digest(q.load(queue/'jobs'/row['job']/'spec.json')) == row['specSHA256'],
                      'training_graph_existing_changed')
        return manifest
    for key in ('question', 'controlledComparison'):
        q.require(isinstance(request[key], str) and 12 <= len(request[key]) <= 1000, 'training_graph_text')
    suite = q.load(checked(request['suite']))
    q.require(set(suite) == {'version', 'baselines', 'excludedGroups'} and suite['version'] == 'training-suite-v1',
              'training_graph_suite')
    excluded = suite['excludedGroups']
    q.require(isinstance(excluded, list) and excluded and all(isinstance(g, str) and g for g in excluded) and
              len(set(excluded)) == len(excluded), 'training_graph_exclusions')
    refs = suite['baselines']
    q.require(isinstance(refs, list) and 1 <= len(refs) <= 32 and
              len({r['job'] for r in refs}) == len(refs), 'training_graph_suite_duplicates')
    baseline = []
    for ref in refs:
        q.require(set(ref) == {'job', 'specSHA256'} and q.ID.fullmatch(ref['job']), 'training_graph_baseline')
        spec = q.load(queue/'jobs'/ref['job']/'spec.json')
        q.require(q.text_digest(spec) == ref['specSHA256'], 'training_graph_baseline_changed')
        q.require(spec.get('template', {}).get('id') in ('T37', 'T63'), 'training_graph_score_template')
        baseline.append(spec)
    q.require(any(s['template']['id'] == 'T37' for s in baseline), 'training_graph_native_suite')
    train = request['training']
    authored = []
    if set(train) == {'reuse'}:
        q.require(q.ID.fullmatch(train['reuse']), 'training_graph_training_id')
        training = q.load(queue/'jobs'/train['reuse']/'spec.json')
    else:
        q.require(set(train) == {'id', 'preparation', 'configuration', 'initialization', 'membership', 'experimentLogRunId'},
                  'training_graph_training_fields')
        prep = train['preparation']
        if isinstance(prep, str):
            q.require(q.ID.fullmatch(prep), 'training_graph_preparation_id')
            preparation = q.load(queue/'jobs'/prep/'spec.json')
        else:
            q.require(isinstance(prep, dict) and prep.get('template') == 'T05', 'training_graph_preparation_template')
            preparation = templates.build(batches.compile_batch(dict(version='experiment-batch-v1', jobs=[prep]), queue)[0])
            authored.append(prep)
        common = dict(version='hcf-template-description-v1', owner='Maximum-mini-NUIAK', parameters={},
                      question=request['question'], decision='Preserve all retained successes and Standard behavior. No automatic promotion.')
        desc = dict(common, id=train['id'], template='T06',
                    inputs={k: train[k] for k in ('configuration', 'initialization', 'membership')},
                    dependencies=[dict(job=preparation['id'], specSHA256=q.text_digest(preparation), outputs=['crops.json'])],
                    training=dict(initialization=train['initialization'], membership=[train['membership']], epochs=30,
                                  resume='restart', storageBudgetBytes=2 << 30, experimentLogRunId=train['experimentLogRunId'],
                                  acceptanceEvidence='Require complete matched Standard and retained-success comparisons.'))
        training = templates.build(desc)
        authored.append(desc)
    q.require(training.get('template', {}).get('id') == 'T06' and training['authority'] == 'training' and
              training['training']['epochs'] == 30 and training['training']['resume'] == 'restart', 'training_graph_trainer')
    inputs = training['template']['inputs']
    frozen_membership(inputs['membership'], excluded)
    config = q.load(checked(inputs['configuration']))
    from hcf_factor_train376 import validate_config
    validate_config(config)
    q.require(config['profile'] == 'balanced' and config['initialization'] == inputs['initialization'],
              'training_graph_profile_or_initialization')
    # The frozen rows, not an implicit trainer profile filter, select training membership.
    checked(inputs['initialization'])
    q.require(any(d['outputs'] == ['crops.json'] for d in training['dependencies']), 'training_graph_preparation_missing')
    reuse = request.get('reuseScores', {})
    q.require(isinstance(reuse, dict) and (not reuse or set(reuse) == {s['id'] for s in baseline}),
              'training_graph_reuse_suite')
    pairs = []
    for index, old in enumerate(baseline, 1):
        values = copy.deepcopy(old['template']['inputs'])
        values['model'] = dict(job=training['id'], output='final.pt')
        ident = f"{request['id']}-score-{index:02}"
        # Input references retain their producer bindings. Unrelated historical gates are not copied.
        parents = {r['job'] for k, r in values.items() if k != 'model' and 'job' in r}
        desc = dict(version='hcf-template-description-v1', id=ident, owner='Maximum-mini-NUIAK',
                    template=old['template']['id'], inputs=values, parameters=old['template']['parameters'],
                    dependencies=[d for d in old.get('dependencies', []) if d['job'] in parents],
                    question=request['question'], decision='Compare identical inputs and preserve every retained success.')
        if reuse:
            ident = reuse[old['id']]
            q.require(isinstance(ident, str) and q.ID.fullmatch(ident), 'training_graph_reuse_id')
        else:
            authored.append(desc)
        pairs.append(dict(id=f'condition-{index:02}', baseline=old['id'], candidate=ident))
    followups = request['followups']
    q.require(isinstance(followups, list) and len(followups) <= 8, 'training_graph_followups')
    for branch in followups:
        q.require(set(branch) == {'when', 'jobs'} and branch['when'] in ('supported', 'contradicted'),
                  'training_graph_branch')
        for desc in branch['jobs']:
            q.require(desc.get('kind') == 'decision-audit' or desc.get('template') in ('T37', 'T63'),
                      'training_graph_followup_scope')
    budget = request['budget']
    q.require(set(budget) == {'maxJobs', 'maxSeconds', 'maxOutputBytes'} and
              all(type(v) is int and v > 0 for v in budget.values()), 'training_graph_budget')
    destination.mkdir(parents=True, exist_ok=True)
    decisions.retain(destination/'request.json', request)
    if authored:
        decisions.retain(destination/'execution.json', dict(version='experiment-batch-v1', jobs=authored))
    plan = dict(version='model-decision-batch-v1', id=request['id'], question=request['question'],
                controlledComparison=request['controlledComparison'], executionBatch=pin(destination/'execution.json') if authored else None,
                training=training['id'], pairs=pairs)
    if followups:
        wrapper = dict(version='workflow-campaign-v1', id=request['id'], decision=dict(plan=plan), branches=followups)
        decisions.retain(destination/'branches.json', wrapper)
        manifest = campaigns.compile_request(destination/'branches.json', destination/'compiled', queue)
    else:
        decisions.retain(destination/'decision-plan.json', plan)
        manifest = decisions.compile_plan(destination/'decision-plan.json', destination/'compiled', queue)
    specs = [q.load(checked(r['spec'])) for r in manifest['jobs']]
    # Charge all new nodes, including unselected branches. Each has one attempt.
    # Reused training is also charged, so this description cannot hide its training cost.
    charged = {s['id']: s for s in specs}
    charged.setdefault(training['id'], training)
    q.require(all(s['limits']['maxAttempts'] == 1 for s in charged.values()), 'training_graph_retry_budget')
    totals = dict(maxJobs=len(charged), maxSeconds=sum(s['limits']['timeoutSeconds'] for s in charged.values()),
                  maxOutputBytes=sum(s['limits']['maxOutputBytes'] for s in charged.values()))
    q.require(all(totals[k] <= budget[k] for k in totals), 'training_graph_budget_exceeded')
    # Pin the short request and suite in every new executable node before admission.
    # Changing a dependency hash requires rebuilding descendants in topological order.
    updated = {}
    (destination/'sealed').mkdir(exist_ok=True)
    for row, spec in zip(manifest['jobs'], specs):
        spec['inputs'] += [pin(destination/'request.json'), request['suite']]
        for dep in spec['dependencies']:
            if dep['job'] in updated:
                dep['specSHA256'] = q.text_digest(updated[dep['job']])
        q.validate(spec)
        updated[spec['id']] = spec
        path = destination/'sealed'/(spec['id']+'.json')
        decisions.retain(path, spec)
        row.update(spec=pin(path), specSHA256=q.text_digest(spec))
    manifest['plan'] = pin(destination/'request.json')
    decisions.retain(destination/'compiled.json', manifest)
    decisions.retain(destination/'budget.json', dict(limits=budget, reserved=totals, attemptsPerNewJob=1,
        historicalTrainingCharged=training['id'] not in updated, executionStarted=False,
        limitation='Reservation ceilings are not ETA. Reused baseline inference is not repeated.'))
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--register', action='store_true')
    parser.add_argument('--approve', action='append', default=[])
    args = parser.parse_args()
    q.require(not args.approve or args.register, 'training_graph_register_required')
    source = q.local_path(q.ROOT, q.relative(args.request.resolve()))
    destination = q.local_path(q.ROOT, q.relative(args.output.resolve()))
    manifest = compile_request(source, destination)
    print(json.dumps(campaigns.admit(manifest, approved=args.approve) if args.register else
                     dict(jobs=len(manifest['jobs']), executionStarted=False)))
