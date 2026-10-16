"""BACKLOG410: turn catalog plans into queue jobs and turn completed results back into catalog decisions.

The catalog (Research/Experiments/backlog405.json) is the single definition store.
A record with a `plan` block expands into template descriptions. The queue still owns approval and execution.
`review` reads completed outputs and proposes an outcome. A person or agent confirms it with `confirm`.
"""
import argparse
import json
import re
import statistics
import time
from pathlib import Path

import experiment_backlog as backlog
import research_queue as q

CATALOG = q.ROOT / 'Research/Experiments/backlog405.json'
TASKS = q.ROOT / 'Tasks.md'
BATCHES = q.ROOT / 'Research/Experiments/batches'
RESULTS = q.ROOT / 'Research/Experiments/results'
PLAN_FIELDS = {'template', 'owner', 'question', 'decision', 'outcomes', 'shared', 'control', 'arms', 'jobPrefix', 'rule'}
RULES = {'any-loss', 'gain-without-loss', 'manual'}
BOILERPLATE = re.compile(r'what does this controlled test establish|does the controlled comparison resolve', re.I)
OUTPUT_LIMIT = 2_000_000


def plan_of(record):
    plan = record.get('plan')
    backlog.require(plan is not None, 'plan_missing:' + record['id'])
    return plan


def validate_plan(record):
    """Check one plan against the template contracts. The compiler repeats input checks at expansion."""
    import hcf_templates395 as templates
    plan = plan_of(record)
    backlog.require(set(plan) <= PLAN_FIELDS and PLAN_FIELDS - {'shared'} <= set(plan), 'plan_fields:' + record['id'])
    backlog.require(plan['template'] in templates.CONTRACTS, 'plan_template_unknown:' + str(plan['template']))
    backlog.require(not BOILERPLATE.search(plan['question']) and len(plan['question'].strip()) >= 40, 'plan_question_generic')
    backlog.require(len(plan['decision'].strip()) >= 20, 'plan_decision')
    backlog.require({'supported', 'contradicted', 'inconclusive'} == set(plan['outcomes']), 'plan_outcomes')
    backlog.require(plan['rule'] in RULES, 'plan_rule')
    backlog.require(re.fullmatch(r'[a-z0-9][a-z0-9.-]{2,40}', plan['jobPrefix']), 'plan_job_prefix')
    arms = plan['arms']
    names = [a['id'] for a in arms]
    backlog.require(arms and len(names) == len(set(names)) and len(arms) <= 40, 'plan_arms')
    backlog.require(plan['control'] in names, 'plan_control_missing')
    inputs, parameters = templates.CONTRACTS[plan['template']][:2]
    for arm in arms:
        # JITTER413: an arm may add dependencies and training fields, for example its own crop producer.
        backlog.require(set(arm) <= {'id', 'label', 'parameters', 'inputs', 'job', 'dependencies', 'training', 'capture'},
                        'plan_arm_fields')
        backlog.require(re.fullmatch(r'[a-z0-9][a-z0-9-]{0,40}', arm['id']), 'plan_arm_id')
        if 'job' in arm:
            continue  # An existing completed job serves as this arm. It is not registered again.
        values = {**plan.get('shared', {}).get('parameters', {}), **arm.get('parameters', {})}
        optional = {'T47': {'scorer'}, 'T20': {'taxonomy'}, 'T25': {'kernelSettings'}}.get(plan['template'], set())
        backlog.require(set(values) - optional == parameters, 'plan_arm_parameters:' + arm['id'])
        if plan['template'] == 'T41':
            from box_intervention410 import parameters as check
            check(values)
        if plan['template'] == 'T48':
            from representation_t48 import parameters as check
            check(values)
        if plan['template'] == 'T43':
            from detector_inference412 import parameters as check
            check(values)
        if plan['template'] == 'T44':
            from quota_comparison413 import parameters as check
            check(values)
        if plan['template'] == 'T47':
            from temporal_pairs414 import parameters as check
            check(values)
        if plan['template'] == 'T49':
            from transition_training415 import parameters as check
            check(values)
        if plan['template'] == 'T46':
            from ios_native_capture_t46 import parameters as check
            check(values)
        if plan['template'] == 'T51':
            from swift_fallback416 import parameters as check
            check(values)
    return plan


