"""Turn admission failures into stable repair tasks. Never execute or approve jobs."""
import argparse
import hashlib
import json
from pathlib import Path
import research_queue as q
from experiment_templates import pin
import workflow_admission440 as admission

BEGIN = '<!-- FLOW478-REPAIRS:BEGIN -->'
END = '<!-- FLOW478-REPAIRS:END -->'


def tasks(reviews):
    grouped = {}
    for review in reviews:
        for row in review['rows']:
            for blocker in row['blockers']:
                reason = blocker['requirement']
                q.require(isinstance(reason, str) and reason, 'repair_requirement_missing')
                # Related consumers share one repair for a named producer.
                parts = reason.split(':')
                key = ':'.join(parts[:2]) if parts[0] in (
                    'producer_requires_review', 'dependency_output_changed',
                    'dependency_spec_changed') else reason
                owner = blocker['owner']
                q.require(owner in ('Maximum-mini-NUIAK','Maximum-mini-TTR','Sillycon-TTR',
                                    'BigDog-NUIAK','BigDog-Coordinator'), 'repair_owner_unknown')
                ident = 'REPAIR-' + hashlib.sha256((owner+'\n'+key).encode()).hexdigest()[:12]
                entry = grouped.setdefault(ident, dict(id=ident, owner=owner, requirement=key,
                    action=blocker['action'], jobs=[], priority=1,
                    acceptance='The named input passes admission. Dependent jobs become waiting or ready.',
                    executionAuthorized=False))
                if row['job'] not in entry['jobs']:
                    entry['jobs'].append(row['job'])
    for entry in grouped.values():
        entry['jobs'].sort()
        entry['priority'] = 0 if len(entry['jobs']) > 1 else 1
    return sorted(grouped.values(),key=lambda t:(t['priority'],-len(t['jobs']),t['id']))


def safe_text(value):
    """Render evidence as text, not Markdown instructions or active links."""
    return ' '.join(str(value).replace('<','(').replace('>',')').replace('`',"'")
                    .replace('[','(').replace(']',')').split())[:300]


def render(document, records):
    q.require(document.count(BEGIN) == document.count(END) and document.count(BEGIN) <= 1,
              'repair_task_markers')
    lines = [BEGIN, '## Generated repair handoff', '',
             'These tasks do not grant execution authority.',
             'Regenerate this section after reviewing the affected campaigns.', '']
    for record in records:
        # Keep detailed raw errors in the ignored report. Public tasks name only a reason code.
        code = record['requirement'].split(':',1)[0]
        if not code.replace('_','').isalnum():
            code = 'input_validation_failure'
        lines += [
            f"- [ ] **{record['id']} — P{record['priority']}: {safe_text(code)}.**",
            f"  Owner: {record['owner']}. Affected jobs: {len(record['jobs'])}.",
            '  Requirement: repair the exact failure in the local admission report.',
            '  Acceptance: the named input passes admission without weakening its checks.',
            '  Use an explicit successor when a submitted input changes.']
    if not records:
        lines.append('The reviewed campaigns have no implementation blockers.')
    lines += ['', END]
    block='\n'.join(lines)
    if BEGIN in document:
        before,rest=document.split(BEGIN)
        _,after=rest.split(END)
        return before+block+after
    return document.rstrip()+'\n\n'+block+'\n'


def run(manifests, output, task_path=None, queue=q.QUEUE):
    q.require(not output.exists(), 'repair_report_exists')
    reviews=[admission.inspect(q.load(path),queue) for path in manifests]
    records=tasks(reviews)
    result=dict(version='research-repair-handoff-v1', sources=[pin(p) for p in manifests],
                tasks=records, executionChanged=False, reviews=reviews)
    q.save(output,result)
    if task_path is not None:
        # Replace only this generated section. Do not change human-owned tasks.
        original=task_path.read_text()
        revised=render(original,records)
        q.require(task_path.read_text()==original,'repair_tasks_changed')
        task_path.write_text(revised)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifests',nargs='+',type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--update-tasks',action='store_true')
    args=parser.parse_args()
    paths=[q.local_path(q.ROOT,q.relative(p.resolve())) for p in args.manifests]
    output=q.local_path(q.ROOT,q.relative(args.output.resolve()))
    result=run(paths,output,q.ROOT/'Tasks.md' if args.update_tasks else None)
    print(json.dumps(dict(repairs=len(result['tasks']),executionChanged=False)))
