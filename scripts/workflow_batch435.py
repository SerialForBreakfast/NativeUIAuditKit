"""Author matched descriptions and inspect graphs without controlling execution."""
import argparse
import collections
import json
import time
from pathlib import Path

import research_queue as q
import research_approval as approval
import model_decision_batch434 as compiler
from experiment_templates import checked


def job_spec(queue, ident):
    q.require(isinstance(ident, str) and q.ID.fullmatch(ident), 'workflow_job_id')
    spec = q.load(queue / 'jobs' / ident / 'spec.json')
    q.require(spec['id'] == ident, 'workflow_job_identity')
    return spec


def scoring_key(spec, queue):
    """Match exact non-model inputs, not names or list positions."""
    template = spec['template']
    q.require(template['id'] in ('T37', 'T63'), 'workflow_score_template')
    inputs = {}
    for name, ref in template['inputs'].items():
        if name == 'model':
            continue
        if 'path' in ref:
            checked(ref)
            inputs[name] = ref
        else:
            q.require(set(ref) == {'job', 'output'}, 'workflow_input_reference')
            deps = [d for d in spec.get('dependencies', []) if d['job'] == ref['job']]
            q.require(len(deps) == 1 and ref['output'] in deps[0]['outputs'], 'workflow_input_dependency')
            resolved = q.dependency_inputs(dict(dependencies=deps), queue)[0]
            inputs[name] = resolved['outputs'][deps[0]['outputs'].index(ref['output'])]
    return q.text_digest(dict(template=template['id'], parameters=template['parameters'], inputs=inputs))


def author(request, queue=q.QUEUE):
    q.require(set(request) == {'version', 'id', 'question', 'controlledComparison', 'training', 'baseline', 'candidate'},
              'workflow_request_fields')
    q.require(request['version'] == 'model-decision-request-v1', 'workflow_request_version')
    q.require(q.ID.fullmatch(request['id']) is not None, 'workflow_batch_id')
    q.require(all(isinstance(request[k], str) and len(request[k].strip()) >= 12
                  for k in ('question', 'controlledComparison')), 'workflow_question')
    train = job_spec(queue, request['training'])
    q.require(train['template']['id'] == 'T06' and train['training']['epochs'] == 30, 'workflow_training_contract')
    indexed = {}
    for side in ('baseline', 'candidate'):
        ids = request[side]
        q.require(isinstance(ids, list) and 1 <= len(ids) <= 32 and len(set(ids)) == len(ids), 'workflow_score_ids')
        indexed[side] = {}
        for ident in ids:
            spec = job_spec(queue, ident)
            if side == 'candidate':
                q.require(spec['template']['inputs']['model'] == dict(job=train['id'], output='final.pt'), 'workflow_candidate_model')
                q.require(any(d['job'] == train['id'] and d['specSHA256'] == q.text_digest(train)
                              and 'final.pt' in d['outputs'] for d in spec['dependencies']), 'workflow_training_dependency')
            key = scoring_key(spec, queue)
            q.require(key not in indexed[side], 'workflow_ambiguous_pair:' + side)
            indexed[side][key] = ident
    q.require(set(indexed['baseline']) == set(indexed['candidate']), 'workflow_unmatched_suite')
    return dict(version='model-decision-batch-v1', id=request['id'], question=request['question'],
                controlledComparison=request['controlledComparison'], executionBatch=None, training=train['id'],
                pairs=[dict(id=f'condition-{n:02}', baseline=indexed['baseline'][key], candidate=indexed['candidate'][key])
                       for n, key in enumerate(sorted(indexed['baseline']), 1)])


