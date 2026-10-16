"""Register reusable descriptions in dependency order. Never start a runner."""
import argparse
import copy
import json
from pathlib import Path
import research_queue as q
import hcf_templates395 as templates
import research_approval as approval
from experiment_templates import pin, checked


def compile_batch(batch, queue=q.QUEUE):
    q.require(set(batch) == {'version', 'jobs'}, 'batch_fields')
    q.require(batch['version'] == 'experiment-batch-v1', 'batch_version')
    jobs = batch['jobs']
    q.require(isinstance(jobs, list) and 0 < len(jobs) <= 100, 'batch_count')
    ids = [j['id'] for j in jobs]
    q.require(len(ids) == len(set(ids)), 'duplicate_job')
    pending = copy.deepcopy(jobs)
    specs, descriptions = {}, []
    while pending:
        progress = False
        for doc in list(pending):
            refs = doc['inputs']
            parents = {r['job'] for r in refs.values() if set(r) == {'job', 'output'}}
            parents.update(d['job'] for d in doc.get('dependencies',[]))
            if any(p in ids and p not in specs for p in parents):
                continue
            dependencies = {}
            for dep in doc.get('dependencies',[]):
                q.require(set(dep)=={'job','specSHA256','outputs'} and q.ID.fullmatch(dep['job']), 'dependency_fields')
                source=specs[dep['job']] if dep['job'] in specs else q.load(queue/'jobs'/dep['job']/'spec.json')
                q.require(dep['specSHA256']==q.text_digest(source), 'dependency_spec_changed')
                for name in dep['outputs']:q.check_name(name)
                dependencies[dep['job']]=copy.deepcopy(dep)
            for key, ref in list(refs.items()):
                if set(ref) == {'file'}:
                    refs[key] = pin(q.local_path(q.ROOT, ref['file']))
                elif set(ref) == {'job', 'attempt', 'output'}:
                    q.require(q.ID.fullmatch(ref['job']) and type(ref['attempt']) is int and ref['attempt'] > 0,
                              'attempt_identity')
                    q.check_name(ref['output'])
                    folder = queue/'jobs'/ref['job']/'attempts'/str(ref['attempt'])
                    result = q.load(folder/'result.json')
                    q.require(result['status'] == 'complete', 'producer_incomplete')
                    value = pin(folder/'out'/ref['output'])
                    q.require(any(r['path'] == ref['output'] and r['sha256'] == value['sha256']
                                  for r in result['outputs']), 'producer_output_changed')
                    refs[key] = value
                elif set(ref) == {'job', 'output'}:
                    parent = ref['job']; q.require(q.ID.fullmatch(parent), 'dependency_identity')
                    q.check_name(ref['output'])
                    source = specs[parent] if parent in specs else q.load(queue/'jobs'/parent/'spec.json')
                    dep = dependencies.setdefault(parent, dict(job=parent, specSHA256=q.text_digest(source), outputs=[]))
                    dep['outputs'].append(ref['output'])
                else:
                    checked(ref)
            doc['dependencies'] = [dict(d, outputs=sorted(set(d['outputs']))) for d in dependencies.values()]
            if doc.get('capture', {}).get('plan') == {'input':'recipe'}:
                doc['capture']['plan'] = refs['recipe']
            spec = templates.build(doc)
            existing = queue/'jobs'/doc['id']/'spec.json'
            if existing.exists():
                q.require(q.load(existing) == spec, 'immutable_job_conflict:' + doc['id'])
            specs[doc['id']] = spec
            descriptions.append(doc)
            pending.remove(next(j for j in pending if j['id'] == doc['id']))
            progress = True
        q.require(progress, 'dependency_cycle')
    return descriptions


def register_batch(batch, queue=q.QUEUE, approved=(), approver='agent:Maximum-mini-NUIAK'):
    # Validate the whole batch before the first registration or approval.
    docs = compile_batch(batch, queue)
    q.require(set(approved) <= {d['id'] for d in docs}, 'approval_outside_batch')
    results = []
    for doc in docs:
        row = templates.register(doc, queue)
        results.append(row)
    if approved:
        # Use the existing dispatch lock. Do not stop or wait on an active batch.
        lock=q.ROOT/'.build/research-queue.lock' if queue==q.QUEUE else queue/'batch-dispatch.lock'
        with q.host_lock(lock):
            for row in results:
                if row['id'] in approved:
                    approval.approve(queue, row['id'], approver,
                                     'Maintainer-approved fixed comparison. Preserve Standard and previous successes.')
                    row['approved'] = True
    return dict(jobs=results, executionStarted=False)


def inspect_batch(batch, queue=q.QUEUE):
    """Report missing requirements per branch without registering work."""
    jobs=batch['jobs']; indexed={j['id']:j for j in jobs}
    q.require(len(indexed)==len(jobs), 'duplicate_job')
    reports=[]
    for job in jobs:
        closure=set()
        def include(ident):
            if ident in closure:return
            closure.add(ident)
            for ref in indexed[ident]['inputs'].values():
                if set(ref)=={'job','output'} and ref['job'] in indexed:include(ref['job'])
        include(job['id'])
        try:
            compile_batch(dict(version=batch['version'],jobs=[j for j in jobs if j['id'] in closure]),queue)
            reports.append(dict(id=job['id'],owner=job['owner'],state='definition-valid',blocker=None))
        except (ValueError,KeyError,OSError) as error:
            reports.append(dict(id=job['id'],owner=job['owner'],state='blocked',blocker=str(error)[:500]))
    return dict(jobs=reports,executionStarted=False,
                limitation='Definition validation is not execution readiness. The queue rechecks approval, resources, and dependencies.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['inspect', 'preview', 'register'])
    parser.add_argument('batch', type=Path)
    parser.add_argument('--approve', action='append', default=[])
    parser.add_argument('--approver', default='agent:Maximum-mini-NUIAK')
    args = parser.parse_args()
    batch = q.load(args.batch)
    result = (inspect_batch(batch) if args.action=='inspect' else compile_batch(batch) if args.action == 'preview'
              else register_batch(batch, approved=args.approve, approver=args.approver))
    print(json.dumps(result, indent=2))
