"""Read receipt-backed campaign findings without importing or controlling workers."""
import hashlib
import json
import re
import html
from collections import Counter

ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def read(path, root, limit=8_000_000):
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('overview_path')
    if path.stat().st_size > limit:
        raise ValueError('overview_size')
    return json.loads(path.read_text())


def summarize(document):
    if document.get('version') not in ('model-batch-decision-v1', 'research-campaign-decision-v1', 'detector-campaign-decision-v1'):
        raise ValueError('overview_schema')
    if document.get('modelAccepted') is not False or document.get('outcome') not in ('supported', 'contradicted', 'inconclusive'):
        raise ValueError('overview_acceptance')
    rows = document.get('rows', [])
    if document.get('version') == 'detector-campaign-decision-v1':
        # This contract changes detector weights while keeping crop scoring fixed.
        rows = [dict(row, arm='detector') for row in rows]
    if not rows or len(rows) > 50000:
        raise ValueError('overview_membership')
    seen = set()
    for row in rows:
        key = (row['profile'], row['arm'], row['id'])
        if key in seen or row['profile'] not in ('standard', 'hcf'):
            raise ValueError('overview_duplicate_or_profile')
        seen.add(key)
        if any(type(row[k]) is not bool for k in ('gain', 'loss', 'newWrong', 'noFocus')):
            raise ValueError('overview_counts')
        if not row.get('group') or not isinstance(row.get('candidate'), str):
            raise ValueError('overview_group_or_outcome')
    slices = []
    for profile, arm in sorted({(r['profile'], r['arm']) for r in rows}):
        subset = [r for r in rows if (r['profile'], r['arm']) == (profile, arm)]
        slices.append(dict(profile=profile, arm=arm, observations=len(subset),
            groups=len({r['group'] for r in subset}), noFocus=sum(r['noFocus'] for r in subset),
            gains=sum(r['gain'] for r in subset), losses=sum(r['loss'] for r in subset),
            newWrong=sum(r['newWrong'] for r in subset), outcomes=dict(Counter(r['candidate'] for r in subset))))
    cases = [{k:r[k] for k in ('id','group','profile','arm','baseline','candidate','gain','loss','newWrong')}
             for r in rows if r['gain'] or r['loss'] or r['newWrong']]
    return dict(outcome=document['outcome'], modelAcceptance='not-granted', slices=slices,
        cases=cases[:1000], omittedCases=max(0,len(cases)-1000), models=document.get('models'),
        retainedFailures=len(document.get('retainedFailures', [])),
        limitation=document.get('limitation', 'Development evidence only. Independent support is not established.'),
        nextAction=document.get('nextAction', 'Review regressions and eligible inputs before another fit.'))


def campaign(entry, queue):
    ident = entry['job']
    if not isinstance(ident, str) or not ID.fullmatch(ident):
        raise ValueError('overview_identity')
    base = queue/'jobs'/ident
    spec = read(base/'spec.json', queue, 1_000_000)
    if spec.get('id') != ident or digest(spec) != entry['specSHA256']:
        raise ValueError('overview_spec_changed')
    matches = []
    last_status = 'pending'
    for attempt in sorted((base/'attempts').glob('*')):
        if not attempt.is_dir() or not (attempt/'result.json').is_file():
            continue
        result = read(attempt/'result.json', queue)
        last_status = result.get('status', 'unavailable')
        if result.get('status') != 'complete':
            continue
        if result.get('specSHA256') != entry['specSHA256']:
            raise ValueError('overview_receipt_spec')
        outputs = [o for o in result.get('outputs', []) if o.get('path') == 'decision.json']
        if len(outputs) != 1:
            raise ValueError('overview_output_missing')
        path = attempt/'out/decision.json'
        doc = read(path, queue)
        if hashlib.sha256(path.read_bytes()).hexdigest() != outputs[0]['sha256']:
            raise ValueError('overview_output_changed')
        matches.append(dict(summarize(doc), attempt=attempt.name, report=str(path.relative_to(queue)),
            execution='complete', evidence='receipt-verified; scientific review remains separate'))
    if len(matches) > 1:
        raise ValueError('overview_multiple_completed_attempts')
    return matches[0] if matches else dict(execution=last_status, evidence='unavailable', modelAcceptance='not-assessed')