def inspect(manifest, queue=q.QUEUE):
    """Read a bounded graph. This snapshot grants no execution authority."""
    q.require(manifest['version'] == 'model-decision-compiled-v1', 'workflow_manifest_version')
    checked(manifest['plan'])
    expected = {r['job']: r['specSHA256'] for r in manifest['existing'] + manifest['jobs']}
    roots = {r['job'] for r in manifest['jobs']}
    approvals = approval.load(queue)
    rows = {}
    visiting = set()

    def visit(ident, digest):
        q.require(ident not in visiting, 'workflow_dependency_cycle:' + ident)
        if ident in rows:
            q.require(rows[ident]['expectedSHA256'] == digest, 'workflow_conflicting_dependency')
            return
        q.require(len(rows) + len(visiting) < 256, 'workflow_graph_limit')
        visiting.add(ident)
        row = dict(job=ident, expectedSHA256=digest, generated=ident in roots, blockers=[], dependencies=[],
                   owner='unknown', execution='unavailable', dispatch='blocked', modelAccepted=False)
        try:
            spec = job_spec(queue, ident)
            row['owner'] = spec.get('owner', 'unknown')
            q.require(q.text_digest(spec) == digest, 'workflow_spec_changed:' + ident)
            state, attempts = q.state(queue / 'jobs' / ident, display_cache=True)
            row['execution'] = state
            row['attemptCount'] = len(attempts)
            row['approved'] = approval.is_approved(queue, spec, approvals, display_cache=True)
            row['budgetSeconds'] = spec.get('limits', {}).get('timeoutSeconds')
            if state == 'complete':
                row['dispatch'] = 'finished'
                for attempt in attempts:
                    result_path = attempt / 'result.json'
                    if not result_path.is_file():
                        continue
                    result = q.load(result_path)
                    if result.get('status') != 'complete' or not q.outputs_intact(attempt, result, display_cache=True):
                        continue
                    row['executionSeconds'] = result.get('wallSeconds')
                    names = {item['path'] for item in result['outputs']}
                    if 'decision.json' in names:
                        decision = q.load(attempt / 'out/decision.json')
                        q.require(decision['version'] == 'model-batch-decision-v1' and decision['modelAccepted'] is False,
                                  'workflow_decision_contract')
                        row['decision'] = dict(outcome=decision['outcome'], slices=decision['slices'],
                                               report=q.relative(attempt / 'out/decision.json'))
                    if 'followup.json' in names:
                        followup = q.load(attempt / 'out/followup.json')
                        q.require(followup['version'] == 'model-batch-followup-v1' and
                                  followup['newTrainingAuthorized'] is False, 'workflow_followup_contract')
                        row['followup'] = followup['action']
                    break
            elif state == 'running':
                row['dispatch'] = 'running'
            elif state == 'pending' and row['approved']:
                row['dispatch'] = 'eligible-pending-runner-checks'
            if state in ('failed', 'exhausted', 'interrupted', 'invalid', 'cancelled'):
                row['blockers'].append('Attempt requires explicit review; no automatic retry.')
                if attempts and (attempts[-1] / 'result.json').is_file():
                    result = q.load(attempts[-1] / 'result.json')
                    row['failure'] = {k: result[k] for k in ('status', 'reason', 'error') if k in result}
            if state not in ('complete', 'running') and not row['approved']:
                row['blockers'].append('Exact approval is missing or its source checks changed.')
            if spec.get('requirements'):
                row['blockers'].append('Declared requirements remain: ' + json.dumps(spec['requirements'])[:1000])
            try:
                q.dependency_inputs(spec, queue, display_cache=True)
            except (ValueError, OSError, KeyError, TypeError) as error:
                row['blockers'].append(str(error)[:1000])
                if state not in ('complete', 'running'):
                    row['dispatch'] = 'blocked'
            for dep in spec.get('dependencies', []):
                row['dependencies'].append(dep['job'])
                visit(dep['job'], dep['specSHA256'])
            if (row['dispatch'] == 'blocked' and row['blockers'] and
                    all(reason.startswith('condition_not_met:') and reason.split(':')[2] in ('supported','contradicted')
                        for reason in row['blockers'])):
                row['dispatch'] = 'branch-not-selected'
            if (row['dispatch'] == 'blocked' and row['blockers'] and
                    all(reason.startswith('dependency_incomplete:') for reason in row['blockers']) and
                    all(rows[dep]['dispatch'] in ('finished', 'running', 'eligible-pending-runner-checks', 'waiting')
                        for dep in row['dependencies'])):
                row['dispatch'] = 'waiting'
        except (ValueError, OSError, KeyError, TypeError) as error:
            row['blockers'].append(str(error)[:1000])
            row['dispatch'] = 'blocked'
        finally:
            visiting.remove(ident)
        rows[ident] = row

    for ident, digest in expected.items():
        visit(ident, digest)
    for row in rows.values():
        affected = set()
        frontier = [row['job']]
        while frontier:
            parent = frontier.pop()
            for other in rows.values():
                if parent in other['dependencies'] and other['job'] not in affected:
                    affected.add(other['job'])
                    frontier.append(other['job'])
        row['affectedGeneratedJobs'] = len(affected & roots)
    generated = [r for r in rows.values() if r['generated']]
    return dict(version='model-decision-status-v1', observedAt=time.time(), executionChanged=False,
                modelAccepted=False, counts=dict(collections.Counter(r['dispatch'] for r in generated)),
                eta='ETA unavailable', etaReason='No qualified comparable duration model is configured.',
                rows=sorted(rows.values(), key=lambda r: (-r['affectedGeneratedJobs'], r['job'])))


