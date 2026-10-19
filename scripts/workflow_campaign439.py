"""Compile one bounded request with existing model jobs and typed follow-up branches."""
import argparse
import copy
import json
from pathlib import Path

import research_queue as q
import research_approval as approval
import model_decision_batch434 as decisions
import experiment_batch402 as batches
import hcf_templates395 as templates
import workflow_batch435 as workflow
from experiment_templates import checked, pin


def compile_request(source, destination, queue=q.QUEUE):
    request = q.load(source)
    q.require(set(request) == {'version', 'id', 'decision', 'branches'}, 'campaign_fields')
    q.require(request['version'] == 'workflow-campaign-v1' and q.ID.fullmatch(request['id']), 'campaign_version')
    choice = request['decision']
    q.require(isinstance(choice, dict) and set(choice) in ({'reuse'}, {'plan'}), 'campaign_decision')
    branches = request['branches']
    q.require(isinstance(branches, list) and 1 <= len(branches) <= 8, 'campaign_branch_limit')
    q.require(all(set(b) == {'when', 'jobs'} and b['when'] in ('supported', 'contradicted')
                  and isinstance(b['jobs'], list) and b['jobs'] for b in branches), 'campaign_branch')
    descriptions = [j for b in branches for j in b['jobs']]
    q.require(len(descriptions) <= 32, 'campaign_job_limit')
    ids = [j['id'] for j in descriptions]
    q.require(len(set(ids)) == len(ids) and all(q.ID.fullmatch(i) for i in ids), 'campaign_duplicate_id')
    destination.mkdir(parents=True, exist_ok=True)
    decisions.retain(destination/'request.json', request)
    if 'reuse' in choice:
        base = q.load(checked(choice['reuse']))
        q.require(base['version'] == 'model-decision-compiled-v1', 'campaign_reuse_version')
        checked(base['plan'])
        existing = base['existing'] + [{k:r[k] for k in ('job','specSHA256')} for r in base['jobs']]
        generated = []
        for row in existing:
            spec = q.load(queue/'jobs'/row['job']/'spec.json')
            q.require(q.text_digest(spec) == row['specSHA256'], 'campaign_existing_changed')
    else:
        decisions.retain(destination/'decision-plan.json', choice['plan'])
        base = decisions.compile_plan(destination/'decision-plan.json', destination/'decision', queue)
        existing, generated = base['existing'], list(base['jobs'])
    specs = {r['job']:q.load(checked(r['spec'])) for r in generated}
    for row in existing:
        specs[row['job']] = q.load(queue/'jobs'/row['job']/'spec.json')
    gates = [s for s in specs.values() if s.get('adapter', {}).get('steps') == ['model_decision434.decision']]
    q.require(len(gates) == 1, 'campaign_decision_count')
    gate = gates[0]
    q.require(not set(ids) & set(specs), 'campaign_job_collision')
    # A metadata-only staging queue lets the existing compiler resolve future specifications.
    # No runner uses this directory. No jobs or attempts are copied into the live queue here.
    staging = destination/'binding'
    for desc in descriptions:
        if desc.get('kind') == 'decision-audit':
            q.require(set(desc)=={'id','kind','question'} and isinstance(desc['question'],str) and len(desc['question'])>=12,'campaign_audit_fields')
            continue
        parents = {r['job'] for r in desc['inputs'].values() if 'job' in r}
        parents.update(d['job'] for d in desc.get('dependencies', []))
        for ident in parents - set(ids) - set(specs):
            q.require(q.ID.fullmatch(ident), 'campaign_parent_id')
            specs[ident] = q.load(queue/'jobs'/ident/'spec.json')
            existing.append(dict(job=ident, specSHA256=q.text_digest(specs[ident])))
    for ident, spec in specs.items():
        (staging/'jobs'/ident).mkdir(parents=True, exist_ok=True)
        decisions.retain(staging/'jobs'/ident/'spec.json', spec)
    for branch in branches:
        # Branch-local compilation prevents a downstream branch from bypassing its condition.
        authored = [d for d in branch['jobs'] if d.get('kind') != 'decision-audit']
        compiled = batches.compile_batch(dict(version='experiment-batch-v1', jobs=authored), staging) if authored else []
        audits=[]
        for desc in branch['jobs']:
            if desc.get('kind') != 'decision-audit':continue
            audits.append(dict(version='research-spec-v2',id=desc['id'],task=request['id'],owner='Maximum-mini-NUIAK',kind='screen',
                jobKind='artifact',authority='diagnostic',question=desc['question'],hypothesis=desc['question'],
                controlledComparison='Compare the same retained cases across baseline and candidate. Separate missing proposals from decision regressions.',
                decisionRule='Preserve all previous successes. Diagnose missing proposals before another classifier fit.',
                nextActionByOutcome=dict(supported='Prepare a compatible proposal comparison without model promotion.',
                    contradicted='Preserve regression cases before choosing a correction.',inconclusive='Request the missing measured evidence.'),
                inputs=[pin(q.MODULES/'workflow_loss_audit439.py')],
                dependencies=[dict(job=gate['id'],specSHA256=q.text_digest(gate),outputs=['decision.json'])],
                evidence=dict(reads=[],artifactReceipt='artifact-receipt.json'),
                adapter=dict(type='python-callable',steps=['workflow_loss_audit439.run'],outputAttributes=['workflow_loss_audit439.OUT']),
                limits=dict(timeoutSeconds=800,maxOutputBytes=100_000_000,maxAttempts=1)))
        for spec in [templates.build(desc) for desc in compiled]+audits:
            q.require(spec['authority'] in ('diagnostic','training'), 'campaign_followup_authority')
            q.require(not spec.get('conditions'), 'campaign_nested_conditions')
            deps = {d['job']:d for d in spec['dependencies']}
            dep = deps.setdefault(gate['id'], dict(job=gate['id'], specSHA256=q.text_digest(gate), outputs=[]))
            q.require(dep['specSHA256'] == q.text_digest(gate), 'campaign_gate_changed')
            dep['outputs'] = sorted(set(dep['outputs']) | {'gate.json'})
            spec['dependencies'] = list(deps.values())
            spec['conditions'] = [dict(job=gate['id'], output='gate.json', outcome=branch['when'])]
            # Internal branch dependencies must name the final, conditioned parent spec.
            for dep in spec['dependencies']:
                if dep['job'] in ids and dep['job'] in specs:
                    dep['specSHA256'] = q.text_digest(specs[dep['job']])
            q.validate(spec)
            specs[spec['id']] = spec
            path = destination/(spec['id']+'-spec.json')
            decisions.retain(path, spec)
            generated.append(dict(job=spec['id'], specSHA256=q.text_digest(spec), spec=pin(path)))
    unique = {r['job']:r for r in existing}
    manifest = dict(version='model-decision-compiled-v1', plan=pin(destination/'request.json'),
                    existing=list(unique.values()), jobs=generated, executionStarted=False, modelAccepted=False)
    decisions.retain(destination/'compiled.json', manifest)
    return manifest


