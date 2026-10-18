"""Check existing jobs and assemble reports without starting execution."""
import argparse
import json
import shutil
import re
import sys
from pathlib import Path
import research_queue as q


def check(ident, queue=q.QUEUE, modules=q.MODULES, approvals=None):
    q.require(isinstance(ident, str) and q.ID.fullmatch(ident), 'job_id')
    result = dict(job=ident, ready=False, blockers=[])
    owner = 'unknown: specification not loaded'
    def blocked(reason):
        result['blockers'].append(dict(owner=owner, requirement=str(reason)))
    try:
        spec = q.validate(q.load(queue / 'jobs' / ident / 'spec.json'), modules)
        owner = spec['owner']
        if queue == q.QUEUE and q.ROOT/'.venv-yolo' != Path(sys.prefix):
            blocked('runtime_interpreter:use_project_venv')
        result.update(owner=owner, task=spec['task'], specSHA256=q.text_digest(spec))
        for requirement in spec.get('requirements', []):
            blocked(requirement)
        q.verify_pins(spec)
        if spec['authority'] == 'training':
            run = spec['training']['experimentLogRunId']
            if not re.search(r'(?<![\w-])' + re.escape(run) + r'(?![\w-])', q.EXPERIMENT_LOG.read_text()):
                blocked('experiment_log_missing:' + run)
        q.dependency_inputs(spec, queue)
        state, _ = q.state(queue / 'jobs' / ident)
        result['state'] = state
        if state != 'pending':
            blocked('job_state:' + state)
        required = max(spec['limits']['maxOutputBytes'], spec.get('training', {}).get('storageBudgetBytes', 0)) + q.STORAGE_MARGIN
        result['storage'] = dict(requiredBytes=required, freeBytes=shutil.disk_usage(queue).free)
        if result['storage']['freeBytes'] < required:
            blocked('storage_insufficient')
        import research_approval
        if not research_approval.is_approved(queue, spec, approvals):
            blocked('not_approved')
        result['ready'] = not result['blockers']
    except (ValueError, OSError, KeyError, TypeError) as error:
        blocked(error)
    result['executionStarted'] = False
    result['limitation'] = 'Runtime ownership and capture state require fresh checks at execution.'
    return result


def report(ids, queue=q.QUEUE, modules=q.MODULES):
    q.require(isinstance(ids, list) and ids and len(ids) == len(set(ids)), 'report_membership')
    rows = [check(ident, queue, modules) for ident in ids]
    complete = all(row.get('state') == 'complete' for row in rows)
    outputs = []
    for row in rows:
        if row.get('state') != 'complete':
            continue
        for attempt in q.attempts_of(queue / 'jobs' / row['job']):
            path = attempt / 'result.json'
            if not path.exists():
                continue
            result = q.load(path)
            if result.get('status') == 'complete' and q.outputs_intact(attempt, result):
                q.require(result['specSHA256'] == row['specSHA256'], 'result_spec_changed')
                comparisons = {}
                for item in result['outputs']:
                    # BACKLOG410: read every small JSON report the attempt lists, not only 3 fixed names.
                    if (item['path'].endswith('.json') and item['path'] != 'artifact-receipt.json'
                            and item.get('bytes', 0) <= 2_000_000):
                        doc = q.load(attempt / 'out' / item['path'])
                        comparisons[item['path']] = {key: doc[key] for key in
                            ('decisions', 'summaryRows', 'againstOriginal', 'scores', 'modelAccepted', 'limitation',
                             'gains', 'lostPriorSuccesses') if isinstance(doc, dict) and key in doc}
                outputs.append(dict(job=row['job'], resultSHA256=q.digest(path), comparisons=comparisons,
                    wallSeconds=result.get('wallSeconds'), outputs=result['outputs']))
                break
    decisions = [dict(job=item['job'], report=name, decisions=doc['decisions'])
                 for item in outputs for name, doc in item['comparisons'].items() if 'decisions' in doc]
    return dict(version='research-decision-index-v1', jobs=rows, verifiedResults=outputs, candidateDecisions=decisions,
        efficiency=dict(completedJobs=len(outputs), plannedJobs=len(ids),
            measuredWorkerSeconds=sum(item.get('wallSeconds') or 0 for item in outputs),
            manualInterventions=None, providerTokens=None, hypothesisToDecisionSeconds=None,
            note='Unknown measurements remain null. Job counts are not independent experiments.'),
        executionComplete=complete, modelAccepted=False,
        decision='Review measured comparisons' if complete else 'Incomplete evidence',
        limitation='This index verifies execution evidence. It does not replace task-specific accuracy or regression reports.')


def write_campaign(task, queue=q.QUEUE, modules=q.MODULES):
    q.require(isinstance(task, str) and q.ID.fullmatch(task), 'task_id')
    ids = [p.name for p in sorted((queue / 'jobs').iterdir())
           if p.is_dir() and (p / 'spec.json').is_file() and q.load(p / 'spec.json')['task'] == task]
    value = report(ids, queue, modules)
    folder = queue / 'campaigns'; folder.mkdir(exist_ok=True)
    q.save(folder / (task + '.json'), value, replace=True)
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jobs', nargs='+')
    args = parser.parse_args()
    print(json.dumps(report(args.jobs), indent=2))
