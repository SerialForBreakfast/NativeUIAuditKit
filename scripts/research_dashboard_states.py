"""Present queue lifecycle and execution readiness as separate facts."""
import json

# Reviewed successor mappings (RECONCILE407 and later). Tasks.md owns closure; these files only label display rows.
RECONCILIATIONS = 'Research/Experiments/reconciliation*.json'


def classify(row, readiness=None):
    state = row['state']
    reasons = list(row.get('requirements') or [])
    if state == 'pending':
        if readiness is None:
            return 'unchecked', ['Readiness has not been checked.']
        reasons = [b['requirement'] for b in readiness.get('blockers', [])]
        if readiness.get('ready') and not reasons:
            return 'ready', []
        if reasons and set(reasons) == {'not_approved'}:
            return 'awaiting-approval', ['Approval is required.']
        return 'blocked', reasons or ['Readiness checks did not pass.']
    return state, reasons


def successors(root):
    """Return {old job: (replacement, reason)} from the reviewed mappings. Unreadable files are skipped."""
    mapping = {}
    for path in sorted(root.glob(RECONCILIATIONS)):
        try:
            doc = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if doc.get('version') != 'research-reconciliation-v1':
            continue
        for pair in doc.get('pairs', []):
            mapping[pair['old']] = (pair['replacement'], pair['reason'])
    return mapping


def supersede(rows, mapping):
    """Label a not-complete row as superseded only when its mapped replacement is complete."""
    states = {row['job']: row['state'] for row in rows}
    for row in rows:
        replacement, reason = mapping.get(row['job'], (None, None))
        if (replacement and states.get(replacement) == 'complete'
                and row['state'] in ('pending', 'blocked', 'exhausted', 'failed')):
            row['displayState'] = 'superseded'
            row['supersededBy'] = replacement
            row['readinessReasons'] = ['Superseded by ' + replacement + '. ' + reason]


def annotate(value, queue, modules):
    from research_readiness import check
    import research_approval
    import research_queue as q
    approvals = research_approval.load(queue)
    for row in value['jobs']:
        readiness = check(row['job'], queue, modules, approvals) if row['state'] == 'pending' else None
        row['displayState'], row['readinessReasons'] = classify(row, readiness)
    supersede(value['jobs'], successors(q.ROOT))
    value['backlog'] = backlog_summary(value['jobs'], q.ROOT)
    return value


def backlog_summary(rows, root):
    """BACKLOG410 catalog view. A missing or invalid catalog hides the panel instead of failing the snapshot."""
    import backlog_pipeline
    try:
        catalog = json.loads((root / 'Research/Experiments/backlog405.json').read_text())
        return backlog_pipeline.status(catalog, rows)
    except (OSError, ValueError, KeyError):
        return None