def admit(manifest, queue=q.QUEUE, approved=(), *, approval_transaction=False):
    """Validate all specifications first. Approve exact IDs separately after registration."""
    q.require(manifest.get('version') == 'model-decision-compiled-v1', 'campaign_manifest_version')
    checked(manifest['plan'])
    specs = [q.load(checked(r['spec'])) for r in manifest['jobs']]
    ids = {s['id'] for s in specs}
    q.require(set(approved) <= ids and len(set(approved)) == len(approved), 'campaign_approval_ids')
    q.require(not approval_transaction or 1 <= len(approved) <= 10, 'campaign_transaction_limit')
    store = approval.load(queue)
    q.require(not any(e.get('action') == 'revoke' and e.get('job') in ids for e in store['events']), 'campaign_revoked')
    for row in manifest['existing']:
        q.require(q.text_digest(q.load(queue/'jobs'/row['job']/'spec.json')) == row['specSHA256'], 'campaign_existing_changed')
    for row, spec in zip(manifest['jobs'], specs):
        q.require(q.text_digest(spec) == row['specSHA256'], 'campaign_spec_changed')
        q.validate(spec)
        q.verify_pins(spec)
        current = queue/'jobs'/spec['id']/'spec.json'
        q.require(not current.exists() or q.load(current) == spec, 'campaign_registration_conflict')
    # Validate training logs, storage, and the entire graph before publishing any child.
    # The authoritative approval and dispatch checks still run after this snapshot.
    from workflow_admission440 import inspect
    review=inspect(manifest,queue)
    q.require(review['canRegister'],'campaign_preflight_failed:'+json.dumps(
        dict(errors=review['errors'],jobs=[r for r in review['rows'] if r['blockers']]),sort_keys=True))
    for row in manifest['jobs']:
        q.submit(checked(row['spec']), queue)
    reason='Maintainer-approved bounded workflow branch. Preserve Standard and previous successes.'
    if approval_transaction:
        from workflow_transaction441 import qualify
        exact={s['id']:q.text_digest(s) for s in specs}
        qualify(queue,[dict(job=ident,sha256=exact[ident],approver='agent:Maximum-mini-NUIAK',reason=reason)
                       for ident in approved],allow_live=True)
    else:
        for ident in approved:
            approval.approve(queue, ident, 'agent:Maximum-mini-NUIAK',reason)
    return dict(registered=len(specs), approved=list(approved), executionStarted=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--register', action='store_true')
    parser.add_argument('--approve', action='append', default=[])
    parser.add_argument('--approval-transaction', action='store_true',
                        help='Publish 1–10 individually named approvals together after all checks.')
    args = parser.parse_args()
    q.require(not (args.approve or args.approval_transaction) or args.register, 'campaign_register_required')
    source = q.local_path(q.ROOT, q.relative(args.request.resolve()))
    target = q.local_path(q.ROOT, q.relative(args.output.resolve()))
    manifest = compile_request(source, target)
    print(json.dumps(admit(manifest, approved=args.approve,approval_transaction=args.approval_transaction) if args.register else
                     dict(jobs=len(manifest['jobs']), executionStarted=False)))


if __name__ == '__main__':
    main()