def job_id(plan, arm):
    return arm.get('job') or plan['jobPrefix'] + '-' + arm['id']


def descriptions(record):
    plan = validate_plan(record)
    shared = plan.get('shared', {})
    docs = []
    for arm in plan['arms']:
        if 'job' in arm:
            continue
        label = arm.get('label', arm['id'])
        docs.append({'version': 'hcf-template-description-v1', 'id': job_id(plan, arm), 'owner': plan['owner'],
                     'template': plan['template'], 'task': record['id'],
                     'question': plan['question'] + ' Arm: ' + label + '.',
                     'hypothesis': record['hypothesis'],
                     'controlledComparison': 'Control arm: ' + plan['control'] + '. ' + record['comparison'],
                     'decision': plan['decision'], 'outcomes': plan['outcomes'],
                     'inputs': {**shared.get('inputs', {}), **arm.get('inputs', {})},
                     'parameters': {**shared.get('parameters', {}), **arm.get('parameters', {})},
                     'dependencies': list(shared.get('dependencies', [])) + list(arm.get('dependencies', []))})
        training = {**shared.get('training', {}), **arm.get('training', {})}
        if training:
            docs[-1]['training'] = training
        # T45: a T03 capture contract. `{"input": "recipe"}` binds the arm's own recipe pin.
        capture = {**shared.get('capture', {}), **arm.get('capture', {})}
        if capture:
            docs[-1]['capture'] = capture
    return docs


def expand(catalog, ident, queue=q.QUEUE, register=False, approve=False, approver='agent:Maximum-mini-NUIAK',
           batches=BATCHES):
    """Write the batch for arms that have no job yet. Optionally register and approve exactly those jobs."""
    import experiment_batch402 as batch_tool
    record = record_of(catalog, ident)
    docs = descriptions(record)
    existing = [d['id'] for d in docs if (queue / 'jobs' / d['id']).exists()]
    new = [d for d in docs if d['id'] not in existing]
    batch = dict(version='experiment-batch-v1', jobs=new)
    result = dict(record=ident, newJobs=[d['id'] for d in new], existingJobs=existing, registered=False,
                  approved=[], executionStarted=False)
    if not new:
        return result
    batches.mkdir(parents=True, exist_ok=True)
    (batches / (ident + '.json')).write_text(json.dumps(batch, indent=2) + '\n')
    result['batch'] = q.relative(batches / (ident + '.json')) if batches.is_relative_to(q.ROOT) else str(batches)
    report = batch_tool.inspect_batch(batch, queue)
    blocked = [r for r in report['jobs'] if r['state'] != 'definition-valid']
    result['blocked'] = blocked
    if register and not blocked:
        ids = [d['id'] for d in new] if approve else []
        batch_tool.register_batch(batch, queue, approved=ids, approver=approver)
        result.update(registered=True, approved=ids)
    return result


def record_of(catalog, ident):
    record = next((r for r in catalog['experiments'] if r['id'] == ident), None)
    backlog.require(record is not None, 'record_unknown:' + ident)
    return record


def task_jobs(queue, ident):
    """Jobs registered for one catalog record, in name order."""
    found = []
    for folder in sorted((queue / 'jobs').iterdir()):
        spec = folder / 'spec.json'
        if spec.is_file() and q.load(spec).get('task') == ident:
            found.append(folder.name)
    return found


def outputs(queue, job):
    """Return the small JSON outputs that the completed attempt lists in its receipt."""
    for attempt in q.attempts_of(queue / 'jobs' / job):
        path = attempt / 'result.json'
        if not path.is_file():
            continue
        result = q.load(path)
        if result.get('status') != 'complete' or not q.outputs_intact(attempt, result):
            continue
        docs = {}
        for item in result['outputs']:
            name = item['path']
            if name.endswith('.json') and name != 'artifact-receipt.json' and item.get('bytes', 0) <= OUTPUT_LIMIT:
                docs[name] = q.load(attempt / 'out' / name)
        return dict(result=q.relative(path), resultSHA256=q.digest(path), wallSeconds=result.get('wallSeconds'),
                    documents=docs)
    return None


