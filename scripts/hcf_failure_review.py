"""Compare retained HCF outcomes without new inference or training."""
from collections import Counter

import research_queue as q

OUT = None


def compare(documents):
    q.require(len(documents) >= 2, 'comparison_methods_missing')
    methods = {}
    for name, document in documents.items():
        rows = document.get('rows')
        q.require(isinstance(rows, list) and rows, 'comparison_rows_missing')
        q.require(all(row.get('outcome') in ('correct', 'wrong', 'miss') for row in rows), 'unknown_outcome')
        q.require(len({row['id'] for row in rows}) == len(rows), 'duplicate_case')
        q.require(all(row.get('role') in ('development', 'retained') for row in rows), 'comparison_role')
        methods[name] = {row['id']: row for row in rows}
    first = next(iter(methods.values()))
    for rows in methods.values():
        q.require(set(rows) == set(first), 'membership_mismatch')
        for ident, row in rows.items():
            for key in ('sha256', 'group', 'role', 'profile', 'family'):
                q.require(key in row and row[key] == first[ident][key], 'case_identity_mismatch:' + key)
    slices = []
    for name, rows in methods.items():
        for key in ('profile', 'family', 'role'):
            for value in sorted({row[key] for row in rows.values()}):
                selected = [row for row in rows.values() if row[key] == value]
                counts = Counter(row['outcome'] for row in selected)
                slices.append(dict(method=name, factor=key, value=value, frames=len(selected),
                    groups=len({row['group'] for row in selected}),
                    counts={outcome: counts[outcome] for outcome in ('correct', 'wrong', 'miss')}))
    shared_misses = sorted(ident for ident in first if all(rows[ident]['outcome'] != 'correct' for rows in methods.values()))
    disagreements = [dict(id=ident, sha256=first[ident]['sha256'], group=first[ident]['group'],
                         outcomes={name: rows[ident]['outcome'] for name, rows in methods.items()})
                     for ident in sorted(first) if len({rows[ident]['outcome'] for rows in methods.values()}) > 1]
    return dict(version='hcf-failure-review-v1', frames=len(first),
                groups=len({row['group'] for row in first.values()}), slices=slices,
                sharedMisses=shared_misses, disagreements=disagreements,
                unsupportedFactors=['size', 'contrast', 'position', 'physical-device', 'no-focus'],
                modelAccepted=False, productionChanged=False,
                nextAction='Inspect shared misses against original geometry before selecting a training correction.',
                limitation='This report compares retained predictions. It does not verify their original inference or independent trial counts.')


def run():
    dependencies = q.load(OUT / 'dependencies.json')
    documents, references = {}, []
    for dependency in dependencies:
        q.require(len(dependency['outputs']) == 1, 'one_comparison_per_method')
        reference, = dependency['outputs']
        path = q.local_path(q.ROOT, reference['path'])
        q.require(q.digest(path) == reference['sha256'], 'comparison_changed')
        documents[dependency['job']] = q.load(path)
        references.append(reference)
    q.save(OUT / 'review.json', compare(documents))
    q.save(OUT / 'sources.json', references)