def prepare(request, output, queue=q.QUEUE, register=False, approve=False):
    q.require(not approve or register, 'workflow_register_required')
    plan = author(request, queue)
    output.mkdir(parents=True, exist_ok=True)
    path = output / 'plan.json'
    compiler.retain(path, plan)
    manifest = compiler.compile_plan(path, output / 'compiled', queue)
    admission = compiler.register(manifest, queue, approve) if register else dict(jobs=len(manifest['jobs']), approved=False)
    return dict(version='model-decision-preparation-v1', manifest=q.relative(output / 'compiled/compiled.json'),
                admission=admission, executionStarted=False, modelAccepted=False)


def summary(report):
    lines = ['# Experiment batch status', '', 'Execution and model acceptance remain separate.', '',
             'Generated jobs: ' + ', '.join(f'{key}: {value}' for key, value in report['counts'].items()),
             report['eta'] + '. ' + report['etaReason'], '', '## Actionable requirements', '']
    for row in report['rows']:
        if row['blockers'] and row['dispatch'] not in ('waiting','branch-not-selected'):
            lines.append(f"- {row['job']} — {row['owner']}; affects {row['affectedGeneratedJobs']} generated jobs.")
            lines.extend('  - ' + str(reason).replace('\n', ' ') for reason in row['blockers'])
    waiting = [row for row in report['rows'] if row['dispatch'] == 'waiting']
    if waiting:
        lines += ['', '## Normal dependency waits', '']
        lines.extend('- ' + row['job'] + ': ' + ', '.join(row['dependencies']) for row in waiting)
    lines += ['', '## Verified decisions', '']
    decisions = [row for row in report['rows'] if row.get('decision')]
    if not decisions:
        lines.append('No verified decision is complete in this snapshot.')
    for row in decisions:
        lines.append(f"- {row['job']}: {row['decision']['outcome']}. Model acceptance is not granted.")
        for part in row['decision']['slices']:
            if part['profile'] == 'standard' and part['arm'] == 'raw-proposal':
                lines.append(f"  - Standard proposal selection: {part['gains']} gains, {part['losses']} losses, "
                             f"{part['newWrongSelections']} new wrong selections.")
    for row in report['rows']:
        if row.get('followup'):
            lines.append(f"- {row['job']}: {row['followup']}")
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['author', 'prepare', 'inspect'])
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--text', action='store_true', help='Print a readable inspection report.')
    parser.add_argument('--register', action='store_true')
    parser.add_argument('--approve-new', action='store_true')
    args = parser.parse_args()
    source = q.local_path(q.ROOT, q.relative(args.source.resolve()))
    q.require(not (args.register or args.approve_new) or args.action == 'prepare', 'workflow_prepare_required')
    q.require(not args.text or args.action == 'inspect', 'workflow_text_inspection_only')
    if args.action == 'prepare':
        q.require(args.output is not None, 'workflow_output_required')
        output = q.local_path(q.ROOT, q.relative(args.output.resolve()))
        print(json.dumps(prepare(q.load(source), output, register=args.register, approve=args.approve_new)))
        return
    result = author(q.load(source)) if args.action == 'author' else inspect(q.load(source))
    if args.output:
        output = q.local_path(q.ROOT, q.relative(args.output.resolve()))
        compiler.retain(output, result)
        print(summary(result) if args.text else json.dumps(dict(output=q.relative(output), executionChanged=False)))
    else:
        print(summary(result) if args.text else json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