def arm_row(queue, arm_id, job):
    state, _ = q.state(queue / 'jobs' / job) if (queue / 'jobs' / job).is_dir() else ('missing', [])
    row = dict(arm=arm_id, job=job, state=state)
    found = outputs(queue, job) if state == 'complete' else None
    if not found:
        return row
    row.update(result=found['result'], resultSHA256=found['resultSHA256'], wallSeconds=found['wallSeconds'])
    # T04-T06 outputs include lists (sources.json, dependencies.json). Only objects carry result fields.
    for doc in (d for d in found['documents'].values() if isinstance(d, dict)):
        for key in ('gains', 'lostPriorSuccesses', 'decisions', 'modelAccepted', 'intervention'):
            if key in doc:
                row[key] = doc[key]
        if isinstance(doc.get('slices'), dict):
            row['outcomes'] = {name: value.get('outcomes') for name, value in doc['slices'].items()
                               if isinstance(value, dict) and 'outcomes' in value}
    return row


def propose(rule, control, rows):
    """Apply the plan's fixed rule. Incomplete arms keep the outcome inconclusive."""
    if rule == 'manual' or any(r['state'] != 'complete' for r in rows):
        return 'inconclusive'
    others = [r for r in rows if r['arm'] != control]
    if rule == 'any-loss':
        return 'supported' if any(r.get('lostPriorSuccesses') for r in others) else 'contradicted'
    # gain-without-loss
    return 'supported' if any(r.get('gains') and not r.get('lostPriorSuccesses') for r in others) else 'contradicted'


def review(catalog, ident, queue=q.QUEUE, results=RESULTS):
    record = record_of(catalog, ident)
    plan = validate_plan(record)
    arms = [(a['id'], job_id(plan, a)) for a in plan['arms']]
    planned = {job for _, job in arms}
    extra = [(job, job) for job in task_jobs(queue, ident) if job not in planned]
    # A failed job that a reviewed reconciliation maps to a completed planned successor is history, not an open arm.
    from research_dashboard_states import successors
    mapping = successors(q.ROOT)
    def replaced(job):
        new = mapping.get(job, (None,))[0]
        return new in planned and (queue / 'jobs' / new).is_dir() and q.state(queue / 'jobs' / new)[0] == 'complete'
    superseded = [dict(job=job, supersededBy=mapping[job][0]) for job, _ in extra if replaced(job)]
    extra = [pair for pair in extra if not replaced(pair[0])]
    rows = [arm_row(queue, arm, job) for arm, job in arms + extra]
    outcome = propose(plan['rule'], plan['control'], rows[:len(arms)])
    value = dict(version='backlog-result-v1', record=ident, question=plan['question'], rule=plan['rule'],
                 control=plan['control'], arms=rows, superseded=superseded, proposedOutcome=outcome,
                 nextAction=plan['outcomes'][outcome], reviewedAt=time.time(),
                 complete=all(r['state'] == 'complete' for r in rows), confirmed=None, modelAccepted=False,
                 limitation='The rule proposes an outcome from recorded gains and losses. Confirmation remains required.')
    results.mkdir(parents=True, exist_ok=True)
    path = results / (ident + '.json')
    if path.is_file():
        value['confirmed'] = json.loads(path.read_text()).get('confirmed')
    path.write_text(json.dumps(value, indent=2) + '\n')
    return value


def confirm(catalog, ident, outcome, by, note, results=RESULTS):
    """Record the confirmed outcome. Supported or contradicted closes the question in the catalog."""
    backlog.require(outcome in ('supported', 'contradicted', 'inconclusive'), 'outcome')
    backlog.require(re.fullmatch(r'maintainer|agent:[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', by), 'confirm_by')
    backlog.require(len(note.strip()) >= 20, 'confirm_note')
    record = record_of(catalog, ident)
    path = results / (ident + '.json')
    value = json.loads(path.read_text())
    backlog.require(value['complete'] or outcome == 'inconclusive', 'review_incomplete')
    value['confirmed'] = dict(outcome=outcome, by=by, note=note.strip(), at=time.time(),
                              nextAction=plan_of(record)['outcomes'][outcome])
    path.write_text(json.dumps(value, indent=2) + '\n')
    relative = q.relative(path) if path.is_relative_to(q.ROOT) else str(path)
    record['result'] = dict(outcome=outcome, path=relative, note=note.strip())
    if outcome != 'inconclusive':
        record['reconciliation'] = dict(disposition='answered', reason=note.strip(), reuse=[relative])
    return value


