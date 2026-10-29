"""Select equal-cost episode groups from verified model failures for review."""
import random
from collections import defaultdict
from pathlib import Path
import research_queue as q
from experiment_templates import checked, pin
from failure_review_sampling493 import rebuild, SUCCESS

OUT = None


def select(rows, metadata, count, seed):
    q.require(type(count) is int and count > 0 and type(seed) is int, 'episode_selection_parameters')
    groups = defaultdict(list)
    for row in rows:
        if row['candidate'] in SUCCESS:
            continue
        group = row['group']
        q.require(group in metadata, 'episode_selection_missing_group')
        groups[group].append(row)
    q.require(count <= len(groups), 'episode_selection_insufficient_groups')
    costs = set()
    categories = {}
    for group, members in groups.items():
        m = metadata[group]
        q.require(set(m) == {'episodeIDs', 'controlFamily', 'transition', 'annotationUnits', 'frameCount', 'role'}, 'episode_selection_metadata')
        q.require(m['role'] in ('train', 'development', 'evaluation', 'review_only'), 'episode_selection_role')
        q.require(m['episodeIDs'] and len(set(m['episodeIDs'])) == len(m['episodeIDs']) and m['controlFamily'] and m['transition'], 'episode_selection_identity')
        q.require(all(type(m[k]) is int and m[k] > 0 for k in ('annotationUnits', 'frameCount')), 'episode_selection_cost')
        costs.add((m['annotationUnits'], m['frameCount']))
        categories[group] = {(m['controlFamily'], m['transition'], r['candidate']) for r in members}
    # Both arms use the same pool. Do not silently remove costly or difficult groups.
    q.require(len(costs) == 1, 'episode_selection_unequal_group_costs')
    owners = {}
    for group in groups:
        for episode in metadata[group]['episodeIDs']:
            q.require(owners.setdefault(episode, group) == group, 'episode_selection_shared_ancestry')
    pool = sorted(groups)
    chosen, covered = [], set()
    while len(chosen) < count:
        group = min((g for g in pool if g not in chosen), key=lambda g: (-len(categories[g] - covered), g))
        chosen.append(group)
        covered.update(categories[group])
    random_groups = random.Random(seed).sample(pool, count)
    units, frames = next(iter(costs))
    def arm(ids):
        return dict(groups=ids, episodes=[e for g in ids for e in metadata[g]['episodeIDs']],
                    categories=[list(c) for c in sorted(set().union(*(categories[g] for g in ids)))],
                    annotationUnits=units * count, frameCount=frames * count,
                    roles={g: metadata[g]['role'] for g in ids})
    return dict(diverse=arm(chosen), random=arm(random_groups), poolGroups=pool, seed=seed,
                trainingAdmitted=False, modelImprovement=False,
                limitation='Selection coverage is not accuracy. Preserve original roles. Training needs separately qualified labels and matched training settings.')


def evaluate(request):
    q.require(set(request) == {'version', 'id', 'comparison', 'metadata', 'count', 'seed'} and request['version'] == 'sdk-episode-selection-v1' and q.ID.fullmatch(request['id']), 'episode_selection_request')
    rows = rebuild(dict(version='failure-review-input-v1', source=request['comparison']))
    return select(rows, q.load(checked(request['metadata'])), request['count'], request['seed'])


def build(path):
    request = q.load(path)
    evaluate(request)
    refs = [pin(path), request['metadata'], request['comparison']['report'], request['comparison']['result']]
    return dict(version='research-spec-v2', id=request['id'], task='SDK529', owner='Maximum-mini-NUIAK',
        kind='screen', jobKind='artifact', authority='diagnostic', dependencies=[], inputs=refs+[pin(Path(__file__))],
        adapter=dict(type='python-callable', steps=['sdk_episode_selection529.run'], outputAttributes=['sdk_episode_selection529.OUT']),
        limits=dict(timeoutSeconds=800, maxOutputBytes=100000000, maxAttempts=1),
        evidence=dict(reads=[r['path'] for r in refs], artifactReceipt='artifact-receipt.json'),
        question='Does episode diversity expose more failure categories at equal annotation and frame budgets?',
        hypothesis='Whole-group selection avoids spending the review budget on adjacent examples of one failure.',
        controlledComparison='Same verified failure pool, group ancestry, frame count, and annotation cost. Change selection only.',
        decisionRule='Report category coverage separately from accuracy. Preserve roles and require qualified labels before training.',
        nextActionByOutcome=dict(supported='Prepare matched training from eligible selected groups with equal epochs and initialization.',
            contradicted='Keep the simpler random selection and report which categories remain uncovered.',
            inconclusive='Keep selection unaccepted and identify the missing independent episodes.'))


def run():
    spec = q.load(OUT.parents[2] / 'spec.json')
    result = evaluate(q.load(checked(spec['inputs'][0])))
    q.save(OUT / 'benchmark_summary.json', dict(version='sdk-episode-selection-report-v1', **result))
    q.save(OUT / 'artifact-receipt.json', dict(version='research-artifact-v1', outputs=[dict(path='benchmark_summary.json', sha256=q.digest(OUT / 'benchmark_summary.json'))]))