def overview(config, queue):
    if config.get('version') != 'research-overview-v1' or not isinstance(config.get('campaigns'), list) or len(config['campaigns']) > 50:
        raise ValueError('overview_config')
    rows = []
    seen = set()
    for entry in config['campaigns']:
        if entry['job'] in seen:
            raise ValueError('overview_duplicate_campaign')
        seen.add(entry['job'])
        row = dict(job=entry['job'], title=entry.get('title',entry['job']), nextRequirements=entry.get('nextRequirements',[]))
        try:
            row.update(campaign(entry, queue))
        except (ValueError, OSError, KeyError, TypeError):
            row.update(execution='unavailable', evidence='verification-failed', modelAcceptance='not-assessed',
                       issue='Missing or changed campaign evidence. Inspect the pinned receipt before use.')
        rows.append(row)
    return dict(version='research-overview-v1', campaigns=rows, modelAccepted=False,
        limitation='Do not add results across campaigns. Cases and groups can overlap. HCF stays separate and optional.')


def attach(snapshot, root):
    path = root/'reports/work/RESEARCH453/overview.json'
    if not path.exists():
        snapshot['researchOverview'] = dict(campaigns=[], issue='No reviewed campaign index is configured.')
        return snapshot
    try:
        config = read(path, root, 1_000_000)
        snapshot['researchOverview'] = overview(config, root/'reports/work/research-queue')
        lanes = config.get('lanes', {})
        for row in snapshot.get('jobs', []):
            lane = lanes.get(row.get('task'))
            row['workflowLane'] = lane if lane in ('priority','reserve','conditional') else 'unassigned'
    except (ValueError, OSError, KeyError, TypeError):
        snapshot['researchOverview'] = dict(campaigns=[], issue='Campaign index validation failed. Execution is unchanged.')
    return snapshot


def markdown(value):
    def safe(text):
        return html.escape(str(text)).replace('|', '&#124;').replace('\n', ' ')
    lines=['# Combined research findings', '', safe(value['limitation']), '',
           'Standard and shipped models remain unchanged. HCF remains optional.', '']
    for row in value['campaigns']:
        lines += ['## '+safe(row['title']), '',
                  'Execution: '+safe(row['execution'])+'. Evidence: '+safe(row['evidence'])+'.',
                  'Model acceptance: '+safe(row['modelAcceptance'])+'.', '']
        if row.get('issue'):lines += [safe(row['issue']), ''];continue
        lines += ['Outcome: '+safe(row.get('outcome','pending'))+'.', '',
                  '| Profile / arm | Observations | Recorded groups | No-focus | Gains | Losses | New wrong |',
                  '|---|---:|---:|---:|---:|---:|---:|']
        for s in row.get('slices',[]):
            lines += ['| '+safe(s['profile']+'/'+s['arm'])+' | '+' | '.join(str(s[k]) for k in
                      ('observations','groups','noFocus','gains','losses','newWrong'))+' |']
        lines += ['',safe(row.get('limitation','Measurements unavailable.')), '',safe(row.get('nextAction','Wait for verified evidence.')), '']
        for requirement in row['nextRequirements']:lines += ['- '+safe(requirement)]
        lines += ['', '### Case-linked changes', '']
        for c in row.get('cases',[]):
            lines += ['- '+safe(c['id']+' / '+c['group']+' / '+c['profile']+' / '+c['arm']+': '+c['baseline']+' → '+c['candidate'])]
        lines += ['', 'Receipt source: '+safe(row.get('report','unavailable'))+'.', '']
    return '\n'.join(lines)+'\n'


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('config', type=Path)
    p.add_argument('--queue', type=Path, default=Path('reports/work/research-queue'))
    p.add_argument('--output', type=Path, required=True)
    args=p.parse_args()
    root=Path.cwd().resolve()
    if not args.output.resolve().is_relative_to(root) or args.output.exists():
        raise ValueError('overview_output_scope_or_exists')
    value=overview(read(args.config,root,1_000_000),args.queue)
    args.output.mkdir(parents=True)
    (args.output/'findings.json').write_text(json.dumps(value,indent=2)+'\n')
    (args.output/'findings.md').write_text(markdown(value))