def estimate(rows):
    """Median measured seconds per task, then per authority. Unknown stays None."""
    done = [r for r in rows if r['state'] == 'complete' and r.get('wallSeconds')]
    by_task, by_authority = {}, {}
    for r in done:
        by_task.setdefault(r['task'], []).append(r['wallSeconds'])
        by_authority.setdefault(r['authority'], []).append(r['wallSeconds'])
    def seconds(row):
        values = by_task.get(row['task']) or by_authority.get(row['authority'])
        return statistics.median(values) if values else None
    return seconds


def status(catalog, rows):
    """Summarize catalog records and queue rows. `rows` are dashboard rows with task, state and displayState."""
    seconds = estimate(rows)
    by_task = {}
    for row in rows:
        by_task.setdefault(row['task'], []).append(row)
    records = []
    for record in catalog['experiments']:
        jobs = [r for r in by_task.get(record['id'], []) if r.get('displayState') != 'superseded']
        ready = [r for r in jobs if r.get('displayState') == 'ready']
        records.append(dict(id=record['id'], title=record['title'], priority=record['priority'],
                            disposition=record['reconciliation']['disposition'], planned='plan' in record,
                            jobs=len(jobs), complete=sum(r['state'] == 'complete' for r in jobs), ready=len(ready),
                            readySeconds=sum(seconds(r) or 0 for r in ready),
                            result=record.get('result', {}).get('outcome')))
    ready_rows = [r for r in rows if r.get('displayState') == 'ready']
    known = [seconds(r) for r in ready_rows]
    # BACKLOG413: the at-a-glance panel needs the next actions, not only counts.
    review = [dict(id=r['id'], title=r['title']) for r in records
              if r['planned'] and r['jobs'] and r['complete'] == r['jobs'] and not r['result']
              and r['disposition'] == 'unresolved']
    try:
        import hcf_templates395 as templates
        top = [dict(kind=g['kind'], template=g['template'], owner=g['owner'], records=len(g['records']),
                    unblocks=g['unblocks'], example=g['examples'][0] if g['examples'] else '',
                    missingTemplate=g['template'] not in templates.CONTRACTS)
               for g in blockers(catalog)[:5]]
    except (ImportError, KeyError, ValueError):
        top = []
    return dict(records=records, readyJobs=len(ready_rows),
                readySeconds=sum(s for s in known if s is not None),
                readyUnknown=sum(s is None for s in known),
                planned=sum(r['planned'] for r in records),
                needsPlan=sum(not r['planned'] and r['disposition'] == 'unresolved' for r in records),
                answered=sum(r['disposition'] == 'answered' for r in records),
                open=sum(r['disposition'] == 'unresolved' for r in records),
                awaitingApproval=sum(r.get('displayState') == 'awaiting-approval' for r in rows),
                blockedJobs=sum(r.get('displayState') in ('blocked', 'exhausted') for r in rows),
                reviewPending=review, topBlockers=top,
                refill=len(ready_rows) < 10)


def blockers(catalog):
    """Rank what blocks open records without a plan: missing templates first, then requirement kind and owner.

    `unblocks` counts the record and every open record that depends on it, directly or not.
    """
    import hcf_templates395 as templates
    open_rows = {r['id']: r for r in catalog['experiments'] if r['reconciliation']['disposition'] == 'unresolved'}
    children = {}
    for r in open_rows.values():
        for parent in r['dependencies']:
            children.setdefault(parent, set()).add(r['id'])
    def reach(ident, seen):
        for child in children.get(ident, ()):
            if child not in seen:
                seen.add(child); reach(child, seen)
        return seen
    groups = {}
    for r in open_rows.values():
        if 'plan' in r:
            continue
        template = r['template']['id']
        first = r['requirements'][0]
        if template not in templates.CONTRACTS:
            key = ('adapter', template, 'Maximum-mini-NUIAK')
        else:
            key = (first['kind'], template, first['owner'])
        group = groups.setdefault(key, dict(kind=key[0], template=key[1], owner=key[2], records=[], unblocks=set(),
                                            examples=[]))
        group['records'].append(r['id'])
        group['unblocks'] |= reach(r['id'], {r['id']})
        if len(group['examples']) < 3:
            group['examples'].append(first['missing'][:160])
    ranked = sorted(groups.values(), key=lambda g: (-len(g['unblocks']), g['template']))
    return [dict(g, records=sorted(g['records']), unblocks=len(g['unblocks'])) for g in ranked]


