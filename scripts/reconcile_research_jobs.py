"""Verify completed successors without changing queue specifications or attempts."""
import argparse
from pathlib import Path
import research_queue as q


def compare(old, new, kind):
    if kind == 'training':
        keys = ('epochs', 'initialization', 'membership')
        return {k: dict(old=old['training'][k], new=new['training'][k],
                        equal=old['training'][k] == new['training'][k]) for k in keys}
    if kind == 'question':
        # Non-template jobs: show the question, authority, and entry points. Inputs can differ.
        fields = dict(question=lambda s: s.get('question'), authority=lambda s: s.get('authority'),
                      steps=lambda s: s.get('adapter', {}).get('steps'))
        return {k: dict(old=f(old), new=f(new), equal=f(old) == f(new)) for k, f in fields.items()}
    q.require(kind == 'template', 'comparison_kind')
    a, b = old['template'], new['template']
    return {k: dict(old=a.get(k), new=b.get(k), equal=a.get(k) == b.get(k))
            for k in ('id', 'inputs', 'parameters')}


def reconcile(document, queue=q.QUEUE):
    q.require(document['version'] == 'research-reconciliation-v1', 'reconciliation_version')
    pairs = document['pairs']
    q.require(pairs and len({r['old'] for r in pairs}) == len(pairs), 'duplicate_source')
    rows = []
    for row in pairs:
        old, new = row['old'], row['replacement']
        q.require(q.ID.fullmatch(old) and q.ID.fullmatch(new) and old != new, 'replacement_identity')
        q.require(len(row['reason']) >= 20, 'replacement_reason')
        before, after = [q.load(queue/'jobs'/ident/'spec.json') for ident in (old, new)]
        verified = []
        for attempt in q.attempts_of(queue/'jobs'/new):
            path = attempt/'result.json'
            if not path.is_file():
                continue
            result = q.load(path)
            if result.get('status') != 'complete':
                continue
            q.require(result['specSHA256'] == q.text_digest(after), 'replacement_spec_changed')
            q.require(q.outputs_intact(attempt, result), 'replacement_outputs_changed')
            verified.append(dict(result=str(path.relative_to(queue)), sha256=q.digest(path),
                                 outputs=result['outputs'], wallSeconds=result.get('wallSeconds')))
        q.require(verified, 'replacement_not_complete:' + new)
        rows.append(dict(**row, oldSpecSHA256=q.text_digest(before),
                         replacementSpecSHA256=q.text_digest(after), verified=verified,
                         controls=compare(before, after, row['comparison'])))
    return dict(version='research-reconciliation-evidence-v1', rows=rows,
                verifiedReplacements=len({r['replacement'] for r in rows}),
                scope='Evidence only. Tasks.md owns scientific closure. Queue specifications and attempts remain unchanged.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mapping', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.relative_to(q.ROOT)
    result = reconcile(q.load(args.mapping))
    output.parent.mkdir(parents=True, exist_ok=True)
    q.save(output, result)
    print(f"Verified {len(result['rows'])} stale jobs against {result['verifiedReplacements']} completed successors.")
