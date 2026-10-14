"""Validate cached binary predictions before reporting measured accuracy."""
import hashlib
import json
from pathlib import Path

VERSION = 'research-evidence-v1'
ARCHETYPES = ('shelf', 'grid', 'hero_detail', 'top_nav_shelf', 'settings_list', 'action_dialog', 'focus_maze')
THEMES = ('dark_standard', 'light_standard', 'dark_low_contrast')


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def checked(pin, root):
    require(isinstance(pin, dict) and set(pin) == {'path', 'sha256'}, 'evidence_pin')
    path = Path(pin['path'])
    require(not path.is_absolute() and '..' not in path.parts, 'evidence_path')
    path = root / path
    require(root.resolve() in path.resolve().parents and path.is_file(), 'evidence_file')
    require(sha(path) == pin['sha256'], 'evidence_hash')
    return path


def score(document, root):
    """Inputs use reviewed binary labels. Null predictions mean abstention."""
    require(document.get('version') == VERSION, 'evidence_version')
    require(document.get('task') in ('focus-state', 'focus-change', 'settling'), 'evidence_task')
    require(document.get('dataRole') in ('training', 'development', 'validation', 'final-audit'), 'evidence_role')
    require(document.get('labelAuthority') in ('reviewed', 'native-observed', 'authored'), 'label_authority')
    require(document.get('sourceDomain') in ('authored', 'native-fixture', 'real-app-simulator', 'physical'), 'source_domain')
    for key in ('model', 'preprocessing', 'settings', 'membership'):
        checked(document[key], root)
    rows = json.loads(checked(document['predictions'], root).read_text())
    membership = json.loads(checked(document['membership'], root).read_text())
    require(isinstance(rows, list) and rows, 'zero_support')
    require(isinstance(membership, list) and membership, 'membership_missing')
    expected = {r['id']: r for r in membership}
    require(len(expected) == len(membership), 'duplicate_membership')
    if document['dataRole'] == 'final-audit':
        selection = json.loads(checked(document['selectionMembership'], root).read_text())
        selected_groups = {g for r in selection for g in [r['group']] + r.get('ancestors', [])}
        audit_groups = {g for r in membership for g in [r['group']] + r.get('ancestors', [])}
        require(not selected_groups & audit_groups, 'selection_audit_leakage')
    ids, group_roles, pixels_roles = set(), {}, {}
    for row in membership:
        for group in [row['group']] + row.get('ancestors', []):
            require(group_roles.get(group, row['role']) == row['role'], 'cross_role_ancestry')
            group_roles[group] = row['role']
        for pin in row['inputs']:
            key = pin['sha256']
            require(pixels_roles.get(key, row['role']) == row['role'], 'cross_role_pixels')
            pixels_roles[key] = row['role']
    tp = tn = fp = fn = abstain = 0
    cells = {f'{a}/{t}': {'support': 0, 'correct': 0} for a in ARCHETYPES for t in THEMES}
    for row in rows:
        require(isinstance(row.get('id'), str) and row['id'] not in ids, 'duplicate_prediction')
        ids.add(row['id'])
        require(type(row.get('label')) is int and row['label'] in (0, 1), 'invalid_label')
        pred = row.get('prediction', 'missing')
        require(pred is None or type(pred) is int and pred in (0, 1), 'invalid_prediction')
        require(row.get('role') == document['dataRole'], 'role_mismatch')
        require(isinstance(row.get('group'), str) and row['group'], 'missing_group')
        require(row['id'] in expected, 'unknown_member')
        require(all(row.get(k) == expected[row['id']].get(k) for k in
                    ('label', 'role', 'group', 'ancestors', 'inputs', 'theme', 'archetype')), 'membership_mismatch')
        require(isinstance(row.get('inputs'), list) and row['inputs'], 'missing_inputs')
        for pin in row['inputs']:
            checked(pin, root)
        require(row.get('theme') in THEMES and row.get('archetype') in ARCHETYPES, 'missing_coverage_identity')
        cell = cells[f"{row['archetype']}/{row['theme']}"]
        cell['support'] += 1
        cell['correct'] += int(pred == row['label'])
        abstain += pred is None
        tp += pred == 1 and row['label'] == 1
        tn += pred == 0 and row['label'] == 0
        fp += pred == 1 and row['label'] == 0
        fn += pred == 0 and row['label'] == 1
    require(ids == {r['id'] for r in membership if r['role'] == document['dataRole']}, 'incomplete_predictions')
    n = len(rows)
    positives = sum(r['label'] == 1 for r in rows)
    negatives = n - positives
    return dict(version=VERSION, evidenceKind='measured', task=document['task'],
                sourceDomain=document['sourceDomain'], dataRole=document['dataRole'],
                labelAuthority=document['labelAuthority'], identities={k: document[k] for k in
                    ('model', 'preprocessing', 'settings', 'membership', 'predictions')},
                metrics=dict(accuracy=(tp + tn) / n, sample_count=n, truePositive=tp, trueNegative=tn,
                    falsePositive=fp, falseNegative=fn, abstentions=abstain, coverage=(n-abstain)/n,
                    positiveRecall=tp/positives if positives else None,
                    falsePositiveRate=fp/negatives if negatives else None,
                    falseStableAmongChanged=fn/positives if positives and document['task'] != 'focus-state' else None,
                    errorAmongStable=fn/(tn+fn) if tn+fn and document['task'] != 'focus-state' else None),
                groups=len({r['group'] for r in rows}), coverage=cells,
                limitations=['Group count does not prove independence.',
                             'This report does not establish model promotion.'])


def classification(spec, attempt):
    if 'benchmark_evaluator.run' in spec['adapter']['steps']:
        return 'placeholder', None
    if spec['kind'] == 'replay':
        return 'replay', None
    if set(spec['adapter']['steps']) & {'research_campaign340.run', 'research_cached340.run', 'research_magnitude340.run'} and attempt and (attempt/'out/diagnostic.json').exists():
        return 'cached-diagnostic', None
    path = attempt / 'out' / 'benchmark_summary.json' if attempt else None
    if path and path.exists():
        value = json.loads(path.read_text())
        contract = attempt / 'out' / 'evidence.json'
        if contract.exists():
            import research_queue
            report = score(json.loads(contract.read_text()), research_queue.ROOT)
            require(value == report, 'summary_changed')
            return 'measured', report
    return 'unverified', None