ADD_REQUIRED = {'title', 'parentTask', 'track', 'priority', 'question', 'comparison', 'baseline', 'sourceEvidence',
                'template', 'outcomes'}
ADD_OPTIONAL = {'hypothesis', 'changedVariable', 'requiredInputs', 'dependencies', 'requirements', 'plan', 'profile',
                'variant', 'owner'}
KIND_STATE = {'adapter': 'Needs adapter', 'data': 'Needs data', 'decision': 'Needs decision',
              'conditional': 'Conditional', 'review': 'Awaiting review'}


def add(catalog, short):
    """Turn a short description into a full catalog record with the next free ID. Return the new record.

    The writer supplies the science: question, comparison, baseline, outcomes, and either a plan or blockers.
    Profile, cost, and acceptance defaults come from the catalog profile and the plan.
    """
    backlog.require(isinstance(short, dict) and ADD_REQUIRED <= set(short) <= ADD_REQUIRED | ADD_OPTIONAL,
                    'add_fields:' + ','.join(sorted(set(short) ^ (ADD_REQUIRED | (set(short) & ADD_OPTIONAL)))))
    backlog.require(not BOILERPLATE.search(short['question']), 'add_question_generic')
    outcomes = dict(short['outcomes'])
    outcomes.setdefault('inconclusive', 'Complete every arm and record missing evidence before a decision.')
    profile_name = short.get('profile', 'diagnostic')
    profile = catalog['profiles'][profile_name]
    owner = short.get('owner', 'Maximum-mini-NUIAK')
    numbers = [int(r['id'].split('-')[1]) for r in catalog['experiments']]
    ident = 'B405-%03d' % (max(numbers) + 1)
    plan = short.get('plan')
    requirements = short.get('requirements') or ([dict(owner=owner, kind='review', missing='Execution and review of the planned arms.',
                                                       unblock='Run backlog_pipeline review, then confirm the outcome.')] if plan else None)
    backlog.require(requirements, 'add_requirements_or_plan')
    record = dict(id=ident, planItem=None, parentTask=short['parentTask'], track=short['track'], title=short['title'],
                  profile=profile_name, priority=short['priority'], question=short['question'],
                  hypothesis=short.get('hypothesis', short['question']), comparison=short['comparison'],
                  changedVariable=short.get('changedVariable', short['comparison']),
                  requiredInputs=short.get('requiredInputs', 'See plan inputs.' if plan else requirements[0]['missing']),
                  sourceEvidence=short['sourceEvidence'],
                  template=dict(id=short['template'], variant=short.get('variant', short['title']),
                                qualification='Check the exact variant; a callable contract alone does not qualify these inputs.'),
                  dependencies=short.get('dependencies', []),
                  acceptance=dict(rule=plan['decision'] if plan else outcomes['supported'],
                                  numericLimits='Inherit exact parent gates. Freeze any new numeric limit before registration.'),
                  outcomes=outcomes, requirements=requirements,
                  reconciliation=dict(disposition='unresolved', reason='Added by backlog_pipeline add.'),
                  existingJobs=[], baseline=short['baseline'],
                  cost=dict(preparationMinutes=profile['preparationMinutes'], reviewMinutes=profile['reviewMinutes'],
                            executionSecondsEstimate=None, executionCeiling=profile['budget'],
                            estimateBasis='Profile defaults. Use measured medians from the queue after the first arm.'))
    if plan:
        record['plan'] = plan
    catalog['experiments'].append(record)
    backlog.validate(catalog)
    if plan:
        validate_plan(record)
    return record


TABLE_BEGIN = '<!-- BACKLOG:BEGIN generated by scripts/backlog_pipeline.py render-tasks -->'
TABLE_END = '<!-- BACKLOG:END -->'


def computed_state(record, queue):
    """State for a planned record. Records without a plan keep their Tasks.md state."""
    plan = plan_of(record)
    jobs = [job_id(plan, a) for a in plan['arms']]
    states = [q.state(queue / 'jobs' / j)[0] if (queue / 'jobs' / j).is_dir() else 'missing' for j in jobs]
    done = sum(s == 'complete' for s in states)
    if done == len(states):
        state = 'Awaiting review' if not record.get('result') else 'Needs decision'
    elif all(s == 'missing' for s in states):
        state = 'Ready to register'
    else:
        state = 'Existing execution'
    return state, f'{done}/{len(states)}'


def render_tasks(catalog, text, queue=q.QUEUE):
    """Rewrite the generated table. Unplanned rows keep their recorded owner and state."""
    previous = backlog.task_states(text)
    lines = ['| ID | Owner | Status | Priority | Scientific question | Jobs | Result |',
             '| --- | --- | --- | --- | --- | --- | --- |']
    for record in catalog['experiments']:
        if record['reconciliation']['disposition'] != 'unresolved':
            continue
        old = previous.get(record['id'], {})
        owner = old.get('owner') or record['requirements'][0]['owner']
        if 'plan' in record:
            state, jobs = computed_state(record, queue)
        else:
            first = record['requirements'][0].get('kind')
            state, jobs = old.get('state', KIND_STATE.get(first, 'Needs data')), '–'
        result = record.get('result', {}).get('outcome', '–')
        lines.append(f"| {record['id']} | {owner} | {state} | P{record['priority']} | {record['title']} | {jobs} | {result} |")
    block = TABLE_BEGIN + '\n' + '\n'.join(lines) + '\n' + TABLE_END
    if TABLE_BEGIN in text:
        head, rest = text.split(TABLE_BEGIN, 1)
        _, tail = rest.split(TABLE_END, 1)
        return head + block + tail
    # First run: replace the hand-kept BACKLOG405 table in place.
    pattern = re.compile(r'\| ID \| Owner \| Status \| Priority \| Scientific question \|\n\| --- [^\n]*\n(?:\| B405-\d{3} \|[^\n]*\n)+')
    backlog.require(pattern.search(text), 'tasks_table_missing')
    return pattern.sub(lambda _: block + '\n', text, count=1)


def save_catalog(catalog, path=CATALOG):
    path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('check', 'expand', 'review', 'confirm', 'render-tasks', 'status', 'blockers', 'add'):
        command = sub.add_parser(name)
        if name in ('expand', 'review', 'confirm'):
            command.add_argument('records', nargs='+')
    sub.choices['expand'].add_argument('--register', action='store_true')
    sub.choices['expand'].add_argument('--approve-listed', action='store_true')
    sub.choices['expand'].add_argument('--approver', default='agent:Maximum-mini-NUIAK')
    sub.choices['add'].add_argument('file', help='JSON list of short record descriptions')
    sub.choices['confirm'].add_argument('--outcome', required=True)
    sub.choices['confirm'].add_argument('--by', required=True)
    sub.choices['confirm'].add_argument('--note', required=True)
    args = parser.parse_args()
    catalog = json.loads(CATALOG.read_text())
    backlog.validate(catalog)
    if args.command == 'check':
        planned = [r for r in catalog['experiments'] if 'plan' in r]
        for record in planned:
            validate_plan(record)
        print(json.dumps(dict(planned=len(planned)), indent=2))
    elif args.command == 'expand':
        print(json.dumps([expand(catalog, ident, register=args.register, approve=args.approve_listed,
                                 approver=args.approver) for ident in args.records], indent=2))
    elif args.command == 'review':
        print(json.dumps([{k: v for k, v in review(catalog, ident).items() if k != 'arms'} for ident in args.records],
                         indent=2))
    elif args.command == 'confirm':
        for ident in args.records:
            confirm(catalog, ident, args.outcome, args.by, args.note)
        backlog.validate(catalog)
        save_catalog(catalog)
        print(json.dumps(dict(confirmed=args.records, outcome=args.outcome), indent=2))
    elif args.command == 'render-tasks':
        TASKS.write_text(render_tasks(catalog, TASKS.read_text()))
        print('Tasks.md backlog table updated.')
    elif args.command == 'add':
        added = [add(catalog, short) for short in json.loads(Path(args.file).read_text())]
        save_catalog(catalog)
        print(json.dumps([dict(id=r['id'], title=r['title'], planned='plan' in r) for r in added], indent=2))
    elif args.command == 'blockers':
        print(json.dumps(blockers(catalog), indent=2))
    elif args.command == 'status':
        from generate_research_dashboard import build_dashboard_data
        value = status(catalog, build_dashboard_data()['jobs'])
        print(json.dumps({k: v for k, v in value.items() if k != 'records'}, indent=2))

if __name__ == '__main__':
    main()
